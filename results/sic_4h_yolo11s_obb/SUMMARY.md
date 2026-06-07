# Improved 4H-SiC OBB Detector

This experiment retrains the SiC dislocation detector with a larger YOLO11s-OBB
model and 1024 px inputs. It uses the same acquisition-session-disjoint validation
split as the baseline, so the comparison does not benefit from split leakage.

## Result

| Metric | YOLO11n baseline | YOLO11s improved | Change |
|---|---:|---:|---:|
| Precision | 0.585 | **0.669** | +0.084 |
| Recall | **0.649** | 0.610 | -0.039 |
| mAP50 | 0.596 | **0.621** | +0.024 |
| mAP50-95 | 0.362 | **0.399** | +0.037 |

The improved checkpoint is substantially more precise and has better average
localization quality, but its recall is lower. It is therefore better when false
alarms are costly, while the baseline still finds slightly more possible defects.

The harder BPD class improved from 0.441 to 0.594 precision and from 0.167 to
0.196 mAP50-95, although BPD recall decreased from 0.485 to 0.356. More diverse
expert-labeled BPD images are the clearest next data improvement.

## Demo Image Confidence

At the same 0.18 display threshold on `20250117test6 (190).jpg`:

| Measurement | Baseline | Improved |
|---|---:|---:|
| Mean confidence | 0.436 | **0.505** |
| Median confidence | 0.413 | **0.462** |
| Maximum confidence | 0.631 | **0.781** |
| Predictions | 7 BPD | 3 TD, 1 BPD |

Confidence is not proof that a marked structure is a physical defect. The expert
annotations remain the ground truth for evaluation.

## Files

- `metrics.json`: independently validated metrics for the best checkpoint
- `parameters.json`: training configuration
- `training/results.csv`: epoch-level training and validation history
- `best_validation/`: validation plots and confusion matrices
- `medium_defect_mosaic_demo/`: expert, improved-model, and original-image posters
- `generate_mosaic.py`: reproducible poster generator

The selected 75 MB checkpoint is intentionally excluded from this curated
publication. It remains in the local experiment directory.
