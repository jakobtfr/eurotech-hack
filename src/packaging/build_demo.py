from __future__ import annotations

import argparse
from pathlib import Path

from src.cli import add_common_flags, run_cli
from src.common import SCHEMA_VERSION, ContractError, load_yaml, relpath, repo_path, save_json
from src.contracts import validate_demo, validate_run


def build_demo(config_path: str | Path) -> str:
    config = load_yaml(config_path)
    runs = config.get("runs") or []
    if not runs and not config.get("allow_empty", False):
        raise ContractError(f"{relpath(config_path)} has no runs; set allow_empty=true only for scaffolding")
    manifest_runs = []
    for run_path in runs:
        run = validate_run(run_path, require_frozen=True)
        manifest_runs.append(
            {
                "run_id": run["run_id"],
                "run_manifest_path": relpath(repo_path(run_path) / "run_manifest.json"),
                "model_name": run["model_name"],
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "demo_id": config.get("demo_id", "demo"),
        "status": config.get("status", "scaffold" if not runs else "ready"),
        "runs": manifest_runs,
        "featured_examples": config.get("featured_examples") or [],
        "risk_maps": config.get("risk_maps") or [],
        "metrics": config.get("metrics") or [],
        "caveats": config.get("caveats") or [],
    }
    manifest_path = config.get("manifest_path", "demo/manifest.json")
    save_json(manifest_path, manifest)
    validate_demo(manifest_path)
    return relpath(manifest_path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the offline demo manifest from frozen run artifacts.")
    parser.add_argument("--config", required=True, help="Demo YAML config.")
    add_common_flags(parser)
    run_cli(parser, lambda args: build_demo(args.config), argv)


if __name__ == "__main__":
    main()
