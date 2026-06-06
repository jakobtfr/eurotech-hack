# Azure ML Training

Azure is used for GPU training/scoring; the dataset laptop is only the staging
machine that uploads the prepared dataset asset.

## One-time Azure setup

```bash
az login
az account set --subscription "<subscription-id>"
az extension add --name ml --upgrade --yes

az group create --name eurotech-hack-rg --location francecentral
az ml workspace create \
  --name eurotech-hack-ml-fr \
  --resource-group eurotech-hack-rg \
  --location francecentral
az configure --defaults group=eurotech-hack-rg workspace=eurotech-hack-ml-fr

az ml compute create -f cloud/azureml/cpu_compute.yml
az ml compute create -f cloud/azureml/gpu_compute.yml
```

Both compute clusters have `min_instances: 0`; they should not run until a job
is submitted.

The GPU cluster uses `Standard_NV6s_v2` because this subscription already has
quota for the `standardNVFamily` in France Central. The earlier T4 route was
blocked by `Standard NCASv3_T4 Family` quota being 0.

## Dataset laptop

Clone this repo on the laptop that has the datasets, then run:

```bash
az login
az account set --subscription "<subscription-id>"
az configure --defaults group=eurotech-hack-rg workspace=eurotech-hack-ml-fr

./cloud/azureml/prepare_dataset_asset.sh \
  --dataset-root /path/to/datasets_ready \
  --min-rows 100
```

That scans the dataset folders, writes generated registry/config/split artifacts
inside `/path/to/datasets_ready`, creates
`/path/to/datasets_ready/splits/combined_no_miic.csv`, rewrites image paths
relative to `/path/to/datasets_ready`, excludes `miic`, and registers the folder
as `azureml:eurotech-hack-datasets-ready:<version>`.

Expected dataset layout:

```text
datasets_ready/
  cps2d_ad/
  deep_pcb/
  mixedwm38/
  mvtec_ad/
  mvtec_loco/
  nffa_sem/
  semi_ad/
  visa/
  zenodo_sic/
  configs/
  registry/
  splits/
    combined_no_miic.csv
```

The scanner labels images from path names. It recognizes common benchmark
folders such as `normal`, `good`, `anomaly`, `defect`, and MVTec-style
`test/<defect-type>`. Images without an inferable label are skipped unless
`scripts/prepare_training_dataset.py --unknown-label normal` is used for a
qualitative normal-only set.

## Local GPU run

On a machine with the datasets and a working PyTorch/DINOv2 environment:

```bash
uv sync --extra dinov2
uv run python scripts/prepare_training_dataset.py \
  --dataset-root /path/to/datasets_ready \
  --min-rows 100

./scripts/train_dinov2_pca.sh \
  --split /path/to/datasets_ready/splits/combined_no_miic.csv \
  --data-root /path/to/datasets_ready \
  --shots 1 \
  --seed 17
```

The local runner writes a frozen `runs/<run_id>` directory in the repo checkout.

## Submit training

After the data asset exists:

```bash
az ml job create -f cloud/azureml/train_dinov2_pca.yml
```

The job mounts the data asset, runs `configs/models/dinov2_pca.yaml`, then
calibrates, evaluates, renders, freezes, validates, and writes `runs/<run_id>`
to the Azure job output.
