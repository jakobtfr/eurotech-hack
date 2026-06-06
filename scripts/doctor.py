from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli import add_common_flags, run_cli  # noqa: E402
from src.common import ContractError, load_yaml, relpath, repo_path  # noqa: E402


def doctor(config_path: str) -> str:
    config = load_yaml(config_path)
    required_paths = [config_path, config.get("registry_path", "data/registry/sources.jsonl")]
    required_paths.extend(config.get("dataset_configs") or [])
    required_paths.extend(config.get("model_configs") or [])
    missing = [path for path in required_paths if not repo_path(path).exists()]
    if missing:
        raise ContractError(f"missing required path(s): {', '.join(missing)}")
    if shutil.which("uv") is None:
        raise ContractError("uv is required to run backend commands")
    return "\n".join(
        [
            "backend scaffold ok",
            f"config={relpath(config_path)}",
            f"registry={relpath(config.get('registry_path', 'data/registry/sources.jsonl'))}",
            f"datasets={len(config.get('dataset_configs') or [])}",
            f"models={len(config.get('model_configs') or [])}",
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate local backend scaffolding prerequisites.")
    parser.add_argument("--config", default="configs/demo.yaml", help="Demo YAML config.")
    add_common_flags(parser)
    run_cli(parser, lambda args: doctor(args.config))


if __name__ == "__main__":
    main()
