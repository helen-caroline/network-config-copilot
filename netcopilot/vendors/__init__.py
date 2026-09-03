from netcopilot.vendors import aruba, cisco_ios, fortigate, juniper, ruckus
from netcopilot.vendors.base import VendorProfile, build_system_prompt

VENDOR_REGISTRY = {
    profile.key: profile
    for profile in (
        cisco_ios.PROFILE,
        fortigate.PROFILE,
        aruba.PROFILE,
        juniper.PROFILE,
        ruckus.PROFILE,
    )
}

VENDOR_CHOICES = sorted(VENDOR_REGISTRY.keys())


def get_vendor(key: str) -> VendorProfile:
    try:
        return VENDOR_REGISTRY[key]
    except KeyError:
        raise ValueError(
            f"Vendor desconhecido: {key!r}. Opções válidas: {', '.join(VENDOR_CHOICES)}"
        ) from None


__all__ = ["VendorProfile", "VENDOR_REGISTRY", "VENDOR_CHOICES", "get_vendor", "build_system_prompt"]
