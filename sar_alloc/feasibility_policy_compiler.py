from __future__ import annotations

from copy import deepcopy
import math
from typing import Any, Dict, Optional

from .config import Config

DEFAULT_DELTA_RULES: Dict[str, Dict[str, float]] = {
    "time_window": {"delta_fraction": 0.5, "delta_cap": 0.05},
    "energy": {"delta_fraction": 0.5, "delta_cap": 0.03},
}


def load_delta_rules(config: Optional[Config] = None) -> Dict[str, Dict[str, float]]:
    rules = deepcopy(DEFAULT_DELTA_RULES)
    overrides = (
        {} if config is None else config.extras.get("relaxation_delta_rules", {})
    )
    if not isinstance(overrides, dict):
        raise ValueError("config.extras['relaxation_delta_rules'] must be an object")
    for violation_type, raw in overrides.items():
        if violation_type not in rules or not isinstance(raw, dict):
            raise ValueError(f"invalid relaxation delta rule: {violation_type}")
        for field in ("delta_fraction", "delta_cap"):
            if field in raw:
                value = float(raw[field])
                if not math.isfinite(value) or value < 0.0:
                    raise ValueError(
                        f"{violation_type}.{field} must be a non-negative finite number"
                    )
                rules[violation_type][field] = value
    return rules


def compile_feasibility_control(
    feasibility_control: Dict[str, Any],
    config: Optional[Config] = None,
) -> Dict[str, Any]:
    mode = str(feasibility_control["mode"])
    if mode in {"strict", "recovery_only"}:
        return {"mode": mode}
    if mode != "relaxed_recoverable":
        raise ValueError(f"unknown feasibility mode: {mode}")

    rules = load_delta_rules(config)
    per_type: Dict[str, Dict[str, float]] = {}
    for item in feasibility_control["relaxation_ratios"]:
        violation_type = str(item.get("violation_type", item.get("type", "")))
        limit_ratio = float(item.get("max_ratio", item.get("limit_ratio", 0.0)))
        rule = rules[violation_type]
        per_type[violation_type] = {
            "limit_ratio": limit_ratio,
            "delta_ratio": min(
                float(rule["delta_cap"]),
                float(rule["delta_fraction"]) * limit_ratio,
            ),
        }
    return {"mode": mode, "per_type": per_type}


__all__ = ["DEFAULT_DELTA_RULES", "load_delta_rules", "compile_feasibility_control"]
