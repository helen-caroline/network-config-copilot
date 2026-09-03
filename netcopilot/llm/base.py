from abc import ABC, abstractmethod

from netcopilot.models import GeneratedCommand
from netcopilot.vendors.base import VendorProfile


class LLMProvider(ABC):
    """Common interface so the CLI doesn't care which LLM API is behind it."""

    @abstractmethod
    def generate_commands(self, request: str, vendor: VendorProfile) -> GeneratedCommand:
        """Translate a natural-language request into vendor CLI commands."""
        raise NotImplementedError
