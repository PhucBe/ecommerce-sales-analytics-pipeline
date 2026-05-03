from __future__ import annotations
from dotenv import load_dotenv
from pathlib import Path
from typing import Any
import yaml
import os


ROOT_DIR = Path(__file__).resolve().parents[2]


def _required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    
    return value


def _require_section(config: dict[str, Any], section_name: str) -> dict[str, Any]:
    section = config.get(section_name)

    if not isinstance(section, dict):
        raise ValueError(f"Missing or invalid '{section_name}' section in config file")
    
    return section


def _require_key(section: dict[str, Any], key_name: str, full_name: str) -> Any:
    if key_name not in section:
        raise ValueError(f"Missing '{full_name}' in config file")
    
    return section[key_name]


def load_app_config(env_name: str | None = None) -> dict[str, Any]:
    load_dotenv(ROOT_DIR / ".env")

    env_name = env_name or os.getenv("APP_ENV", "settings")
    config_path = ROOT_DIR / "config" / f"{env_name}.yml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError(f"Invalid YAML config format: {config_path}")
    
    paths_section = _require_section(config, "paths")
    api_section = _require_section(config, "api")
    posgres_section = _require_section(config, "postgres")
    ingestion_section = _require_section(config, "ingestion")

    _require_key(paths_section, "log_dir", "paths.log_dir")
    _require_key(api_section, "base_url", "api.base_url")
    _require_key(api_section, "timeout_seconds", "api.timeout_seconds")
    _require_key(api_section, "page_limit", "api.page_limit")
    _require_key(api_section, "endpoints", "api.endpoints")
    _require_key(posgres_section, "schema_raw", "postgres.schema_raw")
    _require_key(ingestion_section, "mode", "ingestion.mode")
    _require_key(ingestion_section, "source_system", "ingestion.source_system")
    _require_key(ingestion_section, "truncate_before_load", "ingestion.truncate_before_load")

    config["runtime"] = {
        "env_name": env_name,
        "root_dir": str(ROOT_DIR),
    }

    config["paths"]["log_dir"] = str(
        (ROOT_DIR / config["paths"]["log_dir"]).resolve()
    )

    config["api"]["base_url"] = os.getenv(
        "API_BASE_URL",
        config["api"]["base_url"],
    ).rstrip("/")

    config["postgres"]["host"] = _required_env("POSTGRES_HOST")
    config["postgres"]["port"] = int(os.getenv("POSTGRES_PORT", "5432"))
    config["postgres"]["database"] = _required_env("POSTGRES_DB")
    config["postgres"]["user"] = _required_env("POSTGRES_USER")
    config["postgres"]["password"] = _required_env("POSTGRES_PASSWORD")

    return config