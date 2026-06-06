from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from scripts.prepare_training_dataset import prepare_training_dataset
from src.contracts import validate_split


def test_prepare_training_dataset_generates_combined_split_with_relative_paths(tmp_path: Path) -> None:
    root = tmp_path / "datasets_ready"
    _write_image(root / "visa" / "Data" / "Images" / "Normal" / "ok.png")
    _write_image(root / "visa" / "Data" / "Images" / "Anomaly" / "bad.png")
    _write_image(root / "visa" / "Data" / "Masks" / "Anomaly" / "bad_mask.png")

    combined = prepare_training_dataset(root, datasets=["visa"], min_rows=1)

    rows = validate_split(combined, check_files=False)
    assert {row["label"] for row in rows} == {"good", "anomaly"}
    assert all(not Path(row["image_path"]).is_absolute() for row in rows)
    assert any(row["mask_path"] == "visa/Data/Masks/Anomaly/bad_mask.png" for row in rows)


def test_prepare_training_dataset_excludes_miic_by_default(tmp_path: Path) -> None:
    root = tmp_path / "datasets_ready"
    _write_image(root / "visa" / "normal" / "ok.png")
    _write_image(root / "miic" / "normal" / "sem.png")

    combined = prepare_training_dataset(root, min_rows=1)

    rows = validate_split(combined, check_files=False)
    assert {row["dataset_id"] for row in rows} == {"visa"}


def test_prepare_training_dataset_marks_miic_variants_as_sem(tmp_path: Path) -> None:
    root = tmp_path / "datasets_ready"
    _write_image(root / "miic_partial" / "normal" / "sem.png")

    combined = prepare_training_dataset(root, datasets=["miic_partial"], excluded_datasets=set(), min_rows=1)

    rows = validate_split(combined, check_files=False)
    assert {row["modality"] for row in rows} == {"SEM"}


def _write_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.full((448, 448), 128, dtype=np.uint8), mode="L").save(path)
