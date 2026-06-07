# MIIC — DRAEM (anomalib 2.5) ⚠️ undertrained

Reconstruction-based anomaly detection (DRAEM) trained from scratch on MIIC.

- **Image AUROC 0.702 · AUPR 0.356** (15 epochs, 256px, Apple MPS, perlin anomalies)
- ⚠️ **This is NOT DRAEM's ceiling.** DRAEM reaches ~99% on MIIC in the published
  benchmark only with the **DTD texture dataset** as anomaly source and **hundreds of
  epochs**. This run used neither (perlin-only, 15 epochs) for time reasons, so it
  underperforms even the baseline. It illustrates DRAEM's much higher training cost,
  not its accuracy. See [`../MODEL_COMPARISON.md`](../MODEL_COMPARISON.md).
- `metrics.json` — full metrics + run config
- `heatmaps/` — `anomaly_*` / `normal_*` triptychs

Reproduce / improve: add a DTD dir and far more epochs, e.g.
`.venv-anomalib/bin/python scripts/miic_anomalib_run.py --model draem --epochs 200 --accelerator mps`
