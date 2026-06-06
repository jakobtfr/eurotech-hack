#!/usr/bin/env python3
"""Prepare a leakage-safe SiC split and fine-tune a compact OBB detector."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from pathlib import Path

import torch
import yaml
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "datasets/sic_dislocation_detection_db/bvn-Topazval200"
SAFE_ROOT = REPO_ROOT / "datasets/sic_dislocation_detection_db/leakage_safe"
RESULTS_ROOT = REPO_ROOT / "sic_results"
CLASS_NAMES = {0: "TD", 1: "BPD"}


def session_name(path: Path) -> str:
    match = re.match(r"^(\d{8}test\d+)", path.stem)
    if not match:
        raise ValueError(f"Cannot infer acquisition session from {path.name}")
    return match.group(1)


def label_path(image_path: Path) -> Path:
    return SOURCE_ROOT / "labels" / image_path.parent.name / f"{image_path.stem}.txt"


def link(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        os.symlink(source, destination)


def prepare_split() -> dict[str, object]:
    source_train = list((SOURCE_ROOT / "images/train").glob("*"))
    source_val = list((SOURCE_ROOT / "images/val").glob("*"))
    val_sessions = {session_name(path) for path in source_val}
    selected: dict[str, list[Path]] = {"train": [], "val": []}

    for image in source_train + source_val:
        if session_name(image) in val_sessions:
            if "_aug" not in image.stem:
                selected["val"].append(image)
        else:
            selected["train"].append(image)

    stats: dict[str, object] = {"validation_sessions": sorted(val_sessions), "splits": {}}
    split_sessions: dict[str, set[str]] = {}
    for split, images in selected.items():
        counts: Counter[str] = Counter()
        split_sessions[split] = {session_name(image) for image in images}
        for image in images:
            label = label_path(image)
            link(image.resolve(), SAFE_ROOT / "images" / split / image.name)
            link(label.resolve(), SAFE_ROOT / "labels" / split / label.name)
            for line in label.read_text().splitlines():
                counts[line.split()[0]] += 1
        stats["splits"][split] = {
            "images": len(images),
            "objects": sum(counts.values()),
            "class_objects": {CLASS_NAMES[int(key)]: value for key, value in sorted(counts.items())},
            "sessions": len(split_sessions[split]),
        }

    overlap = split_sessions["train"] & split_sessions["val"]
    if overlap:
        raise RuntimeError(f"Acquisition-session leakage detected: {sorted(overlap)}")

    stats["session_overlap"] = []
    (RESULTS_ROOT / "split_statistics.json").write_text(json.dumps(stats, indent=2) + "\n")
    return stats


def write_data_config() -> Path:
    config_path = RESULTS_ROOT / "sic_cbms_leakage_safe.yaml"
    config = {
        "path": str(SAFE_ROOT),
        "train": "images/train",
        "val": "images/val",
        "test": "",
        "obb": True,
        "names": CLASS_NAMES,
    }
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))
    return config_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--patience", type=int, default=8)
    parser.add_argument("--image-size", type=int, default=768)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--device", default="mps" if torch.backends.mps.is_available() else "cpu")
    parser.add_argument("--run-name", default="yolo11n_obb_cbms_sic")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    RESULTS_ROOT.mkdir(exist_ok=True)
    stats = prepare_split()
    data_config = write_data_config()
    parameters = {
        **vars(args),
        "model": "yolo11n-obb.pt",
        "dataset": "SiC_Dislocation_Detection_DB / CBMS-Dataset",
        "material": "4H-SiC",
        "modality": "photoluminescence",
        "classes": CLASS_NAMES,
        "data_config": str(data_config),
        "split_policy": "Acquisition-session disjoint; augmented images excluded from validation",
        "split_statistics": stats,
        "optimizer": "AdamW",
        "learning_rate": 0.001,
        "weight_decay": 0.0005,
        "amp": False,
    }
    (RESULTS_ROOT / "parameters.json").write_text(json.dumps(parameters, indent=2) + "\n")

    model = YOLO("yolo11n-obb.pt")
    model.train(
        data=str(data_config),
        project=str(RESULTS_ROOT),
        name=args.run_name,
        exist_ok=True,
        epochs=args.epochs,
        patience=args.patience,
        imgsz=args.image_size,
        batch=args.batch_size,
        device=args.device,
        workers=0,
        optimizer="AdamW",
        lr0=0.001,
        weight_decay=0.0005,
        pretrained=True,
        seed=args.seed,
        deterministic=True,
        amp=False,
        cache=False,
        close_mosaic=5,
        plots=True,
        save=True,
        save_period=5,
        verbose=True,
    )


if __name__ == "__main__":
    main()
