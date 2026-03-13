# sar_alloc/evaluator.py
from __future__ import annotations

from typing import Dict, List, Tuple, Any

from .config import Config, ObjectivePolicy, ObjectiveLayer
from .models import Instance, Agent, Task
from .solution import AssignmentSolution, EvalResult


_EPS = 1e-9


def evaluate(
    solution: AssignmentSolution,
    instance: Instance,
    config: Config,
    update_solution_schedule: bool = True,
) -> EvalResult:
    """
    中文注释版：评估分配方案并给出各类指标。

    指标核心（均按最小化）：
    - violation_capability: 任务所需技能缺口的数量总和
    - violation_time_window: 迟到时间窗的超额秒数总和
    - violation_energy: 能耗超出初始能量的部分总和
    - violation_total: 上述违规项求和（用于可行性判断和字典序首层）
    - missed_priority: 未分配任务的优先级总和
    - unassigned_count: 未分配任务的数量
    - energy_total: travel_energy + standby_energy + service_energy
    - total_distance: 所有代理行驶距离之和
    - makespan: 所有代理的最大完工时间（含返仓腿）

    字典序比较：按 config.eval.objective_policy.layers 的顺序取对应指标，
    若某层 direction == "max" 则取负号以统一成"越小越好"。
    """
    # 判断能耗计算方式：True=按时间计算，False=按距离计算
    travel_energy_per_time = float(config.extras.get("travel_energy_per_time", 0.0)) > 0.5

    # 违规项累计：capability/time_window/energy
    violations: Dict[str, float] = {}

    # 全局统计变量初始化
    total_distance = 0.0    # 所有代理行驶的总距离
    total_time = 0.0        # 所有代理消耗的总时间（行驶+等待+服务）
    makespan = 0.0          # 所有代理的最大完工时间

    # 能耗细分：便于组成 energy_total
    travel_energy = 0.0     # 行驶能耗总和
    standby_energy = 0.0    # 待机（等待）能耗总和
    service_energy = 0.0    # 服务能耗总和

    # 调度计划字典：{(代理ID, 任务ID): (服务开始时间, 服务结束时间)}
    schedule = {} if update_solution_schedule else None  # 关键：不需要就别建表

    # 未分配任务相关指标
    unassigned_count = len(solution.unassigned)  # 未分配任务数量
    missed_priority = 0.0                        # 未分配任务的优先级总和
    for tid in solution.unassigned:
        t = instance.task_by_id(tid)
        missed_priority += float(t.priority)

    # 遍历所有代理，评估每个代理的任务路线
    for aid in instance.all_agent_ids():
        agent = instance.agent_by_id(aid)        # 获取当前代理对象
        route = solution.routes.get(aid, [])     # 获取当前代理的任务路线（无则为空列表）

        # 初始化代理状态：从仓库出发
        cur_loc = instance.depot.loc             # 当前位置：仓库
        cur_time = 0.0                           # 当前时间：0时刻
        agent_energy = 0.0                       # 当前代理已消耗的能量

        # 按顺序处理代理路线中的每个任务
        for tid in route:
            task = instance.task_by_id(tid)      # 获取当前任务对象

            # 1. 计算能力缺口（技能不足）
            cap_def = _capability_deficit(agent, task)
            if cap_def > 0:  # 能力缺口计入 violation_capability
                violations["capability"] = violations.get("capability", 0.0) + cap_def

            # 2. 计算从当前位置到任务位置的行驶过程
            dist = instance.distance(cur_loc, task.loc)  # 行驶距离
            t_travel = instance.travel_time(agent, cur_loc, task.loc)  # 行驶时间

            # 更新全局统计
            total_distance += dist
            cur_time += t_travel    # 代理时间推进：行驶耗时
            total_time += t_travel

            # 计算行驶能耗（按时间/距离二选一）
            if travel_energy_per_time:
                e_travel = agent.travel_energy_rate * t_travel  # 按时间计算
            else:
                e_travel = agent.travel_energy_rate * dist      # 按距离计算
            travel_energy += e_travel
            agent_energy += e_travel

            arrival = cur_time  # 到达任务地点的时间

            # 3. 处理提前到达的等待逻辑
            wait = 0.0
            if arrival < task.tw_start:  # 到达早于时间窗，累积等待与待机能耗
                wait = task.tw_start - arrival
                cur_time += wait         # 代理时间推进：等待耗时
                total_time += wait

                # 计算等待（待机）能耗
                e_wait = agent.standby_power * wait
                standby_energy += e_wait
                agent_energy += e_wait

            # 4. 处理任务服务过程
            service_start = cur_time                  # 服务开始时间
            service_end = service_start + task.service_time  # 服务结束时间
            cur_time = service_end                    # 代理时间推进：服务耗时
            total_time += task.service_time

            # 计算迟到时间（超出时间窗结束的部分）
            late = max(0.0, service_start - task.tw_end)
            if late > 0:  # 迟到时间计入 violation_time_window
                violations["time_window"] = violations.get("time_window", 0.0) + late

            # 计算服务能耗（基于任务所需技能）
            e_service = _service_energy(agent, task)
            service_energy += e_service
            agent_energy += e_service

            # 记录该任务的调度时间
            if schedule is not None:
                schedule[(aid, tid)] = (service_start, service_end)

            # 更新代理当前位置为任务位置
            cur_loc = task.loc

        # 5. 处理返回仓库的路段（如果配置启用且代理有任务路线）
        if config.eval.include_depot_legs and len(route) > 0:
            dist_back = instance.distance(cur_loc, instance.depot.loc)  # 返回仓库的距离
            t_back = instance.travel_time(agent, cur_loc, instance.depot.loc)  # 返回时间

            # 更新全局统计
            total_distance += dist_back
            cur_time += t_back    # 代理时间推进：返程耗时
            total_time += t_back

            # 计算返程能耗
            if travel_energy_per_time:
                e_back = agent.travel_energy_rate * t_back
            else:
                e_back = agent.travel_energy_rate * dist_back
            travel_energy += e_back
            agent_energy += e_back

        # 6. 能耗违规：消耗超出初始能量的部分计入 violation_energy
        # 使用 _EPS 防止浮点抖动
        if agent_energy - agent.init_energy > _EPS:
            excess_energy = agent_energy - agent.init_energy
            violations["energy"] = violations.get("energy", 0.0) + excess_energy

        # 7. 记录该代理的完工时间，更新全局 makespan
        makespan = max(makespan, cur_time)

    # 计算违规项总和（用于字典序排序）
    violation_total = sum(violations.values()) if violations else 0.0

    # 判断解是否可行：违规总和小于等于精度阈值视为可行
    is_feasible = violation_total <= _EPS

    # 构建指标字典：后续字典序与记录使用
    total_energy = travel_energy + standby_energy + service_energy
    metrics: Dict[str, float] = {
        "violation_total": float(violation_total),
        "violation_capability": float(violations.get("capability", 0.0)),
        "violation_time_window": float(violations.get("time_window", 0.0)),
        "violation_energy": float(violations.get("energy", 0.0)),
        "missed_priority": float(missed_priority),
        "unassigned_count": float(unassigned_count),
        "energy_total": float(total_energy),
        "total_distance": float(total_distance),
        "makespan": float(makespan),
    }

    # 按 layers 顺序生成"越小越好"的字典序键
    lex_key = _build_lex_key(metrics, config)

    # 构建评估结果对象（最小化字段）
    ev = EvalResult(
        is_feasible=bool(is_feasible),
        violations=dict(violations),
        metrics=metrics,
        lex_key=lex_key,
    )

    # 如果配置要求，将调度计划更新到解决方案对象中
    if update_solution_schedule and schedule is not None:
        solution.schedule = schedule
    # 将评估结果关联到解决方案对象
    solution.eval = ev
    
    # 返回评估结果
    return ev


def _build_lex_key(metrics: Dict[str, float], config: Config) -> Tuple[float, ...]:
    """
    根据 config.eval.objective_policy.layers 生成字典序比较向量。
    向量中的每个元素对应一个目标层（按 direction 调整符号）。
    """
    policy = config.eval.objective_policy
    layers = _validated_layers(policy, config)
    
    key_values: List[float] = []
    for layer in layers:
        value = metrics.get(layer.metric, 0.0)
        # 若优化方向是"max"，反转为"min"（统一成最小化）
        if layer.direction == "max":
            value = -value
        key_values.append(float(value))
    
    return tuple(key_values)


def compare(a: EvalResult, b: EvalResult, config: Config) -> int:
    """
    对比两个方案的评估结果，判定哪个方案更优。
    返回值说明：
      -1: 方案a 优于 方案b
       0: 两个方案打平
       1: 方案b 优于 方案a

    对比策略：仅使用字典序（按预设层级依次对比，含 epsilon 容差）。
    第一层已经是 violation_total（总违规），自动实现"可行性优先"。
    """
    # 获取配置的对比策略
    policy = config.eval.objective_policy
    layers = _validated_layers(policy, config)

    # 按预设层级依次对比（一层定胜负，打平则继续下一层）
    for layer in layers:
        # 获取当前层级要对比的指标值
        va = a.get_metric(layer.metric)
        vb = b.get_metric(layer.metric)

        # 计算差值（va - vb），并根据优化方向调整
        diff = va - vb
        if layer.direction == "max":
            # 若优化方向是max（越大越好），反转差值
            diff = -diff

        # 结合容错阈值（epsilon）判断：差值超出阈值才判定胜负
        if diff < -layer.epsilon - _EPS:
            # a的指标更优
            return -1
        if diff > layer.epsilon + _EPS:
            # b的指标更优
            return 1

    # 所有层级都打平 → 返回 0（完全相等）
    return 0


# --------------------------
# Internal helpers
# --------------------------

def _capability_deficit(agent: Agent, task: Task) -> float:
    """
    检查智能体是否具有任务所需的所有能力。
    采用二元模型：只要智能体具有对应的能力就可以，无需考虑能力程度。
    
    如果任务需要的所有能力在智能体的技能集合中都有，则缺口为0。
    否则，返回任务所需的缺失能力个数（作为缺口）。
    """
    missing_skills = task.skill_req - agent.skills
    return float(len(missing_skills))  # 缺失能力个数作为缺口


def _service_energy(agent: Agent, task: Task) -> float:
    """
    基于所需技能和服务时间计算服务能耗。
    对于任务所需的每个技能，如果代理具备该技能，则能耗 = 服务时间 × 该技能的能耗系数。
    总服务能耗 = 各技能能耗之和。
    
    例如：任务需要技能1（能耗系数0.5），服务时间20，则能耗 = 20 × 0.5 = 10。
    """
    total_energy = 0.0
    # 计算任务所需技能中，智能体具有的技能
    required_and_have = task.skill_req & agent.skills
    
    for skill in required_and_have:
        # 获取该技能的能耗系数，默认为1.0
        energy_rate = agent.skill_energy_rate.get(skill, 1.0)
        # 能耗 = 服务时间 × 能耗系数
        total_energy += task.service_time * energy_rate
    
    return total_energy


def _validated_layers(policy: ObjectivePolicy, config: Config):
    """
    Apply simple guardrails: truncate, drop empty metric names.
    (More complex validation can be done in orchestrator; keep evaluator deterministic.)
    """
    layers = [ly for ly in policy.layers if ly.metric and isinstance(ly.metric, str)]
    if len(layers) > policy.max_layers:
        layers = layers[: policy.max_layers]
    return layers
