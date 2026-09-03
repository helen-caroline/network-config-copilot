from netcopilot.vendors.base import VendorProfile

PROFILE = VendorProfile(
    key="juniper",
    display_name="Juniper (Junos)",
    cli_prompt="user@switch>",
    syntax_guide="""\
Dialeto: Junos (EX series), estilo "set" (modo de configuração).

Exemplos de sintaxe real:
- Criar a VLAN 20:
    set vlans VLAN20 vlan-id 20
- Liberar VLAN 20 de acesso na porta ge-0/0/3:
    set interfaces ge-0/0/3 unit 0 family ethernet-switching vlan members VLAN20
    set interfaces ge-0/0/3 unit 0 family ethernet-switching port-mode access
- Liberar VLAN 30 como tagged (trunk) na porta ge-0/0/24:
    set interfaces ge-0/0/24 unit 0 family ethernet-switching port-mode trunk
    set interfaces ge-0/0/24 unit 0 family ethernet-switching vlan members VLAN30
- Desabilitar uma porta:
    set interfaces ge-0/0/5 disable

Comandos "set" ficam pendentes até um "commit" — não inclua "commit" a menos que \
o pedido peça explicitamente para persistir a mudança.
""",
    dangerous_patterns=[
        r"\brequest\s+system\s+reboot\b",
        r"\brequest\s+system\s+zeroize\b",
        r"\brequest\s+system\s+halt\b",
        r"^\s*delete\s+interfaces\b",
        r"^\s*delete\s+vlans\b",
    ],
)
