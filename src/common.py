from __future__ import annotations

import csv
import json
import platform
import subprocess
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

SCHEMA_VERSION = "1.0"
REPO_ROOT = Path(__file__).resolve().parents[1]


class ContractError(ValueError):
    """Raised when a pipeline artifact violates the local contract."""


def repo_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return REPO_ROOT / candidate


def relpath(path: str | Path) -> str:
    resolved = repo_path(path).resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(resolved)


def load_yaml(path: str | Path) -> dict[str, Any]:
    target = repo_path(path)
    with target.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    if not isinstance(loaded, dict):
        raise ContractError(f"{relpath(target)} must contain a YAML mapping")
    return loaded


def load_json(path: str | Path) -> dict[str, Any]:
    target = repo_path(path)
    with target.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)
    if not isinstance(loaded, dict):
        raise ContractError(f"{relpath(target)} must contain a JSON object")
    return loaded


def save_json(path: str | Path, payload: dict[str, Any]) -> None:
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    target = repo_path(path)
    rows: list[dict[str, Any]] = []
    if not target.exists():
        raise ContractError(f"{relpath(target)} does not exist")
    with target.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                loaded = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ContractError(f"{relpath(target)}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(loaded, dict):
                raise ContractError(f"{relpath(target)}:{line_number}: row must be a JSON object")
            loaded["_line_number"] = line_number
            rows.append(loaded)
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            payload = {key: value for key, value in row.items() if not key.startswith("_")}
            handle.write(json.dumps(payload, sort_keys=True))
            handle.write("\n")


def read_csv(path: str | Path) -> list[dict[str, str]]:
    target = repo_path(path)
    if not target.exists():
        raise ContractError(f"{relpath(target)} does not exist")
    with target.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return []
        return list(reader)


def write_csv(path: str | Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    target = repo_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def require_keys(record: dict[str, Any], required: Iterable[str], context: str) -> None:
    missing = [key for key in required if key not in record]
    if missing:
        raise ContractError(f"{context}: missing required field(s): {', '.join(missing)}")


def iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def environment_snapshot() -> str:
    lines = [
        f"generated_at={iso_now()}",
        f"python={platform.python_version()}",
        f"platform={platform.platform()}",
        f"machine={platform.machine()}",
        f"git_commit={git_commit() or 'unknown'}",
    ]
    return "\n".join(lines) + "\n"


def stable_unit_interval(value: str) -> float:
    import hashlib

    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    integer = int(digest[:12], 16)
    return integer / float(0xFFFFFFFFFFFF)


def fail(message: str) -> None:
    raise SystemExit(message)
