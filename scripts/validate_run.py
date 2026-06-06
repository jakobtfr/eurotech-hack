from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli import add_common_flags, run_cli  # noqa: E402
from src.contracts import validate_run  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a frozen run artifact directory.")
    parser.add_argument("run", help="Run directory.")
    add_common_flags(parser)
    run_cli(parser, lambda args: f"valid frozen run={validate_run(args.run)['run_id']}")


if __name__ == "__main__":
    main()
