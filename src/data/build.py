from __future__ import annotations

import argparse
from pathlib import Path

from src.cli import add_common_flags, run_cli
from src.common import ContractError, load_yaml, relpath, repo_path, write_csv
from src.contracts import SPLIT_FIELDS, validate_registry, validate_split


def build_split(config_path: str | Path) -> str:
    config = load_yaml(config_path)
    dataset_id = config["dataset_id"]
    registry_path = config.get("registry_path", "data/registry/sources.jsonl")
    split_path = config["split_path"]
    rows = [row for row in validate_registry(registry_path) if row["dataset_id"] == dataset_id]
    if rows and not config.get("allow_placeholder_tiles", False):
        raise ContractError(
            f"{relpath(config_path)} found {len(rows)} registry row(s) for {dataset_id!r}, "
            "but real image tiling is not implemented yet. Set allow_placeholder_tiles=true only for local smoke data."
        )
    if not rows and not config.get("allow_empty", False):
        raise ContractError(f"{relpath(config_path)} has no registry rows for {dataset_id!r}")

    split_rows = []
    for source in rows:
        tile_size = int(config.get("tile_size", 448))
        tile_id = f"{source['source_image_id']}__x00000_y00000_s{tile_size:05d}"
        split_rows.append(
            {
                "tile_id": tile_id,
                "source_image_id": source["source_image_id"],
                "dataset_id": source["dataset_id"],
                "category": config.get("category", "default"),
                "wafer_id": source.get("wafer_id") or "",
                "modality": source["modality"],
                "split": "train" if source["source_label"] == "normal" else "test",
                "label": "good" if source["source_label"] == "normal" else "anomaly",
                "image_path": source["source_path"],
                "mask_path": source.get("mask_source_path") or "",
                "tile_x": 0,
                "tile_y": 0,
                "tile_size": tile_size,
                "stride": int(config.get("stride", tile_size)),
                "preprocess_id": config.get("preprocess_id", "rgb_repeat_v1"),
                "support_eligible": source["source_label"] == "normal",
                "demo_allowed": bool(source["demo_allowed"]),
            }
        )

    repo_path(config.get("workbench_root", f"datasets/workbench/{dataset_id}")).mkdir(parents=True, exist_ok=True)
    write_csv(split_path, split_rows, SPLIT_FIELDS)
    validate_split(split_path)
    return relpath(split_path)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic split manifest from the source registry.")
    parser.add_argument("--config", required=True, help="Dataset YAML config.")
    add_common_flags(parser)
    run_cli(parser, lambda args: build_split(args.config), argv)


if __name__ == "__main__":
    main()
