from __future__ import annotations

from typing import Any


def calculate(data: dict[str, Any]) -> dict[str, float | str]:
    actions = max(1, float(data["controlled_actions"]))
    unsafe = max(1, float(data["confirmed_unsafe_actions_blocked"]))
    infrastructure = float(data["annual_infrastructure_cost"])
    validation = float(data["validation_hours"]) * float(data["loaded_hourly_cost"])
    implementation = float(data["implementation_cost"])
    productivity = float(data["latency_cost_per_ms"]) * float(data["added_latency_ms"]) * actions
    total_cost = infrastructure + validation + implementation + productivity
    effectiveness = float(data["demonstrated_control_effectiveness"])
    risk_reduction = {k: round(float(data["incident_probability"][k]) * float(data["probable_impact"][k]) * effectiveness, 2) for k in ("p10", "p50", "p90")}
    ir_savings = float(data["incident_response_hours_avoided"]) * float(data["loaded_hourly_cost"])
    assurance = float(data["assurance_hours_avoided"]) * float(data["loaded_hourly_cost"])
    direct = float(data.get("direct_revenue_enabled", 0))
    contributory = float(data.get("contributory_revenue", 0)) * float(data.get("attribution_factor", 0))
    capacity = float(data.get("additional_reviews", 0)) * float(data.get("qualification_rate", 0)) * float(data.get("average_contract_value", 0))
    net = risk_reduction["p50"] + ir_savings + assurance + direct + contributory - total_cost
    return {
        "cost_per_controlled_action": round((infrastructure + productivity) / actions, 6),
        "cost_per_prevented_unsafe_action": round(total_cost / unsafe, 2),
        "productivity_cost": round(productivity, 2),
        "risk_reduction_p10": risk_reduction["p10"], "risk_reduction_p50": risk_reduction["p50"], "risk_reduction_p90": risk_reduction["p90"],
        "incident_response_savings": round(ir_savings, 2), "assurance_labor_savings": round(assurance, 2),
        "direct_revenue_enabled": round(direct, 2), "contributory_revenue_attributed": round(contributory, 2),
        "capacity_enabled_pipeline": round(capacity, 2), "net_control_benefit_p50": round(net, 2),
        "control_roi_p50": round(net / total_cost, 3) if total_cost else 0,
        "disclaimer": "Illustrative decision support; capacity pipeline is not included as realized revenue or net benefit."
    }
