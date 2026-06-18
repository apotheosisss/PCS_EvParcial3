"""Nodos del pipeline de feature engineering NHANES (feature/b).

Construye diabetes_target (ANTES de imputar sus fuentes), variables derivadas,
codifica categoricas a numerico, selecciona el set final, genera metadata y valida
el contrato del model_input (docs/CONTRATO_FEATURE_B.md).
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

ID_COL = "SEQN"
TARGET = "diabetes_target"
TARGET_SOURCE_COLS = ["DIQ010", "LBXGH", "LBXGLU"]
# Features que el usuario puede ingresar por la API (user_facing).
USER_FACING = ["RIDAGEYR", "RIAGENDR", "BMXBMI", "BMXWAIST", "LBXGH", "LBXGLU", "INDFMPIR"]
BASE_RAW = USER_FACING + ["RIDRETH3"]


def create_diabetes_target(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """Crea diabetes_target con la regla ADA-educativa, antes de imputar sus fuentes.

    diabetes_target = 1 si DIQ010==1 o LBXGH>=6.5 o LBXGLU>=126; 0 en caso contrario.
    Las filas sin ninguna fuente determinable se eliminan (no se inventa un 0).
    """
    rule = dict(params.get("target_rule", {}))
    a1c_thr = float(rule.get("a1c_threshold", 6.5))
    glu_thr = float(rule.get("glucose_threshold", 126))
    diq_pos = rule.get("diq010_positive", 1)

    out = df.copy()
    diq = out["DIQ010"] if "DIQ010" in out else pd.Series(np.nan, index=out.index)
    a1c = out["LBXGH"] if "LBXGH" in out else pd.Series(np.nan, index=out.index)
    glu = out["LBXGLU"] if "LBXGLU" in out else pd.Series(np.nan, index=out.index)

    determined = diq.notna() | a1c.notna() | glu.notna()
    dropped = int((~determined).sum())
    if dropped:
        logger.info("Target indeterminable: %d filas eliminadas", dropped)
    out = out[determined].copy()
    diq, a1c, glu = diq[determined], a1c[determined], glu[determined]

    positive = (
        (diq == diq_pos).fillna(False)
        | (a1c >= a1c_thr).fillna(False)
        | (glu >= glu_thr).fillna(False)
    )
    out[TARGET] = positive.astype(int)

    # Ahora si: imputar las fuentes del target para usarlas como features sin nulos.
    for col in TARGET_SOURCE_COLS:
        if col in out.columns and out[col].isna().any():
            out[col] = out[col].fillna(out[col].median())

    logger.info("diabetes_target -> %s", out[TARGET].value_counts().to_dict())
    return out.reset_index(drop=True)


def create_derived_features(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """Genera variables derivadas clinicas y socioeconomicas."""
    out = df.copy()

    if "RIDAGEYR" in out:
        bins = params.get("age_bins", [[18, 44], [45, 64], [65, 200]])
        edges = [b[0] for b in bins] + [bins[-1][1] + 1]
        labels = [f"age_{b[0]}_{b[1]}" for b in bins]
        out["age_group"] = pd.cut(out["RIDAGEYR"], bins=edges, labels=labels,
                                  right=True, include_lowest=True).astype(str)

    if "BMXBMI" in out:
        b = params.get("bmi_bins", {"underweight": 18.5, "normal": 25, "overweight": 30})

        def _bmi_cat(v):
            if pd.isna(v):
                return "unknown"
            if v < b["underweight"]:
                return "underweight"
            if v < b["normal"]:
                return "normal"
            if v < b["overweight"]:
                return "overweight"
            return "obese"

        out["bmi_category"] = out["BMXBMI"].apply(_bmi_cat)
        out["has_obesity"] = (out["BMXBMI"] >= b["overweight"]).astype(int)

    if "LBXGH" in out:
        out["high_a1c"] = (out["LBXGH"] >= float(params.get("a1c_threshold", 6.5))).astype(int)
    if "LBXGLU" in out:
        out["high_fasting_glucose"] = (
            out["LBXGLU"] >= float(params.get("glucose_threshold", 126))
        ).astype(int)

    if "INDFMPIR" in out:
        pir_bins = params.get("pir_bins", [1, 2, 4])
        edges = [-0.01] + list(pir_bins) + [np.inf]
        labels = [f"income_{i}" for i in range(len(edges) - 1)]
        out["income_group"] = pd.cut(out["INDFMPIR"], bins=edges, labels=labels).astype(str)

    # Derivadas opcionales: solo si las columnas reales existen (codebook NHANES).
    if "PAD680" in out:  # minutos sedentarios
        out["physical_activity_level"] = pd.cut(
            out["PAD680"], bins=[-1, 240, 480, np.inf],
            labels=["activo", "moderado", "sedentario"],
        ).astype(str)
    if "SLD012" in out:  # horas de sueno entre semana
        out["sleep_risk_category"] = out["SLD012"].apply(
            lambda h: "riesgo" if (pd.notna(h) and (h < 6 or h > 9)) else "normal"
        )

    logger.info("Derivadas creadas; columnas ahora=%d", out.shape[1])
    return out


def encode_categorical_variables(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """One-hot de las categoricas presentes; deja todo numerico."""
    out = df.copy()
    candidates = list(params.get("categorical_to_encode", []))
    present = [c for c in candidates if c in out.columns]
    if present:
        out = pd.get_dummies(out, columns=present, prefix=present, dummy_na=False)
    bool_cols = out.select_dtypes(include="bool").columns
    out[bool_cols] = out[bool_cols].astype(int)
    logger.info("Encoding one-hot de %d categoricas -> %d columnas", len(present), out.shape[1])
    return out


def select_final_features(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """Quita columnas excluidas, no numericas residuales, constantes y correlacionadas."""
    out = df.copy()

    drop_features = [c for c in params.get("drop_features", []) if c in out.columns]
    if drop_features:
        logger.info("Excluyendo features por configuracion: %s", drop_features)
        out = out.drop(columns=drop_features)

    obj_cols = [c for c in out.select_dtypes(include="object").columns if c != ID_COL]
    if obj_cols:
        logger.info("Descartando columnas no numericas residuales: %s", obj_cols)
        out = out.drop(columns=obj_cols)

    feature_cols = [c for c in out.columns if c not in (ID_COL, TARGET)]

    if params.get("drop_constant", True):
        const = [c for c in feature_cols if out[c].nunique(dropna=False) <= 1]
        if const:
            logger.info("Descartando columnas constantes: %s", const)
            out = out.drop(columns=const)
            feature_cols = [c for c in feature_cols if c not in const]

    if params.get("drop_perfectly_correlated", True) and len(feature_cols) > 1:
        corr = out[feature_cols].corr().abs()
        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        to_drop = [c for c in upper.columns if (upper[c] >= 0.999).any()]
        if to_drop:
            logger.info("Descartando columnas perfectamente correlacionadas: %s", to_drop)
            out = out.drop(columns=to_drop)

    return out


def build_feature_metadata(df: pd.DataFrame, params: dict[str, Any]) -> dict[str, Any]:
    """Metadata por feature para que feature/c (API) sepa cuales son user_facing."""
    meta = {"target": TARGET, "id": ID_COL, "features": []}
    for col in df.columns:
        if col in (ID_COL, TARGET):
            continue
        meta["features"].append({
            "name": col,
            "dtype": str(df[col].dtype),
            "is_derived": col not in BASE_RAW,
            "user_facing": col in USER_FACING,
            "default": float(df[col].median()),
        })
    return meta


def validate_model_input(df: pd.DataFrame) -> pd.DataFrame:
    """Nodo guardian: verifica TODA la Definition of Done del contrato; lanza si falla."""
    errors = []
    if ID_COL not in df.columns:
        errors.append(f"falta {ID_COL}")
    elif df[ID_COL].duplicated().any():
        errors.append("SEQN duplicado")
    if TARGET not in df.columns:
        errors.append(f"falta {TARGET}")
    else:
        if df[TARGET].isna().any():
            errors.append("target con nulos")
        classes = df[TARGET].value_counts()
        if set(classes.index) != {0, 1}:
            errors.append(f"target debe tener clases 0 y 1, hay {list(classes.index)}")
        elif (classes < 2).any():
            errors.append("alguna clase del target tiene <2 filas")

    feature_cols = [c for c in df.columns if c not in (ID_COL, TARGET)]
    if df[feature_cols].isna().any().any():
        nulls = df[feature_cols].isna().sum()
        errors.append(f"nulos en features: {nulls[nulls > 0].to_dict()}")
    non_numeric = [c for c in feature_cols if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        errors.append(f"features no numericas: {non_numeric}")

    if errors:
        raise ValueError("model_input invalido: " + "; ".join(errors))

    logger.info("model_input VALIDO: %d filas, %d features, target=%s",
                len(df), len(feature_cols), df[TARGET].value_counts().to_dict())
    return df.reset_index(drop=True)
