# Quantum Machine Learning for Defect Detection

## Practical Recommendation

Current quantum hardware is not suitable for directly processing full-resolution
SiC images or replacing the object detector. A practical research architecture is:

```text
SiC image
  -> classical YOLO/DINOv2 feature extraction
  -> candidate defect crop or compact feature vector
  -> PCA or learned reduction to a small number of features
  -> quantum kernel SVM or variational quantum classifier
  -> defect verification and confidence score
```

This preserves high-resolution localization on classical hardware while using a
quantum processor only for the compact classification or anomaly-scoring stage.

## Closely Related Published Work

### Semiconductor Defect Detection by Hybrid Classical-Quantum Deep Learning

- Venue: CVPR 2022
- Tasks: WM-811K wafer-map classification and lithography hotspot classification
- Method: classical feature extractor, small parameterized quantum circuit, and
  classical output layer
- Link: <https://openaccess.thecvf.com/content/CVPR2022/papers/Yang_Semiconductor_Defect_Detection_by_Hybrid_Classical-Quantum_Deep_Learning_CVPR_2022_paper.pdf>

This is the closest published method to the WM-811K experiment in this repository.
It classifies complete wafer patterns; it does not localize individual image
defects.

### Quantum Kernel Methods for Industrial Anomaly Detection

- Focus: small-data industrial anomaly detection using quantum-kernel SVMs
- Includes experiments on real IBM quantum hardware
- Reports that shallow circuits can retain simulator performance, while deeper
  circuits can degrade sharply from accumulated hardware noise
- Link: <https://openreview.net/pdf?id=XqiCX8AVnz>

### Qsco: A Quantum Scoring Module for Open-Set Supervised Anomaly Detection

- Venue: AAAI 2025
- Method: a variational quantum scoring circuit after classical feature extraction
- Relevant to unseen defect classes and limited labeled anomaly data
- Link: <https://arxiv.org/abs/2405.16368>

### Benchmarking MedMNIST on Real Quantum Hardware

- Published in Scientific Reports
- Runs compact medical-image classifiers on real IBM quantum hardware
- Includes hardware-aware circuit generation and error mitigation
- Code: <https://github.com/gurinder-hub/QML_MedMNIST>
- Paper: <https://pmc.ncbi.nlm.nih.gov/articles/PMC12992601/>

### QSurfNet

- Hybrid quantum-classical CNN for surface-defect recognition
- Uses heavily reduced image representations before the quantum layers
- Link: <https://doi.org/10.1007/s11128-023-03930-5>

## Proposed Experiment

1. Use the trained SiC detector to extract candidate defect crops.
2. Extract compact DINOv2 or detector-backbone embeddings.
3. Compare classical RBF-SVM, quantum-kernel SVM, and variational quantum classifier.
4. Evaluate simulator, noisy simulator, and real quantum hardware.
5. Report precision, recall, F1, calibration, runtime, shot count, and circuit depth.

The classical baseline is essential. Higher confidence alone is not evidence of a
quantum advantage.
