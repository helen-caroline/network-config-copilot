from netcopilot.vendors.base import VendorProfile

PROFILE = VendorProfile(
    key="cisco_ios",
    display_name="Cisco IOS",
    cli_prompt="Switch#",
    syntax_guide="""\
Dialeto: Cisco IOS (switches de acesso/distribuição).

Exemplos de sintaxe real:
- Liberar VLAN 20 de acesso na porta GigabitEthernet1/0/3:
    interface GigabitEthernet1/0/3
    switchport mode access
    switchport access vlan 20
    no shutdown
- Criar a VLAN 20 (se ainda não existir):
    vlan 20
    name VLAN20
- Liberar VLAN 30 como tagged (trunk) em uma porta:
    interface GigabitEthernet1/0/24
    switchport mode trunk
    switchport trunk allowed vlan add 30
- Desabilitar uma porta:
    interface GigabitEthernet1/0/5
    shutdown

Use nomes de interface no formato GigabitEthernet<slot>/<módulo>/<porta> quando o \
pedido não especificar o tipo de interface — assuma GigabitEthernet1/0/<porta>.
""",
    dangerous_patterns=[
        r"\breload\b",
        r"\berase\b",
        r"\bformat\b",
        r"\bwrite\s+erase\b",
        r"\bdelete\b.*flash",
        r"\bno\s+ip\s+route\b",
        r"^\s*shutdown\s*$",  # bare shutdown outside interface context is suspicious
    ],
)
