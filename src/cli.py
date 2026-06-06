from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Any

from src.common import ContractError


def run_cli(
    parser: argparse.ArgumentParser, handler: Callable[[argparse.Namespace], Any], argv: list[str] | None = None
) -> None:
    args = parser.parse_args(argv)
    try:
        result = handler(args)
    except ContractError as exc:
        raise SystemExit(f"error: {exc}") from exc
    if result is not None and not getattr(args, "quiet", False):
        if getattr(args, "plain", False):
            print(result)
        else:
            print(result)


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--plain", action="store_true", help="Print stable plain output for scripts.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress success output.")
