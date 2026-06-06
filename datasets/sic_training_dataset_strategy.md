# Dataset Strategy for Silicon Carbide Defect Models

## Important Limitation

No downloadable public dataset identified during the search contains a strong,
ready-to-train collection of real silicon-carbide wafer defect images. Public
SiC studies generally state that their image datasets are private.

Therefore, the public datasets in this repository should be used for
pretraining and domain transfer. Final SiC performance must be validated and
fine-tuned with real SiC images supplied by the project.

## Recommended Priority

1. **Carinthia SEM**: primary supervised semiconductor-defect pretraining.
   It contains 4,591 real semiconductor-wafer SEM images across six defect
   classes.
2. **NFFA-EUROPE SEM**: broad SEM representation pretraining.
3. **CPS2D-AD and IC Cell SEM**: semiconductor structure/domain adaptation.
4. **Wafer Defect Roboflow**: surface-defect segmentation pretraining.
5. **MVTec AD, VisA, and RobustAD-PCB**: generic anomaly-detection and
   robustness benchmarking only.

## MIIC Decision

MIIC remains valuable because it contains 25,160 normal and 116 anomalous SEM
images of integrated circuits with anomaly masks. It is especially useful for
normal-only, unsupervised anomaly-detection training. However, it is not
SiC-specific and its slow download does not block the pipeline.

Use Carinthia as the immediate MIIC substitute. Add MIIC later if the download
becomes practical, then use its normal images for anomaly-detector pretraining
rather than treating it as SiC ground truth.

## Final SiC Adaptation

The final model should be fine-tuned or calibrated on a small project-specific
SiC dataset. Preserve a SiC-only test split and never mix it into generic
pretraining. This is necessary because defects and imaging appearance vary
substantially between silicon, integrated-circuit metal layers, and SiC wafers.
