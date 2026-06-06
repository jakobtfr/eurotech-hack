# Claim Table

This is the source of truth for what can be said in the executive demo.

| Claim | Evidence | Safe wording | Do not say |
|---|---|---|---|
| Few normal references can drive anomaly triage. | Frozen run `20260606T193628Z_dinov2_pca_baseline_v1_k8_seed17`; 8 normal support tiles; DINOv2/PCA residual scoring. | "With eight normal SEM references, the workbench produces an auditable anomaly review queue." | "The model is production-ready." |
| The MIIC partial run has valid image-level evidence. | `metrics.json`: Image AUROC `0.866268`, Image AUPR `0.796814`; 463 test images. | "On recovered MIIC SEM proxy data, image-level ranking is measurable and promising." | "This is validated SiC performance." |
| Pixel metrics are not available for MIIC partial. | `metrics_manifest.json`: `pixel_auroc.valid=false`, reason: aligned masks unavailable. | "Heatmaps are visible, but pixel AUROC is gated because masks were not recovered." | "Pixel localization is quantitatively proven on MIIC partial." |
| The demo exposes failure cases. | Curated examples include a missed anomaly and a false-positive normal. | "The product shows where the current threshold fails, so engineering can tune it." | "Every defect is caught." |
| Decisions are triage labels. | Calibration uses validation-good empirical CDF; `HOLD` means inspection escalation. | "`HOLD` means route to a human or higher-resolution inspection." | "`HOLD` means reject wafer/die." |
| SiC is the target domain, not the validated result. | Public SiC labels/raw data are unavailable; local evidence is SEM proxy. | "The next step is a paired SiC PL/etch/SEM pilot dataset." | "We solve SiC inspection today." |

Approved close:

> We have a working, reproducible few-shot inspection workbench. It turns scarce
> normal SEM references into heatmaps, review decisions, and auditable evidence.
> The next step is a focused pilot with licensed paired SiC inspection data.
