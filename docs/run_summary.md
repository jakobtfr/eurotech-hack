# Run Summary — DINOv2 + PCA-residual on VisA `pcb1`

Date: 2026-06-06
Status: first real DINOv2-encoder proxy runs, end-to-end and frozen.

This is the first set of runs using the **semantic `dinov2_vits14` encoder** (not
the torch-free `pixel_grid_v1` plumbing encoder used in earlier findings). It
fills in the numbers that [`docs/research_findings.md`](research_findings.md)
previously left as an expectation.

> Naming honesty: the model is a **local** frozen-DINOv2 + PCA-residual baseline
> (`dinov2_pca_baseline_v1`). The SubspaceAD repository is recorded as
> *inspiration* only (`model_source_commit 4190506`); these numbers are **not** a
> SubspaceAD result.

---

## 1. Setup (identical across runs)

| Field | Value |
|---|---|
| Dataset | VisA `pcb1` (`dataset_id: visa_pcb1`), license CC BY 4.0 |
| Source images | 1104 (1004 normal + 100 anomaly, 100 with aligned masks) |
| Split | `data/splits/visa_pcb1.csv` (v0), grouped by `source_image_id` |
| Tiles | 6624 total @ 448×448, stride 448, `rgb_repeat_v1` preprocessing |
| Test partition | 351 images / 2106 tiles (1506 good + 600 anomaly tiles) |
| Encoder | `dinov2_vits14`, `forward_features` last layer, 448 input, 32×32 patch grid, dim 384 |
| Scoring | per-patch PCA residual; image score = mean of top-2% patch residuals |
| Calibration | empirical CDF of `validation/good`; review q=0.99, hold q=0.999 |
| Seed | 17 (support set selection) |
| Hardware | Apple Silicon (`macOS-15.1-arm64`), device `mps`, torch 2.12.0, py 3.12.13 |

All metrics are **valid** per `metrics_manifest.json`: image labels and aligned
masks are both available for the test split.

---

## 2. Results — few-shot scaling (seed 17)

| Shots | PCA comps | **Image AUROC** (source-level) | Image AUPR | **Pixel AUROC** | Decisions HOLD / PASS / REVIEW |
|---|---|---|---|---|---|
| 1 | 18 | 0.239 | 0.188 | 0.761 | 6623 / 1 / 0 |
| 2 | 27 | 0.072 | 0.164 | 0.842 | 6514 / 110 / 0 |
| 4 | 35 | 0.397 | 0.306 | 0.949 | 5691 / 933 / 0 |

Reference (prior, torch-free `pixel_grid_v1` on the same split):
Image AUROC **0.553**, Pixel AUROC **0.794**.

Image AUROC is the source-level max-over-tiles metric (the tiling-bias-safe one),
over 351 test images. Pixel AUROC is over the heatmaps vs. aligned masks.

---

## 3. Findings

**(+) Defect localization is strong and scales cleanly with support size.**
Pixel AUROC climbs monotonically `0.761 → 0.842 → 0.949` from 1 → 2 → 4 normal
support tiles. At 4 shots the semantic encoder (0.949) clearly beats the
torch-free baseline (0.794). The heatmaps genuinely find the defect pixels.

**(−) Source-level image ranking is below chance, and worse than the crude
encoder.** Image AUROC is 0.072–0.397 across all shot counts — consistently
below 0.5, and below `pixel_grid_v1`'s 0.553. This **contradicts** the earlier
assumption that DINOv2 would be "materially higher" at the image level. The
likely mechanism: against a tiny normal PCA subspace (1–4 tiles), the dense,
high-frequency component structure of *normal* PCB tiles produces large
residuals, so `max`-over-tiles aggregation lets busy normal images outscore the
small, localized defects of anomaly images — an anti-correlation, not noise (it
reproduces at every shot count). Strong pixel localization with weak image
ranking is internally consistent: the model knows *where* the unusual texture is,
but "unusual texture" on PCB1 is dominated by normal component density, not
defects.

**(~) Calibration over-flags.** Decisions skew almost entirely to `HOLD`; the
`PASS` share grows with shots (1 → 110 → 933) as the normal subspace stabilizes,
and the `REVIEW` band is empty. The area-fraction `HOLD` trigger
(`area_zscore=2.0`, `area_hold_threshold=0.15`) dominates and needs retuning on
`validation/good` before any decision rate is presentable.

---

## 4. Limitations / next steps

- **Single seed (17).** The plan's protocol wants seeds 17/23/42 with mean±std
  before any few-shot row is a headline. These are one-seed point estimates.
- **Revisit image-level aggregation.** `max`-over-tiles is anti-correlated here;
  try mean-of-top-k or a percentile, and re-check whether the image AUROC
  inversion survives. Do not report image AUROC as a win in its current form.
- **Retune calibration.** The HOLD-dominated decision mix is a threshold
  artifact, not a yield/rejection statement.
- **Headline to use today:** *few-shot localization scaling* (Pixel AUROC
  0.76 → 0.95) — defensible and reproducible. The image-level inversion is the
  honest open question, framed as a domain-gap finding per the plan's risk
  register, not hidden.

---

## 5. Reproduce

```bash
# Restore VisA pcb1 images under datasets/visa/data/ (CC BY 4.0):
#   curl -sL https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar \
#     | tar -x -C datasets/visa/data pcb1
uv sync --extra dinov2
uv run python -m src.data.build --config configs/data/visa_pcb1.yaml

for k in 1 2 4; do
  RUN=$(uv run --extra dinov2 python -m src.models.run \
    --config configs/models/dinov2_pca.yaml \
    --split data/splits/visa_pcb1.csv --shots "$k" --seed 17 --plain | tail -n1)
  uv run python -m src.evaluation.calibrate --run "$RUN"
  uv run python -m src.evaluation.evaluate --run "$RUN"
  uv run python -m src.rendering.render --run "$RUN"
  uv run python -m src.packaging.freeze --run "$RUN"
  uv run python scripts/validate_run.py "$RUN"
done
```

Run artifacts live under `runs/` (gitignored, immutable once frozen). The
source-controlled inputs for these runs are `configs/data/visa_pcb1.yaml`,
`data/registry/visa_pcb1.jsonl`, and `configs/models/dinov2_pca.yaml`.
