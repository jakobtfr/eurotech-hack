from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from PIL import Image

from src.cli import add_common_flags, run_cli
from src.common import ContractError, load_yaml, relpath, repo_path, write_csv
from src.contracts import SPLIT_FIELDS, validate_registry, validate_split


def build_split(config_path: str | Path) -> str:
    config = load_yaml(config_path)
    dataset_id = config["dataset_id"]
    registry_path = config.get("registry_path", "data/registry/sources.jsonl")
    split_path = config["split_path"]
    rows = [row for row in validate_registry(registry_path) if row["dataset_id"] == dataset_id]
    if not rows and not config.get("allow_empty", False):
        raise ContractError(f"{relpath(config_path)} has no registry rows for {dataset_id!r}")

    use_placeholder = bool(config.get("allow_placeholder_tiles", False))
    split_rows: list[dict[str, Any]] = []
    for source in rows:
        if use_placeholder:
            split_rows.extend(_placeholder_tiles(source, config))
        else:
            split_rows.extend(_tiles_for_source(source, config))

    repo_path(config.get("workbench_root", f"datasets/workbench/{dataset_id}")).mkdir(parents=True, exist_ok=True)
    write_csv(split_path, split_rows, SPLIT_FIELDS)
    validate_split(split_path)
    return relpath(split_path)


def _tiles_for_source(source: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    tile_size = int(config.get("tile_size", 448))
    stride = int(config.get("stride", tile_size))
    image_path = repo_path(source["source_path"])
    if not image_path.exists():
        raise ContractError(f"source image does not exist: {source['source_path']}")
    with Image.open(image_path) as image:
        width, height = image.size
    origins = _tile_origins(width, height, tile_size, stride)
    return [_split_row(source, config, x, y, tile_size, stride) for (x, y) in origins]


def _tile_origins(width: int, height: int, tile_size: int, stride: int) -> list[tuple[int, int]]:
    xs = list(range(0, max(1, width - tile_size + 1), stride))
    ys = list(range(0, max(1, height - tile_size + 1), stride))
    # Images smaller than one tile still yield a single tile at the origin.
    if width < tile_size:
        xs = [0]
    if height < tile_size:
        ys = [0]
    return [(x, y) for y in ys for x in xs]


def _placeholder_tiles(source: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    tile_size = int(config.get("tile_size", 448))
    return [_split_row(source, config, 0, 0, tile_size, int(config.get("stride", tile_size)))]


def _split_row(
    source: dict[str, Any], config: dict[str, Any], tile_x: int, tile_y: int, tile_size: int, stride: int
) -> dict[str, Any]:
    is_normal = source["source_label"] == "normal"
    return {
        "tile_id": f"{source['source_image_id']}__x{tile_x:05d}_y{tile_y:05d}_s{tile_size:05d}",
        "source_image_id": source["source_image_id"],
        "dataset_id": source["dataset_id"],
        "category": config.get("category", "default"),
        "wafer_id": source.get("wafer_id") or "",
        "modality": source["modality"],
        "split": "train" if is_normal else "test",
        "label": "good" if is_normal else "anomaly",
        "image_path": source["source_path"],
        "mask_path": source.get("mask_source_path") or "",
        "tile_x": tile_x,
        "tile_y": tile_y,
        "tile_size": tile_size,
        "stride": stride,
        "preprocess_id": config.get("preprocess_id", "rgb_repeat_v1"),
        "support_eligible": is_normal,
        "demo_allowed": bool(source["demo_allowed"]),
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic split manifest from the source registry.")
    parser.add_argument("--config", required=True, help="Dataset YAML config.")
    add_common_flags(parser)
    run_cli(parser, lambda args: build_split(args.config), argv)


if __name__ == "__main__":
    main()
