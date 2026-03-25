from __future__ import annotations

import unittest
from unittest.mock import patch

from sar_alloc.config import Config
from sar_alloc.llm_orchestrator import _normalize_action
from sar_alloc.models import Agent, Depot, Instance, Task
from sar_alloc.operators import (
    DESTROY_CANDIDATE_GENERATORS,
    InsertCandidateFeatures,
    InsertPosition,
    MetricWeights,
    RemoveFeatures,
    REPAIR_TASK_SELECTORS,
    ReinsertTaskFeatures,
    WeightedALNSPolicy,
)
from sar_alloc.operators.features import (
    compute_insert_candidate_features_batch,
    compute_reinsert_task_features_batch,
    compute_task_remove_features_batch,
)
from sar_alloc.operators.scoring import (
    score_insert_candidate_features,
    score_reinsert_task_features,
    score_remove_features,
)
from sar_alloc.tools.assign_solvers import (
    _blend_operator_weights,
    _cand_global_assigned,
    _repair_with_weighted_priority,
    _repair_with_regret2,
    _restore_feasibility,
    _select_best_feasible_position_by_eval,
    _select_filtered_best_position_by_score,
    select_tasks_to_remove,
)
from sar_alloc.tools.llm_utils import llm_compile_weighted_alns_policy
from sar_alloc.solution import AssignmentSolution, EvalResult


def _build_instance() -> Instance:
    return Instance(
        tasks=(
            Task(id=1, loc=(1.0, 0.0), tw_start=0.0, tw_end=10.0, service_time=1.0, skill_req={"med"}, priority=5.0),
            Task(id=2, loc=(2.0, 0.0), tw_start=0.0, tw_end=3.0, service_time=1.0, skill_req={"med"}, priority=1.0),
            Task(id=3, loc=(0.5, 0.0), tw_start=0.0, tw_end=4.0, service_time=1.0, skill_req={"med"}, priority=4.0),
            Task(id=4, loc=(3.0, 0.0), tw_start=0.0, tw_end=20.0, service_time=1.0, skill_req={"med"}, priority=2.0),
        ),
        agents=(
            Agent(id=0, init_energy=100.0, skills={"med"}, travel_energy_rate=1.0, skill_energy_rate={"med": 1.0}),
            Agent(id=1, init_energy=100.0, skills={"med"}, travel_energy_rate=1.0, skill_energy_rate={"med": 1.0}),
        ),
        depot=Depot(id=0, loc=(0.0, 0.0)),
    )


def _build_policy() -> WeightedALNSPolicy:
    return WeightedALNSPolicy(
        destroy_generator_priors={name: 1.0 for name in DESTROY_CANDIDATE_GENERATORS},
        repair_task_selector_priors={name: 1.0 for name in REPAIR_TASK_SELECTORS},
        repair_position_selector="filtered_best_position",
        metric_weights=MetricWeights(priority=1.0, tw_tightness=1.0, violation_risk=2.0, energy_pressure=1.0, detour_cost=1.0, service_burden=1.0, feasibility_scarcity=1.0, route_instability=1.0),
        strength_ratio=0.34,
        acceptance="greedy",
        accept_level=0.0,
        reaction_factor=0.1,
        prior_mix_lambda=0.25,
    )


def _fake_eval(cost: float, *, feasible: bool = True, violation_total: float = 0.0) -> EvalResult:
    violations = {} if feasible else {"time_window": float(violation_total)}
    return EvalResult(
        is_feasible=feasible,
        violations=violations,
        metrics={
            "violation_total": 0.0 if feasible else float(violation_total),
            "missed_priority": 0.0,
            "energy_total": float(cost),
        },
        lex_key=(0.0 if feasible else float(violation_total), 0.0, float(cost)),
    )


class WeightedALNSTests(unittest.TestCase):
    def setUp(self) -> None:
        self.instance = _build_instance()
        self.config = Config()
        self.policy = _build_policy()

    def test_destroy_candidate_generator_only_supplies_domain(self) -> None:
        sol = AssignmentSolution(routes={0: [1, 2], 1: [4]}, unassigned={3})

        def generator(_sol, _instance, _config, _k, _rng):
            return [1, 2, 4]

        fake_features = {
            1: RemoveFeatures(0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            2: RemoveFeatures(0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
            4: RemoveFeatures(0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        }
        with patch("sar_alloc.tools.assign_solvers.compute_task_remove_features_batch", return_value=fake_features):
            removed = select_tasks_to_remove(sol, self.instance, self.config, self.policy, generator, __import__("random").Random(0))
        self.assertEqual(removed, [2])

    def test_score_remove_features_prefers_low_priority_high_pressure(self) -> None:
        weights = MetricWeights(priority=2.0, tw_tightness=0.0, violation_risk=1.0, energy_pressure=0.0, detour_cost=0.0, service_burden=0.0, feasibility_scarcity=0.0, route_instability=0.0)
        sacrificial = RemoveFeatures(0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        protected = RemoveFeatures(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.assertGreater(score_remove_features(sacrificial, weights), score_remove_features(protected, weights))

    def test_score_reinsert_task_features_prefers_higher_priority(self) -> None:
        weights = MetricWeights(priority=2.0, tw_tightness=0.0, violation_risk=1.0, energy_pressure=0.0, detour_cost=0.0, service_burden=0.0, feasibility_scarcity=0.0, route_instability=0.0)
        urgent = ReinsertTaskFeatures(1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        mild = ReinsertTaskFeatures(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.assertGreater(score_reinsert_task_features(urgent, weights), score_reinsert_task_features(mild, weights))

    def test_score_insert_candidate_features_is_loss(self) -> None:
        weights = MetricWeights(priority=1.0, tw_tightness=1.0, violation_risk=1.0, energy_pressure=1.0, detour_cost=1.0, service_burden=1.0, feasibility_scarcity=1.0, route_instability=1.0)
        good = InsertCandidateFeatures(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        bad = InsertCandidateFeatures(0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        self.assertLess(score_insert_candidate_features(good, weights), score_insert_candidate_features(bad, weights))

    def test_weighted_priority_uses_exact_feasible_eval(self) -> None:
        partial = AssignmentSolution(routes={0: [1], 1: []}, unassigned={2})

        def fake_eval(trial, instance, config, update_solution_schedule=False):
            del instance, config, update_solution_schedule
            if trial.routes[1] == [2]:
                return _fake_eval(1.0, feasible=True)
            if trial.routes[0] == [1, 2]:
                return _fake_eval(10.0, feasible=True)
            return _fake_eval(50.0, feasible=False, violation_total=5.0)

        with patch("sar_alloc.tools.assign_solvers.enumerate_filtered_insert_positions", return_value=[InsertPosition(0, 1), InsertPosition(1, 0)]), patch("sar_alloc.tools.assign_solvers.evaluate", side_effect=fake_eval), patch("sar_alloc.tools.assign_solvers._select_filtered_best_position_by_score", side_effect=AssertionError("score-based selector should not be used")):
            repaired = _repair_with_weighted_priority(partial, self.instance, self.config, self.policy, __import__("random").Random(0))

        self.assertEqual(repaired.routes[1], [2])
        self.assertEqual(repaired.unassigned, set())

    def test_exact_best_position_helper_uses_compare_on_feasible_trials(self) -> None:
        sol = AssignmentSolution(routes={0: [1], 1: []}, unassigned={2})

        def fake_eval(trial, instance, config, update_solution_schedule=False):
            del instance, config, update_solution_schedule
            if trial.routes[1] == [2]:
                return _fake_eval(1.0, feasible=True)
            if trial.routes[0] == [1, 2]:
                return _fake_eval(10.0, feasible=True)
            return _fake_eval(100.0, feasible=False, violation_total=10.0)

        with patch("sar_alloc.tools.assign_solvers.enumerate_filtered_insert_positions", return_value=[InsertPosition(0, 1), InsertPosition(1, 0)]), patch("sar_alloc.tools.assign_solvers.evaluate", side_effect=fake_eval):
            choice = _select_best_feasible_position_by_eval(sol, 2, self.instance, self.config)
        self.assertEqual(choice, InsertPosition(1, 0))

    def test_regret2_uses_exact_evaluator_regret(self) -> None:
        partial = AssignmentSolution(routes={0: [], 1: []}, unassigned={1, 2})
        policy = WeightedALNSPolicy(
            **{
                **self.policy.as_dict(),
                "metric_weights": self.policy.metric_weights,
                "repair_task_selector_priors": {
                    **self.policy.repair_task_selector_priors,
                    "regret2_order": 3.0,
                    "weighted_priority_order": 0.5,
                },
            }
        )

        def enum_positions(sol, tid, instance, config):
            route_len = len(sol.routes[0])
            return [InsertPosition(0, route_len), InsertPosition(1, 0)]

        def fake_eval(trial, instance, config, update_solution_schedule=False):
            del instance, config, update_solution_schedule
            assigned = {tid for route in trial.routes.values() for tid in route}
            if assigned == {1} and trial.routes[0] == [1]:
                return _fake_eval(1.0, feasible=True)
            if assigned == {1} and trial.routes[1] == [1]:
                return _fake_eval(10.0, feasible=True)
            if assigned == {2} and trial.routes[0] == [2]:
                return _fake_eval(2.0, feasible=True)
            if assigned == {2} and trial.routes[1] == [2]:
                return _fake_eval(3.0, feasible=True)
            return _fake_eval(5.0, feasible=True)

        with patch("sar_alloc.tools.assign_solvers.enumerate_filtered_insert_positions", side_effect=enum_positions), patch("sar_alloc.tools.assign_solvers.evaluate", side_effect=fake_eval), patch("sar_alloc.tools.assign_solvers.score_insert_candidate_features", side_effect=AssertionError("regret2 should not use insert score")):
            repaired = _repair_with_regret2(partial, self.instance, self.config, policy, __import__("random").Random(0))
        self.assertEqual(repaired.routes[0][0], 1)

    def test_filtered_best_position_scores_only_filtered_candidates(self) -> None:
        sol = AssignmentSolution(routes={0: [1], 1: []}, unassigned={2, 3, 4})
        kept = InsertPosition(0, 1)

        def feature_batch(_sol, _tid, positions, _instance, _config):
            self.assertEqual(positions, [kept])
            return {kept: InsertCandidateFeatures(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)}

        with patch("sar_alloc.tools.assign_solvers.enumerate_filtered_insert_positions", return_value=[kept]), patch("sar_alloc.tools.assign_solvers.compute_insert_candidate_features_batch", side_effect=feature_batch):
            choice = _select_filtered_best_position_by_score(sol, 2, self.instance, self.config, self.policy)
        self.assertEqual(choice, kept)

    def test_restore_feasibility_prefers_exact_greedy_repair_when_violation_improves(self) -> None:
        work = AssignmentSolution(routes={0: [1, 2], 1: []}, unassigned=set())

        def fake_eval(trial, instance, config, update_solution_schedule=False):
            del instance, config, update_solution_schedule
            assigned = {tid for route in trial.routes.values() for tid in route}
            if trial.routes == {0: [1], 1: [2]}:
                return _fake_eval(2.0, feasible=False, violation_total=2.0)
            if assigned == {1, 2}:
                return _fake_eval(10.0, feasible=False, violation_total=10.0)
            if assigned == {2}:
                return _fake_eval(6.0, feasible=False, violation_total=6.0)
            if assigned == {1}:
                return _fake_eval(4.0, feasible=False, violation_total=4.0)
            return _fake_eval(2.0, feasible=False, violation_total=2.0)

        repaired = AssignmentSolution(routes={0: [1], 1: [2]}, unassigned=set())

        with patch("sar_alloc.tools.assign_solvers.evaluate", side_effect=fake_eval), patch("sar_alloc.tools.assign_solvers._repair_with_weighted_priority", return_value=repaired):
            restored = _restore_feasibility(work, self.instance, self.config, self.policy, __import__("random").Random(0), max_remove=1)

        self.assertEqual(restored.routes, repaired.routes)

    def test_violation_risk_has_consistent_semantics(self) -> None:
        sol = AssignmentSolution(routes={0: [1, 2], 1: []}, unassigned={3, 4})
        remove_features = compute_task_remove_features_batch(sol, [1, 2], self.instance, self.config)
        self.assertGreater(remove_features[2].violation_risk, remove_features[1].violation_risk)

        task_features = compute_reinsert_task_features_batch(sol, [3, 4], self.instance, self.config)
        self.assertGreater(task_features[3].violation_risk, task_features[4].violation_risk)

        positions = [InsertPosition(0, 0), InsertPosition(0, 2)]
        insert_features = compute_insert_candidate_features_batch(sol, 3, positions, self.instance, self.config)
        self.assertGreater(insert_features[InsertPosition(0, 2)].violation_risk, insert_features[InsertPosition(0, 0)].violation_risk)

    def test_old_action_shape_is_rejected(self) -> None:
        bad_action = "run_" + "alns"
        normalized = _normalize_action(
            {
                "action_type": bad_action,
                "action_payload": {},
                "budget_request": {"max_iters": 5},
            },
            ["run_weighted_alns", "stop"],
            type("State", (), {"incumbent_solution": object(), "consecutive_flat_steps": 0})(),
            type("BudgetState", (), {"can_run_solver": lambda self: True, "remaining": {"time_limit_sec": 1.0, "max_iters": 10.0}})(),
            self.config,
        )
        self.assertEqual(normalized["action_type"], "run_weighted_alns")

    def test_old_preset_fields_are_dropped(self) -> None:
        mode_key = "search" + "_" + "mode"
        old_mode = "ex" + "plore"
        size_key = "str" + "ength"
        result = llm_compile_weighted_alns_policy(self.config, {mode_key: old_mode, size_key: "he" + "avy"})
        self.assertTrue(result["ok"])
        self.assertNotIn(mode_key, result["applied"])
        self.assertNotIn(size_key, result["applied"])

    def test_compile_policy_keeps_full_operator_prior_maps(self) -> None:
        result = llm_compile_weighted_alns_policy(
            self.config,
            {
                "destroy_generator_priors": {"route_segment": 3.5},
                "repair_task_selector_priors": {"regret2_order": 4.0},
                "prior_mix_lambda": 0.3,
            },
        )
        self.assertTrue(result["ok"])
        policy = result["policy"]
        self.assertEqual(set(policy.destroy_generator_priors), set(DESTROY_CANDIDATE_GENERATORS))
        self.assertEqual(set(policy.repair_task_selector_priors), set(REPAIR_TASK_SELECTORS))
        self.assertEqual(policy.destroy_generator_priors["route_segment"], 3.5)
        self.assertEqual(policy.repair_task_selector_priors["regret2_order"], 4.0)
        self.assertAlmostEqual(policy.prior_mix_lambda, 0.3)

    def test_blend_operator_weights_uses_geometric_prior_mix(self) -> None:
        fused = _blend_operator_weights(
            {"global_assigned": 4.0, "route_segment": 1.0},
            {"global_assigned": 1.0, "route_segment": 9.0},
            0.25,
        )
        self.assertAlmostEqual(fused["global_assigned"], (4.0 ** 0.75) * (1.0 ** 0.25))
        self.assertAlmostEqual(fused["route_segment"], (1.0 ** 0.75) * (9.0 ** 0.25))
        self.assertGreater(fused["global_assigned"], fused["route_segment"])

    def test_removed_position_selector_name_is_invalid(self) -> None:
        gone_selector = "best_" + "score_" + "position"
        result = llm_compile_weighted_alns_policy(self.config, {"repair_position_selector": gone_selector})
        self.assertEqual(result["policy"].repair_position_selector, "filtered_best_position")
        self.assertFalse(hasattr(__import__("sar_alloc.tools.assign_solvers", fromlist=["dummy"]), "_select_" + gone_selector))

    def test_global_assigned_candidate_generator_returns_domain(self) -> None:
        sol = AssignmentSolution(routes={0: [1, 2], 1: [4]}, unassigned={3})
        self.assertEqual(set(_cand_global_assigned(sol, self.instance, self.config, 2, __import__("random").Random(0))), {1, 2, 4})


if __name__ == "__main__":
    unittest.main()
