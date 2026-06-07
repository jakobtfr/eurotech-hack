#!/usr/bin/env python3
"""Train an efficient, lot-disjoint WM-811K wafer-map classifier."""

from __future__ import annotations

import argparse
import json
import pickle
import random
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas.core.indexes as core_indexes
import pandas.core.indexes.base as indexes_base
import pandas.core.indexes.range as indexes_range
import torch
from PIL import Image
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedGroupKFold
from torch import nn
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

CLASS_NAMES = ["none", "Center", "Donut", "Edge-Loc", "Edge-Ring", "Loc", "Near-full", "Random", "Scratch"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="datasets/wm811k/data/LSWMD.pkl")
    parser.add_argument("--output", default="wm811k_results")
    parser.add_argument("--image-size", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--samples-per-epoch", type=int, default=60000)
    parser.add_argument("--seed", type=int, default=17)
    return parser.parse_args()


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def save_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_legacy_pickle(path: Path) -> pd.DataFrame:
    # WM-811K was serialized with an old pandas version.
    sys.modules["pandas.indexes"] = core_indexes
    sys.modules["pandas.indexes.base"] = indexes_base
    sys.modules["pandas.indexes.range"] = indexes_range
    with path.open("rb") as handle:
        return pickle.load(handle, encoding="latin1")


def scalar(value: object) -> str:
    while isinstance(value, (list, tuple, np.ndarray)):
        array = np.asarray(value, dtype=object)
        if array.size == 0:
            return ""
        value = array.flat[0]
    return str(value)


def build_cache(df: pd.DataFrame, output: Path, image_size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cache = output / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    maps_path = cache / f"maps_{image_size}.npy"
    labels_path = cache / "labels.npy"
    groups_path = cache / "lot_groups.npy"

    labels_text = np.asarray([scalar(value) for value in df["failureType"]], dtype=object)
    labeled_rows = np.flatnonzero(np.isin(labels_text, CLASS_NAMES))
    labels = np.asarray([CLASS_NAMES.index(labels_text[index]) for index in labeled_rows], dtype=np.int64)
    groups = np.asarray([str(df.iloc[index]["lotName"]) for index in labeled_rows], dtype="U32")

    if maps_path.exists() and labels_path.exists() and groups_path.exists():
        maps = np.load(maps_path, mmap_mode="r")
        cached_labels = np.load(labels_path)
        cached_groups = np.load(groups_path)
        if len(maps) == len(labels) == len(cached_labels) == len(cached_groups):
            return maps, cached_labels, cached_groups

    maps = np.lib.format.open_memmap(
        maps_path, mode="w+", dtype=np.uint8, shape=(len(labeled_rows), image_size, image_size)
    )
    for position, row_index in enumerate(labeled_rows):
        wafer = np.asarray(df.iloc[row_index]["waferMap"], dtype=np.uint8)
        maps[position] = np.asarray(
            Image.fromarray(wafer).resize((image_size, image_size), Image.Resampling.NEAREST), dtype=np.uint8
        )
        if position and position % 25000 == 0:
            print(f"cached {position}/{len(labeled_rows)} maps", flush=True)
    maps.flush()
    np.save(labels_path, labels)
    np.save(groups_path, groups)
    return np.load(maps_path, mmap_mode="r"), labels, groups


def make_splits(labels: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    indices = np.arange(len(labels))
    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    train_val, test = next(outer.split(indices, labels, groups))
    inner = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed + 1)
    inner_train, inner_val = next(inner.split(train_val, labels[train_val], groups[train_val]))
    train = train_val[inner_train]
    val = train_val[inner_val]
    return train, val, test


class WaferDataset(Dataset):
    def __init__(self, maps: np.ndarray, labels: np.ndarray, indices: np.ndarray, augment: bool) -> None:
        self.maps = maps
        self.labels = labels
        self.indices = indices
        self.augment = augment

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, position: int) -> tuple[torch.Tensor, torch.Tensor]:
        index = int(self.indices[position])
        wafer = np.array(self.maps[index], copy=True)
        if self.augment:
            wafer = np.rot90(wafer, random.randrange(4)).copy()
            if random.random() < 0.5:
                wafer = np.fliplr(wafer).copy()
            if random.random() < 0.5:
                wafer = np.flipud(wafer).copy()
        channels = np.stack([wafer == 0, wafer == 1, wafer == 2]).astype(np.float32)
        return torch.from_numpy(channels), torch.tensor(int(self.labels[index]), dtype=torch.long)


class WaferCNN(nn.Module):
    def __init__(self, classes: int) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(0.25), nn.Linear(128, classes))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(inputs))


def predict(
    model: nn.Module, loader: DataLoader, device: torch.device, loss_fn: nn.Module
) -> tuple[float, np.ndarray, np.ndarray]:
    model.eval()
    losses: list[float] = []
    truth: list[np.ndarray] = []
    predicted: list[np.ndarray] = []
    with torch.inference_mode():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            logits = model(inputs)
            losses.append(float(loss_fn(logits, labels).item()))
            truth.append(labels.cpu().numpy())
            predicted.append(logits.argmax(1).cpu().numpy())
    return float(np.mean(losses)), np.concatenate(truth), np.concatenate(predicted)


def metric_summary(truth: np.ndarray, predicted: np.ndarray) -> dict[str, object]:
    defect_truth = truth != 0
    defect_predicted = predicted != 0
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, labels=np.arange(len(CLASS_NAMES)), zero_division=0
    )
    return {
        "accuracy": round(float(accuracy_score(truth, predicted)), 6),
        "balanced_accuracy": round(float(balanced_accuracy_score(truth, predicted)), 6),
        "macro_f1": round(float(f1_score(truth, predicted, average="macro")), 6),
        "weighted_f1": round(float(f1_score(truth, predicted, average="weighted")), 6),
        "binary_normal_vs_defect": {
            "accuracy": round(float(accuracy_score(defect_truth, defect_predicted)), 6),
            "balanced_accuracy": round(float(balanced_accuracy_score(defect_truth, defect_predicted)), 6),
            "f1": round(float(f1_score(defect_truth, defect_predicted)), 6),
        },
        "per_class": {
            name: {
                "precision": round(float(precision[index]), 6),
                "recall": round(float(recall[index]), 6),
                "f1": round(float(f1[index]), 6),
                "support": int(support[index]),
            }
            for index, name in enumerate(CLASS_NAMES)
        },
        "classification_report": classification_report(
            truth,
            predicted,
            labels=np.arange(len(CLASS_NAMES)),
            target_names=CLASS_NAMES,
            zero_division=0,
            output_dict=True,
        ),
    }


def plot_outputs(
    output: Path,
    history: list[dict[str, float]],
    truth: np.ndarray,
    predicted: np.ndarray,
    maps: np.ndarray,
    test_indices: np.ndarray,
    seed: int,
) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot([row["epoch"] for row in history], [row["train_loss"] for row in history], label="train")
    axes[0].plot([row["epoch"] for row in history], [row["val_loss"] for row in history], label="validation")
    axes[0].set_title("Loss")
    axes[0].legend()
    axes[1].plot([row["epoch"] for row in history], [row["val_macro_f1"] for row in history])
    axes[1].set_title("Validation macro-F1")
    axes[1].set_ylim(0, 1)
    figure.tight_layout()
    figure.savefig(output / "training_curves.png", dpi=160)
    plt.close(figure)

    matrix = confusion_matrix(truth, predicted, labels=np.arange(len(CLASS_NAMES)), normalize="true")
    figure, axis = plt.subplots(figsize=(9, 8))
    image = axis.imshow(matrix, vmin=0, vmax=1, cmap="Blues")
    axis.set_xticks(range(len(CLASS_NAMES)), CLASS_NAMES, rotation=45, ha="right")
    axis.set_yticks(range(len(CLASS_NAMES)), CLASS_NAMES)
    axis.set_xlabel("Predicted")
    axis.set_ylabel("True")
    axis.set_title("Normalized test confusion matrix")
    figure.colorbar(image, ax=axis)
    figure.tight_layout()
    figure.savefig(output / "confusion_matrix.png", dpi=180)
    plt.close(figure)

    rng = np.random.default_rng(seed)
    examples = []
    for class_index in range(len(CLASS_NAMES)):
        positions = np.flatnonzero(truth == class_index)
        if len(positions):
            examples.append(int(rng.choice(positions)))
    figure, axes = plt.subplots(3, 3, figsize=(9, 9))
    for axis, position in zip(axes.flat, examples, strict=False):
        axis.imshow(maps[test_indices[position]], cmap="viridis", vmin=0, vmax=2)
        axis.set_title(f"true={CLASS_NAMES[truth[position]]}\npred={CLASS_NAMES[predicted[position]]}")
        axis.axis("off")
    for axis in axes.flat[len(examples) :]:
        axis.axis("off")
    figure.tight_layout()
    figure.savefig(output / "example_predictions.png", dpi=180)
    plt.close(figure)


def main() -> None:
    args = parse_args()
    seed_everything(args.seed)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    started = time.time()
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    print("Loading WM-811K...", flush=True)
    frame = load_legacy_pickle(Path(args.input))
    maps, labels, groups = build_cache(frame, output, args.image_size)
    del frame
    train_indices, val_indices, test_indices = make_splits(labels, groups, args.seed)

    split_groups = {
        "train": set(groups[train_indices]),
        "validation": set(groups[val_indices]),
        "test": set(groups[test_indices]),
    }
    assert split_groups["train"].isdisjoint(split_groups["validation"])
    assert split_groups["train"].isdisjoint(split_groups["test"])
    assert split_groups["validation"].isdisjoint(split_groups["test"])

    train_counts = np.bincount(labels[train_indices], minlength=len(CLASS_NAMES))
    sample_weights = 1.0 / np.sqrt(train_counts[labels[train_indices]].astype(np.float64))
    sampler = WeightedRandomSampler(
        torch.from_numpy(sample_weights), num_samples=min(args.samples_per_epoch, len(train_indices)), replacement=True
    )
    train_loader = DataLoader(
        WaferDataset(maps, labels, train_indices, augment=True),
        batch_size=args.batch_size,
        sampler=sampler,
        num_workers=0,
    )
    val_loader = DataLoader(
        WaferDataset(maps, labels, val_indices, augment=False), batch_size=args.batch_size, shuffle=False, num_workers=0
    )
    test_loader = DataLoader(
        WaferDataset(maps, labels, test_indices, augment=False),
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )

    model = WaferCNN(len(CLASS_NAMES)).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=2)
    loss_fn = nn.CrossEntropyLoss()
    history: list[dict[str, float]] = []
    best_f1 = -1.0
    stale = 0
    best_path = output / "best_model.pt"

    for epoch in range(1, args.epochs + 1):
        model.train()
        train_losses: list[float] = []
        for inputs, batch_labels in train_loader:
            inputs, batch_labels = inputs.to(device), batch_labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(inputs), batch_labels)
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.item()))
        val_loss, val_truth, val_predicted = predict(model, val_loader, device, loss_fn)
        val_f1 = float(f1_score(val_truth, val_predicted, average="macro"))
        scheduler.step(val_f1)
        row = {
            "epoch": epoch,
            "train_loss": round(float(np.mean(train_losses)), 6),
            "val_loss": round(val_loss, 6),
            "val_macro_f1": round(val_f1, 6),
            "learning_rate": optimizer.param_groups[0]["lr"],
        }
        history.append(row)
        print(json.dumps(row), flush=True)
        if val_f1 > best_f1:
            best_f1 = val_f1
            stale = 0
            torch.save(
                {"model_state": model.state_dict(), "class_names": CLASS_NAMES, "image_size": args.image_size},
                best_path,
            )
        else:
            stale += 1
            if stale >= args.patience:
                print("early stopping", flush=True)
                break

    checkpoint = torch.load(best_path, map_location=device, weights_only=True)
    model.load_state_dict(checkpoint["model_state"])
    test_loss, test_truth, test_predicted = predict(model, test_loader, device, loss_fn)
    metrics = metric_summary(test_truth, test_predicted)
    metrics["test_loss"] = round(test_loss, 6)
    metrics["best_validation_macro_f1"] = round(best_f1, 6)
    metrics["elapsed_seconds"] = round(time.time() - started, 2)
    metrics["device"] = str(device)

    parameters = vars(args) | {
        "task": "nine-class wafer-map failure-pattern classification",
        "classes": CLASS_NAMES,
        "architecture": "compact categorical 3-channel CNN",
        "input_encoding": "three one-hot channels for background/good-die/bad-die",
        "split_strategy": "StratifiedGroupKFold; train/validation/test lots are disjoint",
        "sampling": "inverse-sqrt-frequency WeightedRandomSampler",
        "device": str(device),
        "labeled_samples": int(len(labels)),
        "train_samples": int(len(train_indices)),
        "validation_samples": int(len(val_indices)),
        "test_samples": int(len(test_indices)),
        "model_parameters": sum(parameter.numel() for parameter in model.parameters()),
    }
    distributions = {
        split: {CLASS_NAMES[index]: int(count) for index, count in enumerate(np.bincount(labels[indices], minlength=9))}
        for split, indices in {"train": train_indices, "validation": val_indices, "test": test_indices}.items()
    }
    distributions["unique_lots"] = {split: len(values) for split, values in split_groups.items()}
    save_json(output / "parameters.json", parameters)
    save_json(output / "metrics.json", metrics)
    save_json(output / "history.json", history)
    save_json(output / "class_distribution.json", distributions)
    np.save(output / "test_truth.npy", test_truth)
    np.save(output / "test_predictions.npy", test_predicted)
    plot_outputs(output, history, test_truth, test_predicted, maps, test_indices, args.seed)
    print(json.dumps(metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()
