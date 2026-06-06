from __future__ import annotations

import argparse
from pathlib import Path

from src.cli import add_common_flags, run_cli
from src.common import iso_now, relpath, repo_path, save_json
from src.contracts import validate_predictions, validate_run


def freeze_run(run_path: str | Path) -> str:
    run_dir = repo_path(run_path)
    manifest = validate_run(run_dir, require_frozen=False)
    validate_predictions(manifest["predictions_path"], require_rendered_paths=True)
    manifest["status"] = "frozen"
    manifest["completed_at"] = iso_now()
    save_json(run_dir / "run_manifest.json", manifest)
    validate_run(run_dir, require_frozen=True)
    return relpath(run_dir / "run_manifest.json")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Mark a rendered run as immutable for demo packaging.")
    parser.add_argument("--run", required=True, help="Run directory.")
    add_common_flags(parser)
    run_cli(parser, lambda args: freeze_run(args.run), argv)


if __name__ == "__main__":
    main()
