from netcopilot.vendors.base import VendorProfile

PROFILE = VendorProfile(
    key="aruba",
    display_name="Aruba (ArubaOS-CX)",
    cli_prompt="Aruba#",
    syntax_guide="""\
Dialeto: ArubaOS-CX.

Exemplos de sintaxe real:
- Criar a VLAN 20 (se ainda não existir):
    vlan 20
        name VLAN20
- Liberar VLAN 20 de acesso na porta 1/1/3:
    interface 1/1/3
        no shutdown
        vlan access 20
- Liberar VLAN 30 como tagged (trunk) na porta 1/1/24:
    interface 1/1/24
        no routing
        vlan trunk allowed 30
- Desabilitar uma porta:
    interface 1/1/5
        shutdown

Use o formato de interface <chassi>/<slot>/<porta> (ex: 1/1/3) quando o pedido \
mencionar apenas o número da porta.
""",
    dangerous_patterns=[
        r"\berase\b",
        r"\bboot\s+system\b",
        r"\breload\b",
        r"\bwrite\s+erase\b",
        r"\bfactory\b",
    ],
)
