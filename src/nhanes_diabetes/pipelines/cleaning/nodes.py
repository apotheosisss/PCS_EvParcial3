"""Nodos del pipeline de limpieza NHANES (feature/b).

Convierte las 8 tablas crudas NHANES (+ umbrales) en un dataset primario limpio:
une por SEQN, neutraliza codigos especiales, valida rangos fisiologicos, elimina
duplicados, imputa nulos (excepto las 3 columnas fuente del target) y registra una
auditoria ETL en SQLite.
"""
from __future__ import annotations

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

MERGE_KEY = "SEQN"
# Columnas que definen el target: NO se imputan en cleaning (ver CONTRATO_FEATURE_B §3).
TARGET_SOURCE_COLS = ["DIQ010", "LBXGH", "LBXGLU"]
# Prefijos de cuestionarios donde aplican codigos genericos (refused/don't know).
QUESTIONNAIRE_PREFIXES = ("DIQ", "PAQ", "SLQ")


def merge_nhanes_tables(
    nhanes_demo_raw: pd.DataFrame,
    nhanes_diq_raw: pd.DataFrame,
    nhanes_bmx_raw: pd.DataFrame,
    nhanes_ghb_raw: pd.DataFrame,
    nhanes_glu_raw: pd.DataFrame,
    nhanes_paq_raw: pd.DataFrame,
    nhanes_slq_raw: pd.DataFrame,
    nhanes_bpxo_raw: pd.DataFrame,
    params: dict[str, Any],
) -> pd.DataFrame:
    """Une todas las fuentes por SEQN (DEMO como universo, left join del resto)."""
    sources = {
        "demo": nhanes_demo_raw,
        "diq": nhanes_diq_raw,
        "bmx": nhanes_bmx_raw,
        "ghb": nhanes_ghb_raw,
        "glu": nhanes_glu_raw,
        "paq": nhanes_paq_raw,
        "slq": nhanes_slq_raw,
        "bpxo": nhanes_bpxo_raw,
    }
    for name, df in sources.items():
        if MERGE_KEY not in df.columns:
            raise ValueError(f"La fuente '{name}' no contiene la llave '{MERGE_KEY}'")

    # Allowlist por fuente: conserva solo variables previstas (evita fuga de items DIQ,
    # pesos muestrales y columnas redundantes). Si una fuente no esta en keep_columns,
    # se conserva completa.
    keep = dict(params.get("keep_columns", {}))
    for name in list(sources):
        cols = keep.get(name)
        if cols:
            present = [c for c in cols if c in sources[name].columns]
            if MERGE_KEY not in present:
                present = [MERGE_KEY] + present
            missing = [c for c in cols if c not in sources[name].columns]
            if missing:
                logger.warning("Fuente '%s': columnas no encontradas: %s", name, missing)
            sources[name] = sources[name][present]

    merged = sources["demo"].drop_duplicates(subset=MERGE_KEY).copy()
    for name, df in sources.items():
        if name == "demo":
            continue
        df = df.drop_duplicates(subset=MERGE_KEY)
        merged = merged.merge(df, on=MERGE_KEY, how="left", suffixes=("", f"_{name}"))

    if bool(params.get("filter_adults", True)) and "RIDAGEYR" in merged.columns:
        before = len(merged)
        merged = merged[merged["RIDAGEYR"] >= int(params.get("adult_min_age", 18))]
        logger.info("Filtro adultos: %d -> %d filas", before, len(merged))

    if merged[MERGE_KEY].duplicated().any():
        raise ValueError("SEQN duplicado tras el merge; revisar fuentes")

    logger.info("Merge NHANES: %d filas x %d columnas", len(merged), merged.shape[1])
    return merged.reset_index(drop=True)


def replace_special_codes_with_nan(
    df: pd.DataFrame, params: dict[str, Any]
) -> pd.DataFrame:
    """Reemplaza codigos especiales NHANES (7/9/77/99...) por NaN antes de imputar."""
    out = df.copy()
    special_codes: dict[str, list] = dict(params.get("special_codes", {}))
    generic = list(params.get("generic_special_codes", []))

    for col, codes in special_codes.items():
        if col in out.columns:
            out[col] = out[col].replace(list(codes), np.nan)

    if generic:
        for col in out.columns:
            if col == MERGE_KEY:
                continue
            if str(col).upper().startswith(QUESTIONNAIRE_PREFIXES):
                out[col] = out[col].replace(generic, np.nan)

    logger.info("Codigos especiales neutralizados (per-col=%d, genericos=%s)",
                len(special_codes), generic)
    return out


def validate_ranges(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """Convierte a NaN los valores fuera del rango fisiologico definido en params."""
    out = df.copy()
    valid_ranges: dict[str, list] = dict(params.get("valid_ranges", {}))
    for col, bounds in valid_ranges.items():
        if col in out.columns:
            lo, hi = bounds
            mask = (out[col] < lo) | (out[col] > hi)
            n = int(mask.sum())
            if n:
                logger.info("Rango invalido en %s: %d valores -> NaN", col, n)
            out.loc[mask, col] = np.nan
    return out


def clean_and_impute(df: pd.DataFrame, params: dict[str, Any]) -> pd.DataFrame:
    """Elimina duplicados de SEQN e imputa nulos, salvo en las columnas del target."""
    out = df.drop_duplicates(subset=MERGE_KEY).copy()
    protected = set(TARGET_SOURCE_COLS) | {MERGE_KEY}

    for col in out.columns:
        if col in protected:
            continue
        if out[col].isna().any():
            series = out[col]
            if pd.api.types.is_numeric_dtype(series):
                nunique = series.dropna().nunique()
                # binarias / categoricas codificadas -> moda; continuas -> mediana
                if nunique <= 2:
                    fill = series.mode(dropna=True)
                    fill = fill.iloc[0] if not fill.empty else 0
                else:
                    fill = series.median()
            else:
                fill = series.mode(dropna=True)
                fill = fill.iloc[0] if not fill.empty else ""
            out[col] = series.fillna(fill)

    logger.info("Clean+impute: %d filas, nulos restantes (incl. target src)=%d",
                len(out), int(out.isna().sum().sum()))
    return out.reset_index(drop=True)


def build_etl_audit(
    merged: pd.DataFrame, clean: pd.DataFrame, params: dict[str, Any]
) -> pd.DataFrame:
    """Audita filas y nulos antes/despues de la limpieza (Notion fuente 3 / etl_audit)."""
    run_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    rows = [{
        "run_id": run_id,
        "execution_timestamp": ts,
        "stage": "overall",
        "column": "__all__",
        "rows_before": int(len(merged)),
        "rows_after": int(len(clean)),
        "nulls_before": int(merged.isna().sum().sum()),
        "nulls_after": int(clean.isna().sum().sum()),
    }]
    for col in merged.columns:
        nb = int(merged[col].isna().sum())
        na = int(clean[col].isna().sum()) if col in clean.columns else None
        rows.append({
            "run_id": run_id,
            "execution_timestamp": ts,
            "stage": "column",
            "column": str(col),
            "rows_before": int(len(merged)),
            "rows_after": int(len(clean)),
            "nulls_before": nb,
            "nulls_after": na,
        })
    return pd.DataFrame(rows)


def save_etl_audit(etl_audit: pd.DataFrame, params: dict[str, Any]) -> dict[str, Any]:
    """Persiste la auditoria ETL en SQLite (tabla etl_audit)."""
    db_path = Path(params["audit_db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        etl_audit.to_sql("etl_audit", conn, if_exists="append", index=False)
    logger.info("etl_audit guardada en %s (%d filas)", db_path, len(etl_audit))
    return {"db_path": str(db_path), "table": "etl_audit", "rows_saved": int(len(etl_audit))}
