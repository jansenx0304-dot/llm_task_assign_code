# sar_alloc/solution.py
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, is_dataclass
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Set, Tuple, Any

from .models import Instance


AgentID = int
TaskID = int


def _obj_to_dict(o: Any) -> Any:
    if o is None:
        return None
    if is_dataclass(o):
        return asdict(o)
    if hasattr(o, "model_dump"):  # pydantic v2
        return o.model_dump()
    if hasattr(o, "dict"):        # pydantic v1
        return o.dict()
    if hasattr(o, "_asdict"):     # namedtuple
        return o._asdict()
    return vars(o)                # 普通对象（有 __dict__）

@dataclass(slots=True)
class EvalResult:
    """
    评估器输出的统一指标结构（由 tools/evaluator.py 生成）。

    最小化字段（必需）：
    - is_feasible: 解是否满足所有硬约束
    - violations: 三类违规的总量（capability/time_window/energy）
    - metrics: 通用指标字典（用于分层目标的 metric 查找）
    - lex_key: 可选缓存（字典序比较向量）
    """
    is_feasible: bool = False
    violations: Dict[str, float] = field(default_factory=dict)

    # 通用指标（分层目标优先从这里取）
    metrics: Dict[str, float] = field(default_factory=dict)

    # 可选：缓存的字典序 key（比如 (violation_total, missed_priority, energy_total)）
    lex_key: Optional[Tuple[float, ...]] = None

    def get_metric(self, name: str) -> float:
        """
        统一访问口径：优先从 metrics 取。
        特例：violation_total 可以从 violations 求和（避免漏填）。
        """
        if name in self.metrics:
            return float(self.metrics[name])

        # 特例：violation_total 可以即时求和
        if name == "violation_total":
            return float(sum(self.violations.values())) if self.violations else 0.0

        # 未知指标默认 0
        return 0.0


@dataclass(slots=True)
class AssignmentSolution:
    """
    解结构：每个智能体一条任务序列（route），未分配任务集合，及可选的调度信息。

    - routes[agent_id] = [task_id, ...]
    - unassigned = {task_id, ...}
    - schedule[(agent_id, task_id)] = (start, end)  # 可选
    """
    routes: Dict[AgentID, List[TaskID]] = field(default_factory=dict)
    unassigned: Set[TaskID] = field(default_factory=set)
    schedule: Dict[Tuple[AgentID, TaskID], Tuple[float, float]] = field(default_factory=dict)

    # 评估结果缓存（由 evaluator 写入/更新）
    eval: Optional[EvalResult] = None
    solver_diagnostics: Dict[str, Any] = field(default_factory=dict)
    run_summary: Dict[str, Any] = field(default_factory=dict)

    def clone(self, deep: bool = True) -> "AssignmentSolution":
        if not deep:
            return AssignmentSolution(
                routes=self.routes,
                unassigned=self.unassigned,
                schedule=self.schedule,
                eval=self.eval,
                solver_diagnostics=self.solver_diagnostics,
                run_summary=self.run_summary,
            )
        return AssignmentSolution(
            routes={aid: list(seq) for aid, seq in self.routes.items()},
            unassigned=set(self.unassigned),
            schedule=dict(self.schedule),
            eval=self.eval,  # 通常结构改变后 eval 需要置空；此处由调用方决定
            solver_diagnostics=deepcopy(self.solver_diagnostics),
            run_summary=deepcopy(self.run_summary),
        )

    @staticmethod
    def empty_from_instance(instance: Instance, put_all_unassigned: bool = True) -> "AssignmentSolution":
        sol = AssignmentSolution(routes={aid: [] for aid in instance.all_agent_ids()})
        if put_all_unassigned:
            sol.unassigned = set(instance.all_task_ids())
        return sol

    def all_assigned_tasks(self) -> Set[TaskID]:
        s: Set[TaskID] = set()
        for seq in self.routes.values():
            s.update(seq)
        return s

    def add_task(self, agent_id: AgentID, task_id: TaskID, position: Optional[int] = None) -> None:
        if agent_id not in self.routes:
            self.routes[agent_id] = []
        if position is None or position >= len(self.routes[agent_id]):
            self.routes[agent_id].append(task_id)
        else:
            self.routes[agent_id].insert(position, task_id)
        self.unassigned.discard(task_id)
        self.eval = None

    def remove_task(self, agent_id: AgentID, task_id: TaskID, to_unassigned: bool = True) -> None:
        seq = self.routes.get(agent_id, [])
        if task_id in seq:
            seq.remove(task_id)
            if to_unassigned:
                self.unassigned.add(task_id)
            self.schedule.pop((agent_id, task_id), None)
            self.eval = None

    def move_task(
        self,
        from_agent: AgentID,
        to_agent: AgentID,
        task_id: TaskID,
        to_position: Optional[int] = None,
    ) -> None:
        self.remove_task(from_agent, task_id, to_unassigned=False)
        self.add_task(to_agent, task_id, position=to_position)

    def normalize(self, instance: Instance) -> None:
        for aid in instance.all_agent_ids():
            self.routes.setdefault(aid, [])

        valid_tasks = set(instance.all_task_ids())

        for aid, seq in self.routes.items():
            self.routes[aid] = [tid for tid in seq if tid in valid_tasks]

        self.unassigned = {tid for tid in self.unassigned if tid in valid_tasks}

        assigned = self.all_assigned_tasks()
        self.unassigned.difference_update(assigned)

        valid_pairs = {(aid, tid) for aid, seq in self.routes.items() for tid in seq}
        self.schedule = {k: v for k, v in self.schedule.items() if k in valid_pairs}

        self.eval = None

    def to_dict(self) -> Dict[str, Any]:
        ev = self.eval
        ev_dict = None if ev is None else _obj_to_dict(ev)

        # 覆盖/修正 lex_key，确保 JSON 友好（无论原来是 tuple 还是别的可迭代）
        if ev_dict is not None:
            ev_dict["lex_key"] = list(getattr(ev, "lex_key", None)) if getattr(ev, "lex_key", None) is not None else None

        return {
            "routes": {str(aid): list(map(int, seq)) for aid, seq in self.routes.items()},
            "unassigned": list(map(int, self.unassigned)),
            "schedule": {f"{aid}:{tid}": [st, en] for (aid, tid), (st, en) in self.schedule.items()},
            "eval": ev_dict,
            "solver_diagnostics": deepcopy(self.solver_diagnostics),
            "run_summary": deepcopy(self.run_summary),
        }
    
    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "AssignmentSolution":
        routes = {int(aid): list(map(int, seq)) for aid, seq in data.get("routes", {}).items()}
        unassigned = set(map(int, data.get("unassigned", [])))

        schedule: Dict[Tuple[int, int], Tuple[float, float]] = {}
        for k, v in data.get("schedule", {}).items():
            aid_s, tid_s = k.split(":")
            schedule[(int(aid_s), int(tid_s))] = (float(v[0]), float(v[1]))

        sol = AssignmentSolution(
            routes=routes,
            unassigned=unassigned,
            schedule=schedule,
            solver_diagnostics=dict(data.get("solver_diagnostics", {}) or {}),
            run_summary=dict(data.get("run_summary", {}) or {}),
        )

        # eval 建议由 evaluator 重算；这里默认不反序列化为强一致性
        sol.eval = None
        return sol
