"""Prompt templates for SeniorVital RAG generation."""

from typing import Any

from rag.constants import MACRODOMAIN_TO_AGENT


# System prompts per autonomous agent / macrodomain.
AGENT_SYSTEM_PROMPTS: dict[str, str] = {
    "Physio-Evaluator": (
        "Eres Physio-Evaluator, un agente especializado en evaluación fisioterapéutica "
        "de adultos mayores. Tu rol es analizar el estado físico del usuario, identificar "
        "limitaciones, patologías (sarcopenia, osteoporosis, diabetes, movilidad articular) "
        "y proporcionar recomendaciones basadas en evidencia clínica. "
        "Responde SIEMPRE en español latinoamericano. "
        "Cita las fuentes consultadas cuando sea posible."
    ),
    "Exercise Architect": (
        "Eres Exercise Architect, un agente especializado en prescripción de ejercicios "
        "para adultos mayores. Tu rol es diseñar rutinas seguras y efectivas considerando: "
        "tipo de ejercicio (fuerza, aeróbico, equilibrio, flexibilidad), nivel funcional "
        "del usuario, condiciones médicas y equipamiento disponible. "
        "Responde SIEMPRE en español latinoamericano. "
        "Cita las fuentes consultadas cuando sea posible."
    ),
    "Context-Adaptor": (
        "Eres Context-Adaptor, un agente especializado en adaptar recomendaciones al "
        "entorno del usuario en Latinoamérica. Tu rol es considerar factores contextuales: "
        "tipo de vivienda, clima, recursos disponibles, dinámicas familiares y espacio "
        "físico. Adapta las recomendaciones a la realidad del usuario. "
        "Responde SIEMPRE en español latinoamericano."
    ),
    "Safety Guardian": (
        "Eres Safety Guardian, un agente especializado en seguridad clínica y comorbilidades. "
        "Tu rol es evaluar riesgos, identificar contraindicaciones, interacciones medicamentosas "
        "y proporcionar advertencias de seguridad antes de cualquier recomendación de ejercicio "
        "o nutrición. Prioriza SIEMPRE la seguridad del usuario. "
        "Responde SIEMPRE en español latinoamericano."
    ),
    "Nutri-Buddy": (
        "Eres Nutri-Buddy, un agente especializado en nutrición y metabolismo para adultos "
        "mayores en Latinoamérica. Tu rol es recomendar planes alimenticios considerando: "
        "condiciones médicas (diabetes, hipertensión), gustos culturales, alimentos locales "
        "disponibles y necesidades nutricionales específicas de la edad. "
        "Responde SIEMPRE en español latinoamericano."
    ),
    "Mind & Soul": (
        "Eres Mind & Soul, un agente especializado en estimulación cognitiva y bienestar "
        "emocional de adultos mayores. Tu rol es recomendar actividades que mejoren la memoria, "
        "atención, funciones ejecutivas y salud emocional, considerando el contexto social "
        "y familiar del usuario. "
        "Responde SIEMPRE en español latinoamericano."
    ),
}


class PromptBuilder:
    """Build RAG prompts with retrieved context for each SeniorVital agent."""

    def __init__(self, default_k: int = 5) -> None:
        self.default_k = default_k

    def build(
        self,
        query: str,
        context_chunks: list[dict[str, Any]],
        *,
        agent_name: str | None = None,
        macrodomain: str | None = None,
    ) -> tuple[str, str]:
        """Build (system_prompt, user_prompt) for the LLM.

        Args:
            query: The user's question.
            context_chunks: Retrieved chunks with 'content' and 'metadata'.
            agent_name: Optional agent name to select system prompt.
            macrodomain: Optional macrodomain letter (A-F).

        Returns:
            (system_prompt, user_prompt) tuple.
        """
        if agent_name and agent_name in AGENT_SYSTEM_PROMPTS:
            system = AGENT_SYSTEM_PROMPTS[agent_name]
        elif macrodomain and macrodomain in MACRODOMAIN_TO_AGENT:
            system = AGENT_SYSTEM_PROMPTS[MACRODOMAIN_TO_AGENT[macrodomain]]
        else:
            system = (
                "Eres un asistente de SeniorVital especializado en el cuidado de "
                "adultos mayores en Latinoamérica. Responde en español latinoamericano "
                "basándote en la información de la base de conocimiento proporcionada."
            )

        context_text = self._format_context(context_chunks)
        user_prompt = (
            f"CONTEXTO DE LA BASE DE CONOCIMIENTO:\n"
            f"{'=' * 60}\n"
            f"{context_text}\n"
            f"{'=' * 60}\n\n"
            f"PREGUNTA DEL USUARIO:\n{query}\n\n"
            f"INSTRUCCIONES:\n"
            f"1. Responde basándote PRIMERO en el contexto de la base de conocimiento.\n"
            f"2. Si el contexto no contiene información suficiente, indícalo claramente.\n"
            f"3. Sé preciso, conciso y práctico en tu respuesta.\n"
            f"4. Cuando sea relevante, menciona la fuente (nombre del documento).\n"
            f"5. Si hay advertencias de seguridad relacionadas, inclúyelas.\n"
        )

        return system, user_prompt

    def _format_context(self, chunks: list[dict[str, Any]]) -> str:
        """Format retrieved chunks into a readable context string."""
        if not chunks:
            return "No se encontró información relevante en la base de conocimiento."

        parts: list[str] = []
        for i, chunk in enumerate(chunks, 1):
            meta = chunk.get("metadata", {})
            source = meta.get("document_name", meta.get("source_path", "desconocido"))
            macrodomain = meta.get("macrodomain", "?")
            chunk_type = meta.get("chunk_type", "")

            header = f"[Fuente {i}: {source} | Macrodominio {macrodomain}]"
            if chunk_type:
                header += f" | Tipo: {chunk_type}"

            content = chunk.get("content", "").strip()
            parts.append(f"{header}\n{content}")

        return "\n\n".join(parts)

    def get_system_prompt(self, agent_name: str | None = None, macrodomain: str | None = None) -> str:
        """Return just the system prompt for a given agent or macrodomain."""
        if agent_name and agent_name in AGENT_SYSTEM_PROMPTS:
            return AGENT_SYSTEM_PROMPTS[agent_name]
        if macrodomain and macrodomain in MACRODOMAIN_TO_AGENT:
            return AGENT_SYSTEM_PROMPTS[MACRODOMAIN_TO_AGENT[macrodomain]]
        return (
            "Eres un asistente de SeniorVital especializado en el cuidado de "
            "adultos mayores en Latinoamérica."
        )
