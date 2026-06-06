# SiC Wafer Anomaly & Defect Detection — Project Brief

Distilled working notes for the HK EuroTech proposal / hackathon build. Focus: recent CV & anomaly-detection methods (2025–2026), SiC-specific where possible, with usable open-source code and benchmark data.


There's also a sideloaded md file and for downloaded papers and gh repos you can
clone. Check if these could be a help. The premise: We are 4 expert researchers
needing to win a challenge. The jury will be highly experienced Hong Kong
executives.

---

## 1. Thesis

An **open, few-shot, open-vocabulary, open-set** alternative to closed proprietary SiC wafer-inspection tools (SICA / KLA), timed to Hong Kong's third-generation-semiconductor push. The research angle: be the first to test whether the **foundation-encoder anomaly property survives the jump from photographs to wafer physics** (PL / SEM / X-ray modalities).

**The white space:** truly SiC-specific deep-learning defect detection is sparse — only two recent on-topic papers exist, and there is **no public SiC benchmark analogous to WM-811K**. The general semiconductor CV stack (anomalib / PatchCore / WaferDC / TailedCore + WM-811K / MixedWM38 / MIIC) is mature and transferable, but nobody has built the SiC-specific dataset + inline-inspection product. That gap is the investor pitch.

---

## 2. Methods & Papers

Priority on 2025–2026 work with open code. ⚠️ flags mark caveats to handle carefully.

### Core anomaly-detection methods (primary stack)

| Method | What | Fit |
|---|---|---|
| **FoundAD** | Foundation encoders (DINOv3) as few-shot, normal-only visual anomaly detectors; off-manifold residual → heatmaps. | **Primary.** Strong fit for scarce defect labels. Repo + MVTec projector available. |
| **SubspaceAD** | Training-free few-shot AD via subspace modeling (frozen features + normal-subspace residuals). | Simpler training-free baseline. |
| **EfficientAD** | Lightweight unsupervised AD. | Reported as strongest unsupervised approach in the "efficient wafer inspection" study. |
| **DefectFill / SeaS** | Realistic synthetic defect generation via inpainting diffusion. | Pads rare classes (particles, scratches, stains, bridges, missing material). |
| **TailedCore** (CVPR 2025) | Few-shot sampling for long-tailed, noisy/contaminated-normal AD. | Matches real-world scarce/imbalanced SiC data. ⚠️ General industrial, not SiC. |

### SiC-specific (recent — cite as on-topic SOTA)

- **YOLOv8-Seg + WGAN-GP** — instance segmentation of surface defects on coarsely ground SiC wafers; generative augmentation for rare classes. *Computers, Materials & Continua*, Mar 2026. ⚠️ Published by **Tech Science Press, not Elsevier** despite ScienceDirect hosting; paywalled.
- **YOLO11-OBB + enhanced PL** — basal-plane & other dislocations in 4H-SiC via photoluminescence + oriented bounding boxes + class-balanced sampling. *Materials Science in Semiconductor Processing* (Elsevier), Aug 2025. ⚠️ Paywalled.

### Semiconductor AD benchmarks

- **Evaluating Modern Visual AD in Semiconductor Manufacturing** — comparative benchmark of unsupervised VAD on SEM; **introduces MIIC**. arXiv 2505.07576, 2025. ⚠️ ImageNet-pretrained backbones show a domain gap on SEM.
- **Towards Efficient Wafer Visual Inspection** — lightweight AD + segmentation study. ScienceDirect S2667305325001024.
- **WaferDC** (EAAI 2025) — long-tailed SEM wafer defect detection/classification; PatchCore-style memory bank → heatmaps → SegMix + ViT. ⚠️ Main experiments on a proprietary SEM set.
- **Wafer-map classification via Autoencoder augmentation + CNN** — 98.56% on WM-811K. arXiv 2411.11029, Nov 2024. ⚠️ Preprint; baselines are traditional ML only.

### SiC background (frame as context, not recent SOTA)

- **SCDD-Net** — one-stage SiC crystal-defect detector; SiC-Crystal-5K (5,300+ imgs); 99.53% mAP @102fps. *Knowledge-Based Systems*, 2023. ⚠️ Self-reported on own dataset; crystal/ingot microscopy, not wafer maps.
- **Explainable DL for Si/SiC EWS defect maps** — Mod-AlexNet + SHAP/LIME; ~97%. *IEEE Access*, 2022. ⚠️ The claim it does novel-defect anomaly detection was **refuted** — do not cite that aspect.
- **Wolfspeed/Cree DCNN** — non-destructive extended-defect detection on large-diameter 4H-SiC, validated against synchrotron X-Ray Topography; PL ↔ BPD/TSD/TED. *Materials Science Forum* 1004, 2020. ⚠️ Oldest source; use for SiC dislocation taxonomy.

---

## 3. Code Repositories

| Repo | What | Status / License |
|---|---|---|
| [FoundAD](https://github.com/ymxlzgy/FoundAD) | Foundation-encoder few-shot AD; pretrained MVTec projector (campar.in.tum.de). | Primary build target. |
| [SubspaceAD](https://github.com/CLendering/SubspaceAD) | Training-free few-shot AD. | — |
| [anomalib](https://github.com/openvinotoolkit/anomalib) | Largest SOTA VAD collection (PatchCore, PaDiM, EfficientAd); `pip install anomalib`. | Apache-2.0, ~5.8k★, active. ⚠️ Needs transfer learning for SiC. |
| [WaferDC](https://github.com/SpatialAILab/WaferDC) | PyTorch long-tailed SEM wafer detection/classification. | EAAI 2025. ⚠️ Proprietary SEM data. |
| [TailedCore](https://github.com/jungyg/TailedCore) | Long-tail noisy AD few-shot sampling. | CVPR 2025. |
| [MIIC-IAD](https://github.com/wenbihan/MIIC-IAD) | MIIC dataset + comparative AD benchmark. | Research/non-commercial. |
| [MixedWM38 / WaferMap](https://github.com/Junliangwangdhu/WaferMap) | Dataset + Keras/TF multi-label training. | 133★. ⚠️ TF1-era. |
| [ViT Wafer Defect Recognition](https://github.com/PanithanS/Wafers-Defect-Recognition-using-Visual-Transformer) | ViT multi-label baseline on MixedWM38. | MIT, 48★. ⚠️ 2023 code. |
| [DeepPCB](https://github.com/tangsanli5201/DeepPCB) | PCB template/test pairs. | MIT. |

---

## 4. Datasets

### SiC-specific (scarce — collect / harvest)

- **Zenodo SiC etch-pit set** — DOI `10.5281/zenodo.11229837`. *Primary real SiC source.*
- **NFFA-EUROPE SEM set** — guaranteed-available SEM proxy for path validation.
- **SiC-Crystal-5K** — 5,300+ imgs from SCDD-Net; ⚠️ not public, author-collected.
- **CC-BY figure crops** — PMC8897546 (SiC inspection review, all defect types) and arXiv:2511.08989 (GaN); a few dozen good hand-picked crops.

### Silicon / semiconductor images (primary AD targets)

| Dataset | Modality / Size | Labels | Access |
|---|---|---|---|
| **MIIC** | SEM IC metal layers, 512×512; 25,160 normal + 116 anomalous | Image labels, boxes, pixel masks | [GitHub](https://github.com/wenbihan/MIIC-IAD), non-commercial |
| **300 mm wafer visual inspection** | Current-gen wafer imgs; 1,055 imgs, 6,861 labels | 7 defect types, segmentation, PASS/FAIL | Paper only; public access unclear |
| **Wafer Surface Defect** | Die surface 680×680; 500 imgs | Defect-free + particle/scratch/stain/liquid; YOLO boxes | [IEEE DataPort](https://ieee-dataport.org/documents/wafer-surface-defect) |
| **Semi-AD** | Aligned reference/test pairs (substrate, patterned wafer) | Pixel-wise comparison localization | [IEEE DataPort](https://ieee-dataport.org/documents/semi-ad-semiconductor-anomaly-detection-dataset) |
| **CPS2D-AD** | AOI ceramic IC package substrates; large-scale | 6 defect types; category/mask/box | [GitHub](https://github.com/Bingyang0410/CPS2D-AD) |
| **WaferDC** | SEM wafer defects; long-tailed | Variable backgrounds/scales | [GitHub](https://github.com/SpatialAILab/WaferDC) |
| **IC Cell SEM** | SEM IC cells | Cell-level imagery | [PhysicalDB](https://physicaldb.ece.ufl.edu/index.php/ic-cell-image-dataset-using-sem-imaging/) |

### Wafer maps (classification / yield, not microscope CV)

| Dataset | Size | Labels | Access |
|---|---|---|---|
| **WM-811K / LSWMD** | 811,457 maps (~172,950 labeled) | 9 pattern labels | [Kaggle](https://www.kaggle.com/datasets/qingyi/wm811k-wafer-map) |
| **MixedWM38** | 38,015 maps, 52×52 | 1 normal / 8 single / 29 mixed | [GitHub](https://github.com/Junliangwangdhu/WaferMap) |
| **ST-AWFD (Wafer D1/D2)** | D1: 5,105; D2: 1,157 | Process time-series, step IDs | GitHub / STMicroelectronics |
| **SECOM** | 1,567 × 591 features | Pass/fail (sensor table, not imagery) | [UCI](https://archive.ics.uci.edu/dataset/179/secom) |

### Electronics-adjacent fallbacks

| Dataset | Size | Labels | Access |
|---|---|---|---|
| **DeepPCB** | 1,500 pairs, 640×640 | 6 PCB defect types | [GitHub](https://github.com/tangsanli5201/DeepPCB), MIT |
| **DsPCBSD+** | 10,259 imgs | 9 PCB categories | Scientific Data |
| **PCB-Defect** | 1,386 imgs | 6 classes | Published paper |
| **VisA** | 10,821 imgs (9,621 normal, 1,200 anomaly) | Image + pixel labels | [GitHub](https://github.com/amazon-science/spot-diff) / AWS Open Data |
| **Roboflow chip defect seg** | 2,032 imgs | 9 classes, semantic masks | Roboflow, CC BY 4.0 |
| **MVTec AD** | 5,354 imgs | Normal train, anomalous test, masks | [MVTec](https://www.mvtec.com/research-teaching/datasets/mvtec-ad), CC BY-NC-SA |
| **MVTec AD 2** | 8,000+ imgs | Train + public/private test, masks | [MVTec](https://www.mvtec.com/research-teaching/datasets/mvtec-ad-2), CC BY-NC-SA |
| **MVTec LOCO AD** | 3,644 imgs | Logical + structural masks | [MVTec](https://www.mvtec.com/research-teaching/datasets/mvtec-loco-ad), CC BY-NC-SA |

### Method → dataset fit

| Method family | Best fit |
|---|---|
| FoundAD / SubspaceAD | MIIC, Semi-AD, 300 mm wafer, Wafer Surface Defect, VisA, MVTec |
| EfficientAD | 300 mm wafer, MIIC, MVTec, VisA |
| RAID-style retrieval | Semi-AD, MIIC, DeepPCB, patterned wafer/substrate |
| UniSpector / AA-CLIP / MultiADS (naming, open-set) | Wafer Surface Defect, CPS2D-AD, Roboflow chip, VisA, MVTec |
| DefectFill / SeaS (synthesis) | MIIC, Wafer Surface Defect, CPS2D-AD, DeepPCB |
| Supervised seg/det (UPerNet-Swin, SegFormer, YOLO-seg) | Wafer Surface Defect, 300 mm wafer, CPS2D-AD, Roboflow chip |
| CNN / TinyViT / graph (wafer maps) | WM-811K, MixedWM38 |

---

## 5. 24-Hour Execution Plan

**Backbone:** DINOv3 (`facebook/dinov3-vitb16-pretrain-lvd1689m`) is now primary, not a stretch ablation.

### H0–1 — Pre-flight (all four, together)
Spin up H100/H200 → clone FoundAD → `conda create -n foundad python=3.10` → `pip install -r requirements.txt && pip install -e .`. Download DINOv3 weights + the FoundAD MVTec projector. Run the MVTec demo from the README. **M0 = a heatmap renders. Until you see this, you have no project.** Kick off background downloads (Zenodo etch-pit, NFFA SEM; MVTec/VisA as safety net). Agree the integration contract: every module reads/writes a common folder of **448px tiles** + a JSON of `{tile, anomaly_score, heatmap_path, label, novelty_flag}`.

### Swimlanes
- **Lane A — Data (most time-critical):** tile the Zenodo etch-pit images, grayscale→3-channel, CLAHE-enhanced. Harvest CC-BY crops from PMC8897546 + arXiv:2511.08989. Build a tiny classical synthesizer for etch-pit/PL patterns to pad the normal pool. Deliver few-shot reference sets + normal pools per modality. **M1 by H6.**
- **Lane B — Core model:** validate on NFFA SEM first (guaranteed data) — train a DINOv3 projector (`app=train_dinov3`, layer ~10, ViT-6 projector, 448px, patch-16), then swap in real SiC tiles. Produce heatmaps + few-shot AUROC table + the **DINOv3-vs-CLIP-vs-SigLIP ablation** (this is what makes it read as research). **M2 by H14.**
- **Lane C — Naming + open-set:** CLIP/SigLIP zero-shot head over a defect prompt set (basal-plane dislocation, threading screw dislocation etch pit, micropipe, triangular epitaxial defect, stacking fault, scratch). Open-set flag = high manifold residual + low max-CLIP-similarity → "⚠ unknown defect." **M3 by H16.**
- **Lane D — Demo + pitch (start H8):** see below.

### The demo (where "good-looking" is won)
Gradio, dark technical theme. The hero artifact is a **full-wafer defect map** — tile a stitched/synthetic wafer, score every tile, render a wafer-shaped heatmap with hot spots (mimics SICA/KLA output).
1. Input panel with 4–6 **pre-loaded** example images (never depend on a live upload).
2. Money shot: raw image + DINOv3 off-manifold heatmap overlay, before/after slider, clean colormap; full-wafer aggregate map above it.
3. Detections: labeled contours per dislocation/pit with type + confidence (Lane C).
4. Verdict panel: big **PASS / KILL** badge, defect count, live ROI counter (wafers screened × ~$50/wafer saved, anchored to Resonac's figure).
5. "Why it works" tab: DINOv3 vs CLIP heatmaps side by side.

Pre-render everything for the demo images; record a screen capture as backup before presenting.

### Milestones
`H0–1` pre-flight + M0 · `H1–6` Lane A data / Lane B SEM path → M1 · `H6–14` Lane B real SiC + ablation, Lane C naming → M2 · `H8–20` Lane D app + wafer map + deck · `H14–16` M3 · `H16–22` integrate localizer→namer→open-set→verdict, rehearse · `H22–24` buffer, record backup, freeze slides.

### Guardrails (honest pivots)
- FoundAD not running by **H2** → stop everything, debug environment/CUDA first.
- No usable real SiC data by **H6** → commit to the proxy-led story: demo on SEM + MVTec + the etch-pit crops you have; frame SiC as the motivating application.
- Cross-modality transfer clearly failing by **~H12** (AUROC near chance, uninformative maps — likely on low-contrast PL dislocation lines) → pivot headline to *"we mapped where foundation-encoder AD breaks on physics-based imagery."* Still a legitimate, fundable result. Don't overclaim a win you don't have.

---

## 6. Caveats & Open Questions

**Handle carefully in the pitch:**
- Most ScienceDirect/IEEE papers are paywalled — verified via abstracts/titles, not full text.
- Headline numbers (SCDD-Net 99.53% mAP, 98.56% on WM-811K) are self-reported on private/own datasets, not independently reproduced.
- anomalib / TailedCore are general-purpose; SiC's PL / SEM / X-ray modalities carry a documented ImageNet-pretraining domain gap.

**Open questions:**
- Any *public* SiC-specific defect dataset (analogous to WM-811K), or is the field still on proprietary fab data + self-collected sets like SiC-Crystal-5K?
- How well do general unsupervised AD methods (PatchCore / anomalib / TailedCore) transfer to SiC modalities given the domain gap?
- Any 2025–2026 SiC work on full-wafer defect *maps* (not just crystal microscopy / single-defect crops) or real-time inline fab integration?
- Most defensible accuracy/throughput baseline to cite, given the self-reported numbers?
