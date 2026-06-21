"""Servicio de estadísticas poblacionales sobre `model_input.csv`.

Solo expone agregados (conteos y tasas), nunca filas individuales con `SEQN`.
Las variables de agrupación se derivan de las crudas con la misma lógica de bins
que el feature engineering, para que el front muestre cortes consistentes.
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from ..artifacts import ArtifactStore
from ..config import Settings

# Bins alineados con conf/base/parameters.yml (age_bins / bmi_bins).
_AGE_LABELS = ["18-44", "45-64", "65+"]
_AGE_EDGES = [17, 44, 64, 200]
_SEX_MAP = {1: "Hombre", 2: "Mujer"}
_DERIVABLE = {"age_group", "bmi_category", "RIAGENDR"}


def _bmi_category(value: Any) -> str:
    if pd.isna(value):
        return "unknown"
    if value < 18.5:
        return "underweight"
    if value < 25:
        return "normal"
    if value < 30:
        return "overweight"
    return "obese"


def _category_series(df: pd.DataFrame, by: str) -> pd.Series:
    """Devuelve la serie categórica para agrupar; lanza ValueError si no es posible."""
    if by == "age_group":
        if "RIDAGEYR" not in df.columns:
            raise ValueError("RIDAGEYR no disponible para derivar 'age_group'")
        return pd.cut(df["RIDAGEYR"], bins=_AGE_EDGES, labels=_AGE_LABELS).astype(str)
    if by == "bmi_category":
        if "BMXBMI" not in df.columns:
            raise ValueError("BMXBMI no disponible para derivar 'bmi_category'")
        return df["BMXBMI"].apply(_bmi_category)
    if by == "RIAGENDR":
        if "RIAGENDR" not in df.columns:
            raise ValueError("RIAGENDR no disponible")
        return df["RIAGENDR"].apply(
            lambda v: _SEX_MAP.get(int(v), "Otro") if pd.notna(v) else "Desconocido"
        )
    if by in df.columns:
        col = df[by]
        if pd.api.types.is_numeric_dtype(col) and col.nunique() > 20:
            raise ValueError(
                f"'{by}' es numérica de alta cardinalidad; usa age_group/bmi_category/RIAGENDR"
            )
        return col.astype(str)
    raise ValueError(
        f"Variable '{by}' no soportada. Opciones: {sorted(_DERIVABLE)} o una columna existente."
    )


def summary(store: ArtifactStore, s: Settings) -> dict[str, Any]:
    """KPIs de cabecera: nº participantes y prevalencia del target."""
    df = store.model_input()
    n = int(len(df))
    if s.target_col not in df.columns:
        return {"n_participants": n, "n_positive": None, "n_negative": None, "positive_rate": None}
    positive = int(df[s.target_col].sum())
    return {
        "n_participants": n,
        "n_positive": positive,
        "n_negative": n - positive,
        "positive_rate": round(positive / n, 4) if n else None,
    }


def distribution(store: ArtifactStore, s: Settings, by: str) -> dict[str, Any]:
    """Distribución por una variable, con tasa de positivos por bucket."""
    df = store.model_input()
    series = _category_series(df, by)  # ValueError -> 400 en el router
    has_target = s.target_col in df.columns

    work = pd.DataFrame({"key": series.values})
    if has_target:
        work["target"] = df[s.target_col].values

    buckets: list[dict[str, Any]] = []
    for key, group in work.groupby("key", dropna=False):
        rate = round(float(group["target"].mean()), 4) if has_target else None
        buckets.append({"key": str(key), "count": int(len(group)), "positive_rate": rate})
    buckets.sort(key=lambda b: b["key"])
    return {"by": by, "buckets": buckets}
