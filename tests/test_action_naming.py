import unittest

from sar_alloc.config import Budget, Config
from sar_alloc.llm_orchestrator import (
    RUN_ALNS_ACTION,
    AgentState,
    BudgetState,
    _normalize_action,
    _validate_action_spec,
)


def _default_alns_payload(cfg: Config) -> dict:
    defaults = cfg.solver.weighted_alns
    return {
        "destroy_generator_priors": dict(defaults.destroy_generator_priors),
        "repair_task_selector_priors": dict(defaults.repair_task_selector_priors),
        "repair_position_selector": defaults.repair_position_selector,
        "metric_weights": defaults.metric_weights.as_dict(),
        "strength_ratio": defaults.strength_ratio,
        "acceptance": defaults.acceptance,
        "accept_level": defaults.accept_level,
        "reaction_factor": defaults.reaction_factor,
        "prior_mix_lambda": defaults.prior_mix_lambda,
    }


class ActionNamingTests(unittest.TestCase):
    def test_validate_accepts_run_alns(self) -> None:
        cfg = Config()
        parsed = {
            "action_type": RUN_ALNS_ACTION,
            "action_payload": _default_alns_payload(cfg),
            "budget_request": {"time_limit_sec": 1.0},
        }

        error = _validate_action_spec(parsed, [RUN_ALNS_ACTION, "stop"])

        self.assertIsNone(error)

    def test_validate_rejects_run_alns_without_time_limit(self) -> None:
        cfg = Config()
        parsed = {
            "action_type": RUN_ALNS_ACTION,
            "action_payload": _default_alns_payload(cfg),
            "budget_request": {"max_iters": 100},
        }

        error = _validate_action_spec(parsed, [RUN_ALNS_ACTION, "stop"])

        self.assertEqual(error, "missing field 'budget_request.time_limit_sec'")

    def test_normalize_keeps_run_alns(self) -> None:
        cfg = Config()
        state = AgentState(objective_layers=[], incumbent_summary={"exists": True})
        state.incumbent_solution = object()  # sentinel: only presence matters here
        budget_state = BudgetState.from_budget(Budget(time_limit_sec=5.0, max_iters=100), max_solver_calls=3)
        parsed = {
            "action_type": RUN_ALNS_ACTION,
            "action_payload": _default_alns_payload(cfg),
            "budget_request": {"time_limit_sec": 1.0},
        }

        normalized = _normalize_action(parsed, [RUN_ALNS_ACTION, "stop"], state, budget_state, cfg)

        self.assertEqual(normalized["action_type"], RUN_ALNS_ACTION)

    def test_normalize_run_alns_adds_default_time_limit_when_missing(self) -> None:
        cfg = Config()
        state = AgentState(objective_layers=[], incumbent_summary={"exists": True})
        state.incumbent_solution = object()  # sentinel: only presence matters here
        budget_state = BudgetState.from_budget(Budget(time_limit_sec=5.0, max_iters=100), max_solver_calls=3)
        parsed = {
            "action_type": RUN_ALNS_ACTION,
            "action_payload": _default_alns_payload(cfg),
            "budget_request": {"max_iters": 25},
        }

        normalized = _normalize_action(parsed, [RUN_ALNS_ACTION, "stop"], state, budget_state, cfg)

        self.assertEqual(normalized["budget_request"]["time_limit_sec"], cfg.solver.weighted_alns.default_time_limit_sec)
        self.assertEqual(normalized["budget_request"]["max_iters"], 25)


if __name__ == "__main__":
    unittest.main()
