# Public Substitutes for Semi-AD

## What Semi-AD Provides

The supplied Semi-AD readme, preserved locally as
`datasets/semi_ad_dataset_readme.pdf`, describes an unsupervised,
comparison-based semiconductor inspection benchmark with two complementary
formats:

- `pair_set`: aligned normal-reference and test-image pairs.
- `single_set`: normal training images, normal and defective test images, and
  pixel-level ground-truth masks.
- Semiconductor domains: IC substrate ball side, IC substrate chip side, and
  patterned wafer.

No public dataset identified here is an exact replacement for all three
domains and both formats. The following combination is the closest practical
public substitute.

## Recommended Dataset Suite

| Priority | Dataset | Best use | Similarity to Semi-AD | Main limitation |
|---|---|---|---|---|
| 1 | MeiweiPCB | Comparison-based training and pixel localization | Defective PCB images have corresponding normal reference images; pixel masks are supplied | PCB rather than wafer or IC substrate; the public release is incomplete |
| 2 | DeepPCB | Aligned reference/test comparison | Contains 1,500 aligned template/test PCB pairs | Uses bounding boxes instead of pixel masks |
| 3 | CPS2D-AD | Semiconductor-substrate anomaly localization | IC package substrate imagery with pixel and box annotations | Only a partial public release; not organized as aligned pairs |
| 4 | VisA PCB categories | Standard unsupervised anomaly detection | Normal training images, anomalous tests, and masks for four PCB categories | PCB rather than semiconductor wafer/substrate |
| 5 | RobustAD PCB subset | Robustness evaluation | Normal/anomaly PCB images and masks under multiple test conditions | Not comparison-paired and less semiconductor-specific |

## Recommended Experimental Mapping

- Use **MeiweiPCB** and **DeepPCB** to implement and evaluate the
  reference-versus-test branch corresponding to Semi-AD's `pair_set`.
- Use **CPS2D-AD** as the most domain-relevant public semiconductor evaluation
  set.
- Use **VisA PCB** for the standard `single_set` anomaly-detection protocol.
- Use **RobustAD PCB** only as an additional robustness/generalization test.
- Report results separately per dataset. Do not merge their test sets or claim
  that they reproduce the official Semi-AD benchmark.

None of these datasets is specifically a silicon-carbide dataset.
