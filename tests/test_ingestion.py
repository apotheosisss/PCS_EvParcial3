"""Tests del pipeline de ingesta (feature/a)."""
import sqlite3

import pandas as pd
import pytest

from nhanes_diabetes.pipelines.ingestion.nodes import (
    build_ingestion_reports,
    save_ingestion_audit,
    summarize_dataset,
    validate_required_columns,
)


def test_validate_required_columns_passes_when_columns_exist():
    df = pd.DataFrame({"SEQN": [1], "DIQ010": [2]})

    missing = validate_required_columns(df, ["SEQN", "DIQ010"], "DIQ_L")

    assert missing == []


def test_validate_required_columns_raises_when_column_is_missing():
    df = pd.DataFrame({"SEQN": [1]})

    with pytest.raises(ValueError, match="DIQ010"):
        validate_required_columns(df, ["SEQN", "DIQ010"], "DIQ_L")


def test_summarize_dataset_counts_rows_columns_and_missing_values():
    df = pd.DataFrame({"SEQN": [1, 2], "LBXGH": [6.2, None]})

    summary = summarize_dataset(df, "GHB_L")

    assert summary["dataset_name"] == "GHB_L"
    assert summary["rows"] == 2
    assert summary["columns"] == 2
    assert summary["missing_values"] == 1
    assert summary["column_names"] == "SEQN,LBXGH"


def test_build_ingestion_reports_generates_audit_for_all_sources():
    params = {
        "required_columns": {
            "nhanes_demo_raw": ["SEQN", "RIDAGEYR", "RIAGENDR", "RIDRETH3"],
            "nhanes_diq_raw": ["SEQN", "DIQ010"],
            "nhanes_bmx_raw": ["SEQN", "BMXBMI", "BMXWT", "BMXHT"],
            "nhanes_ghb_raw": ["SEQN", "LBXGH"],
            "nhanes_glu_raw": ["SEQN", "LBXGLU"],
            "nhanes_paq_raw": ["SEQN"],
            "nhanes_slq_raw": ["SEQN"],
            "nhanes_bpxo_raw": ["SEQN"],
        }
    }

    audit, summary = build_ingestion_reports(
        nhanes_demo_raw=pd.DataFrame(
            {"SEQN": [1], "RIDAGEYR": [45], "RIAGENDR": [1], "RIDRETH3": [3]}
        ),
        nhanes_diq_raw=pd.DataFrame({"SEQN": [1], "DIQ010": [2]}),
        nhanes_bmx_raw=pd.DataFrame(
            {"SEQN": [1], "BMXBMI": [27.5], "BMXWT": [75.0], "BMXHT": [170.0]}
        ),
        nhanes_ghb_raw=pd.DataFrame({"SEQN": [1], "LBXGH": [5.4]}),
        nhanes_glu_raw=pd.DataFrame({"SEQN": [1], "LBXGLU": [96]}),
        nhanes_paq_raw=pd.DataFrame({"SEQN": [1]}),
        nhanes_slq_raw=pd.DataFrame({"SEQN": [1]}),
        nhanes_bpxo_raw=pd.DataFrame({"SEQN": [1]}),
        diabetes_thresholds=pd.DataFrame(
            {
                "variable": ["LBXGH"],
                "criterio": [">="],
                "valor": [6.5],
                "descripcion": ["A1C compatible con diabetes"],
            }
        ),
        params=params,
    )

    assert len(audit) == 9
    assert len(summary) == 9
    assert set(audit["status"]) == {"ok"}
    assert "umbrales_diabetes" in set(audit["dataset_name"])


def test_save_ingestion_audit_writes_sqlite_table(tmp_path):
    audit = pd.DataFrame(
        {
            "run_id": ["run-1"],
            "execution_timestamp": ["2026-06-13T00:00:00+00:00"],
            "dataset_key": ["nhanes_demo_raw"],
            "dataset_name": ["DEMO_L"],
            "rows": [1],
            "columns": [4],
            "missing_values": [0],
            "required_columns": ["SEQN,RIDAGEYR,RIAGENDR,RIDRETH3"],
            "missing_required_columns": [""],
            "status": ["ok"],
        }
    )
    db_path = tmp_path / "diabetes_nhanes.db"

    result = save_ingestion_audit(audit, {"audit_db_path": str(db_path)})

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute("select count(*) from ingestion_audit").fetchone()[0]

    assert result["rows_saved"] == 1
    assert rows == 1
