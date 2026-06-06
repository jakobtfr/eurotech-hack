"""Frozen-encoder + PCA-residual anomaly adapter.

Algorithm (encoder-agnostic):

1. Extract patch features from ``k`` normal support tiles.
2. Fit a PCA "normal subspace" on the stacked patch features.
3. Score each test patch by its residual distance from that subspace.
4. Aggregate patch residuals into one image-level score.

The feature extractor is selected by ``encoder`` in the model config. The math
below is identical for every encoder, so the dependency-light ``pixel_grid_v1``
extractor verifies the same code path that DINOv2 runs on the GPU box.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from src.common import ContractError
from src.models.adapters import FitInfo, ScoredTile

_IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

# Feature extractor: tile RGB (H, W, 3) uint8 -> (patch_features (n, d), (grid_h, grid_w)).
FeatureExtractor = Callable[[np.ndarray], "tuple[np.ndarray, tuple[int, int]]"]


# --------------------------------------------------------------------------- #
# Tile loading
# --------------------------------------------------------------------------- #
def load_tile_rgb(ref: dict[str, Any], resolution: int) -> np.ndarray:
    """Load, preprocess, crop, and resize one tile into an ``(R, R, 3)`` uint8 array."""

    path = Path(ref["image_path"])
    if not path.exists():
        raise ContractError(f"tile image does not exist: {ref['image_path']}")
    preprocess_id = str(ref.get("preprocess_id") or "rgb_repeat_v1")
    with Image.open(path) as image:
        image = _apply_preprocess(image, preprocess_id)
        crop = _crop(image, ref)
        resized = crop.resize((resolution, resolution), Image.Resampling.BILINEAR)
        return np.asarray(resized, dtype=np.uint8)


def _apply_preprocess(image: Image.Image, preprocess_id: str) -> Image.Image:
    if preprocess_id in {"rgb_repeat_v1", "rgb_repeat_clahe_v1"}:
        # Channel-repeat: collapse to luminance then back to 3 channels so the
        # encoder sees a stable grayscale-derived RGB regardless of source mode.
        return image.convert("L").convert("RGB")
    return image.convert("RGB")


def _crop(image: Image.Image, ref: dict[str, Any]) -> Image.Image:
    tile_size = int(ref.get("tile_size") or 0)
    if tile_size <= 0:
        return image
    x = int(ref.get("tile_x") or 0)
    y = int(ref.get("tile_y") or 0)
    width, height = image.size
    # Clamp so a slightly-too-large tile geometry never reads past the image.
    x = max(0, min(x, max(0, width - tile_size)))
    y = max(0, min(y, max(0, height - tile_size)))
    return image.crop((x, y, x + tile_size, y + tile_size))


# --------------------------------------------------------------------------- #
# Feature extractors
# --------------------------------------------------------------------------- #
class PixelGridFeatureExtractor:
    """Local pixel statistics per grid cell (numpy/pillow only).

    Each cell becomes a small feature vector: per-channel mean and std plus a
    mean gradient magnitude (texture). Real image content drives the features,
    so PCA-residual scoring genuinely separates out-of-distribution patches.
    """

    def __init__(self, grid: int) -> None:
        self.grid = grid
        self.feature_dim = 7

    def __call__(self, tile: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
        rgb = tile.astype(np.float32) / 255.0
        gray = rgb.mean(axis=2)
        gy, gx = np.gradient(gray)
        grad = np.sqrt(gx * gx + gy * gy)
        rows = np.array_split(np.arange(rgb.shape[0]), self.grid)
        cols = np.array_split(np.arange(rgb.shape[1]), self.grid)
        features = []
        for row_idx in rows:
            for col_idx in cols:
                cell = rgb[row_idx[:, None], col_idx]
                cell_grad = grad[row_idx[:, None], col_idx]
                features.append(
                    np.concatenate(
                        [
                            cell.reshape(-1, 3).mean(axis=0),
                            cell.reshape(-1, 3).std(axis=0),
                            [float(cell_grad.mean())],
                        ]
                    )
                )
        return np.asarray(features, dtype=np.float32), (self.grid, self.grid)


class DinoV2FeatureExtractor:
    """Frozen DINOv2 patch features. Requires the ``dinov2`` optional extra."""

    _cache: dict[str, Any] = {}

    def __init__(self, encoder: str, resolution: int) -> None:
        self.encoder = encoder
        self.resolution = resolution
        self._torch = self._import_torch()
        self.device = self._select_device()
        self.model = self._load_model()
        self.patch_size = 14
        self.feature_dim = int(self.model.embed_dim)

    @staticmethod
    def _import_torch() -> Any:
        try:
            import torch
        except ImportError as exc:  # pragma: no cover - exercised only on the GPU box
            raise ContractError("encoder requires torch; install the optional extra: `uv sync --extra dinov2`") from exc
        return torch

    def _select_device(self) -> str:
        torch = self._torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load_model(self) -> Any:  # pragma: no cover - exercised only on the GPU box
        torch = self._torch
        key = self.encoder
        if key not in self._cache:
            model = torch.hub.load("facebookresearch/dinov2", self.encoder)
            model.eval().to(self.device)
            for param in model.parameters():
                param.requires_grad_(False)
            self._cache[key] = model
        return self._cache[key]

    def __call__(self, tile: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:  # pragma: no cover
        torch = self._torch
        normalized = (tile.astype(np.float32) / 255.0 - _IMAGENET_MEAN) / _IMAGENET_STD
        tensor = torch.from_numpy(normalized.transpose(2, 0, 1)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            features = self.model.forward_features(tensor)["x_norm_patchtokens"]
        patches = features.squeeze(0).float().cpu().numpy()
        grid = self.resolution // self.patch_size
        return patches, (grid, grid)


# --------------------------------------------------------------------------- #
# PCA-residual adapter
# --------------------------------------------------------------------------- #
class PCAResidualAdapter:
    def __init__(
        self,
        extractor: FeatureExtractor,
        encoder: str,
        resolution: int,
        feature_dim: int,
        device: str,
        variance_retained: float,
        area_zscore: float,
    ) -> None:
        self._extractor = extractor
        self._encoder = encoder
        self._resolution = resolution
        self._feature_dim = feature_dim
        self._device = device
        self._variance_retained = variance_retained
        self._area_zscore = area_zscore
        self._mean: np.ndarray | None = None
        self._components: np.ndarray | None = None
        self._area_threshold = 0.0
        self._fit_info: FitInfo | None = None

    def fit(self, support_refs: list[dict[str, Any]]) -> FitInfo:
        if not support_refs:
            raise ContractError("model fit requires at least one support tile")
        blocks = []
        grid = (0, 0)
        for ref in support_refs:
            tile = load_tile_rgb(ref, self._resolution)
            features, grid = self._extractor(tile)
            blocks.append(features)
        matrix = np.vstack(blocks).astype(np.float64)
        mean = matrix.mean(axis=0)
        centered = matrix - mean
        # SVD-based PCA (deterministic). Keep the fewest components reaching the
        # configured variance; cap below full rank so residuals are never all 0.
        _, singular, vt = np.linalg.svd(centered, full_matrices=False)
        variance = singular**2
        total = float(variance.sum())
        if total <= 0.0:
            components_kept = 1
            retained = 0.0
        else:
            cumulative = np.cumsum(variance) / total
            components_kept = int(np.searchsorted(cumulative, self._variance_retained) + 1)
            max_components = max(1, min(vt.shape[0] - 1, centered.shape[0] - 1))
            components_kept = max(1, min(components_kept, max_components))
            retained = float(cumulative[components_kept - 1])
        self._mean = mean
        self._components = vt[:components_kept]
        # Calibrate the "anomalous area" threshold against the NORMAL residual
        # scale (support patches), not each test tile's own distribution — a
        # concentrated defect must not raise its own threshold and hide itself.
        normal_residuals = self._patch_residuals(matrix)
        self._area_threshold = float(normal_residuals.mean() + self._area_zscore * normal_residuals.std())
        self._fit_info = FitInfo(
            encoder=self._encoder,
            feature_layer="last",
            input_resolution=self._resolution,
            patch_grid=grid,
            feature_dim=int(matrix.shape[1]),
            support_tiles=len(support_refs),
            pca_components=components_kept,
            pca_variance_retained=round(retained, 6),
            device=self._device,
        )
        return self._fit_info

    def _patch_residuals(self, features: np.ndarray) -> np.ndarray:
        """Per-patch residual magnitude from the fitted normal subspace."""

        centered = features.astype(np.float64) - self._mean
        projection = centered @ self._components.T @ self._components
        residual = centered - projection
        return np.sqrt((residual**2).sum(axis=1))

    def score(self, ref: dict[str, Any]) -> ScoredTile:
        if self._mean is None or self._components is None:
            raise ContractError("adapter.score called before fit")
        tile = load_tile_rgb(ref, self._resolution)
        features, grid = self._extractor(tile)
        patch_scores = self._patch_residuals(features).reshape(grid).astype(np.float32)
        mask = patch_scores > self._area_threshold if self._area_threshold > 0 else np.zeros(grid, dtype=bool)
        return ScoredTile(
            raw_anomaly_score=_image_score(patch_scores),
            patch_scores=patch_scores,
            anomalous_area_fraction=round(float(mask.mean()), 6),
            region_count=_connected_components(mask),
        )

    @property
    def fit_info(self) -> FitInfo:
        if self._fit_info is None:
            raise ContractError("fit_info available only after fit")
        return self._fit_info


def _image_score(patch_scores: np.ndarray) -> float:
    """Mean of the top ~2% patch residuals (robust to a single hot pixel)."""

    flat = patch_scores.ravel()
    top = max(1, int(round(0.02 * flat.size)))
    return round(float(np.mean(np.sort(flat)[-top:])), 6)


def _connected_components(mask: np.ndarray) -> int:
    seen = np.zeros_like(mask, dtype=bool)
    height, width = mask.shape
    count = 0
    for start_y in range(height):
        for start_x in range(width):
            if not mask[start_y, start_x] or seen[start_y, start_x]:
                continue
            count += 1
            queue: deque[tuple[int, int]] = deque([(start_y, start_x)])
            seen[start_y, start_x] = True
            while queue:
                y, x = queue.popleft()
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
    return count


# --------------------------------------------------------------------------- #
# Construction
# --------------------------------------------------------------------------- #
def build_adapter(model_config: dict[str, Any]) -> PCAResidualAdapter:
    encoder = str(model_config.get("encoder", "pixel_grid_v1"))
    resolution = int(model_config.get("input_resolution", 224))
    variance_retained = float(model_config.get("pca_variance_retained", 0.90))
    area_zscore = float(model_config.get("area_zscore", 2.0))

    if encoder.startswith("dinov2"):
        extractor = DinoV2FeatureExtractor(encoder, resolution)
        feature_dim = extractor.feature_dim
        device = extractor.device
    elif encoder == "pixel_grid_v1":
        grid = int(model_config.get("patch_grid", 28))
        pixel_extractor = PixelGridFeatureExtractor(grid)
        extractor = pixel_extractor
        feature_dim = pixel_extractor.feature_dim
        device = "cpu"
    else:
        raise ContractError(f"unknown encoder {encoder!r}")

    return PCAResidualAdapter(
        extractor=extractor,
        encoder=encoder,
        resolution=resolution,
        feature_dim=feature_dim,
        device=device,
        variance_retained=variance_retained,
        area_zscore=area_zscore,
    )
