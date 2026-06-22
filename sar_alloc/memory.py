from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class RunMemory:
    contracts: List[Dict[str, Any]] = field(default_factory=list)
    solver_actions: List[Dict[str, Any]] = field(default_factory=list)

    def record_solver_action(
        self,
        contract_id: str,
        solver_action_index: int,
        decision: Dict[str, Any],
        events: List[str],
    ) -> Dict[str, Any]:
        raw = decision["solver_decision"]
        item = {
            "id": f"M{self.size + 1}",
            "kind": "solver_action",
            "contract_id": contract_id,
            "solver_action_index": solver_action_index,
            "action": raw["action"],
            "destroy_operator_scores": raw.get("destroy_control", {}).get("operator_scores", []),
            "insertion_operator_scores": raw.get("insertion_control", {}).get("operator_scores", []),
            "acceptance_control": raw.get("acceptance_control", {}),
            "events": list(events),
        }
        self.solver_actions.append(item)
        return item

    def record_contract(
        self,
        contract: Dict[str, Any],
        progress: Dict[str, Any],
        events: List[str],
        completion: Dict[str, Any],
    ) -> Dict[str, Any]:
        item = {
            "id": f"M{self.size + 1}",
            "kind": "contract",
            "contract_id": contract["contract_id"],
            "contract_type": contract["contract_type"],
            "stage_goal": contract["stage_goal"],
            "stage_objective_layers": [
                item.get("metric", "") if isinstance(item, dict) else str(item)
                for item in contract["stage_objective_layers"]
            ],
            "feasibility_control": contract["feasibility_control"],
            "progress": progress,
            "result_events": list(events),
            "completion": dict(completion),
        }
        self.contracts.append(item)
        return item

    @property
    def size(self) -> int:
        return len(self.contracts) + len(self.solver_actions)

    def for_supervisor(self, limit: int = 5) -> List[Dict[str, Any]]:
        return (self.contracts + self.solver_actions)[-limit:]

    def for_solver(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.solver_actions[-limit:]

    def as_dict(self) -> Dict[str, Any]:
        return {"contracts": self.contracts, "solver_actions": self.solver_actions}


__all__ = ["RunMemory"]
