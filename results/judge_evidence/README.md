# Judge evidence guide

Use these artifacts to show results and reliability without overloading the
presentation.

## Recommended presentation order

1. **Real SiC relevance:** open `sic_performance_and_integrity.png`.
   Explain that the model detects oriented TD and BPD dislocations in real
   4H-SiC photoluminescence images. Lead with improved precision and
   localization quality, then acknowledge the weaker BPD recall.

2. **Visual proof:** open
   `../sic_4h_dislocation_yolo11n_obb/improved_yolo11s_obb_1024/medium_defect_mosaic_demo/01_model_predictions_with_defect_mosaic.jpg`.
   Show exactly where the detector places oriented boxes.

3. **Reliability discipline:** open `miic_reliability_evidence.png`.
   Explain the fixed validation-derived threshold, confusion matrix, and how
   uncertain cases can be routed for review.

4. **Failure awareness:** show one false positive or missed BPD from the
   validation outputs. Judges usually trust a team more when it can identify
   the model's failure boundary.

## Strong claims

- We trained and validated a detector on **real 4H-SiC** imagery.
- The improved model raises precision from **58.5% to 66.9%** and mAP50-95
  from **36.2% to 39.9%** on the same leakage-safe validation split.
- The split is acquisition-session-disjoint with zero session overlap.
- MIIC demonstrates a broader semiconductor SEM anomaly workflow with a
  validation-calibrated threshold and explicit failure counts.
- Every highlighted region is traceable to a model output and source image.

## Reliability statements

- SiC results are validation metrics because the public dataset has no separate
  held-out test set.
- BPD recall remains limited; more diverse expert-labeled BPD sessions are the
  highest-value data improvement.
- MIIC is a semiconductor SEM proxy, not a SiC dataset, and it has no aligned
  ground-truth masks for pixel-level claims.
- Confidence scores rank model belief; they are not physical proof of a defect.

## What not to show first

- Quantum experiments: they currently add complexity without a decisive gain.
- Large training logs or every generated heatmap.
- Accuracy alone without the class-specific and split-integrity context.
