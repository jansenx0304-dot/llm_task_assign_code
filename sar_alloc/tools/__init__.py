from __future__ import annotations

"""
Tools package for the LLM orchestrator.

The public surface stays small and stable:
- summarize the instance
- apply objective layers
- build an initial solution
- run ALNS on the current solution
- summarize the resulting solution
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
