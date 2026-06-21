"""Servicio de reporting: sirve en JSON los artefactos de evaluación del modelo."""
from __future__ import annotations

from typing import Any

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
