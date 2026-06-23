"""Servicio de reporting: sirve en JSON los artefactos de evaluación del modelo."""
from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)

from ..artifacts import ArtifactStore


def comparison(store: ArtifactStore) -> dict[str, Any]:
    """Tabla comparativa de modelos (`model_comparison.csv`)."""
    df = store.model_comparison()
    return {"models": df.to_dict(orient="records")}


def confusion_matrix(store: ArtifactStore) -> dict[str, Any]:
    """Matriz de confusión como JSON.

    El CSV se guarda sin índice (solo columnas `pred_*`); las etiquetas de fila
    (`real_*`) se reconstruyen por convención, alineadas con las columnas.
    """
    df = store.confusion_matrix()
    columns = [str(c) for c in df.columns]
    matrix = [[int(v) for v in row] for row in df.to_numpy()]
    labels = [c.replace("pred_", "") for c in columns]
    index = [f"real_{lbl}" for lbl in labels[: len(matrix)]]
    return {"labels": labels, "index": index, "columns": columns, "matrix": matrix}


def feature_importance(store: ArtifactStore, top: int | None = None) -> dict[str, Any]:
    """Importancia de variables ordenada desc (`feature_importance.csv`)."""
    df = store.feature_importance().sort_values("importance", ascending=False)
    if top is not None:
        df = df.head(top)
    items = [
        {"feature": str(r["feature"]), "importance": float(r["importance"])}
        for _, r in df.iterrows()
    ]
    return {"importances": items}


def _downsample(*arrays: np.ndarray, n: int = 60) -> list[np.ndarray]:
    length = len(arrays[0])
    idx = (
        np.arange(length)
        if length <= n
        else np.linspace(0, length - 1, n).astype(int)
    )
    return [np.asarray(a)[idx] for a in arrays]


def curves(store: ArtifactStore) -> dict[str, Any]:
    """Curvas de evaluacion derivadas de las predicciones (y_true, probability).

    Devuelve datos para: ROC, Precision-Recall, calibracion, distribucion de scores
    por clase y curva de decision (net benefit). Todo se calcula desde predictions.csv.
    """
    df = store.predictions()
    y = df["y_true"].astype(int).to_numpy()
    p = df["probability"].astype(float).to_numpy()
    n = len(y)
    pos = int(y.sum())
    prevalence = pos / n if n else 0.0

    # ROC
    fpr, tpr, _ = roc_curve(y, p)
    fpr, tpr = _downsample(fpr, tpr)
    roc = [{"fpr": round(float(a), 4), "tpr": round(float(b), 4)} for a, b in zip(fpr, tpr)]

    # Precision-Recall
    prec, rec, _ = precision_recall_curve(y, p)
    prec, rec = _downsample(prec, rec)
    pr = [{"recall": round(float(b), 4), "precision": round(float(a), 4)} for a, b in zip(prec, rec)]

    # Calibracion (reliability diagram, bins por cuantiles)
    obs, pred = calibration_curve(y, p, n_bins=10, strategy="quantile")
    calibration = [
        {"predicted": round(float(a), 4), "observed": round(float(b), 4)}
        for a, b in zip(pred, obs)
    ]

    # Distribucion de scores por clase (proporcion dentro de cada clase)
    bins = np.linspace(0, 1, 21)
    mids = (bins[:-1] + bins[1:]) / 2
    h0, _ = np.histogram(p[y == 0], bins=bins)
    h1, _ = np.histogram(p[y == 1], bins=bins)
    h0 = h0 / max(h0.sum(), 1)
    h1 = h1 / max(h1.sum(), 1)
    distribution = [
        {"score": round(float(m), 3), "sin_diabetes": round(float(a), 4), "con_diabetes": round(float(b), 4)}
        for m, a, b in zip(mids, h0, h1)
    ]

    # Curva de decision (net benefit): modelo vs "tratar a todos"
    decision_curve = []
    for pt in np.linspace(0.02, 0.6, 30):
        w = pt / (1 - pt)
        predv = (p >= pt).astype(int)
        tp = int(((predv == 1) & (y == 1)).sum())
        fp = int(((predv == 1) & (y == 0)).sum())
        nb_model = tp / n - fp / n * w
        nb_all = pos / n - (n - pos) / n * w
        decision_curve.append({
            "threshold": round(float(pt), 3),
            "modelo": round(float(nb_model), 4),
            "tratar_todos": round(float(nb_all), 4),
        })

    return {
        "roc": roc,
        "pr": pr,
        "calibration": calibration,
        "distribution": distribution,
        "decision_curve": decision_curve,
        "roc_auc": round(float(roc_auc_score(y, p)), 4),
        "pr_auc": round(float(average_precision_score(y, p)), 4),
        "prevalence": round(float(prevalence), 4),
        "threshold": float(store.metrics().get("decision_threshold", 0.5)),
    }
