from __future__ import annotations

import numpy as np

from src.models.adapters.dinov2_pca import _clahe


def test_clahe_increases_contrast_of_low_contrast_image() -> None:
    rng = np.random.default_rng(0)
    # Low-contrast: values compressed into a narrow band.
    base = np.tile(np.linspace(100, 150, 128, dtype=np.float32), (128, 1))
    gray = np.clip(base + rng.normal(0, 4, (128, 128)), 0, 255).astype(np.uint8)

    out = _clahe(gray)

    assert out.shape == gray.shape
    assert out.dtype == np.uint8
    assert out.min() >= 0 and out.max() <= 255
    assert out.std() > gray.std()  # contrast expanded
    assert out.max() - out.min() > int(gray.max()) - int(gray.min())  # range stretched


def test_clahe_is_deterministic() -> None:
    rng = np.random.default_rng(1)
    gray = rng.integers(90, 160, (96, 120), dtype=np.uint8)
    assert np.array_equal(_clahe(gray), _clahe(gray))
