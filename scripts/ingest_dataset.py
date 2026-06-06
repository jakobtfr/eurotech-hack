"""Register an on-disk image dataset into the workbench registry + data config.

Scans a folder of normal images (and optionally anomaly images + masks) and emits
`data/registry/<id>.jsonl` plus `configs/data/<id>.yaml`, ready for
`python -m src.data.build`. Works for:

- Labeled benchmarks (MVTec/VisA): --normal-dir + --anomaly-dir + --mask-dir
  -> Image AUROC and (with masks) Pixel AUROC.
- Unlabeled microscopy (SiC/SEM): --normal-dir only -> qualitative heatmaps,
  metrics correctly gated as unavailable.

Example:
    python scripts/ingest_dataset.py --dataset-id visa_pcb1 --modality optical \\
        --normal-dir data/raw/visa/pcb1/Data/Images/Normal \\
        --anomaly-dir data/raw/visa/pcb1/Data/Images/Anomaly \\
        --mask-dir data/raw/visa/pcb1/Data/Masks/Anomaly
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.common import SCHEMA_VERSION, relpath, repo_path  # noqa: E402

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".JPG", ".PNG"}
MODALITIES = {"SEM", "PL", "etch", "optical", "wafer_map", "synthetic", "other"}


def ingest(args: argparse.Namespace) -> str:
    rows: list[dict[str, object]] = []
    for path in _images(args.normal_dir):
        rows.append(_row(args, path, "normal", None))
    if args.anomaly_dir:
        masks = {p.stem: p for p in _images(args.mask_dir)} if args.mask_dir else {}
        for path in _images(args.anomaly_dir):
            rows.append(_row(args, path, "anomaly", _match_mask(path, masks)))
    if not rows:
        raise SystemExit(f"no images found under {args.normal_dir}")

    registry_path = repo_path(args.out_registry)
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    with registry_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")

    config_path = repo_path(args.out_config)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(_config_yaml(args), encoding="utf-8")

    normals = sum(1 for r in rows if r["source_label"] == "normal")
    anomalies = len(rows) - normals
    masked = sum(1 for r in rows if r["mask_source_path"])
    print(
        f"{relpath(registry_path)}: {len(rows)} sources "
        f"({normals} normal, {anomalies} anomaly, {masked} with masks) | config {relpath(config_path)}"
    )
    return relpath(registry_path)


def _images(directory: str | None) -> list[Path]:
    if not directory:
        return []
    base = repo_path(directory)
    if not base.exists():
        raise SystemExit(f"directory does not exist: {directory}")
    return sorted(p for p in base.rglob("*") if p.suffix in IMAGE_EXTENSIONS and p.is_file())


def _match_mask(image: Path, masks: dict[str, Path]) -> Path | None:
    # VisA/MVTec masks share the image stem, sometimes with a _mask suffix.
    for candidate in (image.stem, f"{image.stem}_mask"):
        if candidate in masks:
            return masks[candidate]
    return None


def _row(args: argparse.Namespace, path: Path, label: str, mask: Path | None) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_image_id": f"{args.dataset_id}_{label}_{path.stem}",
        "dataset_id": args.dataset_id,
        "wafer_id": None,
        "source_path": relpath(path),
        "modality": args.modality,
        "source_label": label,
        "mask_source_path": relpath(mask) if mask else None,
        "license_status": args.license_status,
        "license_reference": args.license_reference,
        "demo_allowed": args.demo_allowed,
        "notes": args.notes,
    }


def _config_yaml(args: argparse.Namespace) -> str:
    return (
        "\n".join(
            [
                f'schema_version: "{SCHEMA_VERSION}"',
                f"dataset_id: {args.dataset_id}",
                f"registry_path: {relpath(repo_path(args.out_registry))}",
                f"split_path: data/splits/{args.dataset_id}.csv",
                f"workbench_root: datasets/workbench/{args.dataset_id}",
                f"category: {args.category}",
                f"tile_size: {args.tile_size}",
                f"stride: {args.stride}",
                f"preprocess_id: {args.preprocess_id}",
                "train_fraction: 0.5",
                "validation_fraction: 0.25",
                "allow_empty: false",
                "allow_placeholder_tiles: false",
            ]
        )
        + "\n"
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Register an image dataset into the workbench registry + config.")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--normal-dir", required=True, help="Directory of normal/good images.")
    parser.add_argument("--anomaly-dir", help="Directory of anomalous images (optional).")
    parser.add_argument("--mask-dir", help="Directory of ground-truth masks (optional).")
    parser.add_argument("--modality", default="other", choices=sorted(MODALITIES))
    parser.add_argument("--category", default="default")
    parser.add_argument("--tile-size", type=int, default=448)
    parser.add_argument("--stride", type=int, default=448)
    parser.add_argument("--preprocess-id", default="rgb_repeat_v1")
    parser.add_argument("--license-status", default="unknown", choices=["verified", "restricted", "unknown"])
    parser.add_argument("--license-reference", default="")
    parser.add_argument("--demo-allowed", action="store_true", help="Mark sources publicly displayable.")
    parser.add_argument("--notes", default="")
    parser.add_argument("--out-registry", help="Registry output path (default data/registry/<id>.jsonl).")
    parser.add_argument("--out-config", help="Config output path (default configs/data/<id>.yaml).")
    args = parser.parse_args(argv)
    if not args.out_registry:
        args.out_registry = f"data/registry/{args.dataset_id}.jsonl"
    if not args.out_config:
        args.out_config = f"configs/data/{args.dataset_id}.yaml"
    ingest(args)


if __name__ == "__main__":
    main()
