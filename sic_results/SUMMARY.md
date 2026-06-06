# SiC Training Summary

## What was trained

A compact pretrained `YOLO11n-OBB` detector was fine-tuned on real 4H-SiC
photoluminescence images. Oriented bounding boxes are appropriate because basal
plane dislocations (BPDs) appear as elongated dark structures, while threading
dislocations (TDs) generally appear as dark spots.

This is a real SiC-domain model. It is not trained on WM811K, PCB images, or a
generic industrial-anomaly proxy.

## Efficient training setup

- Device: Apple M4 Pro MPS
- Input resolution: 768 px
- Batch size: 8
- Optimizer: AdamW
- Learning rate: 0.001
- Completed epochs: 18
- Selected checkpoint: epoch 16
- Training images: 2,054
- Validation images: 211 original, non-augmented images
- Split: acquisition-session disjoint

## Validation results

| Class | Precision | Recall | mAP50 | mAP50-95 |
| --- | ---: | ---: | ---: | ---: |
| All | 0.585 | 0.649 | 0.596 | 0.362 |
| TD | 0.729 | 0.812 | 0.834 | 0.556 |
| BPD | 0.441 | 0.485 | 0.359 | 0.167 |

The detector performs strongly on TDs. BPDs remain difficult because they are
the minority class and their low-contrast linear appearance is less consistent.

## Scientific limitations

- The source dataset has no independent test set, so these are validation
  metrics rather than final production claims.
- The data represents 4H-SiC PL imaging and two dislocation classes. It does not
  cover every SiC inspection modality or defect type.
- A production evaluation should use unseen wafers or acquisition sessions from
  the target inspection system.

## Key artifacts

- Best model: `yolo11n_obb_cbms_sic/weights/best.pt`
- Metrics: `metrics.json`
- Parameters: `parameters.json`
- Split audit: `split_statistics.json`
- Confusion matrix and PR curves: `best_validation/`
- Reproducible training entrypoint: `train_sic_obb.py`
