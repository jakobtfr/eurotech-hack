# Dataset Download Status

This file records the local download status of the datasets listed in
`datasets/links.md`.

## Public Downloads

| Dataset | Status | Local path | Notes |
|---|---|---|---|
| MIIC | Manual download required | `datasets/miic/` | Automatic download was stopped and all partial MIIC files were removed. |
| Zenodo SiC supplementary material | Downloaded and checksum verified | `datasets/zenodo_sic/` | The Zenodo record contains only a one-page `content.pdf`, not image data. |
| NFFA-EUROPE SEM | Downloaded, all checksums verified, and extracted | `datasets/nffa_europe_sem/` | Ten categories and 18,577 extracted files; original TAR files retained. |
| VisA | Downloaded, size checked, archive verified, and extracted | `datasets/visa/` | Contains 12,037 extracted files plus the original TAR. |
| DeepPCB | Downloaded and repository commit recorded | `datasets/deep_pcb/` | Commit `08e98c4`; includes `PCBData`. |
| CPS2D-AD | Public partial dataset downloaded, verified, and extracted | `datasets/cps2d_ad/` | Repository commit `047e610`; authors currently expose only a partial dataset. |
| Carinthia semiconductor SEM defects | Downloaded, checksums verified, and extracted | `datasets/carinthia_sem/` | 4,591 grayscale SEM images from real semiconductor wafers across six anonymized defect classes; CC BY 4.0. Best immediately available substitute for MIIC defect-domain transfer, but not SiC-specific. |
| MeiweiPCB | Downloaded, archives verified, and extracted | `datasets/meiwei_pcb/` | Commit `c19045c`; 969 defective images, 969 corresponding normal references, 926 pixel masks, and detection annotations. |
| RobustAD PCB subset | Downloaded and file count verified | `datasets/robustad_pcb/` | Only the PCB category was selected: 1,747 payload files, including 780 normal images, 480 anomaly images, and 480 masks across multiple test conditions. |
| MixedWM38 / WaferMap | Downloaded, verified, and extracted | `datasets/mixedwm38_wafermap/` | Repository commit `10e65ca`; Kaggle archive contains `Wafer_Map_Datasets.npz`. |
| SECOM | Downloaded, extracted, and archive verified | `datasets/secom/` | Contains data, labels, names, and the original ZIP. |
| Wafer Defect Roboflow/Kaggle substitute | Downloaded, archive verified, and extracted | `datasets/wafer_defect_roboflow/` | 4,531 images and matching segmentation labels across seven class IDs. The included `dataV2.yaml` is inconsistent with the labels and must not be used without correction. Kaggle marks the package CC BY-NC-SA 4.0. |

## Manual-Access Downloads

| Dataset | Status | Local path | Notes |
|---|---|---|---|
| MVTec AD | Downloaded | `datasets/MVTec AD/` | 6,644 local files. |
| MVTec AD 2 | Manual access required | `datasets/mvtec_ad_2/` | Requires accepting the provider's access conditions. |
| MVTec LOCO AD | Downloaded | `datasets/MVTec LOCO AD/` | 4,920 local files. |
| WM-811K / LSWMD | Downloaded, verified, extracted, and split for Git LFS | `datasets/wm811k/` | The original `LSWMD.pkl` was split byte-for-byte into two parts below GitHub's 2 GB LFS limit. Reconstruction instructions and checksums are in `datasets/wm811k/data/LSWMD_parts/README.md`. |
| Wafer Surface Defect | Account or manual access required | `datasets/wafer_surface_defect/` | IEEE DataPort access. |
| Semi-AD | Account or manual access required | `datasets/semi_ad/` | IEEE DataPort access. The supplied dataset readme is preserved at `datasets/semi_ad_dataset_readme.pdf`. |
| IC Cell SEM | Downloaded from public directory index | `datasets/ic_cell_sem/` | Preserved the provider's directory structure; 402 files downloaded. |
