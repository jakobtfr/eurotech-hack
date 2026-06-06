# 4H-SiC Dislocation Detection Results

This directory contains an efficient oriented-object detection experiment trained
on real 4H-SiC photoluminescence images from the public
`SiC_Dislocation_Detection_DB`.

The model detects:

- `TD`: threading dislocations, generally visible as dark spots.
- `BPD`: basal plane dislocations, generally visible as elongated dark lines.

## Evaluation policy

The source dataset's published split contains augmented validation images and one
acquisition session shared between train and validation. The training script
creates a stricter split:

- acquisition sessions are disjoint between train and validation;
- augmented CBMS images are used only for training;
- validation contains only original images.

This makes validation more defensible, but the source dataset does not provide a
separate held-out test set. Report the resulting metrics as validation metrics,
not final production performance.

## Run

```bash
.venv/bin/python sic_results/train_sic_obb.py
```

Exact parameters and split statistics are written to `parameters.json` and
`split_statistics.json`. Ultralytics stores model weights, metrics, plots, and
predictions inside the run directory.

## Result

The efficient run completed 18 epochs and selected the epoch-16 checkpoint:

- Overall validation mAP50: `0.596`
- Overall validation mAP50-95: `0.362`
- TD mAP50: `0.834`
- BPD mAP50: `0.359`

The model is already useful as a SiC-specific baseline, but BPD detection is the
main improvement target. See `SUMMARY.md` for interpretation and limitations.
