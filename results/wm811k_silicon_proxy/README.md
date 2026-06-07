# WM-811K Results

This folder contains a reproducible wafer-map failure-pattern classification
experiment trained on the labeled portion of WM-811K.

WM-811K contains electrical wafer-bin maps from silicon manufacturing. It does
not contain microscope images and is not a silicon-carbide dataset. The model
therefore learns spatial wafer-level failure patterns, not SiC surface defects.

## Method

- Task: classify `none` plus eight labeled failure patterns.
- Input: wafer maps resized to `32x32`, encoded as three categorical channels:
  background, good die, and bad die.
- Model: compact CNN trained on Apple MPS.
- Imbalance handling: inverse-square-root class-balanced sampling.
- Evaluation split: train, validation, and test lots are disjoint.
- Selection metric: validation macro-F1 with early stopping.

## Reproduce

```bash
.venv/bin/python wm811k_results/train_wm811k.py
```

The script writes the model, parameters, metrics, cached processed maps,
training history, confusion matrix, and example predictions into this folder.
