from netcopilot.vendors.base import VendorProfile

PROFILE = VendorProfile(
    key="ruckus",
    display_name="Ruckus (ICX / FastIron)",
    cli_prompt="ruckus#",
    syntax_guide="""\
Dialeto: Ruckus ICX (ex-Brocade FastIron).

Exemplos de sintaxe real:
- Criar a VLAN 20 e liberar como untagged na porta 1/1/3:
    vlan 20 name VLAN20 by port
        untagged ethernet 1/1/3
- Liberar VLAN 30 como tagged (trunk) na porta 1/1/24:
    vlan 30 by port
        tagged ethernet 1/1/24
- Desabilitar uma porta:
    interface ethernet 1/1/5
        disable

Use o formato de interface <unidade>/<slot>/<porta> (ex: 1/1/3) quando o pedido \
mencionar apenas o número da porta.
""",
    dangerous_patterns=[
        r"\berase\b",
        r"\breload\b",
        r"\berase\s+startup-config\b",
        r"\bdefault\b.*config",
    ],
)
