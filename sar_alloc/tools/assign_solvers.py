# sar_alloc/tools/assign_solvers.py
from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..config import Budget, Config
from ..console import success
from ..evaluator import compare, evaluate as _evaluate_raw
from ..models import Instance, Location
from ..solution import AssignmentSolution, EvalResult

# =========================================================
# evaluate 全局打点（覆盖本模块内所有 evaluate 调用）
# =========================================================
# 目的：
# - 你在调参/做性能分析时，经常需要知道“每轮迭代里 evaluate 占比多少”
# - 这里用一个轻量 wrapper 统计 evaluate 调用次数与累计耗时
# 注意：
# - 仅影响本模块内调用 evaluate 的位置；不会影响别的模块
# =========================================================

@dataclass
class _EvalStats:
    n: int = 0       # evaluate 调用次数
    t: float = 0.0   # evaluate 累计耗时（秒）


EVAL_STATS = _EvalStats()


def evaluate(*args, **kwargs):  # noqa: F811  (覆盖同名导入)
    """本模块内统一用该 evaluate，以便统计性能。"""
    t0 = time.perf_counter()
    ev = _evaluate_raw(*args, **kwargs)
    dt = time.perf_counter() - t0
    EVAL_STATS.n += 1
    EVAL_STATS.t += dt
    return ev


# =========================================================
# 公共入口
# =========================================================

def solve_assignment(
    instance: Instance,
    init_solution: AssignmentSolution,
    config: Config,
    budget: Budget,
    rng_seed: int = 0,
) -> AssignmentSolution:
    """Run the ALNS search loop from the given initial solution."""
    rng = random.Random(int(rng_seed))

    cur = init_solution.clone(deep=True)
    cur.normalize(instance)
    cur_ev = evaluate(cur, instance, config, update_solution_schedule=False)

    best = cur.clone(deep=True)
    best_ev = cur_ev
    return _solve_alns(instance, cur, cur_ev, best, best_ev, config, budget, rng)



# =========================================================
# ALNS (Adaptive Large Neighborhood Search)
# =========================================================

DestroyOp = Callable[[AssignmentSolution, Instance, Config, random.Random], List[int]]
RepairOp = Callable[[AssignmentSolution, List[int], Instance, Config, random.Random], AssignmentSolution]


def _attach_solver_diagnostics(solution: AssignmentSolution, diagnostics: Dict[str, Any]) -> AssignmentSolution:
    solution.solver_diagnostics = diagnostics
    return solution


def _build_solver_diagnostics(
    *,
    algorithm: str,
    total_iters: int,
    best_update_iters: List[int],
    best_update_lex_keys: List[List[float]],
    returned_solution_source: str,
    initial_solution_feasible: bool,
    returned_solution_feasible: bool,
) -> Dict[str, Any]:
    last_best_iter = best_update_iters[-1] if best_update_iters else None
    return {
        "algorithm": algorithm,
        "total_iters": int(total_iters),
        "best_update_count": len(best_update_iters),
        "best_update_iters": [int(x) for x in best_update_iters],
        "best_update_lex_keys": [list(x) for x in best_update_lex_keys],
        "first_best_iter": int(best_update_iters[0]) if best_update_iters else None,
        "last_best_iter": int(last_best_iter) if last_best_iter is not None else None,
        "plateau_iters_after_last_update": int(total_iters - last_best_iter) if last_best_iter is not None else int(total_iters),
        "initial_solution_feasible": bool(initial_solution_feasible),
        "returned_solution_source": returned_solution_source,
        "returned_solution_feasible": bool(returned_solution_feasible),
    }


def _solve_alns(
    instance: Instance,
    cur: AssignmentSolution,
    cur_ev: EvalResult,
    best: AssignmentSolution,
    best_ev: EvalResult,
    config: Config,
    budget: Budget,
    rng: random.Random,
) -> AssignmentSolution:
    """
    ALNS 主循环（参数尽量少，工程上好调）：

    - destroy_frac：销毁强度（按“当前已分配任务数”的比例）
    - reaction_factor：算子权重更新反应因子
    - acceptance：greedy / threshold / sa
    - accept_level：对“软层变差/不可行小幅反复”的容忍度（0~1）

    设计要点：
    1) destroy/repair 都是“算子集合”，每轮轮盘赌采样；
    2) 采用 Deb's feasibility rules 做比较（可行性优先）；
    3) 允许在“都可行”或“都不可行”场景下用 threshold/SA 放宽；
    4) 周期性触发可行性恢复（保险丝），保证最终能输出可行解的概率。
    """
    alns_cfg = config.solver.alns

    destroy_ops: Dict[str, DestroyOp] = {
        "random_remove": _destroy_random_remove,
        "worst_remove": _destroy_worst_remove,
        "segment_remove": _destroy_segment_remove,
    }
    repair_ops: Dict[str, RepairOp] = {
        # ✅ 去掉 Top-K：这两个 repair 都会尝试“所有 agent + 所有插入位置”
        "greedy_insert": _repair_greedy_insert,
        "regret2_insert": _repair_regret2_insert,
    }

    # 初始权重：都设 1，靠后续反馈自适应
    d_w = {k: 1.0 for k in destroy_ops}
    r_w = {k: 1.0 for k in repair_ops}

    # “一段”长度：每 segment_len 轮做一次权重更新
    if budget.max_iters is not None:
        segment_len = _clamp_int(int(0.10 * int(budget.max_iters)), 10, 200)
    else:
        segment_len = 50

    reaction = float(alns_cfg.reaction_factor)

    # SA 温度：用 accept_level 映射，避免引入更多超参
    accept_level = float(alns_cfg.accept_level)
    T = 0.05 + 0.50 * accept_level
    cooling = _clamp_float(0.999 - 0.02 * accept_level, 0.90, 0.9999)

    it = 0
    t0 = time.time()

    # 维护“最优可行解”：最终优先返回它
    best_feas: Optional[AssignmentSolution] = best.clone(deep=True) if best_ev.is_feasible else None
    best_feas_ev: Optional[EvalResult] = best_ev if best_ev.is_feasible else None

    # 不可行连续次数超过阈值，就触发一次恢复
    best_update_iters: List[int] = []
    best_update_lex_keys: List[List[float]] = []
    restore_every = _clamp_int(int(30 + 70 * (1.0 - accept_level)), 20, 120)
    infeas_streak = 0

    # 算子反馈统计：用于权重更新
    d_score = {k: 0.0 for k in destroy_ops}
    r_score = {k: 0.0 for k in repair_ops}
    d_used = {k: 0 for k in destroy_ops}
    r_used = {k: 0 for k in repair_ops}

    while _budget_ok(budget, t0, it):
        # ---- 本轮统计（可选打印）----
        iter_t0 = time.perf_counter()
        iter_eval_n0 = EVAL_STATS.n
        iter_eval_t0 = EVAL_STATS.t

        it += 1
        # if it % 20 == 0:
            # print(f"ALNS Iteration {it}")

        d_name = _roulette_select(d_w, rng)
        r_name = _roulette_select(r_w, rng)
        d_used[d_name] += 1
        r_used[r_name] += 1

        # ---- 1) 销毁：按 destroy_frac * 已分配任务数 计算强度 ----
        n_assigned = len(list(cur.all_assigned_tasks()))
        strength = _clamp_int(
            int(alns_cfg.destroy_frac * max(1, n_assigned)),
            1,
            min(50, max(1, n_assigned)),
        )

        removed = destroy_ops[d_name](cur, instance, config, rng)
        if len(removed) > strength:
            removed = removed[:strength]

        partial = cur.clone(deep=True)
        _remove_tasks(partial, removed)
        partial.normalize(instance)

        # ---- 2) repair 任务池：统一用 partial.unassigned（包含本轮移除 + 之前遗留未分配）----
        pool_all = list(partial.unassigned)

        # endgame: 未分配很少时，直接全量尝试
        if len(pool_all) <= 5:
            candidates = pool_all
        else:
            candidates = _select_repair_candidates(pool_all, strength, instance, rng)

        trial = repair_ops[r_name](partial, candidates, instance, config, rng)
        trial.normalize(instance)

        ev_trial = evaluate(trial, instance, config, update_solution_schedule=False)

        # ---- 3) 接受准则：Deb + threshold/SA（可行性优先）----
        accepted = _alns_accept(
            cur_ev=cur_ev,
            trial_ev=ev_trial,
            config=config,
            mode=alns_cfg.acceptance,
            rng=rng,
            T=T,
            accept_level=accept_level,
        )

        if accepted:
            cur = trial
            cur_ev = ev_trial

        infeas_streak = 0 if cur_ev.is_feasible else (infeas_streak + 1)

        # ---- 4) 保险丝：周期性/连续不可行过久 -> 强制往可行域拉回 ----
        if (not cur_ev.is_feasible) and (infeas_streak >= restore_every or it % restore_every == 0):
            cur = _restore_feasibility(cur, instance, config, rng, max_remove=8)
            cur.normalize(instance)
            cur_ev = evaluate(cur, instance, config, update_solution_schedule=False)
            infeas_streak = 0 if cur_ev.is_feasible else 1

        # ---- 5) 更新 best（全局最优，不一定可行）与算子得分 ----
        if compare(ev_trial, best_ev, config) < 0:
            best = trial.clone(deep=True)
            best_ev = ev_trial
            d_score[d_name] += 5.0
            r_score[r_name] += 5.0
        elif accepted:
            # 接受但没刷新全局最优：给一点小奖励，避免权重塌缩
            d_score[d_name] += 0.2
            r_score[r_name] += 0.2

        # ---- 6) 维护 best_feasible（最终输出的候选）----
        if ev_trial.is_feasible:
            if best_feas_ev is None or compare(ev_trial, best_feas_ev, config) < 0:
                best_feas = trial.clone(deep=True)
                best_feas_ev = ev_trial
                best_update_iters.append(it)
                best_update_lex_keys.append(list(best_feas_ev.lex_key or ()))
                success(f"ALNS found a new best feasible solution at iter={it}, lex_key={best_feas_ev.lex_key}")

        # ---- 7) SA 降温 ----
        if alns_cfg.acceptance == "sa":
            T = max(1e-9, T * cooling)

        # ---- 8) 分段更新权重 ----
        if it % segment_len == 0:
            _update_weights(d_w, d_score, d_used, reaction)
            _update_weights(r_w, r_score, r_used, reaction)
            for k in d_score:
                d_score[k] = 0.0
                d_used[k] = 0
            for k in r_score:
                r_score[k] = 0.0
                r_used[k] = 0

        # ---- 本轮统计输出（默认关闭，避免刷屏）----
        iter_total_time = time.perf_counter() - iter_t0
        iter_eval_count = EVAL_STATS.n - iter_eval_n0
        iter_eval_time = EVAL_STATS.t - iter_eval_t0
        _ = (iter_eval_time / iter_total_time * 100) if iter_total_time > 0 else 0.0
        # print(f"  iter={it} total={iter_total_time:.4f}s evals={iter_eval_count} eval_time={iter_eval_time:.4f}s eval_ratio={_:.1f}%")

    # 结束：优先返回 best_feasible
    if best_feas is not None:
        evaluate(best_feas, instance, config, update_solution_schedule=True)
        return _attach_solver_diagnostics(
            best_feas,
            _build_solver_diagnostics(
                algorithm="alns",
                total_iters=it,
                best_update_iters=best_update_iters,
                best_update_lex_keys=best_update_lex_keys,
                returned_solution_source="best_feasible",
                initial_solution_feasible=best_ev.is_feasible,
                returned_solution_feasible=True,
            ),
        )

    evaluate(best, instance, config, update_solution_schedule=True)
    return _attach_solver_diagnostics(
        best,
        _build_solver_diagnostics(
            algorithm="alns",
            total_iters=it,
            best_update_iters=best_update_iters,
            best_update_lex_keys=best_update_lex_keys,
            returned_solution_source="best_overall",
            initial_solution_feasible=best_ev.is_feasible,
            returned_solution_feasible=bool(getattr(best.eval, "is_feasible", False)),
        ),
    )


# =========================================================
# 接受准则：Deb +（threshold / SA）
# =========================================================

def _alns_accept(
    cur_ev: EvalResult,
    trial_ev: EvalResult,
    config: Config,
    mode: str,
    rng: random.Random,
    T: float,
    accept_level: float,
) -> bool:
    """
    接受规则的目标是“可行性优先 + 允许一定探索”。

    Deb's rules（主框架）：
    1) 都可行：用 compare（你的字典序/分层策略）比优劣
    2) 一可行一不可行：永远偏向可行（不允许从可行掉回不可行）
    3) 都不可行：优先降低 violation_total；若差不多，再 compare 细分

    mode 扩展：
    - greedy：只接受 Deb 意义下更好的 trial
    - threshold：允许软层或 violation_total “小幅变差”
    - sa：按 exp(-Δ/T) 概率接受变差（Δ 用相对比例）
    """
    tol = 1e-9

    # 1) Deb 意义下更好：直接接受
    if _deb_compare_eval(trial_ev, cur_ev, config, tol=tol) < 0:
        return True

    if mode == "greedy":
        return False

    # 2) 可行/不可行混合：禁止从可行掉回不可行
    if cur_ev.is_feasible and (not trial_ev.is_feasible):
        return False
    if (not cur_ev.is_feasible) and trial_ev.is_feasible:
        return True

    # 3) threshold / sa 放宽
    # 3.1 都可行：只对“软层指标”放宽（不破坏可行性）
    if cur_ev.is_feasible and trial_ev.is_feasible:
        soft_cur = _soft_metric_value(cur_ev, config, fallback_metric="energy_total")
        soft_trial = _soft_metric_value(trial_ev, config, fallback_metric="energy_total")

        denom = max(1.0, abs(soft_cur))
        delta_ratio = (soft_trial - soft_cur) / denom  # >0 表示变差（假定越小越好）

        if mode == "threshold":
            thr = 0.01 + 0.12 * float(accept_level)  # 约 1%~13%
            return delta_ratio <= thr

        if mode == "sa":
            if delta_ratio <= 0:
                return True
            p = math.exp(-delta_ratio / max(1e-12, T))
            return rng.random() < p

        return False

    # 3.2 都不可行：以 violation_total 作为“主指标”放宽
    v_cur = float(cur_ev.get_metric("violation_total"))
    v_trial = float(trial_ev.get_metric("violation_total"))

    denom = max(1.0, abs(v_cur))
    delta_ratio = (v_trial - v_cur) / denom

    if mode == "threshold":
        thr = 0.005 + 0.06 * float(accept_level)  # 约 0.5%~6.5%
        return delta_ratio <= thr

    if mode == "sa":
        if delta_ratio <= 0:
            return True
        p = math.exp(-delta_ratio / max(1e-12, T))
        return rng.random() < p

    return False


# =========================================================
# destroy 算子
# =========================================================

def _destroy_random_remove(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    rng: random.Random,
) -> List[int]:
    """随机移除：把所有已分配任务打乱返回（外层会按 strength 截断）。"""
    assigned = list(sol.all_assigned_tasks())
    rng.shuffle(assigned)
    return assigned


def _destroy_worst_remove(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    rng: random.Random,
) -> List[int]:
    """
    “较差任务”优先移除（轻量启发式，不算严格边际增量）：
    - 服务时间越长越“占资源”
    - 优先级越低越“可牺牲”
    """
    scored: List[Tuple[float, int]] = []
    for tid in sol.all_assigned_tasks():
        t = instance.task_by_id(int(tid))
        score = float(t.service_time) - 0.2 * float(t.priority)
        scored.append((score, int(tid)))
    scored.sort(reverse=True)
    return [tid for _, tid in scored]


def _destroy_segment_remove(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    rng: random.Random,
) -> List[int]:
    """
    连续段移除（结构扰动强）：
    - 随机挑一个 agent
    - 在其 route 上随机截一段连续子序列
    """
    agent_ids = list(instance.all_agent_ids())
    if not agent_ids:
        return []
    aid = rng.choice(agent_ids)
    route = sol.routes.get(aid, [])
    if not route:
        return []
    if len(route) == 1:
        return [route[0]]

    L = len(route)
    i = rng.randrange(L)
    j = rng.randrange(i + 1, L + 1)
    return list(route[i:j])


# =========================================================
# repair 算子
# =========================================================

def _rank_tasks_for_insertion(tids: List[int], instance: Instance, rng: random.Random) -> List[int]:
    """
    待插入任务的排序（只影响 repair 的尝试顺序，不改变最终可行性规则）：
    - 优先级高优先（priority 大的先插）
    - 时间窗越紧（tw_end - tw_start 越小）越先插
    - 加极小随机扰动，避免完全确定性导致某些实例“死锁式重复”
    """
    arr: List[Tuple[float, float, int]] = []
    for tid in tids:
        t = instance.task_by_id(int(tid))
        tw_width = float(t.tw_end) - float(t.tw_start)
        noise = 1e-6 * rng.random()
        arr.append((-float(t.priority), tw_width + noise, int(tid)))
    arr.sort()
    return [tid for _, _, tid in arr]


def _clone_for_local_edit(sol: AssignmentSolution) -> AssignmentSolution:
    """
    repair 内部会大量做“试插入 -> evaluate -> 丢弃”，深拷贝很贵。
    这里做一个“局部编辑友好”的 clone：
    - routes: dict + list 全部复制（避免改到原对象）
    - unassigned: set 复制
    - schedule: 留空（evaluate 会重算）
    """
    out = AssignmentSolution(routes={}, unassigned=set(sol.unassigned), schedule={})
    for aid, route in sol.routes.items():
        out.routes[int(aid)] = list(route)
    return out


def _agent_can_do_task(instance: Instance, aid: int, tid: int) -> bool:
    """技能硬过滤：不满足技能要求的 agent 直接不考虑（否则试插会白算）。"""
    t = instance.task_by_id(int(tid))
    req = set(getattr(t, "skill_req", set()) or [])
    if not req:
        return True
    ag = instance.agent_by_id(int(aid))
    skills = set(getattr(ag, "skills", set()) or [])
    return req.issubset(skills)


def _agent_can_reach_task_within_tw(instance: Instance, aid: int, tid: int) -> bool:
    """安全剪枝（agent 级）：即使该 agent 路线为空，也无法在任务时间窗内开始服务 -> 直接跳过。"""
    agent = instance.agent_by_id(int(aid))
    task = instance.task_by_id(int(tid))

    # evaluator 的起点：depot, time=0
    t_travel = instance.travel_time(agent, instance.depot.loc, task.loc)
    earliest_start = max(float(task.tw_start), float(t_travel))
    return earliest_start <= float(task.tw_end)


def _route_timewindow_bounds(
    instance: Instance,
    aid: int,
    route: List[int],
) -> Tuple[List[float], List[float], bool]:
    """
    【时间窗界分析 - repair 中的关键剪枝】
    
    目标：
    - 计算当前路线 route 上每个任务的时间可行区间 [earliest, latest]
    - 这是一个轻量级的"可行性前检查"：快速发现某些插入位置必然违反时间窗约束
    
    工作流程：
    1) 正向扫描：计算每个任务"最早"可开始服务的时间 earliest[i]
       - 从 depot 出发（time=0），依次按路线顺序行驶 + 服务
       - 若到达时间早于任务时间窗开始，则等待到 tw_start
       - 若 earliest[i] 超过任务的 tw_end，则路线当前不可行 -> 直接返回
    
    2) 反向扫描：计算每个任务"最晚"可开始服务的时间 latest[i]
       - 从路线末尾任务的 tw_end 开始，反向推导
       - latest[i] = min(任务 tw_end, 后续任务最晚时间 - 当前服务时间 - 行驶时间)
       - 若 latest[i] < tw_start，说明该任务被挤在时间窗左边界，路线不可行
    
    返回值：
    - earliest[]：每个任务的最早可开始时间（取决于前序约束）
    - latest[]：每个任务的最晚可开始时间（取决于后序约束）
    - feasible：当前路线在时间窗角度是否可行
    
    应用场景（被 _prune_positions_by_timewindow 调用）：
    - 在 repair 时，枚举某任务的所有可能插入位置 (aid, pos)
    - 若该路线经过时间窗检查发现不可行 -> 跳过整个 agent
    - 若可行 -> 利用 earliest/latest 进一步剪枝"插在哪些位置会导致冲突"
    
    核心优化：避免对不可行路线做重复的冗余 evaluate
    """
    n = len(route)
    if n == 0:
        return [], [], True

    agent = instance.agent_by_id(int(aid))

    # forward earliest：从 depot 出发，正向模拟，计算每个任务的最早开始时间
    earliest: List[float] = [0.0] * n
    cur_loc = instance.depot.loc
    cur_time = 0.0
    feasible = True
    for i, tid in enumerate(route):
        t = instance.task_by_id(int(tid))
        # 行驶到任务位置
        cur_time += float(instance.travel_time(agent, cur_loc, t.loc))
        # 如果提前到达，等待到时间窗开始
        if cur_time < float(t.tw_start):
            cur_time = float(t.tw_start)
        earliest[i] = float(cur_time)
        # 剪枝：若最早开始时间都超过任务截止时间 -> 整条路线时间窗不可行
        if earliest[i] > float(t.tw_end):
            feasible = False
            break
        # 累加服务时间，更新当前位置
        cur_time += float(t.service_time)
        cur_loc = t.loc

    if not feasible:
        return earliest, [0.0] * n, False

    # backward latest：从路线末尾反向推导，计算每个任务的最晚开始时间
    latest: List[float] = [0.0] * n
    last = instance.task_by_id(int(route[-1]))
    latest[-1] = float(last.tw_end)
    # 剪枝：最后一个任务的时间窗本身冲突 -> 路线不可行
    if latest[-1] < float(last.tw_start):
        return earliest, latest, False

    # 从倒数第二个任务开始，依次向前推导 latest
    for i in range(n - 2, -1, -1):
        cur = instance.task_by_id(int(route[i]))
        nxt = instance.task_by_id(int(route[i + 1]))
        # 后续任务最晚开始时间 - 当前任务服务时间 - 行驶时间 = 当前任务最晚开始时间的上界
        bound = latest[i + 1] - float(cur.service_time) - float(instance.travel_time(agent, cur.loc, nxt.loc))
        # 与任务自身时间窗的截止时间取最小值
        latest[i] = min(float(cur.tw_end), bound)
        # 剪枝：若最晚开始时间都小于时间窗开始 -> 该任务被"挤出"时间窗 -> 路线不可行
        if latest[i] < float(cur.tw_start):
            feasible = False
            break

    return earliest, latest, feasible

def _prune_positions_by_timewindow(
    instance: Instance,
    aid: int,
    route: List[int],
    tid: int,
    earliest: List[float],
    latest: List[float],
) -> List[int]:
    L = len(route)
    if L == 0:
        return [0]

    agent = instance.agent_by_id(int(aid))
    t_ins = instance.task_by_id(int(tid))

    # 预构建 prev_loc / nxt_loc 列表（长度 L+1）
    prev_locs: List[Location] = [instance.depot.loc] + [instance.task_by_id(int(x)).loc for x in route]
    nxt_locs: List[Location] = [instance.task_by_id(int(x)).loc for x in route] + [None]  # type: ignore

    # 预计算 travel_time：prev->tid, tid->nxt（长度 L+1）
    tt_prev_to_tid = [float(instance.travel_time(agent, pl, t_ins.loc)) for pl in prev_locs]
    tt_tid_to_nxt = [0.0 if nl is None else float(instance.travel_time(agent, t_ins.loc, nl)) for nl in nxt_locs]

    out: List[int] = []
    for pos in range(L + 1):
        # prev_finish：插入点前一个任务服务完成时间（pos==0 则为 0）
        if pos == 0:
            prev_finish = 0.0
        else:
            prev_task = instance.task_by_id(int(route[pos - 1]))
            prev_finish = float(earliest[pos - 1]) + float(prev_task.service_time)

        # tid 的最早可开始时间（必要条件 1）
        arr_tid = prev_finish + tt_prev_to_tid[pos]
        start_tid = max(arr_tid, float(t_ins.tw_start))
        if start_tid > float(t_ins.tw_end):
            continue

        # nxt 的最早可开始时间 <= latest[pos]（必要条件 2）
        if pos < L:
            nxt_task = instance.task_by_id(int(route[pos]))
            finish_tid = start_tid + float(t_ins.service_time)
            arr_nxt = finish_tid + tt_tid_to_nxt[pos]
            start_nxt_min = max(arr_nxt, float(nxt_task.tw_start))
            if start_nxt_min > float(latest[pos]):
                continue

        out.append(pos)

    return out

def _min_service_energy_lb(instance: Instance, aid: int, tid: int) -> float:
    """服务能耗下界（与 evaluator._service_energy 口径一致，且在 skills 满足时为精确值）"""
    agent = instance.agent_by_id(int(aid))
    task = instance.task_by_id(int(tid))
    # 这里假设已经通过 _agent_can_do_task 保证 task.skill_req ⊆ agent.skills
    return float(task.service_time) * sum(float(agent.skill_energy_rate.get(s, 1.0)) for s in task.skill_req)


def _iter_all_insertions(
    sol: AssignmentSolution,
    tid: int,
    instance: Instance,
) -> List[Tuple[int, int]]:
    """
    生成“所有插入尝试”（去掉 Top-K）：
    - 遍历所有 agent
    - 遍历该 agent route 的所有插入位置 0..L
    返回 (aid, pos) 列表。
    """
    cand: List[Tuple[int, int]] = []
    for aid in instance.all_agent_ids():
        if not _agent_can_do_task(instance, int(aid), int(tid)):
            continue
        if not _agent_can_reach_task_within_tw(instance, int(aid), int(tid)):
            continue

        agent = instance.agent_by_id(int(aid))
        if _min_service_energy_lb(instance, int(aid), int(tid)) > float(agent.init_energy) + 1e-9:
            continue

        route = sol.routes.get(int(aid), [])
        earliest, latest, ok = _route_timewindow_bounds(instance, int(aid), list(route))
        if ok and len(route) > 0:
            pos_list = _prune_positions_by_timewindow(instance, int(aid), list(route), int(tid), earliest, latest)
        else:
            pos_list = list(range(len(route) + 1))

        for pos in pos_list:
            cand.append((int(aid), int(pos)))

    return cand



def _repair_greedy_insert(
    partial: AssignmentSolution,
    removed: List[int],
    instance: Instance,
    config: Config,
    rng: random.Random,
) -> AssignmentSolution:
    """
    贪心修复（可行优先 + 尽量多插）：

    对每个待插任务 tid：
    - 枚举所有 (agent, pos) 插入尝试（无 Top-K）
    - 只在“可行候选”中选择最优插入（Deb 比较/compare）
    - 只要存在可行候选，就立即插入
    - 若完全不存在可行插入位置，则放入 unassigned
    """
    sol = partial.clone(deep=True)

    # endgame：未分配任务很少时，启用“1-step ejection”（踢出 1 个低价值任务为当前任务腾位）
    enable_ejection = len(sol.unassigned) <= 5

    def _eject_candidates(route: List[int], pos: int, tid: int) -> List[int]:
        """从当前路线里挑少量可被踢出的候选任务（局部优先 + 低优先级优先）。"""
        if not route:
            return []

        t_ins = instance.task_by_id(int(tid))
        p_ins = float(getattr(t_ins, "priority", 0.0))

        # 1) 插入点附近（局部挤压通常发生在插入点周围）
        lo = max(0, int(pos) - 2)
        hi = min(len(route) - 1, int(pos) + 2)
        local = [int(route[i]) for i in range(lo, hi + 1)]

        # 2) 全局最低优先级（兜底：能量/班次超限时可能需要踢“最不重要”的）
        def _prio(x: int) -> float:
            return float(getattr(instance.task_by_id(int(x)), "priority", 0.0))

        worst = min(route, key=_prio)

        cand = local + [int(worst)]

        # 过滤：不踢优先级更高的任务（保守保护）
        out: List[int] = []
        seen = set()
        for x in cand:
            if int(x) == int(tid):
                continue
            if int(x) in seen:
                continue
            seen.add(int(x))
            if _prio(int(x)) > p_ins:
                continue
            out.append(int(x))
        return out


    # 插入顺序仍按启发式：优先级高、时间窗紧的先插
    tasks = _rank_tasks_for_insertion(list(removed), instance, rng)

    for tid in tasks:
        best_choice: Optional[Tuple[int, int]] = None
        best_ev: Optional[EvalResult] = None
        best_eject: Optional[int] = None

        for aid, pos in _iter_all_insertions(sol, tid, instance):
            trial = _clone_for_local_edit(sol)
            trial.add_task(int(aid), int(tid), position=int(pos))

            ev = evaluate(trial, instance, config, update_solution_schedule=False)

            # ✅ 先走正常插入：只考虑可行候选
            if ev.is_feasible:
                cmp = _deb_compare_eval(ev, best_ev, config)
                if best_ev is None or cmp < 0:
                    best_ev = ev
                    best_choice = (int(aid), int(pos))
                    best_eject = None
                elif cmp == 0 and rng.random() < 0.3:
                    best_ev = ev
                    best_choice = (int(aid), int(pos))
                    best_eject = None
                continue

            # ---- endgame ejection：若正常不可行，则尝试“踢 1 个任务再插” ----
            if not enable_ejection:
                continue

            route = sol.routes.get(int(aid), [])
            for kick_tid in _eject_candidates(route, int(pos), int(tid)):
                trial2 = _clone_for_local_edit(sol)
                trial2.add_task(int(aid), int(tid), position=int(pos))
                trial2.remove_task(int(aid), int(kick_tid), to_unassigned=True)

                ev2 = evaluate(trial2, instance, config, update_solution_schedule=False)
                if not ev2.is_feasible:
                    continue

                cmp = _deb_compare_eval(ev2, best_ev, config)
                if best_ev is None or cmp < 0:
                    best_ev = ev2
                    best_choice = (int(aid), int(pos))
                    best_eject = int(kick_tid)
                elif cmp == 0 and rng.random() < 0.3:
                    best_ev = ev2
                    best_choice = (int(aid), int(pos))
                    best_eject = int(kick_tid)

        if best_choice is not None:
            aid, pos = best_choice
            sol.add_task(aid, int(tid), position=pos)
            # 如果用了 ejection，则把被踢出的任务放回未分配池（净效果：任务数不变，但结构被重排）
            if best_eject is not None:
                sol.remove_task(int(aid), int(best_eject), to_unassigned=True)
            sol.unassigned.discard(int(tid))
        else:
            sol.unassigned.add(int(tid))


    return sol



def _repair_regret2_insert(
    partial: AssignmentSolution,
    removed: List[int],
    instance: Instance,
    config: Config,
    rng: random.Random,
) -> AssignmentSolution:
    """
    Regret-2 修复（可行优先 + 尽量多插）：

    核心思路：
    - 对每个任务 tid，在“可行插入候选”中找 best1 与 best2
    - regret = cost(best2) - cost(best1)
      regret 越大，表示“现在不插，后面可行插入会变得很差/很少”
    - 每轮选择 regret 最大的任务插入 best1
    - 重复直到没有任何任务存在可行插入位置

    说明：
    - 全程只在可行候选内竞争，不引入不可行插入
    - 相比 greedy，通常更不容易把后续任务“堵死”，插入数量更大
    """
    EPS = 1e-12  # 或者 1e-9
    sol = partial.clone(deep=True)
    remaining = set(int(x) for x in removed)

    def _cost_feasible(ev: EvalResult) -> float:
        """
        仅用于 regret 的标量 cost（越小越好），且只会对可行 ev 调用。
        - 主看软层指标（一般是 objective_policy 的第二层；没有就用 energy_total）
        - 加一点极小扰动，避免完全相等时不稳定
        """
        soft = _soft_metric_value(ev, config, fallback_metric="energy_total")
        return float(soft)

    while remaining:
        chosen_tid: Optional[int] = None
        chosen_choice: Optional[Tuple[int, int]] = None
        chosen_best1_ev: Optional[EvalResult] = None
        chosen_regret: float = -1.0

        any_insertable = False

        # 扫所有剩余任务（按启发式顺序）
        for tid in _rank_tasks_for_insertion(list(remaining), instance, rng):
            best1_choice: Optional[Tuple[int, int]] = None
            best1_ev: Optional[EvalResult] = None
            best2_ev: Optional[EvalResult] = None

            # 枚举所有插入位置，维护“可行”的 best1/best2
            for aid, pos in _iter_all_insertions(sol, tid, instance):
                trial = _clone_for_local_edit(sol)
                trial.add_task(int(aid), int(tid), position=int(pos))

                ev = evaluate(trial, instance, config, update_solution_schedule=False)

                # ✅ 可行优先：不可行候选直接丢弃
                if not ev.is_feasible:
                    continue

                if best1_ev is None or _deb_compare_eval(ev, best1_ev, config) < 0:
                    best2_ev = best1_ev
                    best1_ev = ev
                    best1_choice = (int(aid), int(pos))
                elif best2_ev is None or _deb_compare_eval(ev, best2_ev, config) < 0:
                    best2_ev = ev

            if best1_choice is None or best1_ev is None:
                continue  # 该任务当前无可行插入
            any_insertable = True

            # regret：只有一个可行位置 -> 认为 regret = +inf（必须尽快插）
            if best2_ev is None:
                regret = float("inf")
            else:
                regret = _cost_feasible(best2_ev) - _cost_feasible(best1_ev)

            if regret > chosen_regret:
                chosen_regret = regret
                chosen_tid = int(tid)
                chosen_choice = best1_choice
                chosen_best1_ev = best1_ev
            elif abs(regret - chosen_regret) <= EPS:
                # tie-break：优先 best1 更好；再随机
                #（best1_ev 越好越倾向选）
                if chosen_best1_ev is None or _deb_compare_eval(best1_ev, chosen_best1_ev, config) < 0:
                    chosen_tid = int(tid)
                    chosen_choice = best1_choice
                    chosen_best1_ev = best1_ev
                elif _deb_compare_eval(best1_ev, chosen_best1_ev, config) == 0 and rng.random() < 0.5:
                    chosen_tid = int(tid)
                    chosen_choice = best1_choice
                    chosen_best1_ev = best1_ev

        if not any_insertable or chosen_tid is None or chosen_choice is None or chosen_best1_ev is None:
            # 没有任何任务存在可行插入位置：剩余全部留未分配
            for tid in remaining:
                sol.unassigned.add(int(tid))
            break

        # 执行插入（保证仍可行）
        aid, pos = chosen_choice
        sol.add_task(int(aid), int(chosen_tid), position=int(pos))
        sol.unassigned.discard(int(chosen_tid))
        remaining.remove(int(chosen_tid))

    return sol


# =========================================================
# 通用辅助函数
# =========================================================

def _remove_tasks(sol: AssignmentSolution, tids: List[int]) -> None:
    """
    从解中移除任务，并放入 unassigned。

    实现上用 set 加速：
    - 原写法是“每个 tid 扫所有 route 再 remove”，复杂度偏高
    - 这里改为：每条 route 过滤一遍，最后统一补齐 unassigned
    """
    if not tids:
        return
    remove_set = set(int(x) for x in tids)

    for aid, route in list(sol.routes.items()):
        if not route:
            continue
        new_route = [tid for tid in route if int(tid) not in remove_set]
        sol.routes[int(aid)] = new_route

    # 注意：只要 tid 原来在某个 route 中，被滤掉后就应进入未分配池
    for tid in remove_set:
        sol.unassigned.add(int(tid))


def _select_repair_candidates(
    pool: List[int],
    strength: int,
    instance: Instance,
    rng: random.Random,
) -> List[int]:
    """
    从“未分配池”中挑本轮 repair 要尝试插入的任务子集。

    做“候选子集选择”（属于 ALNS 的常规减枝）：
    - 优先挑高 priority
    - 再混入一部分随机，避免总是只修同一批任务
    """
    if not pool:
        return []

    scored: List[Tuple[float, int]] = []
    for tid in pool:
        t = instance.task_by_id(int(tid))
        scored.append((float(t.priority), int(tid)))
    scored.sort(reverse=True)

    k = _clamp_int(int(strength), 1, len(scored))
    top = [tid for _, tid in scored[:k]]
    rest = [tid for _, tid in scored[k:]]
    rng.shuffle(rest)

    # 混入约一半随机（上限 k//2）
    mix = top + rest[: max(0, min(len(rest), k // 2))]

    # 去重保持顺序
    out: List[int] = []
    seen = set()
    for x in mix:
        if x not in seen:
            seen.add(x)
            out.append(int(x))
    return out


def _deb_compare_eval(a: EvalResult, b: EvalResult, config: Config, tol: float = 1e-9) -> int:
    """
    Deb 可行性规则比较：返回 -1/0/+1（a 更好 / 相等 / b 更好）。
    """
    if b is None:
        return -1  # a 一定更好（因为 b 不存在）
    # 1) 可行性优先
    if a.is_feasible and (not b.is_feasible):
        return -1
    if (not a.is_feasible) and b.is_feasible:
        return 1

    # 2) 都可行：直接用 compare（你定义的字典序/分层策略）
    if a.is_feasible and b.is_feasible:
        c = compare(a, b, config)
        return -1 if c < 0 else (1 if c > 0 else 0)

    # 3) 都不可行：先比 violation_total（更贴近“回可行域”的方向）
    va = float(a.get_metric("violation_total"))
    vb = float(b.get_metric("violation_total"))
    if abs(va - vb) > tol:
        return -1 if va < vb else 1

    # 4) violation_total 近似相等：再用 compare 细分（仍遵循 objective_policy）
    c = compare(a, b, config)
    return -1 if c < 0 else (1 if c > 0 else 0)


def _soft_metric_value(ev: EvalResult, config: Config, fallback_metric: str = "energy_total") -> float:
    """
    取“软层代表指标”的数值（统一成：越小越好）：
    - 默认取 objective_policy 的第二层（index=1）
    - 若 objective_policy 没有第二层，则退回 fallback_metric
    """
    op = getattr(config.eval, "objective_policy", None) if hasattr(config, "eval") else None
    layers = op.layers if (op is not None and hasattr(op, "layers")) else []

    metric = fallback_metric
    direction = "min"
    if layers and len(layers) >= 2:
        metric = layers[1].metric
        direction = layers[1].direction

    v = float(ev.get_metric(metric))
    return -v if direction == "max" else v


def _restore_feasibility(
    sol: AssignmentSolution,
    instance: Instance,
    config: Config,
    rng: random.Random,
    max_remove: int = 8,
) -> AssignmentSolution:
    """
    可行性恢复（保险丝，不是主力优化算子）：

    目标：
    - 当搜索长时间处于不可行状态时，尽量把解拉回可行域
    - 提高“best_feasible 出现概率”，从而保证最终输出可行

    做法（保守）：
    1) 若已可行：直接返回
    2) 否则：从最长 route 中随机移除少量任务，最多 max_remove 次
    3) 对移除的任务再做一次 repair（这里用 greedy，无 Top-K）
       - 仍保留“violation_total 不变差/变好”的护栏
    """
    work = sol.clone(deep=True)
    work.normalize(instance)

    ev = evaluate(work, instance, config, update_solution_schedule=False)
    if ev.is_feasible:
        return work

    removed: List[int] = []
    initial_violation = float(ev.get_metric("violation_total"))

    for _ in range(int(max_remove)):
        candidates = [(aid, rt) for aid, rt in work.routes.items() if rt]
        if not candidates:
            break

        # 优先从最长路线拆任务（更可能快速降低冲突/能量/时窗违规）
        aid = int(max(candidates, key=lambda x: len(x[1]))[0])
        rt = work.routes.get(aid, [])
        if not rt:
            continue

        pos = rng.randrange(len(rt))
        tid = int(rt.pop(pos))
        work.unassigned.add(tid)
        removed.append(tid)

        work.normalize(instance)
        ev = evaluate(work, instance, config, update_solution_schedule=False)
        if ev.is_feasible:
            break

    if removed:
        best_at_removal = float(ev.get_metric("violation_total"))

        # 这里用“无 Top-K 的 greedy repair”
        work_repaired = _repair_greedy_insert(work, removed, instance, config, rng)
        work_repaired.normalize(instance)
        ev_repaired = evaluate(work_repaired, instance, config, update_solution_schedule=False)

        violation_after = float(ev_repaired.get_metric("violation_total"))

        # 选择逻辑：优先不让 violation 变差；若能相对初始改善，也可接受
        if violation_after <= best_at_removal:
            work = work_repaired
        elif violation_after < initial_violation:
            work = work_repaired

    return work


def _roulette_select(weights: Dict[str, float], rng: random.Random) -> str:
    """轮盘赌：按权重随机选择算子。"""
    items = list(weights.items())
    total = sum(max(0.0, w) for _, w in items)
    if total <= 0:
        return items[rng.randrange(len(items))][0]

    r = rng.random() * total
    acc = 0.0
    for k, w in items:
        acc += max(0.0, w)
        if acc >= r:
            return k
    return items[-1][0]


def _update_weights(
    weights: Dict[str, float],
    scores: Dict[str, float],
    used: Dict[str, int],
    reaction: float,
) -> None:
    """
    ALNS 常见的权重更新：
      w <- (1-r)*w + r*avg_score
    - avg_score = 本段累计得分 / 使用次数
    - reaction 越大，权重越“追涨杀跌”
    """
    for k in list(weights.keys()):
        u = int(used.get(k, 0))
        if u <= 0:
            continue
        avg = float(scores.get(k, 0.0)) / max(1, u)
        weights[k] = (1.0 - float(reaction)) * float(weights[k]) + float(reaction) * max(0.0, avg)
        weights[k] = max(1e-6, float(weights[k]))


def _budget_ok(budget: Budget, t0: float, it: int) -> bool:
    """预算检查：时间/迭代任一超出则停止。"""
    if budget.time_limit_sec is not None and (time.time() - t0) >= float(budget.time_limit_sec):
        return False
    if budget.max_iters is not None and it >= int(budget.max_iters):
        return False
    return True


def _clamp_int(x: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(x)))


def _clamp_float(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))
