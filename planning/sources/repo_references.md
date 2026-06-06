# Upstream Repository References

These repositories are not vendored in this project. Clone or cache them
outside the repo when implementation work needs upstream code, then wrap any
outputs behind the local artifact contracts.

| Repository | URL | Pinned commit | Role | License status |
|---|---|---:|---|---|
| SubspaceAD | https://github.com/CLendering/SubspaceAD | `4190506772884efa711512b7aeadd3b4e7928c52` | Primary baseline reference | Apache-2.0 license file observed |
| FoundAD | https://github.com/ymxlzgy/FoundAD | `a590587d96184249eeb59e403cf06dc097fdf347` | Stretch research comparison | No license file observed in checkout |
| TailedCore | https://github.com/jungyg/TailedCore | `7240f04b489fb3d068919e3953cef0ced919a3f8` | Background reference | No license file observed in checkout |
| WaferDC | https://github.com/SpatialAILab/WaferDC | `2b185c2fcc5128227ae6402036c779cdc823d68f` | Wafer defect reference | CC BY-NC-SA 4.0 license file observed |
| WaferMap | https://github.com/Junliangwangdhu/WaferMap | `10e65ca04cf105908cb87abec53c3083333b1bc9` | Wafer-map reference | No license file observed in checkout |
| Wafers Defect Recognition using Visual Transformer | https://github.com/PanithanS/Wafers-Defect-Recognition-using-Visual-Transformer | `d54c4a2787779483755cd7c27094feaa91f29585` | Wafer classification reference | MIT license file observed |
| awesome-industrial-anomaly-detection | https://github.com/M-3LAB/awesome-industrial-anomaly-detection | `79e113227d50405f06a5e8d26d7abf212c363aee` | Literature and repo index | No license file observed in checkout |

Notes:

- Commit hashes are from the former gitlink entries removed on 2026-06-06.
- License status here is a quick local observation, not legal approval for demo
  or redistribution.
- SubspaceAD remains the first implementation target. FoundAD is attempted only
  after the baseline pipeline and demo artifact contract are working.
