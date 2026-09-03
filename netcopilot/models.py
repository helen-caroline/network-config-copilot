from typing import List, Literal

from pydantic import BaseModel, Field


class GeneratedCommand(BaseModel):
    """Structured output the LLM must return for every request."""

    commands: List[str] = Field(
        ..., description="Lista ordenada de comandos de CLI a executar no dispositivo."
    )
    explanation: str = Field(
        ..., description="Explicação em linguagem simples do que esses comandos fazem."
    )
    risk: Literal["low", "medium", "high"] = Field(
        ..., description="Classificação de risco da mudança solicitada."
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Avisos específicos (ex: pode derrubar um trunk, afeta outras VLANs, comando ambíguo).",
    )
