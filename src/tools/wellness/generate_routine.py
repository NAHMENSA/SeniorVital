"""Generate Routine Tool — delega a WellnessAgent para generar rutinas."""

from __future__ import annotations

from typing import Any

from src.tools import ToolResult


class GenerateRoutineTool:
    """Genera una rutina de ejercicios personalizada para el día de hoy.

    Soporta dos modos de inicialización:
    - GenerateRoutineTool(agent=wellness_agent) — legacy, pasa WellnessAgent directamente
    - GenerateRoutineTool(llm=llm, user_data=user_data) — crea WellnessAgent internamente

    Precondiciones: WellnessAgent o (LLMService + UserDataService + RoutineRepository).
    Postcondiciones: Rutina guardada en BD y retornada.
    Efectos secundarios: INSERT en tabla routines.
    """

    name = "generate_routine"
    description = "Genera una rutina de ejercicios personalizada para el día de hoy"

    def __init__(
        self,
        agent: Any = None,
        llm: Any = None,
        user_data: Any = None,
        routine_repo: Any = None,
    ) -> None:
        if agent is not None:
            self._agent = agent
        elif llm is not None and user_data is not None:
            from src.agents.wellness.agent import WellnessAgent
            from src.agents.wellness.config import WellnessConfig

            config = WellnessConfig(
                llm_url=getattr(llm, "_client", None) and getattr(llm._client, "base_url", ""),
                llm_model=getattr(llm, "model", ""),
            )
            self._agent = WellnessAgent(
                llm=llm,
                user_data=user_data,
                routine_repo=routine_repo,
                config=config,
            )
        else:
            raise ValueError(
                "GenerateRoutineTool requires either 'agent' or 'llm'+'user_data'"
            )

    def validate_args(self, **kwargs) -> bool:
        return "user_id" in kwargs

    async def execute(self, **kwargs) -> ToolResult:
        """Ejecuta la generación de rutina.

        Args:
            user_id: ID del usuario.
            force: Si True, regenera aunque ya exista (default: False).

        Returns:
            ToolResult con data={"routine": {...}, "generated_by": "ollama|fallback"}.
        """
        if not self.validate_args(**kwargs):
            return ToolResult(success=False, error="user_id required", tool_name=self.name)

        try:
            user_id = int(kwargs["user_id"])
            force = kwargs.get("force", False)
            result = await self._agent.generate_routine(user_id, force=force)
            return ToolResult(
                success=True,
                data={"routine": result.to_dict(), "generated_by": result.generated_by},
                tool_name=self.name,
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), tool_name=self.name)
