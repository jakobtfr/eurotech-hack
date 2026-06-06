"""Prepare a dataset-root folder for local or Azure DINOv2/PCA training.

The dataset machine is expected to have a folder like:

    datasets_ready/
      visa/
      mvtec_ad/
      nffa_sem/
      ...

This script scans each dataset folder, writes registry/config/split artifacts
inside that same dataset root, and creates one combined split whose image paths
are relative to the root. MIIC is excluded by default until access/licensing is
ready.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cli import add_common_flags, run_cli  # noqa: E402
from src.common import SCHEMA_VERSION, ContractError, repo_path  # noqa: E402
from src.data.build import build_split  # noqa: E402
from src.data.combine_splits import combine_splits  # noqa: E402

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
MASK_PARTS = {"ground_truth", "ground-truth", "gt", "label", "labels", "mask", "masks"}
NORMAL_PARTS = {"good", "negative", "normal", "ok", "regular"}
ANOMALY_PARTS = {
    "abnormal",
    "anomalies",
    "anomalous",
    "anomaly",
    "bad",
    "defect",
    "defective",
    "defects",
    "fault",
    "faulty",
    "ng",
    "positive",
}
MODALITY_BY_DATASET = {
    "mixedwm38": "wafer_map",
    "nffa_sem": "SEM",
    "semi_ad": "SEM",
    "zenodo_sic": "PL",
}


def prepare_training_dataset(
    dataset_root: str | Path,
    combined_split: str | Path = "splits/combined_no_miic.csv",
    datasets: list[str] | None = None,
    excluded_datasets: set[str] | None = None,
    min_rows: int = 1,
    unknown_label: str = "skip",
    license_status: str = "unknown",
    license_reference: str = "",
) -> str:
    root = repo_path(dataset_root).resolve()
    if not root.exists():
        raise ContractError(f"dataset root does not exist: {root}")
    excluded = {_normalize(dataset_id) for dataset_id in (excluded_datasets or {"miic"})}
    dataset_dirs = _dataset_dirs(root, datasets, excluded)
    split_paths: list[Path] = []
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "dataset_root": str(root),
        "excluded_datasets": sorted(excluded),
        "datasets": [],
    }

    for dataset_dir in dataset_dirs:
        dataset_id = dataset_dir.name
        rows = _registry_rows(dataset_dir, dataset_id, unknown_label, license_status, license_reference)
        dataset_report = {
            "dataset_id": dataset_id,
            "source_count": len(rows),
            "normal_count": sum(1 for row in rows if row["source_label"] == "normal"),
            "anomaly_count": sum(1 for row in rows if row["source_label"] == "anomaly"),
        }
        report["datasets"].append(dataset_report)
        if not rows:
            continue

        registry_path = root / "registry" / f"{dataset_id}.jsonl"
        config_path = root / "configs" / f"{dataset_id}.yaml"
        split_path = root / "splits" / f"{dataset_id}_v0.csv"
        _write_jsonl(registry_path, rows)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(_config_yaml(root, dataset_id, registry_path, split_path), encoding="utf-8")
        build_split(config_path)
        split_paths.append(split_path)
        dataset_report["registry_path"] = str(registry_path)
        dataset_report["split_path"] = str(split_path)

    if not split_paths:
        raise ContractError(f"no trainable dataset splits were generated under {root}")

    combined_path = root / combined_split
    combine_splits(split_paths, combined_path, excluded, min_rows=min_rows, path_root=root)
    report["combined_split"] = str(combined_path)
    report_path = root / "training_dataset_manifest.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(combined_path)


def _dataset_dirs(root: Path, requested: list[str] | None, excluded: set[str]) -> list[Path]:
    if requested:
        paths = [root / dataset_id for dataset_id in requested]
        missing = [str(path) for path in paths if not path.exists()]
        if missing:
            raise ContractError(f"requested dataset folder(s) do not exist: {', '.join(missing)}")
    else:
        paths = [path for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")]
        paths = [path for path in paths if path.name not in {"configs", "registry", "splits", "workbench"}]
    return sorted(path for path in paths if _normalize(path.name) not in excluded)


def _registry_rows(
    dataset_dir: Path,
    dataset_id: str,
    unknown_label: str,
    license_status: str,
    license_reference: str,
) -> list[dict[str, Any]]:
    masks = _mask_index(dataset_dir)
    rows = []
    for image_path in _images(dataset_dir):
        if _is_mask_path(dataset_dir, image_path):
            continue
        label = _label_for_path(dataset_dir, image_path, unknown_label)
        if label is None:
            continue
        mask_path = _match_mask(image_path, masks) if label == "anomaly" else None
        rows.append(
            {
                "schema_version": SCHEMA_VERSION,
                "source_image_id": _source_id(dataset_id, label, dataset_dir, image_path),
                "dataset_id": dataset_id,
                "wafer_id": None,
                "source_path": str(image_path),
                "modality": MODALITY_BY_DATASET.get(_normalize(dataset_id), "optical"),
                "source_label": label,
                "mask_source_path": str(mask_path) if mask_path is not None else None,
                "license_status": license_status,
                "license_reference": license_reference,
                "demo_allowed": False,
                "notes": "generated by scripts/prepare_training_dataset.py",
            }
        )
    return sorted(rows, key=lambda row: str(row["source_image_id"]))


def _images(directory: Path) -> list[Path]:
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS and not path.name.startswith(".")
    )


def _mask_index(dataset_dir: Path) -> dict[str, Path]:
    masks: dict[str, Path] = {}
    for path in _images(dataset_dir):
        if not _is_mask_path(dataset_dir, path):
            continue
        for key in _mask_keys(path):
            masks.setdefault(key, path)
    return masks


def _is_mask_path(dataset_dir: Path, path: Path) -> bool:
    parts = {_token(part) for part in path.relative_to(dataset_dir).parts[:-1]}
    return bool(parts & MASK_PARTS)


def _label_for_path(dataset_dir: Path, path: Path, unknown_label: str) -> str | None:
    parts = [_token(part) for part in path.relative_to(dataset_dir).parts[:-1]]
    part_set = set(parts)
    if part_set & ANOMALY_PARTS:
        return "anomaly"
    if part_set & NORMAL_PARTS:
        return "normal"
    if "test" in part_set and not (part_set & NORMAL_PARTS):
        return "anomaly"
    if unknown_label == "normal":
        return "normal"
    if unknown_label == "anomaly":
        return "anomaly"
    return None


def _match_mask(image_path: Path, masks: dict[str, Path]) -> Path | None:
    for key in _mask_keys(image_path):
        if key in masks:
            return masks[key]
    return None


def _mask_keys(path: Path) -> list[str]:
    stem = _token(path.stem)
    stripped = re.sub(r"(_|-)?(mask|gt|ground_truth)$", "", stem)
    return [stem, stripped]


def _source_id(dataset_id: str, label: str, dataset_dir: Path, image_path: Path) -> str:
    relative = image_path.relative_to(dataset_dir).with_suffix("")
    slug = _token("_".join(relative.parts))
    digest = hashlib.sha1(str(relative).encode("utf-8")).hexdigest()[:8]
    return f"{_token(dataset_id)}_{label}_{slug}_{digest}"


def _token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _normalize(dataset_id: str) -> str:
    return dataset_id.strip().lower()


def _config_yaml(root: Path, dataset_id: str, registry_path: Path, split_path: Path) -> str:
    return (
        "\n".join(
            [
                f'schema_version: "{SCHEMA_VERSION}"',
                f"dataset_id: {dataset_id}",
                "version: v0",
                f"category: {dataset_id}",
                f"registry_path: {registry_path}",
                f"split_path: {split_path}",
                f"workbench_root: {root / 'workbench' / dataset_id}",
                "tile_size: 448",
                "stride: 448",
                "preprocess_id: rgb_repeat_v1",
                "train_fraction: 0.5",
                "validation_fraction: 0.25",
                "allow_empty: false",
                "allow_placeholder_tiles: false",
            ]
        )
        + "\n"
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True))
            handle.write("\n")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Prepare dataset-root registry, splits, and combined training split.")
    parser.add_argument("--dataset-root", required=True, help="Folder containing ready dataset subfolders.")
    parser.add_argument(
        "--combined-split",
        default="splits/combined_no_miic.csv",
        help="Combined split path, relative to dataset root unless absolute.",
    )
    parser.add_argument("--dataset", action="append", help="Only prepare this dataset folder. Repeatable.")
    parser.add_argument(
        "--exclude-dataset",
        action="append",
        default=["miic"],
        help="Dataset id to skip. Repeatable. Defaults to miic.",
    )
    parser.add_argument("--min-rows", type=int, default=1, help="Fail if the combined split has fewer rows.")
    parser.add_argument(
        "--unknown-label",
        choices=["skip", "normal", "anomaly"],
        default="skip",
        help="How to treat images whose path does not reveal normal/anomaly label.",
    )
    parser.add_argument("--license-status", choices=["verified", "restricted", "unknown"], default="unknown")
    parser.add_argument("--license-reference", default="")
    add_common_flags(parser)
    run_cli(
        parser,
        lambda args: prepare_training_dataset(
            args.dataset_root,
            args.combined_split,
            args.dataset,
            set(args.exclude_dataset),
            args.min_rows,
            args.unknown_label,
            args.license_status,
            args.license_reference,
        ),
        argv,
    )


if __name__ == "__main__":
    main()
