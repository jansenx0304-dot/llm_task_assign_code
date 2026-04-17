# sar_alloc/example_generator.py
from __future__ import annotations

"""
example_generator.py - 实例生成器（可复现实验用）

目标：
1) 生成的实例“至少存在一个完全可行解”（capability/time_window/energy 均无违规）
2) 同时具备难度：时间窗紧、能量紧、技能异质性强 -> 让 TS/ALNS/LLM 调参更有意义
3) 关键参数可调：你可以用同一套生成器做不同方向的对比实验

建议放置：
- 本文件：sar_alloc/example_generator.py
- 生成数据：sar_alloc/data/instances/{demo,benchmarks,random}/...

========================
你可以做的实验方向（建议）
========================
A. 规模扩展（Scalability）
   - n_tasks, n_agents

B. 时间窗紧约束（Time window tightness）
   - tw_late_slack（越小越难）
   - max_wait（等待窗口，影响是否允许“提前到达再等”）
   - route_overlap（不同 agent 的任务在时间上是否重叠，增加插入/交换难度）

C. 能量紧约束（Energy tightness）
   - energy_margin（越接近 0 越难；过小会出现“刚好卡边界”的可行性）
   - travel_energy_rate_range / standby_power_range / skill_energy_rate_range（不同能耗结构敏感性）

D. 技能异质性（Skill complexity / bottleneck）
   - skill_pool_size（技能种类）
   - agent_skill_frac（每个 agent 拥有技能的比例）
   - rare_skill_task_frac（“只少数 agent 能做”的任务比例，会制造瓶颈）
   - max_task_skills（任务所需技能数量，越大越难）

E. 空间结构（Spatial structure）
   - spatial_scale（地图尺度，越大路程越长 -> 时间窗/能量更紧）
   - cluster_spread（簇内离散度；小=明显聚类，更适合构造型初始解；大=更像随机散点）
   - n_clusters（通常≈n_agents；也可以设置不同以制造跨簇访问）

F. 目标冲突与策略鲁棒性（Objective tradeoff）
   - priority_skew（你可自行改 priority 分布：高优先级任务集中/分散）
   - shared_skill_task_frac（多个 agent 都能做但时窗紧 -> “选择谁做”更难）

说明：
- evaluator 的“可行性”定义：violation_total <= 1e-9，
  violation_total = capability + time_window(late) + energy(excess)。
- 未分配任务不会影响 violation_total，但会影响 missed_priority/unassigned_count。

运行：
- 在 IDE 里直接运行本文件即可生成一个 demo 实例 JSON。
"""

import json
import math
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------
# 允许直接在 IDE 里 “Run file”：
# 若以脚本方式运行（非 python -m），确保项目根目录在 sys.path，便于绝对导入 sar_alloc.*
# ---------------------------------------------------------
_THIS = Path(__file__).resolve()
_PROJECT_ROOT = _THIS.parents[1]  # .../<repo_root>/sar_alloc/example_generator.py -> repo_root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from sar_alloc.models import Agent, Depot, Instance, Task, euclidean


# -------------------------
# 可调参数（实验用）
# -------------------------
@dataclass
class GenConfig:
    # 规模
    n_tasks: int = 60
    n_agents: int = 4
    seed: int = 0

    # 空间结构
    spatial_scale: float = 80.0         # 地图尺度（坐标范围大致 [-scale, scale]）
    n_clusters: Optional[int] = None    # None -> 默认等于 n_agents
    cluster_spread: float = 12.0        # 簇内离散度（越小越聚类）

    # 时间窗难度
    tw_late_slack: float = 6.0          # tw_end = tw_start + slack（越小越紧）
    max_wait: float = 3.0               # 允许“提前到达后等待”的最大等待时间（制造等待/站立能耗）
    route_overlap: float = 0.25         # [0,1] 不同 agent 的时间起点扰动比例（越大越重叠）

    # 服务时间
    service_time_min: float = 2.0
    service_time_max: float = 360.0

    # 技能复杂度
    skill_pool_size: int = 5
    agent_skill_frac: float = 0.55      # 每个 agent 拥有技能的比例（0~1）
    task_requires_skill_prob: float = 0.85
    max_task_skills: int = 2
    rare_skill_task_frac: float = 0.25    # “瓶颈技能任务”的比例（只少数 agent 能做）
    shared_skill_task_frac: float = 0.35  # “多 agent 可做”的比例（但时窗紧 -> 选择困难）

    # 能耗/速度异质性
    speed_min: float = 0.9
    speed_max: float = 1.4
    travel_energy_rate_min: float = 0.8   # evaluator 默认按距离算 travel_energy（config.extras 未开启 per_time）
    travel_energy_rate_max: float = 1.3
    standby_power_min: float = 0.00
    standby_power_max: float = 0.05
    skill_energy_rate_min: float = 0.15
    skill_energy_rate_max: float = 0.55

    # 能量紧约束：init_energy = planned_energy * (1 + energy_margin)
    energy_margin: float = 0.005          # 越小越难（0.00~0.15 合理）


# -------------------------
# JSON 序列化（与 runner.load_instance_from_json 兼容）
# -------------------------
def instance_to_json_dict(inst: Instance) -> Dict:
    return {
        "depot": {"id": int(inst.depot.id), "x": float(inst.depot.loc[0]), "y": float(inst.depot.loc[1])},
        "agents": [
            {
                "id": int(a.id),
                "init_energy": float(a.init_energy),
                "skills": sorted(list(a.skills)),
                "speed": float(a.speed),
                "travel_energy_rate": float(a.travel_energy_rate),
                "standby_power": float(a.standby_power),
                "skill_energy_rate": {str(k): float(v) for k, v in a.skill_energy_rate.items()},
            }
            for a in inst.agents
        ],
        "tasks": [
            {
                "id": int(t.id),
                "x": float(t.loc[0]),
                "y": float(t.loc[1]),
                "tw_start": float(t.tw_start),
                "tw_end": float(t.tw_end),
                "service_time": float(t.service_time),
                "skill_req": sorted(list(t.skill_req)),
                "priority": float(t.priority),
            }
            for t in inst.tasks
        ],
        "default_speed": float(inst.default_speed),
    }


def save_instance_json(inst: Instance, out_path: str | Path) -> Path:
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(instance_to_json_dict(inst), ensure_ascii=False, indent=2), encoding="utf-8")
    return p


# -------------------------
# 生成核心：保证存在“可行参考路线”
# -------------------------
def generate_instance(cfg: GenConfig) -> Tuple[Instance, Dict[int, List[int]]]:
    """
    返回：
    - instance
    - feasible_routes: {agent_id: [task_id, ...]}  一组已知可行路线（用于你做 sanity check）
    """
    rng = random.Random(int(cfg.seed))

    # 1) skills pool
    skill_pool = [f"s{i}" for i in range(int(cfg.skill_pool_size))]

    # 2) cluster centers
    n_clusters = int(cfg.n_clusters) if cfg.n_clusters is not None else int(cfg.n_agents)
    centers: List[Tuple[float, float]] = []
    for k in range(n_clusters):
        ang = 2.0 * math.pi * (k / max(1, n_clusters))
        r = cfg.spatial_scale * 0.55
        centers.append((r * math.cos(ang), r * math.sin(ang)))

    depot = Depot(id=0, loc=(0.0, 0.0))

    # 3) create agents (init_energy 待后续回填)
    agents_tmp: List[Agent] = []
    # 先保证技能覆盖：每个 skill 至少被一个 agent 拥有
    cover_assignment = {s: rng.randrange(cfg.n_agents) for s in skill_pool}
    for aid in range(cfg.n_agents):
        skills = set()
        for s, owner in cover_assignment.items():
            if owner == aid:
                skills.add(s)
        # 再按 agent_skill_frac 补充
        for s in skill_pool:
            if s not in skills and rng.random() < cfg.agent_skill_frac:
                skills.add(s)
        if len(skills) == 0:
            skills.add(rng.choice(skill_pool))

        speed = rng.uniform(cfg.speed_min, cfg.speed_max)
        travel_energy_rate = rng.uniform(cfg.travel_energy_rate_min, cfg.travel_energy_rate_max)
        standby_power = rng.uniform(cfg.standby_power_min, cfg.standby_power_max)
        skill_energy_rate = {s: rng.uniform(cfg.skill_energy_rate_min, cfg.skill_energy_rate_max) for s in skills}

        agents_tmp.append(
            Agent(
                id=aid,
                init_energy=0.0,  # placeholder
                skills=skills,
                speed=speed,
                travel_energy_rate=travel_energy_rate,
                standby_power=standby_power,
                skill_energy_rate=skill_energy_rate,
            )
        )

    # 4) allocate task counts per agent（让每个 agent 都有任务，且总和= n_tasks）
    base = cfg.n_tasks // cfg.n_agents
    rem = cfg.n_tasks % cfg.n_agents
    counts = [base + (1 if i < rem else 0) for i in range(cfg.n_agents)]
    if min(counts) == 0:
        counts = [max(1, c) for c in counts]
        while sum(counts) > cfg.n_tasks:
            j = max(range(cfg.n_agents), key=lambda i: counts[i])
            counts[j] -= 1

    # 5) build a "reference feasible schedule" for each agent, then derive time windows from it
    tasks: List[Task] = []
    feasible_routes: Dict[int, List[int]] = {aid: [] for aid in range(cfg.n_agents)}

    tid = 0
    for aid, n_i in enumerate(counts):
        agent = agents_tmp[aid]
        center = centers[aid % n_clusters]

        # 时间起点扰动：制造不同 agent 之间的时间重叠与冲突
        start_time = rng.uniform(0.0, cfg.route_overlap * 20.0)

        cur_loc = depot.loc
        cur_time = start_time

        # 给每个 agent 一个“主方向”，让路径带一点序（但仍有随机）
        heading = rng.uniform(0.0, 2.0 * math.pi)

        for _ in range(n_i):
            step = rng.uniform(0.0, cfg.cluster_spread * 0.6)
            cx = center[0] + rng.gauss(0.0, cfg.cluster_spread) + step * math.cos(heading)
            cy = center[1] + rng.gauss(0.0, cfg.cluster_spread) + step * math.sin(heading)

            dist = euclidean(cur_loc, (cx, cy))
            t_travel = dist / (agent.speed if agent.speed > 0 else 1.0)
            arrival = cur_time + t_travel

            # 参考服务开始时间 = arrival + wait_target（<=max_wait）
            wait_target = rng.uniform(0.0, cfg.max_wait)
            service_start = arrival + wait_target

            service_time = rng.uniform(cfg.service_time_min, cfg.service_time_max)

            # 时间窗：紧约束（tw_end 接近 service_start）
            tw_start = service_start
            tw_end = service_start + cfg.tw_late_slack

            # 技能需求：保证可行（必须是该 agent skills 的子集）
            skill_req: set[str] = set()
            if rng.random() < cfg.task_requires_skill_prob:
                k = rng.randint(1, max(1, cfg.max_task_skills))
                pool = list(agent.skills)
                rng.shuffle(pool)
                skill_req = set(pool[: min(k, len(pool))])

            priority = float(rng.choice([0.0, 1.0, 2.0, 3.0]))

            tasks.append(
                Task(
                    id=tid,
                    loc=(cx, cy),
                    tw_start=tw_start,
                    tw_end=tw_end,
                    service_time=service_time,
                    skill_req=skill_req,
                    priority=priority,
                )
            )
            feasible_routes[aid].append(tid)

            cur_time = service_start + service_time
            cur_loc = (cx, cy)
            tid += 1

    # 6) 难度增强：把一部分任务改成 rare/shared 类型（仍保证参考路线可行）
    all_tids = list(range(cfg.n_tasks))
    rng.shuffle(all_tids)

    n_rare = int(cfg.rare_skill_task_frac * cfg.n_tasks)
    n_shared = int(cfg.shared_skill_task_frac * cfg.n_tasks)

    skill_owners: Dict[str, List[int]] = {s: [] for s in skill_pool}
    for a in agents_tmp:
        for s in a.skills:
            skill_owners.setdefault(s, []).append(a.id)

    rare_skill_candidates = sorted(skill_owners.keys(), key=lambda s: len(skill_owners[s]))
    common_skills = sorted(skill_owners.keys(), key=lambda s: -len(skill_owners[s]))

    rare_tids = all_tids[:n_rare]
    shared_tids = all_tids[n_rare:n_rare + n_shared]

    tasks_by_id = {t.id: t for t in tasks}

    def _replace_task(tid_: int, new_req: set[str], new_priority: float) -> None:
        t = tasks_by_id[tid_]
        tasks_by_id[tid_] = Task(
            id=t.id,
            loc=t.loc,
            tw_start=t.tw_start,
            tw_end=t.tw_end,
            service_time=t.service_time,
            skill_req=new_req,
            priority=new_priority,
        )

    # rare: 指定“稀缺技能”（同时保证参考路线对应 agent 拥有该技能）
    for tid_ in rare_tids:
        owner_aid = next(aid for aid, seq in feasible_routes.items() if tid_ in seq)
        owner_agent = agents_tmp[owner_aid]
        chosen = None
        for s in rare_skill_candidates:
            if s in owner_agent.skills:
                chosen = s
                break
        if chosen is None:
            chosen = next(iter(owner_agent.skills))
        _replace_task(tid_, {chosen}, float(rng.choice([2.0, 3.0])))

    # shared: 指定“常见技能”（多 agent 都有，但时窗仍紧 -> 分配更难）
    for tid_ in shared_tids:
        owner_aid = next(aid for aid, seq in feasible_routes.items() if tid_ in seq)
        owner_agent = agents_tmp[owner_aid]
        chosen = None
        for s in common_skills:
            if s in owner_agent.skills:
                chosen = s
                break
        if chosen is None:
            chosen = next(iter(owner_agent.skills))
        _replace_task(tid_, {chosen}, float(rng.choice([1.0, 2.0, 3.0])))

    # 7) 计算参考路线下的能量消耗，回填每个 agent 的 init_energy（保证可行但接近边界）
    agents: List[Agent] = []
    for aid in range(cfg.n_agents):
        agent = agents_tmp[aid]
        route = feasible_routes[aid]

        cur_loc = depot.loc
        cur_time = 0.0
        energy = 0.0

        for tid_ in route:
            t = tasks_by_id[tid_]
            dist = euclidean(cur_loc, t.loc)
            t_travel = dist / (agent.speed if agent.speed > 0 else 1.0)

            cur_time += t_travel
            energy += agent.travel_energy_rate * dist  # evaluator 默认按距离算

            arrival = cur_time
            if arrival < t.tw_start:
                wait = t.tw_start - arrival
                cur_time += wait
                energy += agent.standby_power * wait

            cur_time += t.service_time
            for s in (t.skill_req & agent.skills):
                energy += t.service_time * float(agent.skill_energy_rate.get(s, 1.0))

            cur_loc = t.loc

        # include depot legs（config 默认 True）
        if len(route) > 0:
            dist_back = euclidean(cur_loc, depot.loc)
            energy += agent.travel_energy_rate * dist_back

        init_energy = energy * (1.0 + float(cfg.energy_margin))
        jitter = rng.uniform(0.0, 0.02)  # 防止浮点卡边界
        init_energy = max(init_energy, energy * (1.0 + jitter))

        agents.append(
            Agent(
                id=agent.id,
                init_energy=init_energy,
                skills=set(agent.skills),
                speed=agent.speed,
                travel_energy_rate=agent.travel_energy_rate,
                standby_power=agent.standby_power,
                skill_energy_rate=dict(agent.skill_energy_rate),
            )
        )

    # 8) 打乱任务顺序：避免同一 agent 的任务在列表中连续出现（影响贪心插入等算法的公平性）
    task_order = list(range(cfg.n_tasks))
    rng.shuffle(task_order)

    inst = Instance(
        tasks=tuple(tasks_by_id[task_order[i]] for i in range(cfg.n_tasks)),
        agents=tuple(agents),
        depot=depot,
        default_speed=1.0,
    )

    return inst, feasible_routes


# -------------------------
# 可选：自检（用现有 evaluator 验证参考路线确实可行）
# -------------------------
def verify_reference_feasible(inst: Instance, routes: Dict[int, List[int]]) -> None:
    """
    使用当前代码库的 evaluator 做一次硬性自检：
    - capability/time_window/energy 均应无违规
    - is_feasible 必须为 True
    """
    from sar_alloc.config import Config
    from sar_alloc.solution import AssignmentSolution
    from sar_alloc.evaluator import evaluate

    sol = AssignmentSolution(
        routes={int(aid): list(seq) for aid, seq in routes.items()},
        unassigned=set(),
    )
    cfg = Config()  # 默认 include_depot_legs=True，travel_energy_per_time=False
    ev = evaluate(sol, inst, cfg, update_solution_schedule=True)
    if not ev.is_feasible:
        raise RuntimeError(
            "Generated instance reference routes are NOT feasible.\n"
            f"violations={ev.violations}\nmetrics={ev.metrics}"
        )


# -------------------------
# 便捷接口：生成并写入 sar_alloc/data/instances
# -------------------------
def default_output_path(tag: str = "demo", name: str = "instance") -> Path:
    root = Path(__file__).resolve().parent  # sar_alloc/
    return root / "data" / "instances" / tag / f"{name}.json"


def generate_and_save(cfg: GenConfig, out_path: Optional[str | Path] = None, tag: str = "demo") -> Path:
    inst, routes = generate_instance(cfg)
    # 生成器自检：确保至少存在一组严格可行路线
    verify_reference_feasible(inst, routes)

    if out_path is None:
        out_path = default_output_path(tag=tag, name=f"seed{cfg.seed}_T{cfg.n_tasks}_A{cfg.n_agents}")

    p = save_instance_json(inst, out_path)

    # 同目录写一个“参考可行路线”文件，便于 debug / sanity check
    route_path = Path(p).with_suffix(".routes.json")
    route_path.write_text(json.dumps({str(k): v for k, v in routes.items()}, ensure_ascii=False, indent=2), encoding="utf-8")

    return p


# -------------------------
# IDE 入口
# -------------------------
if __name__ == "__main__":
    # 你可以在 IDE 里直接改这里，然后 Run
    # 参数含义：
    # - n_tasks/n_agents: 任务数/人员数
    # - seed: 随机种子，保证复现
    # - tw_late_slack: 时间窗宽度（越小越紧）
    # - energy_margin: 初始能量冗余比例（越小越难）
    # - skill_pool_size: 技能种类数
    # - rare_skill_task_frac: 稀缺技能任务占比
    # - shared_skill_task_frac: 常见技能任务占比（时窗仍紧）
    # - spatial_scale: 地图尺度
    # - cluster_spread: 簇内离散度
    cfg = GenConfig(
        n_tasks=100,
        n_agents=6,
        seed=42,
        tw_late_slack=100.0,
        energy_margin=0.0005,
        skill_pool_size=4,
        rare_skill_task_frac=0.25,
        shared_skill_task_frac=0.35,
        spatial_scale=200.0,
        cluster_spread=500.0,
    )

    out = generate_and_save(cfg, tag="demo")
    print(f"[example_generator] saved: {out}")
