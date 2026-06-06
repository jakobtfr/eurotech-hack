from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from src.models.adapters import get_adapter

_CONFIG = {
    "encoder": "pixel_grid_v1",
    "patch_grid": 16,
    "input_resolution": 128,
    "pca_variance_retained": 0.9,
    "area_zscore": 2.0,
}


def _normal(rng: np.random.Generator, size: int = 224) -> np.ndarray:
    base = np.tile(np.linspace(40, 200, size, dtype=np.float32), (size, 1))
    noisy = np.clip(base + rng.normal(0, 5, (size, size)), 0, 255).astype(np.uint8)
    return np.stack([noisy] * 3, axis=2)


def _save(path: Path, array: np.ndarray) -> None:
    Image.fromarray(array, mode="RGB").save(path)


def _ref(path: Path) -> dict[str, object]:
    return {"image_path": str(path), "tile_x": 0, "tile_y": 0, "tile_size": 0, "preprocess_id": "rgb_repeat_v1"}


def test_pca_residual_separates_anomaly_from_normal(tmp_path: Path) -> None:
    rng = np.random.default_rng(0)
    normals = []
    for index in range(3):
        path = tmp_path / f"normal_{index}.png"
        _save(path, _normal(rng))
        normals.append(path)
    defect = _normal(rng)
    defect[80:160, 80:160] = 255  # bright out-of-distribution blob
    defect_path = tmp_path / "defect.png"
    _save(defect_path, defect)

    adapter = get_adapter(_CONFIG)
    fit_info = adapter.fit([_ref(normals[0]), _ref(normals[1])])
    assert fit_info.pca_components >= 1
    assert fit_info.pca_components < fit_info.feature_dim  # residual is never trivially zero

    held_out_normal = adapter.score(_ref(normals[2]))
    anomalous = adapter.score(_ref(defect_path))

    assert anomalous.raw_anomaly_score > held_out_normal.raw_anomaly_score
    assert anomalous.anomalous_area_fraction > held_out_normal.anomalous_area_fraction
    assert anomalous.region_count >= 1
    assert anomalous.patch_scores.shape == (16, 16)


def test_score_before_fit_raises(tmp_path: Path) -> None:
    path = tmp_path / "x.png"
    _save(path, _normal(np.random.default_rng(1)))
    adapter = get_adapter(_CONFIG)
    try:
        adapter.score(_ref(path))
    except Exception as exc:  # noqa: BLE001
        assert "before fit" in str(exc)
    else:
        raise AssertionError("expected score-before-fit to raise")
