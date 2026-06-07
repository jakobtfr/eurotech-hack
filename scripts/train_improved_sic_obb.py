#!/usr/bin/env python3
"""Train the stronger high-resolution SiC oriented-box detector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from ultralytics import YOLO

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = REPO_ROOT / "sic_results"
OUTPUT_ROOT = RESULTS_ROOT / "improved_yolo11s_obb_1024"
DATA_CONFIG = RESULTS_ROOT / "sic_cbms_leakage_safe.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--patience", type=int, default=6)
    parser.add_argument("--image-size", type=int, default=1024)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--device", default="mps" if torch.backends.mps.is_available() else "cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    parameters = {
        **vars(args),
        "model": "yolo11s-obb.pt",
        "dataset": "SiC_Dislocation_Detection_DB / CBMS-Dataset",
        "material": "4H-SiC",
        "modality": "photoluminescence",
        "data_config": str(DATA_CONFIG),
        "split_policy": "Acquisition-session disjoint; augmented images excluded from validation",
        "optimizer": "AdamW",
        "learning_rate": 0.0005,
        "weight_decay": 0.0005,
        "cosine_learning_rate": True,
        "amp": False,
    }
    (OUTPUT_ROOT / "parameters.json").write_text(json.dumps(parameters, indent=2) + "\n")

    model = YOLO("yolo11s-obb.pt")
    model.train(
        data=str(DATA_CONFIG),
        project=str(OUTPUT_ROOT),
        name="training",
        exist_ok=True,
        epochs=args.epochs,
        patience=args.patience,
        imgsz=args.image_size,
        batch=args.batch_size,
        device=args.device,
        workers=0,
        optimizer="AdamW",
        lr0=0.0005,
        weight_decay=0.0005,
        cos_lr=True,
        pretrained=True,
        seed=args.seed,
        deterministic=True,
        amp=False,
        cache="ram",
        close_mosaic=5,
        plots=True,
        save=True,
        save_period=5,
        verbose=True,
    )


if __name__ == "__main__":
    main()
