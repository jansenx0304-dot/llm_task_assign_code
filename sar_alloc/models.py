# sar_alloc/models.py
# 文件位置: sar_alloc/models.py (数据模型定义)
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Mapping, Optional, Tuple, Set

Location = Tuple[float, float]  # (x, y)


@dataclass(frozen=True, slots=True)
class Task:
    id: int
    loc: Location
    tw_start: float
    tw_end: float
    service_time: float
    skill_req: Set[str] = field(default_factory=set)
    priority: float = 0.0


@dataclass(frozen=True, slots=True)
class Agent:
    """
    智能体：初始能量、能力、速度、不同能力能耗、待机能耗（个体差异）
    能力模型改为：skills为集合，表示智能体具有的能力（二元模型）
    """

    id: int
    init_energy: float
    skills: Set[str] = field(default_factory=set)

    # ✅ 新增：每个智能体自己的速度（距离单位/时间单位）
    speed: float = 1.0

    # 行驶能耗：可按“每距离单位能耗”或“每时间单位能耗”，由 evaluator 定义口径
    travel_energy_rate: float = 1.0

    # 待机能耗：每时间单位能耗（各 agent 可不同）
    standby_power: float = 0.0

    # 执行任务时能力相关能耗：skill -> 能耗系数
    skill_energy_rate: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Depot:
    id: int
    loc: Location


def euclidean(a: Location, b: Location) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return (dx * dx + dy * dy) ** 0.5


@dataclass(frozen=True, slots=True)
class Instance:
    """
    问题实例：任务、智能体、救援中心（depot），以及距离/时间计算函数。

    - 若提供 travel_time_fn：优先用它
    - 否则：travel_time = distance / agent.speed（speed<=0 时回退 default_speed）
    """

    tasks: Tuple[Task, ...]
    agents: Tuple[Agent, ...]
    depot: Depot

    distance_fn: Callable[[Location, Location], float] = euclidean
    travel_time_fn: Optional[Callable[[Agent, Location, Location], float]] = None

    # 兜底速度（当 agent.speed <= 0 时使用）
    default_speed: float = 1.0

    # -------------------------
    # ✅ 运行时缓存（避免在 ALNS/TS 试探评估时重复计算）
    # 注意：Instance 是 frozen dataclass，但这些字段是可变容器，
    #       允许在运行时填充缓存以提升性能。
    #       若 travel_time_fn 随时间/环境变化（非纯函数），请勿启用 travel_time 缓存。
    # -------------------------
    _dist_cache: Dict[Tuple[Location, Location], float] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )
    _tt_cache: Dict[Tuple[int, Location, Location], float] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )
    _task_index_cache: Dict[int, Task] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )
    _agent_index_cache: Dict[int, Agent] = field(
        default_factory=dict, init=False, repr=False, compare=False
    )

    def task_by_id(self, tid: int) -> Task:
        # cached index
        if not self._task_index_cache:
            self._task_index_cache.update({t.id: t for t in self.tasks})
        return self._task_index_cache[tid]

    def agent_by_id(self, aid: int) -> Agent:
        # cached index
        if not self._agent_index_cache:
            self._agent_index_cache.update({a.id: a for a in self.agents})
        return self._agent_index_cache[aid]

    def all_task_ids(self) -> Tuple[int, ...]:
        return tuple(t.id for t in self.tasks)

    def all_agent_ids(self) -> Tuple[int, ...]:
        return tuple(a.id for a in self.agents)

    def distance(self, a: Location, b: Location) -> float:
        # fast-path: memoize symmetric distance
        key = (a, b)
        v = self._dist_cache.get(key)
        if v is not None:
            return v

        d = self.distance_fn(a, b)
        # store both directions (distance is symmetric for euclidean)
        self._dist_cache[key] = d
        self._dist_cache[(b, a)] = d
        return d

    def travel_time(self, agent: Agent, a: Location, b: Location) -> float:
        # memoize travel time by (agent_id, from, to)
        # ⚠️ 如果 travel_time_fn 不是纯函数（依赖时间/状态），请禁用该缓存或每轮清空。
        tkey = (agent.id, a, b)
        tv = self._tt_cache.get(tkey)
        if tv is not None:
            return tv

        if self.travel_time_fn is not None:
            t = self.travel_time_fn(agent, a, b)
        else:
            # reuse cached distance
            dist = self.distance(a, b)
            spd = (
                agent.speed
                if agent.speed > 0
                else (self.default_speed if self.default_speed > 0 else 1.0)
            )
            t = dist / spd

        self._tt_cache[tkey] = t
        return t

    def clear_caches(self) -> None:
        """手动清空缓存（例如 travel_time_fn 随环境变化时）。"""
        self._dist_cache.clear()
        self._tt_cache.clear()
        self._task_index_cache.clear()
        self._agent_index_cache.clear()
