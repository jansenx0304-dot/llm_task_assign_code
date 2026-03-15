# sar_alloc/tools/llm_utils.py
"""
面向大模型的反馈工具。
将评估结果以 LLM 需要的格式返回，动态裁剪指标。
"""
from __future__ import annotations

from typing import Any, Dict

from ..config import Config
from ..models import Instance
from ..solution import AssignmentSolution
from ..evaluator import evaluate

import math
import random
from typing import Any, Dict, List, Tuple, Set

from ..models import Instance, Task, Agent

from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from ..config import Config, ObjectiveLayer, ObjectivePolicy

import json

_EPS = 1e-9

def llm_solution_summary(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    update_solution_schedule: bool = True,
) -> Dict[str, Any]:
    """
    面向大模型的"轻量反馈接口"。

    ✅ 设计目标：
    - 不改变 evaluate() 的内部输出与其他代码依赖（TS/ALNS/构造器不动）
    - 只把 LLM 需要的"目标相关信息"返回给 orchestrator
    - metrics 按 objective_policy 动态裁剪：没写进目标的指标不返回

    返回字段：
    - is_feasible: 是否严格可行
    - lex_key: 当前 objective_policy 下的字典序向量（越小越好）
    - metrics: 仅包含 policy.layers 引用到的 metric + violation_total
    - objective_layers: 当前 policy 层信息（方便 LLM 自解释/调参）
    """
    # 先调用你现有的 evaluate（保持内部逻辑一致）
    ev = evaluate(solution, instance, config, update_solution_schedule=update_solution_schedule)

    policy = config.eval.objective_policy
    layers = [ly for ly in policy.layers if ly.metric and isinstance(ly.metric, str)]
    if len(layers) > policy.max_layers:
        layers = layers[: policy.max_layers]

    # 需要暴露给 LLM 的指标集合：必含 violation_total + policy 中出现的 metrics
    needed = {"violation_total"}
    for ly in layers:
        needed.add(ly.metric)

    # 从 ev.metrics 裁剪（若某个 metric 不存在，则按 0.0 兜底）
    metrics_out: Dict[str, float] = {}
    for m in needed:
        metrics_out[m] = float(ev.metrics.get(m, 0.0))

    # 同步把层信息也回传（英文提示用在 TOOL_SPECS 里，这里保持结构化数据即可）
    objective_layers = [
        {
            "name": ly.name,
            "metric": ly.metric,
            "direction": ly.direction,
            "epsilon": float(ly.epsilon),
        }
        for ly in layers
    ]

    return {
        "is_feasible": bool(ev.is_feasible),
        "lex_key": list(ev.lex_key) if ev.lex_key is not None else [],
        "objective_layers": objective_layers,
    }


def llm_instance_summary(
    instance: Instance,
    rng_seed: int = 0,
) -> Dict[str, Any]:
    """
    LLM 用最小实例摘要（version=3），仅保留 toolchain 选择真正需要的信号：
    - 规模：n_tasks, n_agents
    - 技能：uncoverable_task_frac, hard_tasks_frac
    - 时间窗：negative_slack_frac_lb（乐观下界仍不可行比例）
    - 能量：energy_tight_frac_lb（粗下界紧迫比例）
    - 空间：cluster_strength, radius95_to_depot（含自适应聚类采样预算）
    """
    import math
    import random
    from typing import Any, Dict, List

    rng = random.Random(rng_seed)

    tasks: List[Task] = list(getattr(instance, "tasks", []))
    agents: List[Agent] = list(getattr(instance, "agents", []))

    n_tasks = len(tasks)
    n_agents = len(agents)

    # -------------------------
    # 0) 兜底：无任务或无智能体
    # -------------------------
    if n_tasks == 0 or n_agents == 0:
        return {
            "n_tasks": int(n_tasks),
            "n_agents": int(n_agents),
            "skills": {
                "uncoverable_task_frac": 0.0,
                "hard_tasks_frac": 0.0,
            },
            "time_window_risk": {
                "negative_slack_frac_lb": 0.0,
            },
            "energy_risk": {
                "energy_tight_frac_lb": 0.0,
            },
            "spatial": {
                "cluster_strength": 0.0,
                "radius95_to_depot": 0.0,
            },
        }

    depot_loc = instance.depot.loc  # (x, y)

    # -------------------------
    # 工具：技能可行
    # -------------------------
    def _can_do(agent: Agent, task: Task) -> bool:
        return set(getattr(task, "skill_req", set())).issubset(set(getattr(agent, "skills", set())))

    # -------------------------
    # 1) skills：不可覆盖比例 + 强瓶颈任务比例
    # -------------------------
    uncoverable = 0
    hard_tasks = 0  # 可执行 agent 数 <= 1 的任务占比（强瓶颈）
    for t in tasks:
        c = 0
        for a in agents:
            if _can_do(a, t):
                c += 1
        if c == 0:
            uncoverable += 1
        if c <= 1:
            hard_tasks += 1

    uncoverable_task_frac = float(uncoverable / max(1, n_tasks))
    hard_tasks_frac = float(hard_tasks / max(1, n_tasks))

    # -------------------------
    # 2) time_window_risk：负松弛下界比例（乐观仍不可行）
    # -------------------------
    negative_slack = 0
    for t in tasks:
        tw_s = float(getattr(t, "tw_start", 0.0))
        tw_e = float(getattr(t, "tw_end", 0.0))
        loc = getattr(t, "loc", depot_loc)

        best_travel = None
        for a in agents:
            # 不按技能过滤：只做紧迫性“下界粗判”，避免泄露更细过程
            try:
                tt = float(instance.travel_time(a, depot_loc, loc))
            except Exception:
                # travel_time 不可用则退化用距离作下界
                tt = float(instance.distance(depot_loc, loc))

            if best_travel is None or tt < best_travel:
                best_travel = tt

        lb_arrival = float(best_travel or 0.0)
        lb_start = max(tw_s, lb_arrival)
        if lb_start > tw_e + _EPS:
            negative_slack += 1

    negative_slack_frac_lb = float(negative_slack / max(1, n_tasks))

    # -------------------------
    # 3) energy_risk：能量紧迫下界比例（粗判）
    # -------------------------
    ENERGY_MARGIN = 0.15  # 固定内部阈值，不暴露给 LLM
    tight = 0
    for t in tasks:
        loc = getattr(t, "loc", depot_loc)
        dist = float(instance.distance(depot_loc, loc))
        service_time = float(getattr(t, "service_time", 0.0))

        best_ratio = None  # LB_energy / init_energy（越小越不紧）
        for a in agents:
            if not _can_do(a, t):
                continue
            init_e = float(getattr(a, "init_energy", 0.0))
            if init_e <= _EPS:
                continue

            travel_rate = float(getattr(a, "travel_energy_rate", 0.0))

            # 服务能耗系数（按任务所需技能取均值；缺省 1.0）
            req = set(getattr(t, "skill_req", set()))
            rate_map = getattr(a, "skill_energy_rate", {}) or {}
            ser_rates = [float(rate_map.get(sk, 1.0)) for sk in req] if req else []
            mean_skill_rate = float(sum(ser_rates) / max(1, len(ser_rates))) if ser_rates else 0.0

            # 粗下界：往返航行 + 服务（不计等待/绕行）
            lb_energy = (travel_rate * dist * 2.0) + (service_time * mean_skill_rate)
            ratio = lb_energy / init_e

            if best_ratio is None or ratio < best_ratio:
                best_ratio = ratio

        # 技能无人可做 → 已在 uncoverable 中体现，这里不重复计紧
        if best_ratio is None:
            continue

        if best_ratio > (1.0 - ENERGY_MARGIN):
            tight += 1

    energy_tight_frac_lb = float(tight / max(1, n_tasks))

    # -------------------------
    # 4) spatial：radius95 + cluster_strength（自适应采样预算）
    # -------------------------
    d_to_depot = [float(instance.distance(depot_loc, getattr(t, "loc", depot_loc))) for t in tasks]
    mean_dist_to_depot = float(sum(d_to_depot) / max(1, len(d_to_depot)))
    radius95_to_depot = float(_quantile(d_to_depot, 0.95)) if d_to_depot else 0.0

    def _adaptive_cluster_params(n: int) -> Tuple[int, int]:
        """
        固定好的默认自适应策略（无需再调）：
        - pool 约为 40*sqrt(n)，sample 约为 14*sqrt(n)
        - 上下限裁剪 + 不超过 n + sample<=pool
        """
        n = max(1, int(n))
        sqrt_n = math.sqrt(n)

        # 这组常数适合典型 SAR/任务分配规模（几十~几千）
        min_pool, max_pool = 120, 1500
        min_sample, max_sample = 60, 450

        pool = int(40.0 * sqrt_n)
        sample = int(14.0 * sqrt_n)

        pool = max(min_pool, min(max_pool, pool))
        pool = min(pool, n)
        pool = max(2, pool)

        sample = max(min_sample, min(max_sample, sample))
        sample = min(sample, pool)
        sample = max(2, sample)

        return sample, pool

    CLUSTER_SAMPLE, CLUSTER_POOL = _adaptive_cluster_params(n_tasks)

    # 为了更稳：内部做少量重复估计取均值（不增加输出字段，不暴露细节）
    REPEAT = 3 if n_tasks >= 80 else 1
    nn_vals: List[float] = []
    for k in range(REPEAT):
        rng_k = random.Random(rng_seed + 10007 * k)
        nn_vals.append(
            float(
                _mean_nearest_neighbor_distance(
                    instance=instance,
                    tasks=tasks,
                    rng=rng_k,
                    sample=CLUSTER_SAMPLE,
                    pool=CLUSTER_POOL,
                )
            )
        )

    nn_mean = float(sum(nn_vals) / max(1, len(nn_vals)))
    cluster_strength = 0.0
    if mean_dist_to_depot > _EPS:
        # 归一化后映射到 [0,1]：最近邻相对越小越聚类
        cluster_strength = 1.0 - (nn_mean / (mean_dist_to_depot + _EPS))
        cluster_strength = float(max(0.0, min(1.0, cluster_strength)))

    return {
        "version": 3,
        "n_tasks": int(n_tasks),
        "n_agents": int(n_agents),
        "skills": {
            "uncoverable_task_frac": float(uncoverable_task_frac),
            "hard_tasks_frac": float(hard_tasks_frac),
        },
        "time_window_risk": {
            "negative_slack_frac_lb": float(negative_slack_frac_lb),
        },
        "energy_risk": {
            "energy_tight_frac_lb": float(energy_tight_frac_lb),
        },
        "spatial": {
            "cluster_strength": float(cluster_strength),
            "radius95_to_depot": float(radius95_to_depot),
        },
    }


# =========================================================
# 让 LLM 修改 objective_policy 的工具函数（核心）
# =========================================================

_ALLOWED_METRICS: Dict[str, str] = {
    # feasibility / violations
    "violation_total": "Total constraint violation (0 means feasible).",
    # "violation_capability": "Skill/capability violation (missing skills count).",
    # "violation_time_window": "Time-window violation (lateness beyond tw_end).",
    # "violation_energy": "Energy violation (excess over init_energy).",
    # assignment quality
    "unassigned_count": "Number of unassigned tasks.",
    "missed_priority": "Sum of priorities of unassigned tasks.",
    # efficiency / time
    "energy_total": "Total energy used.",
    "total_distance": "Total travel distance.",
    "makespan": "Max route completion time over agents.",
}


def llm_available_metrics() -> Dict[str, Any]:
    """
    给编排器/LLM 用：返回“允许被 objective_policy 引用”的 metric 列表与释义。
    - 这个函数不依赖 instance / solution
    - 用于 prompt 生成与合法性校验
    """
    return {
        "metrics": [{"name": k, "desc": v} for k, v in _ALLOWED_METRICS.items()],
    }


def llm_apply_objective(
    config: Config,
    objective_spec: Dict[str, Any],
) -> Dict[str, Any]:
    """
    根据 LLM 产出的 objective_spec，更新 config.eval.objective_policy.layers。

    关键约束：
    - max_layers 是系统侧护栏（由 config 控制），LLM 不应调整
    - objective_spec 只接受 layers（以及每层字段）
    - 会按 config.eval.objective_policy.max_layers 自动截断
    """
    allowed = set(_ALLOWED_METRICS.keys())

    layers_in = objective_spec.get("layers", None)
    if not isinstance(layers_in, list) or len(layers_in) == 0:
        return {
            "error": "objective_spec.layers must be a non-empty list.",
            "allowed_metrics": sorted(allowed),
            "max_layers_limit": int(config.eval.objective_policy.max_layers),
        }

    # max_layers 由系统控制：忽略 objective_spec 里可能带的 max_layers
    max_layers = int(getattr(config.eval.objective_policy, "max_layers", 6))
    max_layers = max(1, max_layers)

    normalized: List[ObjectiveLayer] = []
    dropped: List[Dict[str, Any]] = []

    for i, item in enumerate(layers_in):
        if isinstance(item, str):
            metric = item
            direction = "min"
            epsilon = 0.0
            name = item
        elif isinstance(item, dict):
            metric = item.get("metric", "")
            direction = item.get("direction", "min")
            epsilon = item.get("epsilon", 0.0)
            name = item.get("name", metric or f"layer_{i}")
        else:
            dropped.append({"index": i, "reason": "layer must be str or dict", "raw": repr(item)})
            continue

        if not isinstance(metric, str) or metric not in allowed:
            dropped.append({"index": i, "reason": "unknown metric", "metric": metric})
            continue

        if direction not in ("min", "max"):
            dropped.append({"index": i, "reason": "direction must be 'min' or 'max'", "direction": direction})
            continue

        try:
            epsilon = float(epsilon)
        except Exception:
            dropped.append({"index": i, "reason": "epsilon must be float", "epsilon": epsilon})
            continue
        if epsilon < 0:
            epsilon = 0.0

        if not isinstance(name, str) or not name.strip():
            name = metric

        normalized.append(ObjectiveLayer(name=name, metric=metric, direction=direction, epsilon=epsilon))

        # 系统侧截断
        if len(normalized) >= max_layers:
            break

    if not normalized:
        return {
            "ok": False,
            "error": "No valid layers after validation.",
            "dropped_layers": dropped,
            "allowed_metrics": sorted(allowed),
            "max_layers_limit": max_layers,
        }

    config.eval.objective_policy.layers = list(normalized)

    return {
        "ok": True,
        "version": 1,
        "max_layers_limit": max_layers,
        "applied_layers": [
            {"name": ly.name, "metric": ly.metric, "direction": ly.direction, "epsilon": ly.epsilon}
            for ly in normalized
        ],
        "dropped_layers": dropped,
        "allowed_metrics": sorted(allowed),
    }


# =========================================================
# 将 LLM 给出的 solver 参数应用到 Config（与 apply_objective 同层次的工具函数）
# =========================================================

def llm_apply_solver_params(config: Config, solver_alg: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据 LLM 产出的 solver 参数，更新 config.solver.vnd 或 config.solver.alns。

    输入：
    - solver_alg: "vnd" 或 "alns"
    - params: dict，包含可调参数的增量

    返回：
    - {ok, solver_alg, applied: dict, dropped: list}
    """
    applied: Dict[str, Any] = {}
    dropped: List[Dict[str, Any]] = []

    def _clamp(v: Any, lo: float, hi: float, name: str) -> float:
        try:
            x = float(v)
        except Exception:
            dropped.append({"param": name, "reason": "not a float", "value": repr(v)})
            # 不写入，返回边界不生效，仅用于日志
            return None  # type: ignore[return-value]
        if x < lo:
            x = lo
        if x > hi:
            x = hi
        applied[name] = x
        return x

    if solver_alg == "alns":
        al = config.solver.alns
        if "destroy_frac" in params:
            val = _clamp(params["destroy_frac"], 0.02, 0.40, "destroy_frac")
            if val is not None:
                al.destroy_frac = val
        if "reaction_factor" in params:
            val = _clamp(params["reaction_factor"], 0.05, 0.40, "reaction_factor")
            if val is not None:
                al.reaction_factor = val
        if "acceptance" in params:
            acc = str(params["acceptance"]) if params["acceptance"] is not None else ""
            if acc in ("greedy", "threshold", "sa"):
                al.acceptance = acc  # type: ignore[assignment]
                applied["acceptance"] = acc
            else:
                dropped.append({"param": "acceptance", "reason": "must be greedy|threshold|sa", "value": acc})
        if "accept_level" in params:
            val = _clamp(params["accept_level"], 0.0, 1.0, "accept_level")
            if val is not None:
                al.accept_level = val
        return {"ok": True, "solver_alg": "alns", "applied": applied, "dropped": dropped}

    if solver_alg == "vnd":
        vnd = config.solver.vnd
        if "local_search_passes" in params:
            try:
                lsp = int(params["local_search_passes"])
            except Exception:
                dropped.append({"param": "local_search_passes", "reason": "not an int", "value": repr(params["local_search_passes"])})
            else:
                lsp = max(1, min(8, lsp))
                vnd.local_search_passes = lsp
                applied["local_search_passes"] = lsp
        return {"ok": True, "solver_alg": "vnd", "applied": applied, "dropped": dropped}

    # 未知算法
    dropped.append({"param": "solver_alg", "reason": "unknown", "value": repr(solver_alg)})
    return {"ok": False, "solver_alg": str(solver_alg), "applied": applied, "dropped": dropped}


# =========================================================
# 文本格式化（将 JSON/dict/list 转为分段纯文本供 prompt 使用）
# =========================================================

def format_available_metrics(spec: Dict[str, Any]) -> str:
    items = []
    mlist = spec.get("metrics", [])
    for m in mlist:
        name = str(m.get("name", ""))
        desc = str(m.get("desc", ""))
        if name:
            items.append(f"- {name}: {desc}")
    text = [
        "Available metrics:",
        *items,
    ]
    return "\n".join(text).strip()


def format_objective_layers_text(layers: List[Any]) -> str:
    lines = []
    for i, ly in enumerate(layers, start=1):
        try:
            name = getattr(ly, "name", None)
            metric = getattr(ly, "metric", None)
            direction = getattr(ly, "direction", None)
            epsilon = getattr(ly, "epsilon", None)
        except Exception:
            name = None
            metric = None
            direction = None
            epsilon = None
        if isinstance(ly, dict):
            name = ly.get("name", name)
            metric = ly.get("metric", metric)
            direction = ly.get("direction", direction)
            epsilon = ly.get("epsilon", epsilon)
        name = str(name) if name is not None else ""
        metric = str(metric) if metric is not None else ""
        direction = str(direction) if direction is not None else ""
        try:
            eps_val = float(epsilon) if epsilon is not None else 0.0
            eps_str = f"{eps_val:.2f}"
        except Exception:
            eps_str = "0.00"
        lines.append(f"{i}. {name} | metric: {metric} | direction: {direction}")
    return "\n".join(lines).strip()


def format_instance_summary(summary: Dict[str, Any]) -> str:
    """
    Format instance summary (version 3) for LLM prompt.
    Adapted to the simplified llm_instance_summary structure.
    """
    lines = []
    n_tasks = summary.get("n_tasks", 0)
    n_agents = summary.get("n_agents", 0)
    lines.append(f"- Number of tasks: {n_tasks}")
    lines.append(f"- Number of agents: {n_agents}")

    skills = summary.get("skills", {}) or {}
    lines.append("\nSkill coverage:")
    lines.append(f"- Tasks no agent can do: {skills.get('uncoverable_task_frac', 0.0):.2f}")
    lines.append(f"- Bottleneck tasks (≤1 agent capable): {skills.get('hard_tasks_frac', 0.0):.2f}")

    tw = summary.get("time_window_risk", {}) or {}
    lines.append("\nTime-window tightness:")
    lines.append(f"- Tasks infeasible even optimistically: {tw.get('negative_slack_frac_lb', 0.0):.2f}")

    er = summary.get("energy_risk", {}) or {}
    lines.append("\nEnergy constraint:")
    lines.append(f"- Tasks with tight energy budget: {er.get('energy_tight_frac_lb', 0.0):.2f}")

    sp = summary.get("spatial", {}) or {}
    lines.append("\nSpatial distribution:")
    lines.append(f"- Clustering strength (0=scattered, 1=clustered): {sp.get('cluster_strength', 0.0):.2f}")
    lines.append(f"- 95th percentile distance to depot: {sp.get('radius95_to_depot', 0.0):.2f}")
    
    return "\n".join(lines).strip()


def format_solution_summary(summary: Dict[str, Any]) -> str:
    lines = ["Solution quality:"]
    lines.append(f"- Feasible (all constraints satisfied): {bool(summary.get('is_feasible', False))}")
    lex = summary.get("lex_key", []) or []
    layers = summary.get("objective_layers", []) or []
    if layers:
        lines.append("Objective layers with values:")
        for i, ly in enumerate(layers):
            name = ly.get("name", "") if isinstance(ly, dict) else ""
            metric = ly.get("metric", "") if isinstance(ly, dict) else ""
            direction = ly.get("direction", "") if isinstance(ly, dict) else ""
            val = lex[i] if i < len(lex) else None
            try:
                val_str = f"{float(val):.2f}" if val is not None else "N/A"
            except Exception:
                val_str = str(val) if val is not None else "N/A"
            lines.append(f"- {name} | metric: {metric}: {val_str} | direction: {direction}")
    else:
        try:
            lex_str = ", ".join(f"{float(x):.2f}" for x in lex)
        except Exception:
            lex_str = ", ".join(str(x) for x in lex)
        lines.append(f"- Lexicographic key (objective layers): [{lex_str}]")

    return "\n".join(lines).strip()


# =========================================================
# 内部工具函数（不对 LLM 暴露）
# =========================================================

def _quantile(xs: List[float], q: float) -> float:
    """简单分位数（q in [0,1]），线性插值。"""
    if not xs:
        return 0.0
    q = max(0.0, min(1.0, float(q)))
    ys = sorted(float(x) for x in xs)
    n = len(ys)
    if n == 1:
        return ys[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return ys[lo]
    w = pos - lo
    return ys[lo] * (1.0 - w) + ys[hi] * w


def _mean_nearest_neighbor_distance(
    instance: Instance,
    tasks: List[Task],
    rng: random.Random,
    sample: int,
    pool: int,
) -> float:
    """
    平均最近邻距离的近似计算：
    - 小规模（<=800）时做 O(n^2) 精确最近邻
    - 大规模时：对 sample 个任务，在 pool 个候选中找最近邻（近似）
    """
    n = len(tasks)
    if n <= 1:
        return 0.0

    locs: List[Tuple[float, float]] = [getattr(t, "loc", (0.0, 0.0)) for t in tasks]

    def dist(i: int, j: int) -> float:
        return float(instance.distance(locs[i], locs[j]))

    # 精确
    if n <= 800:
        nn = []
        for i in range(n):
            best = None
            for j in range(n):
                if i == j:
                    continue
                d = dist(i, j)
                if best is None or d < best:
                    best = d
            nn.append(float(best or 0.0))
        return float(sum(nn) / max(1, len(nn)))

    # 近似
    s = min(int(sample), n)
    p = min(int(pool), n)
    idx_sample = rng.sample(range(n), s) if s < n else list(range(n))
    idx_pool = rng.sample(range(n), p) if p < n else list(range(n))

    nn = []
    pool_set = set(idx_pool)
    for i in idx_sample:
        best = None
        # 确保 pool 里有其他点
        for j in idx_pool:
            if i == j:
                continue
            d = dist(i, j)
            if best is None or d < best:
                best = d
        # 如果 pool 恰好只包含自身（极小概率），就退化随机找一个不同点
        if best is None:
            j = i
            while j == i:
                j = rng.randrange(n)
            best = dist(i, j)
        nn.append(float(best))

    return float(sum(nn) / max(1, len(nn)))

