"""Tests del pipeline de modelado (feature/c)."""
import numpy as np
import pandas as pd
import pytest

from nhanes_diabetes.pipelines.modeling.nodes import (
    evaluate_models,
    select_and_finalize,
    split_data,
    train_models,
)


@pytest.fixture
def model_input() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 300
    a1c = rng.normal(5.6, 1.2, n).clip(4, 14)
    glu = rng.normal(100, 25, n).clip(60, 300)
    return pd.DataFrame(
        {
            "SEQN": np.arange(n),
            "RIDAGEYR": rng.integers(18, 80, n),
            "RIAGENDR": rng.integers(1, 3, n),
            "BMXBMI": rng.normal(28, 6, n).clip(15, 60),
            "LBXGH": a1c,
            "LBXGLU": glu,
            "diabetes_target": ((a1c >= 6.5) | (glu >= 126)).astype(int),
        }
    )


@pytest.fixture
def params() -> dict:
    return {"test_size": 0.25, "random_state": 42}


def test_split_excludes_id_and_target(model_input, params):
    split = split_data(model_input, params)
    assert "SEQN" not in split["feature_cols"]
    assert "diabetes_target" not in split["feature_cols"]
    assert len(split["X_train"]) + len(split["X_test"]) == len(model_input)


def test_split_raises_without_target(params):
    bad = pd.DataFrame({"SEQN": [1, 2], "RIDAGEYR": [40, 50]})
    with pytest.raises(ValueError):
        split_data(bad, params)


def test_full_modeling_flow(model_input, params):
    split = split_data(model_input, params)
    models = train_models(split, params)
    assert set(models) == {"logistic_regression", "random_forest", "gradient_boosting"}

    evaluation = evaluate_models(models, split)
    final = select_and_finalize(models, evaluation, split)

    bundle = final["model_bundle"]
    assert "model" in bundle and "feature_cols" in bundle
    assert 0.0 <= final["metrics"]["metrics"]["roc_auc"] <= 1.0
    assert len(final["predictions"]) == len(split["X_test"])
    assert final["confusion_matrix"].shape == (2, 2)
