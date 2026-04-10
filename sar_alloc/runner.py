# sar_alloc/runner.py
from __future__ import annotations

"""
Runner 设计目标：
1) 简单易用，清晰 —— IDE 里改 DEV_SETTINGS 后直接点运行
2) 不依赖命令行 —— 默认不需要输入任何参数
3) 直接可运行 —— 没有实例文件也能用 demo instance 跑通 orchestrator 流程

推荐运行方式：
- IDE：打开本文件，直接 Run
- 命令行（可选）：python -m sar_alloc.runner
"""

import random
import json
import os 
import sys
import time
import traceback
import shutil
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

# ---------------------------------------------------------
# 允许直接运行该文件（而不是 -m 模式）时，自动把项目根目录加到 sys.path
# 这样 IDE “Run file” 也能正常 import sar_alloc 包
# ---------------------------------------------------------
_THIS = Path(__file__).resolve()
_PROJECT_ROOT = _THIS.parents[1]  # .../<repo_root>/sar_alloc/runner.py -> repo_root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ---------------------------------------------------------
# 业务 imports（使用绝对 import，配合上面的 sys.path 注入更稳）
# ---------------------------------------------------------
from sar_alloc.config import Config, Budget  # noqa: E40222
from sar_alloc.console import bullets, kv, section, success  # noqa: E402
from sar_alloc.models import Instance, Depot, Agent, Task  # noqa: E402
from sar_alloc.llm_client import build_llm_client  # noqa: E402
from sar_alloc.llm_orchestrator import run_orchestrator  # noqa: E402
from sar_alloc.tools import instance_summary, solution_summary  # noqa: E402

# =========================================================
# ✅ IDE 直接改这里：开发/运行参数
# =========================================================
DEV_SETTINGS: Dict[str, Any] = {
    # 目标描述（自然语言）
    "user_goal_text": "我需要抢救高价值的任务，然后在保证所有任务完成的同时尽可能减少油耗等资源浪费。",

    # 例如：data/instances/demo.json
    "instance_path": "sar_alloc/data/instances/demo/seed42_T100_A6.json",

    # 是否使用 dummy LLM （测试除大模型以外的功能用）
    "dummy_llm": False,
    "dummy_mode": "echo",

    # 若 dummy_llm=False，可在这里写真实 LLM 参数
    "llm_base_url": os.getenv("LLM_BASE_URL", "").strip(),
    "llm_api_key": os.getenv("LLM_API_KEY", "").strip(),
    "llm_model": os.getenv("LLM_MODEL", "").strip(),

    # 随机种子（会影响 init/solver 的随机行为）
    "rng_seed": random.randint(0, 2**31 - 1),

    # Orchestrator 调参轮数
    "max_agent_steps": 10,
    "max_solver_calls": 10,
    "max_stagnation_steps": 3,

    # 预算：两者任意设置其一或多个，solver 会满足“任一达到就停”
    "budget": {
        "time_limit_sec": 500.0,
        "max_iters": 10000,
    },

    # 是否写出 runs 目录文件（config/summary/solution）
    "save_runs": True,
    "runs_dir": "sar_alloc/data/runs",
}

# =========================================================
# JSON <-> Instance：实例加载（runner 内部用，尽量宽容）
# =========================================================

def _as_loc(obj: Mapping[str, Any]) -> Tuple[float, float]:
    # 支持 {x,y} / {loc:[x,y]} / {"loc":{"x":...,"y":...}}
    if "loc" in obj:
        loc = obj["loc"]
        if isinstance(loc, (list, tuple)) and len(loc) >= 2:
            return (float(loc[0]), float(loc[1]))
        if isinstance(loc, dict) and "x" in loc and "y" in loc:
            return (float(loc["x"]), float(loc["y"]))
    return (float(obj.get("x", 0.0)), float(obj.get("y", 0.0)))


def load_instance_from_json(path: str) -> Instance:
    """
    支持的 JSON schema（推荐）：
    {
      "depot": {"id":0, "x":0, "y":0},
      "agents": [
        {"id":0, "init_energy":100, "skills":["medic"], "speed":1.0,
         "travel_energy_rate":1.0, "standby_power":0.0, "skill_energy_rate":{"medic":1.0}}
      ],
      "tasks": [
        {"id":0, "x":10, "y":5, "tw_start":0, "tw_end":50, "service_time":5,
         "skill_req":["medic"], "priority":1.0}
      ],
      "default_speed": 1.0
    }
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Instance JSON not found: {p}")

    data = json.loads(p.read_text(encoding="utf-8"))

    depot_d = data.get("depot", {"id": 0, "x": 0, "y": 0})
    depot = Depot(id=int(depot_d.get("id", 0)), loc=_as_loc(depot_d))

    agents: List[Agent] = []
    for a in data.get("agents", []):
        agents.append(
            Agent(
                id=int(a["id"]),
                init_energy=float(a.get("init_energy", 0.0)),
                skills=set(a.get("skills", []) or []),
                speed=float(a.get("speed", 1.0)),
                travel_energy_rate=float(a.get("travel_energy_rate", 1.0)),
                standby_power=float(a.get("standby_power", 0.0)),
                skill_energy_rate=dict(a.get("skill_energy_rate", {}) or {}),
            )
        )

    tasks: List[Task] = []
    for t in data.get("tasks", []):
        tasks.append(
            Task(
                id=int(t["id"]),
                loc=_as_loc(t),
                tw_start=float(t.get("tw_start", 0.0)),
                tw_end=float(t.get("tw_end", 0.0)),
                service_time=float(t.get("service_time", 0.0)),
                skill_req=set(t.get("skill_req", []) or []),
                priority=float(t.get("priority", 0.0)),
            )
        )

    default_speed = float(data.get("default_speed", 1.0))
    return Instance(tasks=tuple(tasks), agents=tuple(agents), depot=depot, default_speed=default_speed)


# =========================================================
# runs 输出：便于复现实验/调参
# =========================================================

def _jsonable(x: Any) -> Any:
    if x is None:
        return None
    if callable(x) and not isinstance(x, type):
        # Skip functions and methods (but not classes)
        return None
    if is_dataclass(x):
        return asdict(x)
    if isinstance(x, set):
        return sorted(list(x))  # Convert set to sorted list
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    return x


def save_run_artifacts(
    runs_dir: str,
    *,
    cfg: Config,
    inst_sum: Dict[str, Any],
    sol_sum: Dict[str, Any],
    solution_obj: Any,
    instance_obj: Optional[Instance] = None,
    instance_path: Optional[str] = None,
    tag: str = "",
    out_dir: Optional[Path] = None,
) -> Path:
    out = out_dir if out_dir is not None else prepare_run_dir(runs_dir, tag=tag)
    out.mkdir(parents=True, exist_ok=True)

    (out / "config.json").write_text(json.dumps(_jsonable(cfg), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "instance_summary.json").write_text(json.dumps(_jsonable(inst_sum), ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "solution_summary.json").write_text(json.dumps(_jsonable(sol_sum), ensure_ascii=False, indent=2), encoding="utf-8")

    # solution_obj 通常是 AssignmentSolution：有 to_dict()
    sol_dict = solution_obj.to_dict() if hasattr(solution_obj, "to_dict") else _jsonable(solution_obj)
    (out / "solution.json").write_text(json.dumps(sol_dict, ensure_ascii=False, indent=2), encoding="utf-8")

    # 保存当前使用的 instance
    if instance_obj is not None:
        inst_dict = asdict(instance_obj)
        (out / "instance.json").write_text(json.dumps(_jsonable(inst_dict), ensure_ascii=False, indent=2), encoding="utf-8")
    elif instance_path and Path(instance_path).exists():
        # 如果提供了实例文件路径，直接复制文件
        shutil.copy2(instance_path, out / "instance.json")

    return out


def prepare_run_dir(runs_dir: str, *, tag: str = "") -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    name = f"{ts}{('-' + tag) if tag else ''}"
    out = Path(runs_dir) / name
    out.mkdir(parents=True, exist_ok=True)
    return out


def prepare_run_log_path(runs_dir: str, *, tag: str = "") -> Path:
    ts = time.strftime("%Y%m%d-%H%M%S")
    name = f"{ts}{('-' + tag) if tag else ''}.log"
    out = Path(runs_dir)
    out.mkdir(parents=True, exist_ok=True)
    return out / name


class _TeeTextStream:
    def __init__(self, primary: Any, mirror: Any) -> None:
        self._primary = primary
        self._mirror = mirror

    @property
    def encoding(self) -> str:
        return getattr(self._primary, "encoding", None) or "utf-8"

    def write(self, data: str) -> int:
        written = self._primary.write(data)
        self._mirror.write(data)
        return written

    def flush(self) -> None:
        self._primary.flush()
        self._mirror.flush()

    def isatty(self) -> bool:
        return bool(getattr(self._primary, "isatty", lambda: False)())

    def __getattr__(self, name: str) -> Any:
        return getattr(self._primary, name)


@contextmanager
def tee_console_to_file(log_path: Path):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    with log_path.open("a", encoding="utf-8") as fh:
        sys.stdout = _TeeTextStream(original_stdout, fh)
        sys.stderr = _TeeTextStream(original_stderr, fh)
        try:
            yield
        finally:
            sys.stdout.flush()
            sys.stderr.flush()
            sys.stdout = original_stdout
            sys.stderr = original_stderr


# =========================================================
# Runner 主流程（IDE 直接调用 main()）
# =========================================================

def main(settings: Optional[Dict[str, Any]] = None) -> None:
    s = dict(DEV_SETTINGS)
    if settings:
        s.update(settings)

    # ---------- 1) 准备 instance ----------
    instance_path = (s.get("instance_path") or "").strip()
    inst = load_instance_from_json(instance_path)
    inst_src = f"json:{instance_path}"


    # ---------- 2) 准备 config / budget ----------
    cfg = Config()
    cfg.rng_seed = int(s.get("rng_seed", 0))

    b = s.get("budget", {}) or {}
    budget = Budget(
        time_limit_sec=(None if b.get("time_limit_sec") is None else float(b["time_limit_sec"])),
        max_iters=(None if b.get("max_iters") is None else int(b["max_iters"])),
    )

    # ---------- 3) 准备 LLM client ----------
    dummy_llm = bool(s.get("dummy_llm", True))
    client = build_llm_client(
        dummy=dummy_llm,
        dummy_mode=str(s.get("dummy_mode", "echo")),
        base_url=(s.get("llm_base_url") or None),
        api_key=(s.get("llm_api_key") or None),
        model=(s.get("llm_model") or None),
    )

    # ---------- 4) 跑 orchestrator ----------
    user_goal_text = str(s.get("user_goal_text", "")).strip() or "minimize violation_total"
    max_agent_steps = s.get("max_agent_steps")
    max_solver_calls = s.get("max_solver_calls")
    max_stagnation_steps = int(s.get("max_stagnation_steps", 3))

    section("Runner Start", icon="🚀")
    kv("instance", inst_src, icon="📦")
    kv("dummy_llm", dummy_llm, icon="🤖")
    kv("seed", cfg.rng_seed, icon="🎲")
    kv("max_agent_steps", max_agent_steps, icon="🔁")
    kv("max_solver_calls", max_solver_calls, icon="🧮")
    kv("max_stagnation_steps", max_stagnation_steps, icon="📉")
    kv(
        "budget",
        f"time_limit_sec={budget.time_limit_sec}, max_iters={budget.max_iters}",
        icon="⏱️",
    )
    kv("goal", user_goal_text, icon="🎯")

    t0 = time.time()
    sol = run_orchestrator(
        client=client,
        instance=inst,
        user_goal_text=user_goal_text,
        config=cfg,
        budget=budget,
        rng_seed=cfg.rng_seed,
        max_agent_steps=max_agent_steps,
        max_solver_calls=max_solver_calls,
        max_stagnation_steps=max_stagnation_steps,
    )
    dt = time.time() - t0

    # ---------- 5) 打印摘要（对齐 objective_policy） ----------
    inst_sum = instance_summary(instance=inst)
    sol_sum = solution_summary(solution=sol, instance=inst, config=cfg)

    section("Run Complete", icon="🏁")
    success(f"Finished in {dt:.3f}s")
    bullets(
        "Routes",
        [f"agent {aid}: {seq}" for aid, seq in sorted(sol.routes.items(), key=lambda x: x[0])],
        icon="🛣️",
    )
    kv("unassigned_count", len(sol.unassigned), icon="📭")
    kv("unassigned", sorted(sol.unassigned), icon="📭")

    # ---------- 6) 可选：落盘 runs/<timestamp>/... ----------
    if bool(s.get("save_runs", True)):
        out = save_run_artifacts(
            s.get("runs_dir", "runs"),
            cfg=cfg,
            inst_sum=inst_sum,
            sol_sum=sol_sum,
            solution_obj=sol,
            instance_obj=inst,
            instance_path=instance_path,
            tag=("dummy" if dummy_llm else "llm"),
        )
        success(f"Artifacts saved to: {out}")


_plain_main = main


def main(settings: Optional[Dict[str, Any]] = None) -> None:
    s = dict(DEV_SETTINGS)
    if settings:
        s.update(settings)

    log_path = prepare_run_log_path(
        s.get("runs_dir", "runs"),
        tag=("dummy" if bool(s.get("dummy_llm", True)) else "llm"),
    )
    with tee_console_to_file(log_path):
        print(f"[LOG] Writing run log to: {log_path}")
        try:
            _plain_main(settings=s)
        except Exception as exc:
            print(f"[ERROR] Run failed: {exc}")
            traceback.print_exc()
            raise


# =========================================================
# 可选：命令行（你不想用也没关系）
# =========================================================
if __name__ == "__main__":
    # 默认直接用 DEV_SETTINGS，IDE/脚本点运行即可
    main()
