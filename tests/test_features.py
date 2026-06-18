"""Tests del pipeline de feature engineering (feature/b)."""
import numpy as np
import pandas as pd
import pytest

from nhanes_diabetes.pipelines.feature_engineering.nodes import (
    build_feature_metadata,
    create_derived_features,
    create_diabetes_target,
    encode_categorical_variables,
    select_final_features,
    validate_model_input,
)

FPARAMS = {
    "target_rule": {"diq010_positive": 1, "a1c_threshold": 6.5, "glucose_threshold": 126},
    "a1c_threshold": 6.5,
    "glucose_threshold": 126,
    "age_bins": [[18, 44], [45, 64], [65, 200]],
    "bmi_bins": {"underweight": 18.5, "normal": 25, "overweight": 30},
    "pir_bins": [1, 2, 4],
    "categorical_to_encode": ["RIDRETH3", "age_group", "bmi_category", "income_group"],
    "drop_constant": True,
    "drop_perfectly_correlated": False,
}


def _clean():
    return pd.DataFrame(
        {
            "SEQN": [1, 2, 3, 4, 5, 6],
            "RIDAGEYR": [50, 30, 60, 70, 40, 25],
            "RIAGENDR": [1, 2, 1, 2, 1, 2],
            "RIDRETH3": [3, 4, 3, 6, 3, 4],
            "INDFMPIR": [2.0, 0.5, 1.0, 4.0, 3.0, 0.8],
            "BMXBMI": [31.0, 24.0, 28.0, 33.0, 22.0, 26.0],
            "BMXWAIST": [110, 80, 95, 115, 78, 88],
            "DIQ010": [1.0, 2.0, 2.0, 2.0, 2.0, 2.0],
            "LBXGH": [7.0, 5.4, 6.0, 6.8, 5.0, 5.5],
            "LBXGLU": [140.0, 100.0, 110.0, 90.0, 95.0, 105.0],
        }
    )


def test_target_rule_cases():
    df = create_diabetes_target(_clean(), FPARAMS)
    t = dict(zip(df.SEQN, df.diabetes_target))
    assert t[1] == 1  # DIQ010==1 (y LBXGLU 140>=126)
    assert t[4] == 1  # A1C 6.8 >= 6.5
    assert t[2] == 0  # ningun criterio


def test_target_drops_undetermined_rows():
    df = _clean()
    df.loc[df.SEQN == 6, ["DIQ010", "LBXGH", "LBXGLU"]] = np.nan
    out = create_diabetes_target(df, FPARAMS)
    assert 6 not in out.SEQN.values
    assert out.diabetes_target.isna().sum() == 0


def test_derived_and_encoding_numeric():
    df = create_diabetes_target(_clean(), FPARAMS)
    df = create_derived_features(df, FPARAMS)
    assert df.loc[df.SEQN == 1, "has_obesity"].iloc[0] == 1  # BMI 31 >= 30
    assert df.loc[df.SEQN == 5, "has_obesity"].iloc[0] == 0  # BMI 22
    enc = encode_categorical_variables(df, FPARAMS)
    obj = [c for c in enc.columns if enc[c].dtype == object and c != "SEQN"]
    assert obj == []  # nada object salvo SEQN


def test_metadata_marks_user_facing():
    df = create_diabetes_target(_clean(), FPARAMS)
    df = create_derived_features(df, FPARAMS)
    df = select_final_features(encode_categorical_variables(df, FPARAMS), FPARAMS)
    meta = build_feature_metadata(df, FPARAMS)
    names = {f["name"]: f for f in meta["features"]}
    assert names["RIDAGEYR"]["user_facing"] is True
    assert names["has_obesity"]["is_derived"] is True


def test_validate_passes_on_good_input():
    df = create_diabetes_target(_clean(), FPARAMS)
    df = create_derived_features(df, FPARAMS)
    df = encode_categorical_variables(df, FPARAMS)
    df = select_final_features(df, FPARAMS)
    validate_model_input(df)  # no debe lanzar


def test_validate_raises_on_nulls_or_single_class():
    bad = pd.DataFrame({"SEQN": [1, 2], "diabetes_target": [1, 1], "x": [1.0, 2.0]})
    with pytest.raises(ValueError):
        validate_model_input(bad)  # una sola clase
    bad2 = pd.DataFrame({"SEQN": [1, 2], "diabetes_target": [0, 1], "x": [1.0, np.nan]})
    with pytest.raises(ValueError):
        validate_model_input(bad2)  # nulos en features
