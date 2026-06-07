# MIIC — CFA (anomalib 2.5)

Feature-based anomaly detection (CFA: Coupled-hypersphere Feature Adaptation,
WideResNet50 backbone) trained on MIIC normal images.

- **Image AUROC 0.922 · AUPR 0.886** (5 epochs, 256px, Apple MPS)
- Beats the frozen DINOv2+PCA baseline (0.879 / 0.763) — see
  [`../MODEL_COMPARISON.md`](../MODEL_COMPARISON.md).
- `metrics.json` — full metrics + run config (sklearn image-level scores)
- `heatmaps/` — `anomaly_*` / `normal_*` triptychs (original | heatmap | overlay)

Reproduce: `.venv-anomalib/bin/python scripts/miic_anomalib_run.py --model cfa --epochs 5 --accelerator mps`
