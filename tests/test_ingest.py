from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from scripts.ingest_dataset import main as ingest_main
from src.contracts import validate_registry


def _img(path: Path, rng: np.random.Generator) -> None:
    Image.fromarray(rng.integers(0, 255, (64, 64, 3), dtype=np.uint8), mode="RGB").save(path)


def test_ingest_labeled_dataset_with_masks(tmp_path: Path) -> None:
    rng = np.random.default_rng(2)
    normal_dir = tmp_path / "Normal"
    anomaly_dir = tmp_path / "Anomaly"
    mask_dir = tmp_path / "Masks"
    for d in (normal_dir, anomaly_dir, mask_dir):
        d.mkdir()
    for i in range(3):
        _img(normal_dir / f"n{i}.png", rng)
    for i in range(2):
        _img(anomaly_dir / f"a{i}.png", rng)
        Image.fromarray(np.zeros((64, 64), dtype=np.uint8), mode="L").save(mask_dir / f"a{i}.png")

    registry = tmp_path / "reg.jsonl"
    config = tmp_path / "cfg.yaml"
    ingest_main(
        [
            "--dataset-id", "ing",
            "--normal-dir", str(normal_dir),
            "--anomaly-dir", str(anomaly_dir),
            "--mask-dir", str(mask_dir),
            "--modality", "optical",
            "--license-status", "verified",
            "--demo-allowed",
            "--out-registry", str(registry),
            "--out-config", str(config),
        ]
    )

    rows = validate_registry(registry)
    assert len(rows) == 5
    normals = [r for r in rows if r["source_label"] == "normal"]
    anomalies = [r for r in rows if r["source_label"] == "anomaly"]
    assert len(normals) == 3 and len(anomalies) == 2
    assert all(r["mask_source_path"] for r in anomalies)  # masks matched by stem
    assert all(not r["mask_source_path"] for r in normals)
    assert config.exists() and "dataset_id: ing" in config.read_text()
