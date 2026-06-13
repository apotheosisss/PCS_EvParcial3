"""Nodos de ingesta y validacion de fuentes NHANES."""
from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


DATASET_LABELS = {
    "nhanes_demo_raw": "DEMO_L",
    "nhanes_diq_raw": "DIQ_L",
    "nhanes_bmx_raw": "BMX_L",
    "nhanes_ghb_raw": "GHB_L",
    "nhanes_glu_raw": "GLU_L",
    "nhanes_paq_raw": "PAQ_L",
    "nhanes_slq_raw": "SLQ_L",
    "nhanes_bpxo_raw": "BPXO_L",
    "diabetes_thresholds": "umbrales_diabetes",
}


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    dataset_name: str,
) -> list[str]:
    """Return missing required columns for a dataframe."""
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"{dataset_name} no contiene columnas obligatorias: {missing}")
    return missing_columns


def summarize_dataset(df: pd.DataFrame, dataset_name: str) -> dict[str, Any]:
    """Build a compact summary for one source dataset."""
    return {
        "dataset_name": dataset_name,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values": int(df.isna().sum().sum()),
        "column_names": ",".join(map(str, df.columns)),
    }


def build_ingestion_reports(
    nhanes_demo_raw: pd.DataFrame,
    nhanes_diq_raw: pd.DataFrame,
    nhanes_bmx_raw: pd.DataFrame,
    nhanes_ghb_raw: pd.DataFrame,
    nhanes_glu_raw: pd.DataFrame,
    nhanes_paq_raw: pd.DataFrame,
    nhanes_slq_raw: pd.DataFrame,
    nhanes_bpxo_raw: pd.DataFrame,
    diabetes_thresholds: pd.DataFrame,
    params: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Validate ingestion inputs and generate audit tables."""
    datasets = {
        "nhanes_demo_raw": nhanes_demo_raw,
        "nhanes_diq_raw": nhanes_diq_raw,
        "nhanes_bmx_raw": nhanes_bmx_raw,
        "nhanes_ghb_raw": nhanes_ghb_raw,
        "nhanes_glu_raw": nhanes_glu_raw,
        "nhanes_paq_raw": nhanes_paq_raw,
        "nhanes_slq_raw": nhanes_slq_raw,
        "nhanes_bpxo_raw": nhanes_bpxo_raw,
        "diabetes_thresholds": diabetes_thresholds,
    }
    required_columns = dict(params.get("required_columns", {}))
    required_columns["diabetes_thresholds"] = [
        "variable",
        "criterio",
        "valor",
        "descripcion",
    ]

    run_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    audit_rows = []
    summary_rows = []

    for dataset_key, df in datasets.items():
        dataset_name = DATASET_LABELS.get(dataset_key, dataset_key)
        required = required_columns.get(dataset_key, [])
        validate_required_columns(df, required, dataset_name)

        summary = summarize_dataset(df, dataset_name)
        summary_rows.append(summary)
        audit_rows.append(
            {
                "run_id": run_id,
                "execution_timestamp": timestamp,
                "dataset_key": dataset_key,
                "dataset_name": dataset_name,
                "rows": summary["rows"],
                "columns": summary["columns"],
                "missing_values": summary["missing_values"],
                "required_columns": ",".join(required),
                "missing_required_columns": "",
                "status": "ok",
            }
        )

    return pd.DataFrame(audit_rows), pd.DataFrame(summary_rows)


def save_ingestion_audit(
    ingestion_audit: pd.DataFrame,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Persist ingestion audit rows in SQLite."""
    db_path = Path(params["audit_db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        ingestion_audit.to_sql(
            "ingestion_audit",
            connection,
            if_exists="append",
            index=False,
        )

    return {
        "db_path": str(db_path),
        "table": "ingestion_audit",
        "rows_saved": int(len(ingestion_audit)),
    }
