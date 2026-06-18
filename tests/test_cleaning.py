"""Tests del pipeline de limpieza (feature/b)."""
import sqlite3

import pandas as pd
import pytest

from nhanes_diabetes.pipelines.cleaning.nodes import (
    build_etl_audit,
    clean_and_impute,
    merge_nhanes_tables,
    replace_special_codes_with_nan,
    save_etl_audit,
    validate_ranges,
)

PARAMS = {
    "filter_adults": True,
    "adult_min_age": 18,
    "special_codes": {"DIQ010": [7, 9]},
    "generic_special_codes": [77, 99],
    "valid_ranges": {
        "RIDAGEYR": [18, 80],
        "BMXBMI": [10, 70],
        "LBXGH": [3, 20],
        "LBXGLU": [30, 500],
    },
}


def _raw():
    demo = pd.DataFrame(
        {
            "SEQN": [1, 2, 3, 4],
            "RIDAGEYR": [50, 30, 9, 70],  # SEQN 3 es menor de edad
            "RIAGENDR": [1, 2, 1, 2],
            "RIDRETH3": [3, 4, 3, 6],
            "INDFMPIR": [2.0, 0.5, 1.0, 4.0],
        }
    )
    diq = pd.DataFrame({"SEQN": [1, 2, 4], "DIQ010": [1, 9, 2]})
    bmx = pd.DataFrame(
        {"SEQN": [1, 2, 4], "BMXBMI": [31.0, 24.0, 999.0], "BMXWAIST": [110, 80, 95]}
    )
    ghb = pd.DataFrame({"SEQN": [1, 2, 4], "LBXGH": [7.0, 5.4, 6.0]})
    glu = pd.DataFrame({"SEQN": [1, 4], "LBXGLU": [140, 100]})
    empty = pd.DataFrame({"SEQN": [1, 2, 4]})
    return demo, diq, bmx, ghb, glu, empty.copy(), empty.copy(), empty.copy()


def test_merge_one_row_per_seqn_and_adult_filter():
    merged = merge_nhanes_tables(*_raw(), PARAMS)
    assert merged["SEQN"].is_unique
    assert 3 not in merged["SEQN"].values  # menor de 18 filtrado
    assert {"DIQ010", "BMXBMI", "LBXGH", "LBXGLU"}.issubset(merged.columns)


def test_merge_raises_without_seqn():
    demo, diq, bmx, ghb, glu, paq, slq, bpxo = _raw()
    bad = bmx.drop(columns=["SEQN"])
    with pytest.raises(ValueError, match="SEQN"):
        merge_nhanes_tables(demo, diq, bad, ghb, glu, paq, slq, bpxo, PARAMS)


def test_special_codes_become_nan():
    merged = merge_nhanes_tables(*_raw(), PARAMS)
    out = replace_special_codes_with_nan(merged, PARAMS)
    assert pd.isna(out.loc[out.SEQN == 2, "DIQ010"].iloc[0])  # 9 -> NaN


def test_validate_ranges_sets_out_of_range_to_nan():
    merged = merge_nhanes_tables(*_raw(), PARAMS)
    out = validate_ranges(merged, PARAMS)
    assert pd.isna(out.loc[out.SEQN == 4, "BMXBMI"].iloc[0])  # 999 -> NaN


def test_clean_imputes_but_protects_target_sources():
    merged = merge_nhanes_tables(*_raw(), PARAMS)
    out = replace_special_codes_with_nan(merged, PARAMS)
    out = validate_ranges(out, PARAMS)
    clean = clean_and_impute(out, PARAMS)
    non_target = [c for c in clean.columns if c not in ("DIQ010", "LBXGH", "LBXGLU", "SEQN")]
    assert clean[non_target].isna().sum().sum() == 0
    # DIQ010 de SEQN 2 era 9 -> NaN y NO debe imputarse en cleaning
    assert pd.isna(clean.loc[clean.SEQN == 2, "DIQ010"].iloc[0])


def test_etl_audit_written_to_sqlite(tmp_path):
    merged = merge_nhanes_tables(*_raw(), PARAMS)
    clean = clean_and_impute(
        validate_ranges(replace_special_codes_with_nan(merged, PARAMS), PARAMS), PARAMS
    )
    audit = build_etl_audit(merged, clean, PARAMS)
    db = tmp_path / "diabetes_nhanes.db"
    res = save_etl_audit(audit, {"audit_db_path": str(db)})
    with sqlite3.connect(db) as conn:
        n = conn.execute("select count(*) from etl_audit").fetchone()[0]
    assert res["rows_saved"] == len(audit) and n == len(audit)
    assert (audit["stage"] == "overall").any()


def test_merge_keep_columns_allowlist():
    params = dict(PARAMS)
    params["keep_columns"] = {"demo": ["SEQN", "RIDAGEYR"], "diq": ["SEQN", "DIQ010"]}
    merged = merge_nhanes_tables(*_raw(), params)
    assert "RIAGENDR" not in merged.columns
    assert {"RIDAGEYR", "DIQ010", "BMXBMI"}.issubset(merged.columns)
