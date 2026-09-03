from netcopilot.vendors.base import VendorProfile

PROFILE = VendorProfile(
    key="fortigate",
    display_name="Fortigate",
    cli_prompt="FortiGate #",
    syntax_guide="""\
Dialeto: FortiOS (Fortigate), estilo config/edit/next/end.

Exemplos de sintaxe real:
- Atribuir a VLAN 20 (interface VLAN já existente "vlan20") à porta port3 como \
membro de uma zona/softswitch, ou definir port3 como untagged nessa VLAN:
    config system interface
        edit "vlan20"
            set vlanid 20
            set interface "port3"
        next
    end
- Criar uma política de firewall simples permitindo tráfego entre duas interfaces:
    config firewall policy
        edit 0
            set name "allow-vlan20"
            set srcintf "vlan20"
            set dstintf "wan1"
            set srcaddr "all"
            set dstaddr "all"
            set schedule "always"
            set service "ALL"
            set action accept
        next
    end
- Desabilitar uma interface:
    config system interface
        edit "port3"
            set status down
        next
    end

Use aspas duplas em nomes de interface/política, como no FortiOS real.
""",
    dangerous_patterns=[
        r"\bexecute\s+factoryreset\b",
        r"\bexecute\s+reboot\b",
        r"\bexecute\s+shutdown\b",
        r"\bformat\b",
        r"^\s*purge\b",
        r"\bset\s+action\s+deny\b.*all",
    ],
)
