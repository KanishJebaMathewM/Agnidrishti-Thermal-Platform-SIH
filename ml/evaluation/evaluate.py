"""
Evaluation script.

Run after training to produce a comprehensive evaluation report:
1. Confusion matrix (5x5)
2. Per-class precision, recall, F1
3. Overall accuracy
4. Macro-averaged metrics
5. Feature importance plot (XGBoost built-in) — saved if matplotlib is available
6. Calibration curve for confidence scores — saved if matplotlib is available

Also compares against two simple baselines the XGBoost model must outperform:
  "always predict the majority class"
  "predict Industrial Incident if within 2km of an industrial facility, else Unknown"

Do not optimize only for accuracy: this system's cost of a missed genuinely
abnormal event outweighs the cost of an extra review candidate, so per-class
recall (especially for Industrial Incident / Forest Fire) is reported
alongside accuracy, not folded away by it.

Plotting is optional and best-effort: the numeric report (JSON) is produced
regardless of whether matplotlib/seaborn import successfully in the current
environment.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ml.features.feature_columns import CLASS_LABELS, CLASS_TO_IDX, FEATURE_COLUMNS_V1

DEFAULT_REPORT_DIR = Path(__file__).resolve().parent / "reports"


def _to_matrix(df: pd.DataFrame, feature_columns: list[str] = FEATURE_COLUMNS_V1) -> np.ndarray:
    return df[feature_columns].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)


def _classification_report(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    labels = list(range(len(CLASS_LABELS)))
    precisions = precision_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    recalls = recall_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    f1s = f1_score(y_true, y_pred, labels=labels, average=None, zero_division=0)
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "per_class": {
            CLASS_LABELS[i]: {"precision": float(precisions[i]), "recall": float(recalls[i]), "f1": float(f1s[i])}
            for i in labels
        },
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=labels).tolist(),
        "confusion_matrix_labels": CLASS_LABELS,
    }


def majority_class_baseline(train_df: pd.DataFrame, n: int) -> np.ndarray:
    """Baseline 1: always predict the most frequent class in the training set."""
    majority_label = Counter(train_df["label"].astype(str)).most_common(1)[0][0]
    return np.full(n, CLASS_TO_IDX[majority_label])


def industrial_proximity_baseline(df: pd.DataFrame) -> np.ndarray:
    """Baseline 2: predict Industrial Incident within 2km of a facility, else Unknown."""
    dist = pd.to_numeric(df["nearest_industrial_dist_km"], errors="coerce")
    preds = np.where(dist <= 2.0, CLASS_TO_IDX["Industrial Incident"], CLASS_TO_IDX["Unknown"])
    return preds


def evaluate_model(
    model,
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_columns: list[str] = FEATURE_COLUMNS_V1,
    output_dir: Path = DEFAULT_REPORT_DIR,
    model_version: str = "unknown",
) -> dict:
    """
    Produce the full evaluation report comparing the model against both
    required baselines, and write it (plus best-effort plots) to
    `output_dir`.
    """
    X_test = _to_matrix(test_df, feature_columns)
    y_test = test_df["label"].astype(str).map(CLASS_TO_IDX).to_numpy()
    y_pred = model.predict(X_test)

    model_report = _classification_report(y_test, y_pred)

    majority_pred = majority_class_baseline(train_df, len(y_test))
    majority_report = _classification_report(y_test, majority_pred)

    proximity_pred = industrial_proximity_baseline(test_df)
    proximity_report = _classification_report(y_test, proximity_pred)

    report = {
        "model_version": model_version,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "n_test_samples": int(len(y_test)),
        "model": model_report,
        "baselines": {
            "majority_class": majority_report,
            "industrial_proximity_rule": proximity_report,
        },
        "outperforms_majority_baseline": model_report["f1_macro"] > majority_report["f1_macro"],
        "outperforms_proximity_baseline": model_report["f1_macro"] > proximity_report["f1_macro"],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "evaluation_report.json").write_text(json.dumps(report, indent=2))

    _try_save_plots(model, model_report, test_df, output_dir, feature_columns)

    return report


def _try_save_plots(model, model_report: dict, test_df: pd.DataFrame, output_dir: Path,
                     feature_columns: list[str]) -> None:
    """Best-effort plotting. Never raises — the numeric report is what matters."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - environment dependent
        (output_dir / "PLOTS_SKIPPED.txt").write_text(
            f"Plotting skipped: matplotlib unavailable ({exc}). Numeric report is unaffected."
        )
        return

    try:
        cm = np.array(model_report["confusion_matrix"])
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(cm, cmap="Blues")
        ax.set_xticks(range(len(CLASS_LABELS)))
        ax.set_yticks(range(len(CLASS_LABELS)))
        ax.set_xticklabels(CLASS_LABELS, rotation=45, ha="right")
        ax.set_yticklabels(CLASS_LABELS)
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title("Confusion Matrix")
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center")
        fig.colorbar(im)
        fig.tight_layout()
        fig.savefig(output_dir / "confusion_matrix.png")
        plt.close(fig)
    except Exception:
        pass

    try:
        importances = getattr(model, "feature_importances_", None)
        if importances is not None:
            order = np.argsort(importances)[::-1]
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.barh([feature_columns[i] for i in order], importances[order])
            ax.invert_yaxis()
            ax.set_title("Feature Importance")
            fig.tight_layout()
            fig.savefig(output_dir / "feature_importance.png")
            plt.close(fig)
    except Exception:
        pass

    try:
        X_test = _to_matrix(test_df, feature_columns)
        probas = model.predict_proba(X_test)
        confidence = probas.max(axis=1)
        y_test = test_df["label"].astype(str).map(CLASS_TO_IDX).to_numpy()
        y_pred = model.predict(X_test)
        correct = (y_pred == y_test).astype(float)

        bins = np.linspace(0, 1, 11)
        bin_idx = np.digitize(confidence, bins) - 1
        bin_idx = np.clip(bin_idx, 0, len(bins) - 2)
        bin_acc = [correct[bin_idx == b].mean() if np.any(bin_idx == b) else np.nan for b in range(len(bins) - 1)]

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect calibration")
        ax.plot(bins[:-1] + 0.05, bin_acc, marker="o", label="Model")
        ax.set_xlabel("Predicted confidence")
        ax.set_ylabel("Observed accuracy")
        ax.set_title("Calibration Curve")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_dir / "calibration_curve.png")
        plt.close(fig)
    except Exception:
        pass


def main():
    import argparse
    import joblib

    from ml.datasets.build_dataset import build_training_dataset, temporal_split
    from ml.datasets.synthetic import generate_synthetic_dataset

    parser = argparse.ArgumentParser(description="Evaluate a trained AGNIDRISHTI classifier.")
    parser.add_argument("--model-path", type=Path,
                         default=Path(__file__).resolve().parent.parent / "models" / "xgb_v1_0.joblib")
    parser.add_argument("--n-per-class", type=int, default=200)
    args = parser.parse_args()

    if not args.model_path.exists():
        raise SystemExit(
            f"No model artifact at {args.model_path}. Run `python -m ml.training.train_classifier` first."
        )

    model = joblib.load(args.model_path)

    records = generate_synthetic_dataset(n_per_class=args.n_per_class)
    df = build_training_dataset(records)
    train_df, _, test_df = temporal_split(df)

    report = evaluate_model(model, train_df, test_df, model_version=str(args.model_path.stem))
    print(json.dumps({k: v for k, v in report.items() if k != "model"}, indent=2))
    print(f"Model accuracy: {report['model']['accuracy']:.3f} | f1_macro: {report['model']['f1_macro']:.3f}")


if __name__ == "__main__":
    main()
