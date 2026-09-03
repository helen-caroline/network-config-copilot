from netcopilot.models import GeneratedCommand
from netcopilot.validator import validate
from netcopilot.vendors import get_vendor

CISCO = get_vendor("cisco_ios")


def test_low_risk_command_passes():
    generated = GeneratedCommand(
        commands=["interface GigabitEthernet1/0/3", "switchport access vlan 20"],
        explanation="Libera a VLAN 20 de acesso na porta 3.",
        risk="low",
        warnings=[],
    )
    result = validate(generated, CISCO)
    assert result.ok
    assert result.blocked_reasons == []


def test_dangerous_pattern_is_blocked():
    generated = GeneratedCommand(
        commands=["reload"],
        explanation="Reinicia o switch.",
        risk="low",
        warnings=[],
    )
    result = validate(generated, CISCO)
    assert not result.ok
    assert any("reload" in reason.lower() for reason in result.blocked_reasons)


def test_high_risk_is_blocked_unless_forced():
    generated = GeneratedCommand(
        commands=["interface GigabitEthernet1/0/3"],
        explanation="Pedido ambíguo.",
        risk="high",
        warnings=["Não ficou claro qual VLAN aplicar."],
    )
    blocked = validate(generated, CISCO)
    assert not blocked.ok

    forced = validate(generated, CISCO, allow_high_risk=True)
    assert forced.ok


def test_empty_commands_is_blocked():
    generated = GeneratedCommand(commands=[], explanation="Nada a fazer.", risk="low", warnings=[])
    result = validate(generated, CISCO)
    assert not result.ok
