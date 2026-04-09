from __future__ import annotations

"""Centralized scoring functions for unified weighted ALNS operators.

Task score and insert score share one metric vector, but task score orders
tasks while insert score ranks filtered insertion positions.
"""

from .types import InsertCandidateFeatures, MetricWeights, ReinsertTaskFeatures, RemoveFeatures


def score_remove_features(features: RemoveFeatures, weights: MetricWeights) -> float:
    """Higher is better for removal priority.

    `priority` is inverted here so low-priority assigned tasks are easier to tear down.
    Every other feature is aligned so that larger normalized values mean higher
    removal pressure.
    """
    return (
        float(weights.priority) * (1.0 - float(features.priority))
        + float(weights.tw_tightness) * float(features.tw_tightness)
        + float(weights.violation_risk) * float(features.violation_risk)
        + float(weights.energy_pressure) * float(features.energy_pressure)
        + float(weights.detour_cost) * float(features.detour_cost)
        + float(weights.service_burden) * float(features.service_burden)
        + float(weights.feasibility_scarcity) * float(features.feasibility_scarcity)
        + float(weights.route_instability) * float(features.route_instability)
    )


def score_reinsert_task_features(features: ReinsertTaskFeatures, weights: MetricWeights) -> float:
    """Higher is better for choosing which unassigned task to reinsert next.

    This score never chooses the final insertion position.
    """
    return (
        float(weights.priority) * float(features.priority)
        + float(weights.tw_tightness) * float(features.tw_tightness)
        + float(weights.violation_risk) * float(features.violation_risk)
        + float(weights.energy_pressure) * float(features.energy_pressure)
        + float(weights.detour_cost) * float(features.detour_cost)
        + float(weights.service_burden) * float(features.service_burden)
        + float(weights.feasibility_scarcity) * float(features.feasibility_scarcity)
        + float(weights.route_instability) * float(features.route_instability)
    )


def score_insert_candidate_features(features: InsertCandidateFeatures, weights: MetricWeights) -> float:
    """Lower is better for an insertion action.

    This is the primary ranking signal for filtered insertion positions.
    Strict evaluation only certifies feasibility after ranking.
    """
    return (
        float(weights.priority) * (1.0 - float(features.priority))
        + float(weights.tw_tightness) * float(features.tw_tightness)
        + float(weights.violation_risk) * float(features.violation_risk)
        + float(weights.energy_pressure) * float(features.energy_pressure)
        + float(weights.detour_cost) * float(features.detour_cost)
        + float(weights.service_burden) * float(features.service_burden)
        + float(weights.feasibility_scarcity) * float(features.feasibility_scarcity)
        + float(weights.route_instability) * float(features.route_instability)
    )
