from __future__ import annotations

import argparse
import glob
from pathlib import Path

from src.cli import add_common_flags, run_cli
from src.common import ContractError, relpath, repo_path, write_csv
from src.contracts import SPLIT_FIELDS, validate_split


def combine_splits(
    split_paths: list[str | Path],
    output_path: str | Path,
    excluded_datasets: set[str] | None = None,
    min_rows: int = 0,
    path_root: str | Path | None = None,
) -> str:
    excluded = {_normalize_dataset_id(dataset_id) for dataset_id in (excluded_datasets or {"miic"})}
    root = repo_path(path_root).resolve() if path_root is not None else None
    rows = []
    source_counts: dict[str, int] = {}
    excluded_counts: dict[str, int] = {}

    for split_path in _ordered_existing_paths(split_paths):
        for row in validate_split(split_path, check_files=root is None):
            dataset_id = _normalize_dataset_id(row["dataset_id"])
            if dataset_id in excluded:
                excluded_counts[dataset_id] = excluded_counts.get(dataset_id, 0) + 1
                continue
            if root is not None:
                row = dict(row)
                row["image_path"] = _relative_to_root(root, row["image_path"])
                row["mask_path"] = _relative_to_root(root, row["mask_path"])
            rows.append(row)
            source_counts[dataset_id] = source_counts.get(dataset_id, 0) + 1

    if len(rows) < min_rows:
        raise ContractError(
            f"combined split has {len(rows)} row(s), below required minimum {min_rows}; "
            f"input datasets={_format_counts(source_counts)}, excluded={_format_counts(excluded_counts)}"
        )

    write_csv(output_path, rows, SPLIT_FIELDS)
    validate_split(output_path, check_files=root is None)
    return relpath(output_path)


def _ordered_existing_paths(paths: list[str | Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        matches = [repo_path(match) for match in glob.glob(str(path))]
        if matches:
            expanded.extend(matches)
        else:
            expanded.append(repo_path(path))
    unique = sorted({path.resolve(): path for path in expanded}.values())
    if not unique:
        raise ContractError("no split CSV paths were provided")
    missing = [relpath(path) for path in unique if not path.exists()]
    if missing:
        raise ContractError(f"split CSV path(s) do not exist: {', '.join(missing)}")
    return unique


def _normalize_dataset_id(dataset_id: str) -> str:
    return dataset_id.strip().lower()


def _relative_to_root(root: Path, value: str) -> str:
    if value == "":
        return ""
    path = Path(value)
    if not path.is_absolute():
        return value
    try:
        return str(path.resolve().relative_to(root))
    except ValueError as exc:
        raise ContractError(f"path is outside dataset root {root}: {path}") from exc


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{dataset_id}:{count}" for dataset_id, count in sorted(counts.items()))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Combine split CSVs, excluding datasets that must not be trained.")
    parser.add_argument(
        "--split",
        action="append",
        nargs="+",
        required=True,
        help="Split CSV path or glob. Repeatable.",
    )
    parser.add_argument("--output", required=True, help="Combined split CSV path.")
    parser.add_argument(
        "--exclude-dataset",
        action="append",
        default=["miic"],
        help="Dataset id to exclude from the combined split. Repeatable. Defaults to miic.",
    )
    parser.add_argument("--min-rows", type=int, default=0, help="Fail if the combined split has fewer rows.")
    parser.add_argument(
        "--path-root",
        help="Rewrite absolute image_path and mask_path values to be relative to this dataset asset root.",
    )
    add_common_flags(parser)
    run_cli(
        parser,
        lambda args: combine_splits(
            [path for group in args.split for path in group],
            args.output,
            set(args.exclude_dataset),
            args.min_rows,
            args.path_root,
        ),
        argv,
    )


if __name__ == "__main__":
    main()
