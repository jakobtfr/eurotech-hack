# SiC Wafer Anomaly and Defect Detection - Implementation Plan

Planning artifact created from the local control documents and sources only.

Control documents:
- `AGENTS.md`: planning-only session, maintain artifacts under `output/`, cite source IDs and exact files/sections, separate verified claims, assumptions, pitch framing, and open questions.
- `prompt.md` (`BRIEF`): project thesis, candidate methods, datasets, repos, and 24-hour hackathon plan.
- `sources/manifest.md`: authoritative source IDs and local file paths.

## Committee Decision

The plan should target a credible demo and research claim, not a fully validated SiC inspection product. The most defensible build is:

1. Use **FoundAD** as the primary research headline because the brief asks for a foundation-encoder few-shot anomaly detector and the local repo supports DINOv3-based train, AD, and demo modes (`R1`, `sources/repos/FoundAD/README.md`, `foundad/main.py`, `foundad/src/train.py`, `foundad/src/AD.py`).
2. Use **SubspaceAD** as the training-free fallback and baseline because it is simpler to run, has explicit CLI support, and avoids projector training if FoundAD or DINOv3 access blocks progress (`R2`, `sources/repos/SubspaceAD/README.md`, `main.py`, `src/subspacead/config.py`).
3. Use **semiconductor proxy validation** on MIIC or other available SEM data before claiming any SiC transfer. P7 shows MIIC is public, large-scale SEM, and explicitly highlights the domain gap from natural-image pretraining (`P7`, `sources/md/2505.07576v1.md`, Sections 3.1, 4.1, 4.2).
4. Use **SiC PL/etch-pit data** for qualitative proof and the demo if acquired in time. P1 and P11 verify that PL images can reveal 4H-SiC dislocations, but also show low contrast, ambiguous boundaries, and dependence on destructive etch labels for validation (`P1`, Sections 1, 2.1.3, 3.3, 4; `P11`, Abstract, Materials and Equipment, Results and Discussion, Summary).
5. Avoid claiming a new public SiC benchmark or production accuracy unless the dataset is actually collected, licensed, split, and measured during the build. Treat that as pitch framing and future work, not a verified result.

## Verified Claims

- 4H-SiC PL inspection is relevant, but the imaging task is hard because dislocation defects can be low contrast with indistinct boundaries, requiring enhancement before detection. P1 applies Gaussian spot homogenization, brightness/contrast adjustment, denoising, YOLO11-OBB, and class-balanced multi-sampling for 4H-SiC PL dislocation detection (`P1`, Abstract, Sections 1, 2.1.3, 2.2, 3.1.3, 3.2, 3.3).
- The strongest directly relevant SiC PL paper still reports a meaningful limitation: YOLO11-OBB plus CBMS reaches an overall mAP50 of 0.700 in the reported TD/BPD detection result, and BPD recall remains weak (`P1`, Section 3.3, Fig. 18 discussion, Conclusions).
- SiC crystal microscopy has strong self-reported supervised results, but it is not the same task as open-set wafer inspection. SCDD-Net reports SiC-Crystal-5K with 5,125 actual images after augmentation, mAP@0.5 of 0.9953, and 102 FPS, while also saying the dataset should be expanded for richer industrial scenarios (`P2`, `sources/md/1-s2.0-S095070512300744X-main.md`, Abstract, Table 1, Table 3, Table 5, Conclusion).
- PL-NDT can be correlated with destructive etch-derived defect labels in SiC. Wolfspeed/Cree reports PL-NDT plus DCNN inference for BPD, TD, TSD, and TED, with BPD density correlation to etch values at slope 1.13 and R2 0.84 over N=308 wafers (`P11`, `sources/md/MSF.1004.321.md`, Abstract, Results and Discussion, Fig. 5, Summary).
- Modern wafer/semiconductor anomaly methods transfer imperfectly across modalities. P7 explicitly warns that ImageNet-pretrained feature methods face a domain gap on SEM, while still reporting strong MIIC results for feature-based methods such as CFA and STFPM (`P7`, Sections 3.1, 4.1, 4.2).
- EfficientAD is a strong lightweight baseline for wafer visual inspection. On a private 300 mm wafer dataset, P4 reports EfficientAD as best among tested unsupervised anomaly methods, with image-wise F1 82.35 and pixel-level PRO 75.14, but the data is not shareable (`P4`, `sources/md/1-s2.0-S2667305325001024-main.md`, Abstract, Sections 3.1, 5.1, Table 2, Data availability).
- WaferDC validates useful engineering ideas for SEM wafer inspection: multi-cluster memory banks for background/scale variation and SegMix augmentation for long-tailed defect classification. Its main SEM dataset is proprietary (`P3`, `sources/md/1-s2.0-S0952197625023504-main.md`, Abstract, Sections 3.1-3.3, 4.1, Tables 1-8, Limitations).
- FoundAD's evidence is on MVTec-AD and VisA, not SiC. It reports strong few-shot results using frozen foundation encoders and a nonlinear projector, with DINOv3 best in its ablation (`P8`, `sources/md/2510.01934v1.md`, Abstract, Tables 1-5, Section 3.3).
- SubspaceAD's evidence is also on MVTec-AD and VisA, not SiC. It reports training-free PCA subspace residual scoring on frozen DINOv2 features; DINOv3-7B is explicitly worse than DINOv2-G in the provided appendix table (`P9`, `sources/md/2602.23013v3.md`, Abstract, Sections 3.2-3.4, Table 1, Section 4.7, Appendix Table 7).
- Wafer-map classification sources are useful for yield-pattern context but are not microscope/PL anomaly-localization evidence. P5 uses WM-811K wafer maps, and R5/R6 use MixedWM38 electrical wafer maps (`P5`, `sources/md/2411.11029v1.md`, Abstract, Section 2.1, Table 4; `R5`, `sources/repos/WaferMap/README.md`; `R6`, `sources/repos/Wafers-Defect-Recognition-using-Visual-Transformer/README.md`).

## Assumptions

- DINOv3 access and weights are available for the team. R1 requires users to have rights to DINOv3 and to download trained manifold projectors for quick demos (`R1`, `README.md`, Quick Start).
- Challenge machines have enough GPU memory for FoundAD or at least SubspaceAD. R1 and R2 both recommend Python 3.10; R2 benchmark scripts assume H100-class resources, though manual category-level runs can be smaller (`R1`, `requirements.txt`, `README.md`; `R2`, `scripts/benchmark_few_shot.sh`).
- The Zenodo SiC etch-pit set, NFFA SEM proxy, MIIC, MVTec, or VisA can be downloaded during the session. They are not present in `sources/manifest.md`; only papers and repos are local.
- The challenge permits pre-rendered demo outputs and public/proxy datasets.
- The brief's Hong Kong executive framing is the target narrative, but local sources do not verify the market timing, competitor details, or Resonac wafer-cost figure.

## Pitch Framing

- Frame the project as an **open few-shot inspection workbench for third-generation semiconductor defects**, not a direct replacement for KLA/SICA on day one.
- The research question is: **Do foundation-encoder anomaly residuals remain useful when moving from photographic industrial benchmarks into wafer physics modalities such as SEM and PL?**
- The product wedge is: collect scarce normal SiC images, produce tile heatmaps quickly, flag unknown defects, and route suspicious regions to engineer review.
- The honest win condition is not "production-grade accuracy"; it is a defensible demonstration that the system can ingest wafer imagery, localize suspect regions, quantify uncertainty, and expose where transfer works or breaks.
- Avoid claiming "first public SiC benchmark" unless the dataset release, license, and evaluation protocol are actually prepared.

## Source Ledger

### C0 - AGENTS.md

- Contribution: Governs this session. Requires planning only, local-source preference, Markdown before PDFs, output artifacts under `output/`, citations to source IDs/files/sections, and explicit separation of verified claims, assumptions, pitch framing, and open questions.
- Relevant claims: This deliverable must be an implementation plan, not code.
- Caveats/trust: Highest authority for task format, but not technical evidence.
- Inspect later: Entire file.
- Missing context: None for planning format.

### BRIEF - prompt.md

- Contribution: Primary project thesis, method shortlist, data shortlist, repo list, and 24-hour execution sketch.
- Relevant claims: The proposed angle is open, few-shot, open-vocabulary, open-set SiC wafer inspection; FoundAD is the primary stack; SubspaceAD, EfficientAD, DefectFill/SeaS, TailedCore, WaferDC, MIIC, WM-811K, MixedWM38, and proxy datasets form the method/data landscape.
- Caveats/trust: High as user intent and proposal framing. Medium to low as factual evidence where it asserts market gaps, latest papers, competitor names, and cost/ROI numbers without local source verification.
- Inspect later: Sections 1 Thesis, 2 Methods and Papers, 3 Code Repositories, 4 Datasets, 5 24-Hour Execution Plan, 6 Caveats and Open Questions.
- Missing context: Actual challenge rules, evaluation criteria, allowed datasets, available GPUs, download credentials, and whether the team is expected to release data.

### P1 - Enhanced PL YOLO11-OBB for 4H-SiC

- File: `sources/md/1-s2.0-S0925963525008027-main.md`
- Contribution: Most directly relevant SiC PL defect-detection source. Supports PL preprocessing, OBBs for elongated BPDs, class-balanced sampling, and the caveat that BPD remains difficult.
- Relevant claims: PL defects in high-doping 4H-SiC have low contrast and unclear boundaries; the authors use image enhancement plus YOLO11-OBB and CBMS; overall reported mAP50 for YOLO11-OBB (CBMS) in Fig. 18 discussion is 0.700 with weaker BPD recall.
- Caveats/trust: Peer-reviewed Elsevier article, high topical relevance. Dataset is self-built and not public in local materials; performance is supervised, not open-set; BPD result is not strong enough to use as a triumphant benchmark.
- Inspect later: Abstract; Sections 1, 2.1.2, 2.1.3, 2.2, 3.1.3, 3.2.1, 3.2.2, 3.3, 4; Table 1; Figs. 9-19.
- Missing context: Dataset access, annotation files, exact class counts after CBMS, train/test split, image license, and whether PL images can be redistributed.

### P2 - SCDD-Net for SiC crystal defects

- File: `sources/md/1-s2.0-S095070512300744X-main.md`
- Contribution: SiC defect taxonomy and high-performance supervised crystal microscopy baseline.
- Relevant claims: SiC-Crystal-5K covers TSD, BPD, TED, and MP with 5,125 actual images after augmentation; SCDD-Net reports mAP@0.5 0.9953, mAP@0.5:0.95 0.7320, and 102 FPS.
- Caveats/trust: Peer-reviewed source, but lower implementation relevance because it targets crystal/ingot microscopy and supervised detection on an author-collected dataset. The headline metric should be cited as self-reported, not independently validated.
- Inspect later: Abstract; Section 2.1; Fig. 2; Table 1; Table 3; Table 4; Table 5; Conclusion.
- Missing context: Public availability of SiC-Crystal-5K, annotation format, licensing, and raw image examples.

### P3 - WaferDC SEM wafer detection/classification

- File: `sources/md/1-s2.0-S0952197625023504-main.md`
- Contribution: SEM wafer pipeline pattern: multi-cluster memory bank, anomaly heatmaps, SegMix augmentation, PEFT ViT classifier, long-tail handling.
- Relevant claims: SEM wafer data has diverse background types, variable scales, and long-tail defect distributions; WaferDC improves detection and classification on a proprietary SEM wafer dataset plus DTD-Synthetic and MTD; SegMix uses anomaly heatmaps to synthesize balanced defects.
- Caveats/trust: Peer-reviewed article and local repo. Main SEM wafer dataset is proprietary, so use the method concepts and code paths but not its data claims as directly reproducible.
- Inspect later: Abstract; Fig. 1; Sections 3.1, 3.2, 3.3, 4.1, 4.4, 4.5; Tables 1-8, 10, 15-18; Limitations.
- Missing context: Proprietary SEM data access, cluster-count selection for SiC/PL, and whether SegMix masks are meaningful for PL dislocation lines.

### P4 - Efficient wafer visual inspection

- File: `sources/md/1-s2.0-S2667305325001024-main.md`
- Contribution: Lightweight wafer inspection benchmark and practical dual-stage decision framing.
- Relevant claims: Dataset has 1,055 300 mm wafer images, 6,861 labels, seven defect types, PASS/FAIL labels; EfficientAD is best among tested unsupervised AD models; UPerNet-Swin is best among tested segmentation models; dual-stage EfficientAD plus UPerNet-Swin supports PASS/FAIL/RECOVER/DISCARD style decisions.
- Caveats/trust: Open-access article, good engineering relevance. Dataset is not available to the authors for sharing, so it cannot be the hackathon's reproducible dataset.
- Inspect later: Abstract; Sections 3.1, 3.2, 5.1, 5.2, 5.3; Tables 1-6; Appendix B; Appendix D; Data availability.
- Missing context: Public dataset access, labels, severity thresholds, and exact EfficientAD/anomalib config.

### P5 - WM-811K autoencoder augmentation plus CNN

- File: `sources/md/2411.11029v1.md`
- Contribution: Wafer-map classification context and class-imbalance augmentation example.
- Relevant claims: WM-811K has 811,457 wafer images, 172,950 manually labeled maps, and 25,519 defective labeled wafers; CNN-AUG reports 0.9856 accuracy on eight wafer-map defect classes.
- Caveats/trust: Preprint and wafer-map classification, not microscope/PL anomaly localization. Traditional baselines are limited. Use for background only.
- Inspect later: Abstract; Section 2.1; Figs. 2, 7, 8; Table 4; Table 5; References.
- Missing context: Code availability, exact split reproducibility, whether unlabeled WM-811K data is used, and independent benchmark comparisons.

### P6 - TailedCore

- File: `sources/md/2504.02775v2.md`
- Contribution: Long-tail/noisy-normal anomaly detection method. Useful if normal-pool contamination and class imbalance become key implementation risks.
- Relevant claims: Defines the tail-versus-noise dilemma; proposes TailSampler and TailedCore; evaluates on modified MVTecAD and VisA noisy long-tail settings; reports TailedCore outperforms PatchCore and SoftPatch in most settings.
- Caveats/trust: CVPR 2025 paper with local repo. It is general industrial AD, not semiconductor or SiC; datasets are artificially transformed to create long-tail/noisy settings.
- Inspect later: Abstract; Sections 1, 6.1, 6.3.3, 6.3.4, 6.4, 7; Tables 3-6; Fig. 4; Fig. 5.
- Missing context: Whether SiC reference pools contain enough contamination or unknown tail classes to justify adding this complexity in the first build.

### P7 - MIIC VAD benchmark

- File: `sources/md/2505.07576v1.md`
- Contribution: Strongest public SEM proxy justification and domain-gap warning.
- Relevant claims: MIIC has 25,276 SEM images: 25,160 normal and 116 anomalous, with 512x512 resolution and masks/labels; feature-based methods work on SEM but ImageNet pretraining has a domain gap; CFA leads image-level F1 among tested feature methods while STFPM leads pixel F1.
- Caveats/trust: arXiv benchmark, but very relevant and public-data oriented. Not SiC and not PL.
- Inspect later: Abstract; Sections 2.1, 3.1, 3.2, 3.4, 4.1, 4.2, 5; Tables 1-3.
- Missing context: MIIC download status, license restrictions, exact dataset split files, and whether non-commercial restrictions apply.

### P8 - FoundAD

- File: `sources/md/2510.01934v1.md`
- Contribution: Primary foundation-encoder anomaly method and research thesis support.
- Relevant claims: Foundation visual encoders show feature-distance correlation with anomaly area; FoundAD trains a projector from synthesized abnormal features to normal features; DINOv3 is the best FoundAD backbone in the reported ablation; layer selection and Top-K matter.
- Caveats/trust: ICLR 2026/preprint style source with local repo. Evidence is MVTec-AD and VisA, not SiC/SEM/PL. DINOv3 access may be gated.
- Inspect later: Abstract; Fig. 2; Fig. 3; Tables 1-5; Section 3.3; Section 3.4; supplementary tables for per-class results.
- Missing context: DINOv3 license/access, trained projector downloads, correct crop/layer for the local repo, and behavior on grayscale SEM/PL.

### P9 - SubspaceAD

- File: `sources/md/2602.23013v3.md`
- Contribution: Training-free few-shot baseline/fallback using frozen DINOv2 features plus PCA residuals.
- Relevant claims: SubspaceAD extracts patch-level DINOv2 features from a few normal images, fits PCA, and scores residuals; reports strong 1/2/4-shot MVTec-AD and VisA results; DINOv3-7B appendix results are worse than DINOv2-G for this method.
- Caveats/trust: CVPR 2026/preprint style source with local repo. Still not SiC/SEM/PL; uses MVTec/VisA and relatively high-resolution DINOv2-G defaults.
- Inspect later: Abstract; Sections 3.2, 3.3, 3.4, 4.5, 4.7, 5; Table 1; Table 3; Table 4; Appendix Table 7; Appendix failure cases.
- Missing context: Runtime on challenge hardware, dataset loader adaptation for arbitrary SiC tile folders, and whether PCA residuals are stable on low-contrast PL.

### P10 - UniSpector

- File: `sources/md/2604.02905v1.md`
- Contribution: Open-set and visual-prompt framing for defect naming/localization.
- Relevant claims: Closed-set detectors fail on novel defect types; anomaly detectors localize but do not distinguish defect classes; UniSpector uses visual prompts, spatial-spectral prompt encoding, contrastive prompt encoding, and prompt-guided query selection; performance depends on exemplar prompts and remains weaker cross-domain.
- Caveats/trust: CVPR 2026/preprint style source. No local repo in manifest. Heavy for 24 hours; best used as pitch framing and a future naming module.
- Inspect later: Abstract; Sections 1, 3, 4.3, 4.4, 5; Tables 1-6; Appendix A.2 prompt allocation; Fig. 8.
- Missing context: Code availability, prompt exemplars for SiC classes, and whether spectral prompt features apply to PL/SEM grayscale images.

### P11 - Wolfspeed/Cree PL-NDT DCNN for SiC

- File: `sources/md/MSF.1004.321.md`
- Contribution: Industrial SiC PL-NDT validation logic and defect taxonomy.
- Relevant claims: PL-NDT images of 150 mm 4H-SiC wafers can correlate to etch-derived BPD, TD, TSD, and TED features; a DCNN trained on etch-labeled PL images can infer defect locations from PL images; BPD density correlation against etch count reports slope 1.13 and R2 0.84 over N=308.
- Caveats/trust: Older 2020 conference/journal source from Wolfspeed/Cree; proprietary DCNN and data; useful for context and taxonomy, not open-source implementation.
- Inspect later: Abstract; Introduction; Materials and Equipment; Results and Discussion; Figs. 1-5; Summary.
- Missing context: Network architecture, data volume, annotation tooling, license/access, and production acceptance thresholds.

### H1 - IEEE Xplore stub

- File: `sources/md/IEEE Xplore Full-Text PDF_.md`
- Raw: `sources/raw/IEEE Xplore Full-Text PDF_.html`
- Contribution: None. Converted Markdown is empty.
- Relevant claims: Manifest says the IEEE PDF returned HTTP 403 during conversion. Local raw HTML is access-control/script boilerplate, not paper content.
- Caveats/trust: Not usable as evidence.
- Inspect later: Only if IEEE access is provided; otherwise skip.
- Missing context: Paper title, abstract, bibliographic metadata, and PDF access.

### H2 - IEEE Xplore stub 2

- File: `sources/md/IEEE Xplore Full-Text PDF_2.md`
- Raw: `sources/raw/IEEE Xplore Full-Text PDF_2.html`
- Contribution: None. Converted Markdown is empty.
- Relevant claims: Manifest says the IEEE PDF returned HTTP 403 during conversion.
- Caveats/trust: Not usable as evidence.
- Inspect later: Only if IEEE access is provided; otherwise skip.
- Missing context: Paper title, abstract, bibliographic metadata, and PDF access.

## Repository Inventory

### R1 - FoundAD

- Repo: `https://github.com/ymxlzgy/FoundAD`
- Local path: `sources/repos/FoundAD`
- Commit: `a590587d9618`
- Contribution: Primary few-shot foundation-encoder anomaly detector and demo path.
- Useful files:
  - `README.md`: environment, DINOv3 rights note, projector download links, demo/train/inference commands.
  - `requirements.txt`, `setup.py`: installation.
  - `foundad/main.py`: Hydra/DDP entrypoint with `train`, `AD`, and `demo` modes.
  - `foundad/configs/config.yaml`: base data/testing settings; Top-K defaults and augmentation flags.
  - `foundad/configs/app/train_dinov3.yaml`: local default DINOv3 config, `crop_size: 512`, `pred_depth: 6`, `n_layer: 3`.
  - `foundad/configs/app/test.yaml`: test app config.
  - `foundad/src/sample.py`: few-shot subset creation from `train/good` or `train/ok`.
  - `foundad/src/train.py`: CutPaste synthesis and projector training.
  - `foundad/src/AD.py`: metrics, heatmaps, and demo heatmap export.
  - `foundad/src/datasets/dataset.py`: dataset loader to adapt for custom SiC tile folders.
- Caveats: DINOv3 access and pretrained projector downloads are external; local default crop/layer differs from the brief's 448px/layer-10 suggestion and must be verified.

### R2 - SubspaceAD

- Repo: `https://github.com/CLendering/SubspaceAD`
- Local path: `sources/repos/SubspaceAD`
- Commit: `419050677288`
- Contribution: Training-free fallback and baseline.
- Useful files:
  - `README.md`: method summary, setup, data prep, manual command.
  - `requirements.txt`, `pyproject.toml`: installation.
  - `main.py`: end-to-end CLI, PCA fitting, scoring, visualizations.
  - `src/subspacead/config.py`: arguments for dataset, backbone, resolution, k-shot, PCA explained variance, CLAHE, saliency masks, patching.
  - `src/subspacead/core/extractor.py`: DINO/HF feature extraction.
  - `src/subspacead/core/pca.py`: PCA and Kernel PCA models.
  - `src/subspacead/data/datasets.py`: dataset handlers to adapt for custom SiC data.
  - `src/subspacead/post_process/scoring.py`: image/pixel scoring.
  - `scripts/benchmark_few_shot.sh`: recommended DINOv2-G, 672px, k-shot, 30 augmentations, PCA EV 0.99.
  - `tools/prepare_visa.py`: VisA format utility.
- Caveats: Built for MVTec/VisA folder structures; DINOv2-G may be heavy. Needs adaptation for arbitrary SiC tile data.

### R3 - TailedCore

- Repo: `https://github.com/jungyg/TailedCore`
- Local path: `sources/repos/TailedCore`
- Commit: `7240f04b489f`
- Contribution: Long-tail/noisy-normal robustness option.
- Useful files:
  - `README.md`: installation, generated noisy long-tail MVTecAD/VisA datasets, command pattern.
  - `main.py`: experiment entrypoint.
  - `configs/tailedcore_mvtec.yaml`, `configs/tailedcore_visa.yaml`: model configs.
  - `src/coreset_model.py`: PatchCore, SoftPatch, TailedCore implementation.
  - `src/sampler.py`: TailSampler, AdaptiveTailSampler, LOF/TailedLOF samplers.
  - `src/class_size.py`, `src/adaptive_class_size.py`: class-size prediction and few-shot sampling.
  - `make_all_mvtecad_nlt.sh`, `make_all_visa_nlt.sh`: synthetic noisy long-tail data generation.
- Caveats: Adds complexity that is probably too high for the primary build. Evidence is general industrial AD, not semiconductor or SiC.

### R4 - WaferDC

- Repo: `https://github.com/SpatialAILab/WaferDC`
- Local path: `sources/repos/WaferDC`
- Commit: `2b185c2fcc51`
- Contribution: SEM wafer detection/classification reference implementation and SegMix/memory-bank ideas.
- Useful files:
  - `README.md`: method summary, setup, two-stage command flow, license.
  - `1step_defect_detetion/step1_1_train_k_means.py`: clustering for multi-cluster memory bank.
  - `1step_defect_detetion/step1_2_normal_augmentation.py`: normal augmentation.
  - `1step_defect_detetion/step1_3_run_patchcore.py` and `step1_3_run_patchcore_magnetic.sh`: PatchCore stage.
  - `1step_defect_detetion/test1_2_load_and_evaluate_patchcore.py`: thresholding, evaluation, heatmap export.
  - `1step_defect_detetion/patchcore/*`: embedded PatchCore implementation.
  - `2step_defect_classification/main.py`: PEFT classifier entrypoint.
  - `2step_defect_classification/configs/data/wafer.yaml`: wafer dataset path config.
  - `2step_defect_classification/configs/model/clip_vit_b16_peft_wafer.yaml`: CLIP ViT-B/16 PEFT config, normal label handling.
  - `2step_defect_classification/datasets/wafer.py`: wafer dataset text-list format.
- Caveats: Main SEM wafer data is proprietary; code has hardcoded paths and Python 3.8/PyTorch-version assumptions. License is CC BY-NC-ND 4.0, so reuse carefully.

### R5 - WaferMap

- Repo: `https://github.com/Junliangwangdhu/WaferMap`
- Local path: `sources/repos/WaferMap`
- Commit: `10e65ca04cf1`
- Contribution: MixedWM38 dataset and older Keras/TensorFlow multi-label wafer-map baseline.
- Useful files:
  - `README.md`: MixedWM38 description, data keys `arr_0` and `arr_1`, dataset sources, pattern taxonomy.
  - `trian_mutil_label.py`: Keras multi-label training, data loading, deformable convolution model.
  - `layers_train.py`, `deform_conv.py`: deformable convolution layer.
  - `Dataset Figure/*.png`: visual taxonomy examples.
- Caveats: Electrical wafer maps, not microscope/PL imagery. TF1-era style code and typo in filename.

### R6 - ViT Wafer Defect Recognition

- Repo: `https://github.com/PanithanS/Wafers-Defect-Recognition-using-Visual-Transformer`
- Local path: `sources/repos/Wafers-Defect-Recognition-using-Visual-Transformer`
- Commit: `d54c4a278777`
- Contribution: Notebook-level ViT baseline for MixedWM38 wafer-map classification.
- Useful files:
  - `README.md`: MixedWM38 context and reported 98.98% accuracy.
  - `MixedDefectWafer_ViT_v1b.ipynb`: data loader, label reader, ViT model cells.
  - `model_vit_v1b.index`, `model_vit_v1b_history`: saved artifacts/history.
- Caveats: Notebook uses a local Windows dataset path in code cells; not directly runnable without edits. Wafer maps only, not visual inspection imagery.

### R7 - awesome-industrial-anomaly-detection

- Repo: `https://github.com/M-3LAB/awesome-industrial-anomaly-detection`
- Local path: `sources/repos/awesome-industrial-anomaly-detection`
- Commit: `79e113227d50`
- Contribution: Method landscape checklist and pointers to current SOTA, benchmarks, datasets, and anomaly synthesis.
- Useful files:
  - `README.md`: current method list; entries for SubspaceAD, UniSpector, FoundAD, SeaS, AA-CLIP, TailedCore, DefectFill, EfficientAD, WinCLIP, MVTec, VisA.
  - `paper_tree.png`, `timeline.png`: overview visuals.
- Caveats: Curated list, not primary evidence. Use only for discovery and cross-checking, not for technical claims.

## Implementation Plan

### Workstream 0 - Governance and Evidence

Owner: research lead.

Deliverables:
- `data/source_registry.jsonl`: every input image, source ID, license/access note, modality, split, and preprocessing version.
- `docs/claim_table.md`: verified claims only, with source ID and section/file.
- `runs/<timestamp>/config.yaml`: exact model, crop size, layer, k-shot, threshold, and data split used.

Steps:
1. Freeze claim language before coding: "evaluates transfer" and "few-shot workbench" are allowed; "production replacement", "first public benchmark", and ROI numbers require verification.
2. Make every plotted metric reproducible from a saved CSV and split file.
3. Keep source-derived caveats visible in the pitch appendix.

### Workstream 1 - Data and Tiling

Owner: data engineer plus SiC domain expert.

Primary data priority:
1. Real SiC source named in `BRIEF`: Zenodo SiC etch-pit set, if downloadable and license permits.
2. SiC PL/figure crops from P1/P11 only if licensing permits and manually cropped examples are acceptable.
3. SEM proxy: MIIC from P7, because it is public and semiconductor-specific.
4. Safety fallback: MVTec AD and VisA, because R1/R2 support them directly.
5. Wafer-map sources R5/R6 only for an optional yield-map context slide, not the anomaly-localization demo.

Preprocessing contract:
- Convert grayscale PL/SEM to RGB by channel repeat for foundation encoders.
- Create square tiles with deterministic IDs.
- Try 512px first for FoundAD because local `R1` config defaults to `crop_size: 512`; test 448px only as an ablation if time permits.
- Try 672px for SubspaceAD because R2 benchmark scripts and P9 ablations use that setting.
- Apply CLAHE as an explicit on/off switch, not silently. P1 supports image enhancement for PL; R2 has a `--use_clahe` flag.
- Save tile metadata as:

```json
{
  "tile_id": "source_image__x0000_y0000_s0512",
  "source_id": "P1-or-dataset-name",
  "modality": "PL|SEM|etch|wafer_map|synthetic",
  "image_path": "...",
  "preprocess": "rgb_repeat+clahe_v1",
  "split": "support|validation|test|demo",
  "label": "normal|BPD|TD|unknown|proxy_anomaly|null",
  "mask_path": null
}
```

Exit criteria:
- At least one normal-only support set and one test/demo set exist.
- At least five preloaded demo examples exist even if real SiC data is limited.
- Every example has source/license status recorded.

### Workstream 2 - Core Anomaly Models

Owner: CV anomaly lead.

Primary path: FoundAD.
- Install R1 environment.
- Download or mount DINOv3 weights and the FoundAD projector, if permitted.
- Run the R1 MVTec or VisA demo exactly once to prove heatmap rendering.
- Adapt dataset loader or folder layout to SiC/SEM tiles.
- Train a small projector with local defaults first: `crop_size: 512`, `n_layer: 3`, `pred_depth: 6`.
- Then run a minimal ablation: DINOv3 layer/crop from local default versus the brief's suggested layer/crop, if time permits.

Fallback and baseline: SubspaceAD.
- Install R2.
- Run a single category MVTec/VisA command from R2 README.
- Adapt the dataset handler for a flat tile folder.
- Fit PCA using k normal SiC/SEM images with `k_shot` in {1, 2, 4}, `aug_count: 30`, `pca_ev: 0.99`.
- Use R2's `--use_clahe` for PL ablation.

Secondary baselines:
- EfficientAD through anomalib only if dependency setup is fast; P4 justifies it, but no local anomalib repo is present.
- PatchCore/WaferDC only if the demo needs a classic memory-bank baseline; R4 can be inspected but is likely too hard to adapt in 24 hours.

Exit criteria:
- For each demo tile: anomaly score, heatmap image, and model config are saved.
- For any dataset with labels/masks: image AUROC and pixel AUROC or PRO are saved.
- Failure cases are preserved; they are useful for the honest research narrative.

### Workstream 3 - Naming, Open-Set Flagging, and Verdicts

Owner: open-set and UX lead.

Minimal implementation:
- Contour connected hot regions from anomaly heatmaps.
- Attach non-binding labels from a fixed prompt list: `BPD`, `threading dislocation`, `micropipe`, `scratch`, `particle`, `stain`, `unknown`.
- Compute novelty flag as: high anomaly residual and low naming confidence.

Important caveat:
- Do not claim reliable defect naming without supervised labels or a visual-prompt model. P10 supports open-set visual prompting as a research direction, but no local UniSpector repo is available.

Verdict logic:
- `PASS`: all tile scores below conservative threshold.
- `REVIEW`: localized defects or unknown flag.
- `KILL`: severe/high-area anomaly or many clustered hot tiles.
- Thresholds must be labeled as demo heuristics unless calibrated on a validation set.

Exit criteria:
- Each scored tile emits:

```json
{
  "tile_id": "...",
  "anomaly_score": 0.0,
  "heatmap_path": "...",
  "label": "unknown",
  "novelty_flag": true,
  "verdict": "REVIEW"
}
```

### Workstream 4 - Demo

Owner: demo engineer plus pitch lead.

First screen:
- Operational dashboard, not a landing page.
- Preloaded examples only; live upload is optional.
- Main visual: synthetic or stitched wafer map with tile-level heat overlay.
- Detail panel: raw tile, heatmap overlay, before/after slider, contours, score, novelty flag, verdict.
- Research tab: FoundAD versus SubspaceAD or FoundAD versus EfficientAD if available.

Pre-render:
- Heatmaps for every demo example.
- A screen recording as backup.
- Static PNG fallback for the full-wafer heatmap.

Exit criteria:
- Demo runs offline from local files.
- Every displayed claim links back to source or run artifact.
- No metric appears without a dataset/split/config label.

### Workstream 5 - Evaluation

Owner: evaluation lead.

Minimum metrics:
- For proxy datasets with labels/masks: image AUROC, AUPR, pixel AUROC, and PRO where masks exist.
- For real SiC without labels: qualitative heatmap audit with domain-expert notes and an "unlabeled qualitative only" label.
- For demo thresholds: false-negative-sensitive thresholding inspired by P4 Section 5.1.1, but clearly marked as heuristic unless calibrated.

Comparison table:
- FoundAD on MVTec/VisA sanity run.
- FoundAD on SEM proxy.
- SubspaceAD on SEM proxy.
- Optional EfficientAD/PatchCore if quick.
- SiC qualitative examples separately, unless labels exist.

Exit criteria:
- CSV metrics and selected qualitative examples are generated.
- Negative results are summarized, not hidden.

## 24-Hour Execution Schedule

H0-H1:
- Install R1 and R2.
- Confirm DINOv3/DINOv2 weights.
- Run at least one known demo heatmap.
- Start dataset downloads.

H1-H4:
- Build tile dataset registry and preprocessing.
- Create support/test/demo folders.
- Run SubspaceAD on a small known dataset if FoundAD is blocked.

H4-H8:
- Run FoundAD or SubspaceAD on SEM proxy.
- Generate first heatmaps and metric CSV.
- Begin demo shell with preloaded examples.

H8-H14:
- Add SiC PL/etch-pit qualitative examples.
- Run k-shot/crop/CLAHE ablations.
- Create full-wafer aggregate heatmap.

H14-H18:
- Add open-set/unknown flag heuristics.
- Freeze demo examples.
- Write claim table and pitch caveats.

H18-H22:
- Polish dashboard, pre-render all views, record backup.
- Build final metric and qualitative comparison table.

H22-H24:
- Freeze environment and outputs.
- Rehearse with exact wording: verified results, assumptions, and next-step ask.

## Guardrails and Pivots

- If FoundAD does not run by H2: use SubspaceAD as the core demo and keep FoundAD as planned next step.
- If DINOv3 access is blocked: use DINOv2 via SubspaceAD and phrase the foundation-encoder claim around DINOv2, with DINOv3 as a planned ablation.
- If no real SiC data is available by H6: demo on MIIC/SEM proxy plus a small number of licensed SiC figure crops, clearly marked qualitative.
- If cross-modality transfer fails: pitch the result as a map of where natural-image foundation features break on PL/SEM wafer physics, with a concrete plan for SiC-specific normal-data collection and projector adaptation.
- If metrics look weak: prioritize visual audit, calibrated thresholds, and uncertainty routing over overclaiming accuracy.

## Open Questions for the User or Team

- Which datasets are already downloaded or permitted for the challenge: Zenodo SiC, NFFA SEM, MIIC, MVTec, VisA, or private wafer images?
- Are DINOv3 weights and FoundAD projector downloads accessible under the challenge environment and license?
- What is the challenge judging rubric: technical novelty, business pitch, demo polish, accuracy, speed, or deployment feasibility?
- Is internet access available during the hackathon?
- What GPU and storage are actually available?
- Are the team allowed to use figure crops from papers, and under what license?
- Is the Resonac `$50/wafer saved` number in the brief sourced somewhere outside the local materials?
- Should the final artifact include a public dataset-release plan, or only a private pilot dataset plan?

## Final Recommendation

Build the pitch around a conservative but sharp claim:

> We built an open few-shot wafer-physics anomaly workbench that tests whether foundation visual encoders can transfer from industrial photographs into SiC/semiconductor inspection. It produces tile heatmaps, unknown-defect flags, and full-wafer risk maps from a handful of normal examples, while clearly separating proxy-validated results from qualitative SiC evidence.

The implementation should start with FoundAD only if the pretrained assets run immediately. SubspaceAD should be kept ready as the reliability path because it is training-free, local, and easier to adapt. WaferDC, TailedCore, UniSpector, and wafer-map classifiers should inform the deck and future work unless time remains after the primary heatmap pipeline and demo are stable.
