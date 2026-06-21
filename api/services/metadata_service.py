"""Servicio de metadatos: describe las features del modelo y los umbrales clínicos.

Si feature/b entregó `feature_metadata.json` se usa como fuente de verdad; si no,
los metadatos se infieren del bundle (feature_cols + feature_means) y de un catálogo
estático alineado con `conf/base/parameters.yml` y el diccionario de datos.
"""
from __future__ import annotations

from typing import Any

from ..artifacts import ArtifactStore

# Features que un usuario final puede ingresar por la API (resto se infiere/imputa).
USER_FACING = {
    "RIDAGEYR", "RIAGENDR", "BMXBMI", "BMXWAIST", "LBXGH", "LBXGLU", "INDFMPIR", "RIDRETH3",
}
# Variables crudas NHANES (lo demás se considera derivado).
BASE_RAW = {
    "RIDAGEYR", "RIAGENDR", "RIDRETH3", "INDFMPIR", "BMXBMI", "BMXWAIST", "LBXGH", "LBXGLU",
}

# Etiquetas, unidades y rangos válidos (rangos tomados de cleaning.valid_ranges).
FEATURE_CATALOG: dict[str, dict[str, Any]] = {
    "RIDAGEYR": {"label": "Edad", "unit": "años", "min": 18, "max": 80},
    "RIAGENDR": {"label": "Sexo (1=hombre, 2=mujer)", "min": 1, "max": 2},
    "RIDRETH3": {"label": "Grupo racial/étnico", "min": 1, "max": 7},
    "INDFMPIR": {"label": "Ratio ingreso/pobreza", "min": 0, "max": 5},
    "BMXBMI": {"label": "Índice de masa corporal", "unit": "kg/m²", "min": 10, "max": 70},
    "BMXWAIST": {"label": "Circunferencia de cintura", "unit": "cm", "min": 40, "max": 200},
    "LBXGH": {"label": "Hemoglobina glicosilada (HbA1c)", "unit": "%", "min": 3, "max": 20},
    "LBXGLU": {"label": "Glucosa en ayunas", "unit": "mg/dL", "min": 30, "max": 500},
    "has_obesity": {"label": "Obesidad (IMC ≥ 30)", "min": 0, "max": 1},
    "high_a1c": {"label": "HbA1c alta (≥ 6.5)", "min": 0, "max": 1},
    "high_fasting_glucose": {"label": "Glucosa alta (≥ 126)", "min": 0, "max": 1},
}


def build_features(store: ArtifactStore) -> dict[str, Any]:
    """Devuelve la lista de features del modelo con sus metadatos enriquecidos."""
    bundle = store.bundle()
    feature_cols: list[str] = bundle["feature_cols"]
    means: dict[str, float] = bundle.get("feature_means", {})

    meta_file = store.feature_metadata()
    by_name: dict[str, dict[str, Any]] = {}
    if meta_file:
        by_name = {f["name"]: f for f in meta_file.get("features", [])}

    features: list[dict[str, Any]] = []
    for col in feature_cols:
        mf = by_name.get(col, {})
        catalog = FEATURE_CATALOG.get(col, {})
        default = mf.get("default")
        if default is None and col in means:
            default = round(float(means[col]), 4)
        features.append(
            {
                "name": col,
                "label": catalog.get("label", col),
                "dtype": mf.get("dtype", "float"),
                "user_facing": bool(mf.get("user_facing", col in USER_FACING)),
                "is_derived": bool(mf.get("is_derived", col not in BASE_RAW)),
                "default": default,
                "min": catalog.get("min"),
                "max": catalog.get("max"),
                "unit": catalog.get("unit"),
            }
        )

    return {
        "n_features": len(feature_cols),
        "feature_names": feature_cols,
        "features": features,
    }


def get_thresholds(store: ArtifactStore) -> dict[str, Any]:
    """Sirve los umbrales educativos (`umbrales_diabetes.csv`) como JSON."""
    df = store.thresholds()
    items = [
        {
            "variable": str(r["variable"]),
            "op": str(r["criterio"]),
            "value": float(r["valor"]),
            "description": (None if r.get("descripcion") is None else str(r["descripcion"])),
        }
        for _, r in df.iterrows()
    ]
    return {"thresholds": items}
