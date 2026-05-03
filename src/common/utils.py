from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import re


def ensure_directory(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_batch_id(prefix: str = "api_ingestion") -> str:
    timestamp = utc_now().strftime("%Y%m%d_%H%M%S")
    
    return f"{prefix}_{timestamp}"


def sanitize_identifier(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_]", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")

    if value and value[0].isdigit():
        value = f"col_{value}"

    return value