# Execution Guide — DINOv2 + PCA-residual on VisA `pcb1`

Step-by-step to reproduce the runs reported in
[`docs/run_summary.md`](run_summary.md). Everything runs locally; on Apple
Silicon it uses the MPS GPU automatically (falls back to CUDA, then CPU).

> This is a **training-free** model: there is no checkpoint to load. The only
> weights are the frozen DINOv2 encoder (downloaded + cached by torch); the PCA
> "normal subspace" is re-fit at run time from the recorded support set. See
> [§5 Where the model lives](#5-where-the-model-lives).

---

## 1. Prerequisites

| Need | Version / note |
|---|---|
| Python | 3.12 (managed by `uv`) |
| `uv` | https://docs.astral.sh/uv/ |
| Disk | ~1 GB for VisA `pcb1` images + run artifacts |
| Network | once, to download the VisA tar and the DINOv2 weights |
| GPU | optional; Apple MPS / CUDA used if present, else CPU |

Install the backend with the optional `dinov2` extra (pulls torch):

```bash
uv sync --extra dinov2
```

## 2. Restore the dataset (VisA `pcb1`, CC BY 4.0)

The image files are **not** committed. Stream just the `pcb1` category out of the
public VisA tar into the path the registry expects:

```bash
mkdir -p datasets/visa/data
curl -sL https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar \
  | tar -x -C datasets/visa/data pcb1
```

Expect `datasets/visa/data/pcb1/Data/Images/{Normal,Anomaly}` and
`.../Masks/Anomaly` with **1004 normal + 100 anomaly + 100 masks**.

Validate the registry (already committed at `data/registry/visa_pcb1.jsonl`):

```bash
uv run python scripts/validate_registry.py data/registry/visa_pcb1.jsonl
```

## 3. Build the leakage-safe split

```bash
uv run python -m src.data.build --config configs/data/visa_pcb1.yaml
# -> data/splits/visa_pcb1.csv  (6624 tiles @ 448px; grouped by source image)
```

## 4. Run the pipeline (per shot count)

The model config is `configs/models/dinov2_pca.yaml` (encoder `dinov2_vits14`).
Run each shot count end to end — fit + score, calibrate, evaluate, render,
freeze, and validate:

```bash
for k in 1 2 4; do
  RUN=$(uv run --extra dinov2 python -m src.models.run \
    --config configs/models/dinov2_pca.yaml \
    --split data/splits/visa_pcb1.csv --shots "$k" --seed 17 --plain | tail -n1)
  echo "RUN=$RUN"
  uv run python -m src.evaluation.calibrate --run "$RUN"
  uv run python -m src.evaluation.evaluate  --run "$RUN"
  uv run python -m src.rendering.render     --run "$RUN"
  uv run python -m src.packaging.freeze     --run "$RUN"
  uv run python scripts/validate_run.py "$RUN"
done
```

The single-command convenience wrapper (scoring → … → validate for one run) is:

```bash
./scripts/train_dinov2_pca.sh \
  --split data/splits/visa_pcb1.csv --data-root . --shots 1 --seed 17
```

Read the metrics:

```bash
cat runs/<run_id>/metrics.json          # image/pixel AUROC, decision counts
cat runs/<run_id>/metrics_manifest.json # which metrics are valid and why
```

Expected (seed 17): Pixel AUROC **0.761 / 0.842 / 0.949** for k = 1 / 2 / 4;
source-level Image AUROC stays below chance (see the run summary for the honest
discussion).

## 5. Where the model lives

There is **no `model.pt`**. After a run you have:

| Artifact | Location | Role |
|---|---|---|
| DINOv2 encoder weights | `~/.cache/torch/hub/checkpoints/dinov2_vits14_pretrain.pth` (~84 MB) | Frozen, shared by every run; auto-downloaded |
| PCA subspace metadata | `runs/<run_id>/config.resolved.json` → `model_evidence` | `pca_components`, variance, dim (the fit itself is recomputed) |
| Support set | `runs/<run_id>/support_set.csv` | The exact tile(s) the PCA was fit on |
| Per-tile scores | `runs/<run_id>/patch_scores/*.npy` | Raw residual maps |
| Predictions / visuals / metrics | `runs/<run_id>/{predictions.jsonl,heatmaps,overlays,risk_maps,metrics.json}` | Outputs |

Reproducibility = frozen DINOv2 weights + `support_set.csv` + `--seed` +
`configs/models/dinov2_pca.yaml`. Everything under `runs/` is **gitignored** and
**immutable once frozen**.

## 6. Quick checks

```bash
uv run ruff check .
uv run pytest -q
uv run python scripts/validate_run.py runs/<run_id>   # 'valid frozen run'
```
