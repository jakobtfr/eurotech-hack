# Research Findings — SiC Wafer Anomaly Workbench

Date: 2026-06-06
Status: proxy pipeline working end-to-end (L0–L1 on public data); SiC evidence
blocked on data access (qualitative path ready).

## TL;DR

- We built a **training-free** few-shot anomaly detector (frozen encoder + PCA
  residual) and a reproducible pipeline that turns normal reference images into
  heatmaps, calibrated `PASS/REVIEW/HOLD` decisions, and a risk map.
- On a real labeled benchmark (**VisA `pcb1`**) it produces a genuine
  **Pixel AUROC 0.794** and source-level **Image AUROC 0.553** with the crude
  torch-free encoder.
  - **Update (2026-06-06):** the semantic `dinov2_vits14` encoder has now been
    run end-to-end (see [`docs/run_summary.md`](run_summary.md)). It is
    **materially higher at pixel localization** (Pixel AUROC up to **0.949** at
    4 shots) but, contrary to the earlier expectation, **below chance at
    source-level Image AUROC** (0.072–0.397) — the `max`-over-tiles aggregation
    is anti-correlated with the image label on PCB1. Strong localization, weak
    image ranking; treated as an open domain-gap finding, not a headline win.
- **The SiC data itself is not publicly available** — the reference dataset is
  "available upon request" and there is no public mirror. This is the real
  bottleneck; SiC remains a *qualitative* track and a concrete pilot-data ask.
- Two methodological pitfalls were found and fixed: **tiling bias** in image
  AUROC and **small-sample calibration** false-positives.

---

## 1. Method

The primary model is the plan's baseline (training-free, normal-only, few-shot):

1. Extract patch features from `k` normal support tiles (frozen encoder).
2. Fit a **PCA "normal subspace"** on the stacked patch features.
3. Score each test patch by its **residual distance** from that subspace.
4. Aggregate patch residuals → image score; reshape → pixel heatmap.

There is **no gradient training**: the only fit is a single SVD on the support
features. The encoder is pluggable:

| Encoder | Dependencies | Role |
|---|---|---|
| `dinov2_vits14` | torch (optional `dinov2` extra), GPU | Headline semantic encoder |
| `pixel_grid_v1` | numpy/pillow only | Torch-free plumbing validator / CI |

Both feed the identical scoring + rendering code, so the torch-free path
verifies exactly what DINOv2 runs.

**Calibration & decisions.** Raw scores are normalized by the empirical CDF of
**held-out `validation/good`** normals (midrank/Hazen plotting position).
Thresholds (`review` 0.990, `hold` 0.999 quantiles) map to `PASS/REVIEW/HOLD`.
These are triage labels, not production rejections.

---

## 2. Dataset landscape (key finding)

The central constraint is **data availability**, not modeling.

| Dataset | Domain | Labels/Masks | Availability | Use here |
|---|---|---|---|---|
| **VisA / MVTec AD** | industrial (PCB, objects) | image + pixel masks | **public** (VisA direct, MVTec form) | metric-bearing proxy (L1) |
| **MIIC** | semiconductor SEM | image + pixel | gated / access pending | preferred SEM proxy (not yet usable) |
| **4H-SiC PL/etch** | **SiC wafer** | none public | **"available upon request"** | qualitative only (L2), blocked |
| NFFA-EUROPE SEM | SEM microscopy | none | public but ~tens of GB | optional modality bridge |

**SiC is not downloadable.** The reference dataset is the supplementary material
for *"Combining unsupervised and supervised learning in microscopy enables defect
analysis of a full 4H-SiC wafer"* ([arXiv 2402.13353][arxiv],
[MRS Communications][mrs]). Its [Zenodo record][zenodo] contains **only a
postprocessed PDF**; the paper's data-availability statement reads:

> "Postprocessed data is available at zenodo, raw microscopy data is available
> upon request." / "Code is available upon request."

A broad search (Kaggle / Hugging Face / GitHub) found **no public SiC defect
microscopy dataset** — this class of data is proprietary across the field.

**Implication:** A labeled SiC result requires an explicit data request (or an
industry partner). Until then, SiC is shown qualitatively and its absence is the
concrete pilot-data ask. The plan's contingency applies: use VisA/MVTec for the
metric, keep SiC/SEM qualitative.

---

## 3. Proxy results — VisA `pcb1`

Subset: 60 normal + 40 anomaly images → 600 tiles (448², train 180 / val 90 /
test 330). Encoder `pixel_grid_v1`, 4-shot, seed 17.

| Metric | Value | Notes |
|---|---|---|
| **Pixel AUROC** | **0.794** | heatmap vs aligned GT masks |
| Image AUROC (per-source) | 0.553 | tiles aggregated per image (max) |
| Image AUPR | 0.784 | |

Interpretation: the **defect pixels rank above background** (Pixel AUROC 0.79)
even with a crude pixel-statistics encoder, confirming the pipeline computes a
real, defensible metric on real labeled data. The modest image AUROC reflects
the encoder, not the pipeline (see §4.3).

---

## 4. Engineering findings

### 4.1 Tiling bias inflates/deflates image metrics
A localized-defect image tiles into several patches; only some contain the
defect, yet all carry the image's "anomaly" label. Scoring **per tile** pushed
image AUROC to **0.46 (below chance)**. Aggregating tiles to one score per
source image (max over tiles) before AUROC restored it to **0.55**. Image-level
metrics must be computed **per source**, not per tile.

### 4.2 Small-sample calibration false-positives
With few validation normals, the empirical CDF saturates: the top normal maps to
1.0 and trips the `hold` threshold (a normal flagged `HOLD`). Fixes applied:
(a) a held-out `validation/good` split so calibration is not self-referential;
(b) a **midrank (Hazen)** CDF so a reference normal maps to its rank midpoint,
not 1.0. Residual: normals scoring above the *small* validation maximum still
escalate — this converges to the designed ~0.1% false-positive rate with
adequate validation N (tracked as an open issue).

### 4.3 Encoder ceiling — the case for DINOv2
`pixel_grid_v1` keys on whatever is statistically distinct (bright metal,
silkscreen) rather than the *semantic* defect, so per-tile localization on subtle
PCB defects is weak. It is a **plumbing validator**. Semantic frozen features
(**DINOv2**) attend to "unlike normal" and are the headline encoder for real
localization quality.

### 4.4 Low-contrast preprocessing (CLAHE)
SiC PL imagery is low-contrast with indistinct boundaries. A fixed CLAHE
preprocessing (`rgb_repeat_clahe_v1`) is implemented as an **explicit, recorded
ablation** (never a hidden default), enabling a raw-vs-CLAHE
preprocessing-sensitivity comparison when SiC imagery is obtained.

---

## 5. Proxy vs SiC — honest framing

- VisA/MVTec numbers **validate execution**, not semiconductor transfer, and must
  never be presented as SiC performance.
- SiC heatmaps (when available) are **qualitative** unless verified labels exist.
- The wafer-style risk map carries a provenance badge (`real spatial` /
  `stitched field` / `synthetic montage`).

---

## 6. Next steps

1. **DINOv2 on the GPU box** — run the same `visa_pcb1` config with
   `configs/models/dinov2_pca.yaml` (`uv sync --extra dinov2`); expect sharper
   localization and higher AUROC.
2. **Full VisA/MVTec eval** — more categories, 1/2/4-shot scaling curve (L1 + an
   L3 headline candidate).
3. **SiC pilot data ask** — request the raw 4H-SiC microscopy from the paper
   authors; until then keep SiC qualitative with the CLAHE ablation ready.
4. **Calibration at scale** — re-confirm the false-positive rate once a
   realistically sized validation set is available.

---

## 7. Reproduction

```bash
# 1. register a dataset laid out as normal/ + anomaly/ (+ masks/)
python scripts/ingest_dataset.py --dataset-id visa_pcb1 --modality optical \
  --normal-dir  <pcb1>/Data/Images/Normal \
  --anomaly-dir <pcb1>/Data/Images/Anomaly \
  --mask-dir    <pcb1>/Data/Masks/Anomaly

# 2. build tiles -> fit/score -> calibrate -> evaluate -> render -> freeze
python -m src.data.build       --config configs/data/visa_pcb1.yaml
RUN=$(python -m src.models.run  --config configs/models/pixel_pca.yaml \
        --split data/splits/visa_pcb1.csv --shots 4 --seed 17 --plain | tail -1)
python -m src.evaluation.calibrate --run "$RUN"
python -m src.evaluation.evaluate  --run "$RUN"   # metrics.json: image/pixel AUROC
python -m src.rendering.render     --run "$RUN"
python -m src.packaging.freeze     --run "$RUN"
```

Swap `pixel_pca.yaml` → `dinov2_pca.yaml` (with `uv sync --extra dinov2`) for the
semantic encoder on a GPU box.

---

## References

- [arXiv 2402.13353 — full 4H-SiC wafer defect analysis][arxiv]
- [MRS Communications version][mrs]
- [Zenodo 11229837 — supplementary material (PDF only)][zenodo]
- VisA dataset (Amazon) and MVTec AD — see `datasets/links.md`
- Upstream method references — see `planning/sources/repo_references.md`

[arxiv]: https://arxiv.org/abs/2402.13353
[mrs]: https://link.springer.com/article/10.1557/s43579-024-00563-2
[zenodo]: https://zenodo.org/records/11229837
