import re
from dataclasses import dataclass, field
from typing import List

from netcopilot.models import GeneratedCommand
from netcopilot.vendors.base import VendorProfile


@dataclass
class ValidationResult:
    ok: bool
    blocked_reasons: List[str] = field(default_factory=list)


def validate(
    generated: GeneratedCommand, vendor: VendorProfile, allow_high_risk: bool = False
) -> ValidationResult:
    """Deterministic safety net on top of the LLM's own risk classification.

    The LLM decides *what* to run and how risky it is; this function is the
    one place that can veto it before anything touches a real device.
    """
    reasons: List[str] = []

    if not generated.commands:
        reasons.append("O modelo não retornou nenhum comando para executar.")

    for cmd in generated.commands:
        for pattern in vendor.dangerous_patterns:
            if re.search(pattern, cmd, re.IGNORECASE):
                reasons.append(f'Comando bloqueado (padrão perigoso "{pattern}"): {cmd}')

    if generated.risk == "high" and not allow_high_risk:
        detail = "; ".join(generated.warnings) or generated.explanation
        reasons.append(f"Risco classificado como ALTO pelo modelo: {detail}")

    return ValidationResult(ok=not reasons, blocked_reasons=reasons)
