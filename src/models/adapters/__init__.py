"""Anomaly model adapters.

An adapter fits a *normal subspace* on a few normal support tiles and scores
test tiles by their residual distance from that subspace. The scoring math is a
single, encoder-agnostic implementation (`PCAResidualAdapter`); the feature
extractor is pluggable:

- ``dinov2_vits14`` / ``dinov2_vitb14`` -> frozen DINOv2 patch features (needs
  the ``dinov2`` optional dependency, intended for the GPU box).
- ``pixel_grid_v1`` -> dependency-light local pixel statistics (numpy/pillow),
  so the identical pipeline can be exercised and verified without torch.

All adapters honor the same prediction contract: ``fit`` then ``score`` returning
a :class:`ScoredTile`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np


@dataclass(frozen=True)
class FitInfo:
    """Provenance recorded after fitting the normal subspace."""

    encoder: str
    feature_layer: str
    input_resolution: int
    patch_grid: tuple[int, int]
    feature_dim: int
    support_tiles: int
    pca_components: int
    pca_variance_retained: float
    device: str


@dataclass
class ScoredTile:
    """One scored tile.

    ``patch_scores`` is a 2-D ``(grid_h, grid_w)`` array of per-patch residual
    magnitudes; rendering upsamples it into a pixel heatmap.
    """

    raw_anomaly_score: float
    patch_scores: np.ndarray
    anomalous_area_fraction: float
    region_count: int


class AnomalyAdapter(Protocol):
    def fit(self, support_refs: list[dict[str, Any]]) -> FitInfo: ...

    def score(self, ref: dict[str, Any]) -> ScoredTile: ...


def get_adapter(model_config: dict[str, Any]) -> AnomalyAdapter:
    """Construct an adapter from a resolved model config."""

    from src.models.adapters.dinov2_pca import build_adapter

    return build_adapter(model_config)
