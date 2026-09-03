import pytest

from netcopilot.vendors import VENDOR_CHOICES, get_vendor
from netcopilot.vendors.base import build_system_prompt


@pytest.mark.parametrize("key", VENDOR_CHOICES)
def test_every_vendor_builds_a_system_prompt(key):
    vendor = get_vendor(key)
    prompt = build_system_prompt(vendor)
    assert vendor.display_name in prompt or vendor.key in prompt or len(prompt) > 100
    assert vendor.dangerous_patterns  # every vendor must define at least one guardrail


def test_unknown_vendor_raises():
    with pytest.raises(ValueError):
        get_vendor("not-a-real-vendor")
