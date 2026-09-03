import json
import os

from openai import OpenAI

from netcopilot.llm.base import LLMProvider
from netcopilot.models import GeneratedCommand
from netcopilot.vendors.base import VendorProfile, build_system_prompt

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str | None = None):
        self.client = OpenAI()
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    def generate_commands(self, request: str, vendor: VendorProfile) -> GeneratedCommand:
        schema_hint = json.dumps(GeneratedCommand.model_json_schema(), ensure_ascii=False)
        system = (
            f"{build_system_prompt(vendor)}\n\n"
            "Responda SOMENTE com um JSON válido (sem markdown, sem texto extra) "
            f"seguindo exatamente este schema:\n{schema_hint}"
        )
        completion = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": request},
            ],
        )
        raw = completion.choices[0].message.content
        return GeneratedCommand.model_validate(json.loads(raw))
