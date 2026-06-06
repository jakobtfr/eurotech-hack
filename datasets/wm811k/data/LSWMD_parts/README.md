# Reconstructing LSWMD.pkl

`LSWMD.pkl` was split into Git LFS-compatible binary parts because the original
file is larger than GitHub's 2 GB per-file LFS limit.

Reconstruct it from the repository root:

```bash
cat datasets/wm811k/data/LSWMD_parts/LSWMD.pkl.part-* \
  > datasets/wm811k/data/LSWMD.pkl
```

Verify the reconstructed file:

```bash
shasum -a 256 datasets/wm811k/data/LSWMD.pkl
```

Expected SHA-256:

```text
1d04fccb3dd3176b276878b926b20fead7e077c5751e4d353ea9741a5e7b5c65
```

Part checksums:

```text
a794611686e86f1cc26e1539bf2caadcee24928fa1c7131894442e88a2b63361  LSWMD.pkl.part-000
801a337a2ea41bb0047ab546c9d77d3c7eae12642ea9237e1c4c3a1f653a7d14  LSWMD.pkl.part-001
```
