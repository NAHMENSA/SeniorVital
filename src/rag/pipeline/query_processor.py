"""Query preprocessing for SeniorVital RAG pipeline."""

import re
from typing import Any

from rag.constants import AGENT_TO_MACRODOMAIN, MACRODOMAIN_TO_AGENT


# Keyword → macrodomain mapping for intent detection.
MACRODOMAIN_KEYWORDS: dict[str, list[str]] = {
    "A": [
        "sarcopenia", "dinapenia", "osteoporosis", "movilidad", "articular",
        "fisioterapia", "evaluación física", "diagnóstico", "patología",
        "fuerza muscular", "flexibilidad", "equilibrio", "dolor", "articulación",
        "hueso", "masa muscular", "capacidad funcional",
    ],
    "B": [
        "ejercicio", "entrenamiento", "rutina", "aeróbico", "fuerza",
        "resistencia", "flexibilidad", "equilibrio", "calentamiento",
        "estiramiento", "ejercitarse", "actividad física", "prescripción",
        "repeticiones", "series", "densidad", "volumen",
    ],
    "C": [
        "entorno", "hogar", "domicilio", "exterior", "casa",
        "latinoamérica", "clima", "vivienda", "espacio", "adaptación",
        "parque", "calle", "escalera", "silla", "barrio",
    ],
    "D": [
        "seguridad", "contraindicación", "riesgo", "precaución",
        "comorbilidad", "enfermedad crónica", "diabetes", "hipertensión",
        "cardiopatía", "medicamento", "interacción", "emergencia",
        "limitación", "alerta",
    ],
    "E": [
        "nutrición", "dieta", "alimentación", "comida", "nutrición",
        "proteína", "carbohidrato", "grasa", "vitamina", "mineral",
        "peso", "imc", "metabolismo", "caloría", "comer", "beber",
        "fruta", "verdura", "frijol", "maíz",
    ],
    "F": [
        "cognitivo", "memoria", "atención", "concentración", "relajación",
        "ansiedad", "depresión", "emocional", "bienestar", "estrés",
        "sueño", "descanso", "meditación", "estimulación", "cerebro",
        "funciones ejecutivas", "estado de ánimo",
    ],
}

AGENT_KEYWORDS: dict[str, list[str]] = {
    "Physio-Evaluator": ["fisioterapia", "evaluación física", "diagnóstico"],
    "Exercise Architect": ["ejercicio", "rutina", "entrenamiento", "prescripción"],
    "Context-Adaptor": ["entorno", "hogar", "adaptación", "latinoamérica"],
    "Safety Guardian": ["seguridad", "riesgo", "contraindicación", "precaución"],
    "Nutri-Buddy": ["nutrición", "dieta", "alimentación"],
    "Mind & Soul": ["cognitivo", "memoria", "emocional", "relajación"],
}


class QueryProcessor:
    """Preprocess and enrich user queries for RAG retrieval."""

    def __init__(self) -> None:
        pass

    def process(
        self,
        query: str,
        *,
        agent_name: str | None = None,
        macrodomain: str | None = None,
    ) -> dict[str, Any]:
        """Process a raw query into a structured request.

        Args:
            query: Raw user query.
            agent_name: Optional explicit agent override.
            macrodomain: Optional explicit macrodomain override.

        Returns:
            Dict with 'normalized_query', 'detected_macrodomain',
            'detected_agent', 'filters'.
        """
        normalized = self._normalize(query)

        detected_macrodomain = macrodomain
        detected_agent = agent_name

        if not detected_macrodomain and not detected_agent:
            detected_macrodomain = self._detect_macrodomain(normalized)
            if detected_macrodomain:
                detected_agent = MACRODOMAIN_TO_AGENT.get(detected_macrodomain)

        if detected_macrodomain and not detected_agent:
            detected_agent = MACRODOMAIN_TO_AGENT.get(detected_macrodomain)
        elif detected_agent and not detected_macrodomain:
            detected_macrodomain = AGENT_TO_MACRODOMAIN.get(detected_agent)

        filters: dict[str, str] = {}
        if detected_macrodomain:
            filters["macrodomain"] = detected_macrodomain

        return {
            "normalized_query": normalized,
            "detected_macrodomain": detected_macrodomain,
            "detected_agent": detected_agent,
            "filters": filters,
        }

    def _normalize(self, query: str) -> str:
        """Normalize query: lowercase, collapse whitespace, strip."""
        q = query.lower().strip()
        q = re.sub(r"\s+", " ", q)
        return q

    def _detect_macrodomain(self, normalized_query: str) -> str | None:
        """Score each macrodomain by keyword overlap, return best if above threshold."""
        scores: dict[str, int] = {}
        for domain, keywords in MACRODOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in normalized_query)
            if score > 0:
                scores[domain] = score

        if not scores:
            return None

        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        if scores[best] >= 1:
            return best
        return None
