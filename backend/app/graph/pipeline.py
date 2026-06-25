"""
LangGraph claim routing pipeline.
Defines the state machine, edges, and conditional routing logic.
"""
from langgraph.graph import StateGraph, END
from app.graph.state import ClaimState
from app.agents.nodes import (
    intake_validator,
    claim_classifier,
    policy_validator,
    fraud_scorer,
    priority_scorer,
    department_router,
    response_composer,
)


# ── Conditional edge functions ─────────────────────────────────────────────────

def route_after_validator(state: ClaimState) -> str:
    """If input is completely invalid, skip to response. Otherwise classify."""
    errors = state.get("errors", [])
    if len(errors) > 2:
        return "response_composer"
    return "claim_classifier"


def route_after_fraud(state: ClaimState) -> str:
    """If fraud score is critical (5), skip priority scoring and route directly."""
    if state.get("fraud_score", 1) == 5:
        return "department_router"
    return "priority_scorer"


# ── Build the graph ───────────────────────────────────────────────────────────

def build_claim_graph() -> StateGraph:
    graph = StateGraph(ClaimState)

    # Add all agent nodes
    graph.add_node("intake_validator",  intake_validator)
    graph.add_node("claim_classifier",  claim_classifier)
    graph.add_node("policy_validator",  policy_validator)
    graph.add_node("fraud_scorer",      fraud_scorer)
    graph.add_node("priority_scorer",   priority_scorer)
    graph.add_node("department_router", department_router)
    graph.add_node("response_composer", response_composer)

    # Entry point
    graph.set_entry_point("intake_validator")

    # Conditional edge after validation
    graph.add_conditional_edges(
        "intake_validator",
        route_after_validator,
        {
            "claim_classifier": "claim_classifier",
            "response_composer": "response_composer",
        }
    )

    # Linear edges (always run these in sequence)
    graph.add_edge("claim_classifier",  "policy_validator")
    graph.add_edge("policy_validator",  "fraud_scorer")

    # Conditional edge after fraud scoring
    graph.add_conditional_edges(
        "fraud_scorer",
        route_after_fraud,
        {
            "priority_scorer":   "priority_scorer",
            "department_router": "department_router",
        }
    )

    graph.add_edge("priority_scorer",   "department_router")
    graph.add_edge("department_router", "response_composer")
    graph.add_edge("response_composer", END)

    return graph.compile()


# Singleton compiled graph — created once on import
claim_graph = build_claim_graph()
