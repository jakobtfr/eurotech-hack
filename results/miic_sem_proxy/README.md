# MIIC Semiconductor SEM Proxy Results

Resultados visibles del run `runs/20260606T193603Z_dinov2_pca_baseline_v1_k16_seed17`
(la carpeta `runs/` está en `.gitignore`, por eso estos resultados se exportan aquí).

**Dataset:** MIIC — imágenes SEM reales de circuitos integrados (semiconductor).
**Modelo:** DINOv2 ViT-S/14 (frozen) + PCA-residual, few-shot (k=16 normales), sin entrenamiento.

## Métricas (`metrics.json`)

| Métrica | Valor |
|---|---|
| Image AUROC | **0.879** |
| Image AUPR | 0.763 |
| Pixel AUROC | `null` (MIIC no trae máscaras de ground-truth) |
| Test | 463 imágenes (347 normales + 116 anómalas) |

## Cómo leer las imágenes

Cada panel es un **triptych**: `original | heatmap | overlay`.
- **heatmap**: azul = normal, amarillo/rojo = residual alto (anómalo).
- **overlay**: la imagen original con el heatmap encima → el rojo marca el defecto.

## Carpetas

- `anomaly_comparisons/` — los **116** casos anómalos, ordenados por score (`001` = más anómalo).
- `normal_comparisons/` — 8 normales de muestra (deberían salir limpios, sin highlight).
- `gallery_top_anomalies.png` — montaje con las 16 anomalías de mayor score (vista rápida).

## Nota honesta sobre la localización

La detección a nivel de imagen es sólida (AUROC 0.88). La localización pixel-a-pixel
es **cualitativa** (sin máscaras no se puede medir): en muchos casos el rojo cae sobre
el defecto real, pero a veces resalta una estructura de layout poco frecuente que no
estaba entre los 16 tiles de soporte. Para afinar: más shots (k=64+), normalización
por imagen en el overlay, o CLAHE en el preprocess.

## Additional model comparisons

- `cfa/`: CFA metrics and representative heatmaps. CFA is the strongest MIIC
  image-level model in this result package.
- `draem/`: DRAEM metrics and representative heatmaps.
- `../judge_evidence/miic_reliability_evidence.png`: confusion matrix,
  precision-recall curve, score separation, and review-policy evidence.

Regenerate the DINOv2/PCA examples with:
`uv run python scripts/export_miic_results.py`
