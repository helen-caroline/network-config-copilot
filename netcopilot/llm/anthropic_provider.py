import os

import anthropic

from netcopilot.llm.base import LLMProvider
from netcopilot.models import GeneratedCommand
from netcopilot.vendors.base import VendorProfile, build_system_prompt

DEFAULT_MODEL = "claude-opus-5"


class AnthropicProvider(LLMProvider):
    def __init__(self, model: str | None = None):
        self.client = anthropic.Anthropic()
        self.model = model or os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)

    def generate_commands(self, request: str, vendor: VendorProfile) -> GeneratedCommand:
        response = self.client.messages.parse(
            model=self.model,
            max_tokens=2048,
            system=build_system_prompt(vendor),
            messages=[{"role": "user", "content": request}],
            output_format=GeneratedCommand,
        )
        return response.parsed_output
