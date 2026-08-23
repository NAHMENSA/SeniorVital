"""Shared constants for SeniorVital RAG — agent-to-macrodomain mapping."""

# Map from autonomous agent name to knowledge macrodomain.
AGENT_TO_MACRODOMAIN: dict[str, str] = {
    "Physio-Evaluator": "A",
    "Exercise Architect": "B",
    "Context-Adaptor": "C",
    "Safety Guardian": "D",
    "Nutri-Buddy": "E",
    "Mind & Soul": "F",
}

# Reverse mapping.
MACRODOMAIN_TO_AGENT: dict[str, str] = {v: k for k, v in AGENT_TO_MACRODOMAIN.items()}
