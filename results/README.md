# Curated Experiment Results

This directory contains compact, reviewable outputs from the local experiments.
It intentionally excludes raw datasets, caches, repetitive per-image exports, and
large intermediate checkpoints.

## Experiments

### `sic_4h_yolo11s_obb/`

The primary result: oriented-box detection of threading dislocations (TD) and
basal-plane dislocations (BPD) in real 4H-SiC photoluminescence images.

- `SUMMARY.md`: readable comparison with the previous YOLO11n baseline
- `metrics.json`: independently validated metrics
- `metrics_comparison.json`: baseline-versus-improved metric changes
- `parameters.json`: training configuration
- `best_validation/`: curves, confusion matrices, labels, and predictions
- `medium_defect_mosaic_demo/`: expert annotations, model predictions, and source image
- `training/results.csv`: epoch-level training and validation history

The 75 MB trained checkpoint is intentionally not committed. It remains available
in the local experiment directory.

### `sic_4h_detection_markers/`

Representative whole-image visualizations from the SiC oriented-box detector,
including enlarged defect crops.

### `sic_4h_anomaly_heatmaps/`

Representative anomaly-heatmap triptychs for real 4H-SiC images. These outputs are
qualitative because pixel-level anomaly masks are unavailable.

### `miic_sem_proxy/`

MIIC semiconductor SEM anomaly-detection proxy results. MIIC is useful for
semiconductor anomaly research but is not a SiC dataset.

- DINOv2 + PCA-residual: image AUROC `0.879`
- CFA: image AUROC `0.922`
- Includes metrics, a top-anomaly gallery, and representative examples

### `wm811k_silicon_proxy/`

WM-811K silicon wafer-map failure-pattern classification. This is a spatial
wafer-map proxy, not microscope imagery and not SiC. The compact final model and
training script are included because the checkpoint is small.

## Reproduction Scripts

Relevant scripts are under `scripts/`. They expect the corresponding local
datasets to be materialized separately; datasets are not part of this results
publication.
