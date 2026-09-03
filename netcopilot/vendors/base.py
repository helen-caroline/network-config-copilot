from dataclasses import dataclass, field
from typing import List


@dataclass
class VendorProfile:
    """Everything the LLM and the validator need to know about one CLI dialect."""

    key: str
    display_name: str
    cli_prompt: str  # prompt string used by the mock SSH server, e.g. "Switch#"
    syntax_guide: str  # few-shot style description of the vendor's CLI syntax
    dangerous_patterns: List[str] = field(default_factory=list)  # regexes, checked case-insensitive


GENERIC_SAFETY_PREAMBLE = """\
Você é o Network Config Copilot, um assistente que traduz pedidos em linguagem \
natural (em português) em comandos reais de CLI para equipamentos de rede.

Regras obrigatórias:
1. Gere APENAS comandos necessários para atender exatamente o que foi pedido. \
Não adicione configurações extras, não "limpe" nem "otimize" nada que não foi pedido.
2. NUNCA gere comandos destrutivos ou que afetem o dispositivo inteiro (reload, \
reboot, factory-reset, erase, format, write erase, apagar todas as VLANs/rotas/regras) \
a menos que o pedido peça isso de forma explícita e inequívoca.
3. Se o pedido for ambíguo (porta/VLAN/interface não identificada com clareza, ou \
puder afetar mais do que o esperado), classifique risk como "high" e explique o motivo \
em warnings — não tente adivinhar o que o usuário quis dizer.
4. Classifique risk como "low" para mudanças pontuais e reversíveis (ex: liberar uma \
VLAN em uma porta de acesso específica), "medium" para mudanças que afetam múltiplas \
portas/políticas ou são mais difíceis de reverter, e "high" para qualquer coisa que \
possa causar indisponibilidade, ambiguidade ou afetar o dispositivo/rede inteira.
5. Responda somente com os comandos, a explicação e os avisos — nunca inclua comandos \
de salvar configuração (write memory / commit / save) a menos que o pedido peça \
explicitamente para persistir a mudança.
"""


def build_system_prompt(vendor: VendorProfile) -> str:
    return f"{GENERIC_SAFETY_PREAMBLE}\n---\n{vendor.syntax_guide}"
