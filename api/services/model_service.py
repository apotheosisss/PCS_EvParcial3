"""Servicio de predicción: construye filas, ejecuta el modelo y clasifica el riesgo.

Reproduce el contrato del bundle (`feature_cols`, `feature_means`): las features
provistas se usan tal cual y el resto se rellena con la media del training set,
igual que hacía la versión monolítica de la API.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from ..artifacts import ArtifactStore
from ..config import Settings


def risk_band(proba: float, s: Settings) -> str:
    """Banda cualitativa de riesgo a partir de la probabilidad."""
    if proba < s.risk_band_low:
        return "bajo"
    if proba < s.risk_band_high:
        return "medio"
    return "alto"


def build_matrix(payloads: list[dict[str, Any]], bundle: dict[str, Any]) -> pd.DataFrame:
    """Construye un DataFrame con TODAS las features del modelo, en orden.

    Cada payload aporta las features que tenga; las faltantes se rellenan con la
    media del training set. Las claves desconocidas se ignoran.
    """
    feature_cols = bundle["feature_cols"]
    means = bundle.get("feature_means", {})
    rows: list[dict[str, Any]] = []
    for payload in payloads:
        row = {col: means.get(col, 0.0) for col in feature_cols}
        for key, value in payload.items():
            if value is not None and key in row:
                row[key] = value
        rows.append(row)
    return pd.DataFrame(rows)[feature_cols]


def predict(
    payloads: list[dict[str, Any]], store: ArtifactStore, s: Settings
) -> tuple[list[dict[str, Any]], str]:
    """Predice para uno o varios registros. Devuelve (resultados, model_version)."""
    bundle = store.bundle()
    X = build_matrix(payloads, bundle)
    proba = bundle["model"].predict_proba(X)[:, 1]
    # Umbral optimizado guardado en el bundle por el modelo (fallback al de settings).
    threshold = float(bundle.get("threshold", s.decision_threshold))

    results: list[dict[str, Any]] = []
    for p in proba:
        p = float(p)
        pred = int(p >= threshold)
        results.append(
            {
                "prediction": pred,
                "label": "riesgo_diabetes" if pred == 1 else "sin_riesgo",
                "probability": round(p, 4),
                "risk_band": risk_band(p, s),
            }
        )
    return results, bundle.get("model_version", "v1.0.0")
