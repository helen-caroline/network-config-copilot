import argparse
import os
import sys

from dotenv import load_dotenv

from netcopilot.audit import log_transaction
from netcopilot.llm.anthropic_provider import AnthropicProvider
from netcopilot.llm.base import LLMProvider
from netcopilot.llm.openai_provider import OpenAIProvider
from netcopilot.ssh_client import SwitchSSHClient
from netcopilot.validator import validate
from netcopilot.vendors import VENDOR_CHOICES, get_vendor


def build_provider(name: str) -> LLMProvider:
    if name == "anthropic":
        return AnthropicProvider()
    if name == "openai":
        return OpenAIProvider()
    raise ValueError(f"Provider desconhecido: {name!r}")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="netcopilot",
        description=(
            "Network Config Copilot: traduz um pedido em linguagem natural para "
            "comandos de rede reais, valida (dry-run) e só então aplica via SSH."
        ),
    )
    parser.add_argument("request", help='Pedido em linguagem natural, ex: "libera a vlan 20 na porta 3"')
    parser.add_argument("--vendor", choices=VENDOR_CHOICES, required=True, help="Dialeto de CLI alvo")
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai"],
        default=os.getenv("LLM_PROVIDER", "anthropic"),
        help="Qual API de LLM usar (default: $LLM_PROVIDER ou 'anthropic')",
    )
    parser.add_argument("--host", default=os.getenv("NETCOPILOT_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("NETCOPILOT_PORT", "2222")))
    parser.add_argument("--username", default=os.getenv("NETCOPILOT_USERNAME", "admin"))
    parser.add_argument("--password", default=os.getenv("NETCOPILOT_PASSWORD"))
    parser.add_argument("--key-filename", default=os.getenv("NETCOPILOT_KEY_FILE"))
    parser.add_argument(
        "--apply", action="store_true", help="Aplica os comandos via SSH (default: só dry-run)"
    )
    parser.add_argument(
        "--yes", action="store_true", help="Não pede confirmação interativa antes de aplicar"
    )
    parser.add_argument(
        "--force", action="store_true", help="Aplica mesmo se o risco for classificado como ALTO"
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    load_dotenv()
    args = parse_args(argv)
    vendor = get_vendor(args.vendor)
    provider = build_provider(args.provider)

    print(f"→ Pedido:  {args.request}")
    print(f"→ Vendor:  {vendor.display_name}")
    print(f"→ LLM:     {args.provider}\n")

    generated = provider.generate_commands(args.request, vendor)

    print("Comandos gerados:")
    for cmd in generated.commands:
        print(f"  {cmd}")
    print(f"\nExplicação: {generated.explanation}")
    print(f"Risco: {generated.risk.upper()}")
    if generated.warnings:
        print("Avisos:")
        for w in generated.warnings:
            print(f"  - {w}")

    result = validate(generated, vendor, allow_high_risk=args.force)

    audit_entry = {
        "request": args.request,
        "vendor": args.vendor,
        "provider": args.provider,
        "generated_commands": generated.commands,
        "risk": generated.risk,
        "explanation": generated.explanation,
        "warnings": generated.warnings,
        "validation_ok": result.ok,
        "blocked_reasons": result.blocked_reasons,
        "dry_run": not args.apply,
        "applied": False,
    }

    if not result.ok:
        print("\n✗ Validação bloqueou a execução:")
        for reason in result.blocked_reasons:
            print(f"  - {reason}")
        log_transaction(audit_entry)
        return 1

    if not args.apply:
        print("\n(dry-run) Nenhum comando foi enviado ao dispositivo. Use --apply para executar.")
        log_transaction(audit_entry)
        return 0

    if not args.yes:
        confirm = input("\nAplicar estes comandos no dispositivo agora? [s/N] ").strip().lower()
        if confirm not in ("s", "sim", "y", "yes"):
            print("Cancelado pelo usuário.")
            log_transaction(audit_entry)
            return 0

    client = SwitchSSHClient(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        key_filename=args.key_filename,
    )
    client.connect()
    try:
        transcript = client.run_commands(generated.commands)
    finally:
        client.close()

    print("\nSaída do dispositivo:")
    for step in transcript:
        print(f"$ {step['command']}")
        print(step["output"])

    audit_entry["applied"] = True
    audit_entry["device_transcript"] = transcript
    log_transaction(audit_entry)
    print("✓ Comandos aplicados e registrados no audit log.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
