# sar_alloc/tools/__init__.py
from __future__ import annotations

"""
Tools package (for LLM Orchestrator).

本目录对外暴露“稳定且少量”的工具函数：LLM 只需要
- 选择 init / solver 工具
- 通过 Config / Budget 调参
不要直接改求解器内部细节（move/operator 的实现细节属于内部）。

推荐用法：
1) 先用 inst.instance_summary 快速了解实例规模/结构，用于选 init/solver 参数
2) 用 policy.apply_objective 将“人类目标描述”落到 config.eval.objective_policy（分层字典序目标）
3) 用 init.build_initial_solution 构造一个初始解
4) 用 assign.solve_assignment 做改进（TS / ALNS）
5) 用 eval.solution_summary 获取“与当前 objective_policy 对齐”的反馈（只暴露目标相关指标）

注意：
- solution_summary() 会内部调用 evaluate()，但只返回与 objective_policy 相关的“裁剪后的摘要”
- instance_summary() 只做“实例结构摘要”，不依赖求解结果
- apply_objective() 会修改传入的 config（in-place），这是预期行为
"""

from .init_solutions import build_initial_solution
from .assign_solvers import solve_assignment
from ..evaluator import evaluate, compare
from .llm_utils import (
    llm_solution_summary as solution_summary,
    llm_instance_summary as instance_summary,
    llm_apply_objective as apply_objective,
    llm_available_metrics as available_metrics,
    llm_apply_solver_params as apply_solver_params,
)

__all__ = [
    "instance_summary",
    "available_metrics",
    "apply_objective",
    "build_initial_solution",
    "solve_assignment",
    "solution_summary",
    "apply_solver_params",
]
