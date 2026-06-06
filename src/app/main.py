from __future__ import annotations

import argparse
import json

from src.cli import add_common_flags, run_cli
from src.contracts import validate_demo


def show_manifest(manifest_path: str, offline: bool = True) -> str:
    manifest = validate_demo(manifest_path)
    summary = {
        "demo_id": manifest["demo_id"],
        "status": manifest["status"],
        "offline": offline,
        "run_count": len(manifest.get("runs") or []),
        "example_count": len(manifest.get("featured_examples") or []),
        "caveats": manifest.get("caveats") or [],
    }
    return json.dumps(summary, indent=2, sort_keys=True)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate and summarize the offline demo manifest.")
    parser.add_argument("--manifest", required=True, help="Demo manifest JSON path.")
    parser.add_argument(
        "--offline", action="store_true", help="Confirm the app must not require network or live training."
    )
    add_common_flags(parser)
    run_cli(parser, lambda args: show_manifest(args.manifest, args.offline), argv)


if __name__ == "__main__":
    main()
