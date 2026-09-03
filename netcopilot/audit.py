import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

AUDIT_LOG_PATH = os.getenv("NETCOPILOT_AUDIT_LOG", "audit_log.jsonl")


def log_transaction(entry: Dict[str, Any]) -> None:
    """Append one JSON line per request: what was asked, generated, validated,
    and (if applicable) applied. This is the audit trail a real network-change
    process would require."""
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), **entry}
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
