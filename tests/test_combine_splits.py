from __future__ import annotations

from pathlib import Path

import pytest

from src.common import ContractError
from src.contracts import SPLIT_FIELDS, validate_split
from src.data.combine_splits import combine_splits


def test_combine_splits_excludes_miic_by_default(tmp_path: Path) -> None:
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"
    output = tmp_path / "combined.csv"
    _write_split(first, [_row("tile_a", "source_a", "zenodo_sic"), _row("tile_b", "source_b", "MIIC")])
    _write_split(second, [_row("tile_c", "source_c", "visa")])

    combine_splits([first, second], output)

    rows = validate_split(output)
    assert [row["dataset_id"] for row in rows] == ["zenodo_sic", "visa"]
    assert all(row["dataset_id"].lower() != "miic" for row in rows)


def test_combine_splits_min_rows_fails_after_exclusions(tmp_path: Path) -> None:
    split = tmp_path / "miic.csv"
    output = tmp_path / "combined.csv"
    _write_split(split, [_row("tile_a", "source_a", "miic")])

    with pytest.raises(ContractError, match="below required minimum"):
        combine_splits([split], output, min_rows=1)


def test_combine_splits_can_rewrite_paths_relative_to_dataset_root(tmp_path: Path) -> None:
    dataset_root = tmp_path / "asset"
    dataset_root.mkdir()
    image = dataset_root / "visa" / "normal.png"
    image.parent.mkdir()
    image.write_bytes(b"placeholder")
    split = tmp_path / "split.csv"
    output = tmp_path / "combined.csv"
    row = _row("tile_a", "source_a", "visa").split(",")
    row[SPLIT_FIELDS.index("image_path")] = str(image)
    _write_split(split, [",".join(row)])

    combine_splits([split], output, path_root=dataset_root)

    assert validate_split(output, check_files=False)[0]["image_path"] == "visa/normal.png"


def test_combine_splits_accepts_existing_relative_paths_with_dataset_root(tmp_path: Path) -> None:
    dataset_root = tmp_path / "asset"
    dataset_root.mkdir()
    split = tmp_path / "split.csv"
    output = tmp_path / "combined.csv"
    row = _row("tile_a", "source_a", "visa").split(",")
    row[SPLIT_FIELDS.index("image_path")] = "visa/normal.png"
    _write_split(split, [",".join(row)])

    combine_splits([split], output, path_root=dataset_root)

    assert validate_split(output, check_files=False)[0]["image_path"] == "visa/normal.png"


def _write_split(path: Path, rows: list[str]) -> None:
    path.write_text(",".join(SPLIT_FIELDS) + "\n" + "\n".join(rows) + "\n", encoding="utf-8")


def _row(tile_id: str, source_id: str, dataset_id: str) -> str:
    values = {
        "tile_id": tile_id,
        "source_image_id": source_id,
        "dataset_id": dataset_id,
        "category": "demo",
        "wafer_id": "",
        "modality": "SEM",
        "split": "train",
        "label": "good",
        "image_path": "",
        "mask_path": "",
        "tile_x": "0",
        "tile_y": "0",
        "tile_size": "448",
        "stride": "448",
        "preprocess_id": "rgb_repeat_v1",
        "support_eligible": "true",
        "demo_allowed": "false",
    }
    return ",".join(values[field] for field in SPLIT_FIELDS)
