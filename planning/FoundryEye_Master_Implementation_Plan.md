# FoundryEye — Master Implementation Plan (Ultimate / Concise)

**What:** open, few-shot, open-vocabulary, open-set SiC wafer-defect inspection. **Stack:** DINOv3 (frozen) + FoundAD manifold-residual AD + CLIP/SigLIP naming + open-set gate + full-wafer aggregate map. **Resources:** 4 researchers, 1× H100/H200, 24 h.

**Win conditions (decide which at H14 from M2):**
- **A — transfer works:** "open few-shot SiC inspection rivaling closed tools, on one GPU."
- **B — partial fail:** "first map of where foundation-encoder AD breaks on SiC physics + the open benchmark to fix it."
Both first-mover, both fundable, both honest.

**Hypothesis (falsifiable):** a frozen natural-image encoder (DINOv3) + a tiny manifold-projection head fitted on a *handful of defect-free SiC tiles* yields anomaly heatmaps with image-AUROC ≫ chance and localization competitive with ImageNet AD baselines, **with no SiC pre-training.** Tested via an encoder ablation (DINOv3 vs DINOv2/CLIP/SigLIP) — the ablation *is* the result.

---

## 4 non-negotiable correctness rules
1. **DINOv3 is gated** (Meta approval can take *days*). Request access **now**. Fallback = **DINOv2 (Apache, un-gated)**; FoundAD has `train_dinov2`/`test_dinov2`. Frame as "DINOv2/v3 family" if needed.
2. **The pretrained MVTec projector is NOT a SiC model** — M0 sanity only. For SiC you **train your own** projector on SiC normals (`mode=train`).
3. **Split by source image, not by tile** — no wafer contributes tiles to both train and test. Assert it in code.
4. **Multi-seed only** ({42,43,44}); report mean±std + bootstrap CI. Single-seed few-shot numbers are not presentable.

---

## Architecture + the contract
```
raw wafer ─▶ TILE 448px/stride384 + CLAHE ─▶ DINOv3 (frozen, ViT-B/16, layer n) ─▶ 28×28 patch tokens
        ─▶ FoundAD projector (few-shot ViT) ─▶ residual heatmap + anomaly_score
        ─▶ CLIP/SigLIP namer + open-set gate ─▶ {label, novelty_flag}
        ─▶ reassemble tiles ─▶ wafer heatmap ─▶ PASS/KILL + defect count + ROI$
```
**Integration contract** — one JSON row per tile (+ `index.parquet`); every lane reads/writes only this:
```json
{"tile_id":"w07_x12_y08","source_image":"w07.png","tile_bbox":[x0,y0,x1,y1],"modality":"PL",
 "encoder":"dinov3_vitb16","projector_ckpt":"sic_pl_s42@1950","anomaly_score":0.87,
 "heatmap_path":"...","pred_label":"bpd","label_confidence":0.62,"max_clip_similarity":0.31,
 "novelty_flag":false,"gt_label":null,"gt_mask_path":null,"seed":42}
```
Rules: `anomaly_score` normalized [0,1] per `(encoder,ckpt)` via train-normal min/max; heatmaps = 448×448 float PNG; `gt_*` null if absent.

---

## Lanes (owner · deliverable · milestone)
| Lane | Owner | Deliverable | Milestone |
|---|---|---|---|
| **A — Data** | R1 | tiled, license-clean bank + few-shot sets + data card + `index.parquet` | **M1 @ H6** |
| **B — Model** | R2 | SiC heatmaps + headline ablation table (mean±std) | **M2 @ H14** |
| **C — Naming/open-set** | R3 | CLIP/SigLIP labels + calibrated novelty gate in JSON | **M3 @ H16** |
| **D — Demo/pitch** | R4 | Gradio app (wafer map + verdict) + deck + backup video | by H22 |

Lane B validates the full path on **proxy data (NFFA SEM / MIIC)** before SiC tiles exist; when SiC lands, only `data.test_root` changes.

---

## Exact build sequence (the precise core)

### Phase 0 — H0 setup + M0 gate
```bash
conda create -n foundad python=3.10 -y && conda activate foundad
git clone https://github.com/ymxlzgy/FoundAD && cd FoundAD
pip install -r requirements.txt && pip install -e .
pip install anomalib open_clip_torch opencv-python-headless pyarrow gradio
huggingface-cli login                      # DINOv3 access requested NOW
# download pretrained MVTec projector → ./logs/   (M0 only)
python foundad/main.py mode=demo app=test testing.segmentation_vis=True \
  data.dataset=mvtec data.data_name=mvtec_1shot data.test_root=assets/mvtec
```
**Gate: a heatmap must render by H2, else all-hands debug env/CUDA/DINOv3.** Also smoke-test `anomalib` EfficientAD on one MVTec class.

### Phase 1 — data → tiles → few-shot (Lane A)
```bash
python src/tiling.py --src <raw> --out /data/sic/sic_pl --size 448 --stride 384 \
  --gray2rgb --clahe --drop-empty           # log dropped tiles
# coerce to MVTec layout:  sic_pl/train/good  sic_pl/test/{good,<defect>}  sic_pl/ground_truth/<defect>
python foundad/src/sample.py source=/data/sic/sic_pl target=/data/fewshot/sic_pl_seed42 seed=42 num_samples=4
python foundad/src/sample.py source=/data/sic/sic_pl target=/data/fewshot/sic_pl_seed43 seed=43 num_samples=4
python foundad/src/sample.py source=/data/sic/sic_pl target=/data/fewshot/sic_pl_seed44 seed=44 num_samples=4
```

### Phase 2 — train SiC projector (Lane B; run on proxy first, identical cmd)
```bash
python foundad/main.py mode=train data.batch_size=8 data.dataset=mvtec \
  data.data_name=sic_pl_seed42 data.data_path=/data/fewshot \
  app=train_dinov3 app.meta.n_layer=10 diy_name=sic_pl_s42
```

### Phase 3 — inference + heatmaps
```bash
python foundad/main.py mode=AD data.dataset=mvtec data.data_name=sic_pl_seed42 \
  diy_name=sic_pl_s42 data.test_root=/data/sic/sic_pl \
  app=test_dinov3 app.ckpt_step=<your_saved_step> testing.K_top_mvtec=10 testing.segmentation_vis=True
```

### Phase 4 — encoder ablation
Repeat Phases 2–3 with `app=train_dinov2 | train_clip | train_siglip` (+ paired `test_*`). Hold seed/layer/K/tiles fixed. Add `anomalib` EfficientAD + PatchCore as ImageNet references; SubspaceAD as training-free control *(confirm its arXiv ID/repo at H0)*.

### Phase 5 — naming, open-set, wafer map, app (Lanes C/D)
- **Namer:** crop each above-threshold region → CLIP/SigLIP zero-shot vs prompt set → `pred_label`, `label_confidence`, `max_clip_similarity`.
- **Open-set gate:** `novelty_flag = (anomaly_score ≥ τ_anom) AND (max_clip_similarity ≤ τ_sim)` → "⚠ unknown defect"; calibrate τ on validation (Youden J).
- **Wafer aggregate (`src/wafer_aggregate.py`):** tile → score → paste each heatmap at `tile_bbox`, **average overlaps** → apply circular wafer+notch mask → threshold → contours, defect count, defects/cm². *(Mirrors real fab practice: XY-stage frame capture → per-frame classify → map to coords.)*

**Naming prompt set:** BPD line · TSD etch pit · TED etch pit · micropipe · triangular stacking fault · carrot defect · scratch · particle · stain/residue · "normal SiC surface" (null).

---

## Experimental protocol
**Metrics:** image **AUROC + AUPR** (imbalance), pixel **AUROC + AUPRO** (size-fair), **F1-max** + confusion matrix, **throughput** (tiles/s, per-wafer latency) + projector param count.

**Headline table** (each cell = mean±std over {42,43,44}, +bootstrap CI on AUROC):
| Frozen encoder | MIIC SEM (proxy) | SiC etch-pit | SiC PL (BPD-hard) |
|---|---|---|---|
| **DINOv3 ViT-B/16** | | | |
| DINOv2 ViT-B/14 | | | |
| CLIP ViT-B | | | |
| SigLIP | | | |
| EfficientAD (ImageNet ref) | | | |
| PatchCore (ImageNet ref) | | | |
| SubspaceAD (training-free ctrl) | | | |

**Sweeps:** few-shot K∈{1,2,4,8} (the "how little data" curve — pitch gold); layer n∈{6,9,11} (fix on proxy); CLAHE on/off; stride. **Reproducibility:** pinned `environment.yml`, frozen Hydra configs, all seeds, FoundAD commit hash, `index.parquet`.

---

## Timeline (H0–H24)
| H | A | B | C | D | Milestone |
|---|---|---|---|---|---|
| 0–1 | preflight, downloads | M0 demo | prompt set | — | **M0 heatmap** |
| 1–6 | tile SiC + synth + card | proxy (SEM/MIIC) path | build namer | — | **M1 tiles** |
| 6–14 | feed SiC to B | SiC heatmaps + ablation + refs | — | start app + wafer map | **M2 table** |
| 8–20 | — | K/layer/CLAHE sweeps | calibrate gate | Gradio + deck | — |
| 14–16 | — | freeze numbers | — | — | **M3 naming/open-set** |
| 16–22 | **all-hands integrate** → rehearse | | | | integrated demo |
| 22–24 | buffer · record backup · freeze · slides | | | | **ship** |

---

## Risk → pivot
| Risk | Trigger | Pivot |
|---|---|---|
| DINOv3 access late | no HF email by H0 | use **DINOv2** backbone |
| env/CUDA broken | M0 fails @H2 | hard-gate all-hands debug |
| no SiC data @H6 | Lane A blocked | **proxy-led story**: SEM+MVTec+crops, SiC = motivation |
| transfer fails @~H12 | maps near chance (low-contrast PL) | **headline = "where AD breaks"** (win-condition B); don't overclaim |
| numbers too noisy | std swamps mean | already covered: ≥3 seeds + CI; report honestly |
| live demo dies | upload/GPU hiccup | **prerender all assets + backup video + curated gallery** (no live-upload dependency) |
| license overclaim | jury IP question | data card splits commercial/NC; MVTec=CC-BY-NC-SA, DINOv3=research license; say "open code + research weights" |

---

## Demo + pitch
**Gradio (dark theme):** curated 4–6-image gallery (no live upload) · money shot = raw+heatmap before/after slider with full-wafer map above · labeled detections (type+confidence) · big **PASS/KILL** + defect count + **live ROI counter** · "why it works" tab = DINOv3-vs-CLIP heatmaps side by side. **Prerender everything; record a backup capture.**
**ROI:** wafers × per-wafer saving — anchor per-wafer $ to a **cited published figure** (Resonac, per notes — verify on slide), state assumptions; sourced + bounded beats a hero number.
**Deck (8):** opportunity (HK 3rd-gen push) → gap (no public SiC benchmark) → insight (FoundAD survives wafer physics?) → system → money shot → evidence (table + K-curve) → why us/now → ask+roadmap. If result is B, swap slide 3–6 to the "where it breaks + open benchmark" story.

---

## Data sources (verify links @H0)
**SiC (harvest early):** Zenodo etch-pit `10.5281/zenodo.11229837` (verify resolves) · NFFA-EUROPE SEM (proxy, guaranteed) · CC-BY crops PMC8897546 + arXiv:2511.08989 · classical synthesizer. *(SiC-Crystal-5K = author-private, cite only.)*
**Proxy/benchmark:** MIIC (github.com/wenbihan/MIIC-IAD; arXiv:2505.07576) · Wafer Surface Defect (IEEE DataPort) · Semi-AD · VisA · MVTec AD/AD2/LOCO (NC) · DeepPCB (MIT).
**Out of scope (electrical grids, not imagery):** WM-811K, MixedWM38, SECOM.
**Code/papers:** FoundAD github.com/ymxlzgy/FoundAD (arXiv:2510.01934, ICLR’26) · DINOv3 `facebook/dinov3-vitb16-pretrain-lvd1689m` (gated) + github.com/facebookresearch/dinov3 · anomalib (Apache) · WaferDC (EAAI’25) · TailedCore (CVPR’25, arXiv:2504.02775) · DefectFill (arXiv:2503.13985). SiC background: SCDD-Net (KBS’23), Wolfspeed/Cree DCNN+XRT (MSF 1004, ’20, taxonomy), YOLO11-OBB+PL (’25).

---

## Definition of done
M0–M3 green · headline ablation table (mean±std+CI) in `REPORT.md` · K-curve + CLAHE/layer sweeps · offline Gradio app (wafer map + PASS/KILL + ROI + detections + open-set + DINOv3-vs-CLIP panel) · backup video · 8-slide deck (honest to the result) · data card + pinned env + frozen configs.
