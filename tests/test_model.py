"""Tests del pipeline de modelado (feature/c) — version mejorada."""
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
    n = 400
    age = rng.integers(18, 80, n)
    waist = rng.normal(95, 15, n)
    # target con senal real (no trivial) + ruido
    logit = -6 + 0.05 * age + 0.02 * waist + rng.normal(0, 1, n)
    y = (1 / (1 + np.exp(-logit)) > 0.5).astype(int)
    return pd.DataFrame({
        "SEQN": np.arange(n),
        "RIDAGEYR": age,
        "RIAGENDR": rng.integers(1, 3, n),
        "BMXBMI": rng.normal(28, 6, n),
        "BMXWAIST": waist,
        "diabetes_target": y,
    })


@pytest.fixture
def params() -> dict:
    return {
        "test_size": 0.25, "random_state": 42, "cv_folds": 3,
        "balance_method": "class_weight", "selection_metric": "f1",
        "scale_features": True, "tune_hyperparams": False,
    }


def test_split_excludes_id_and_target(model_input, params):
    split = split_data(model_input, params)
    assert "SEQN" not in split["feature_cols"]
    assert "diabetes_target" not in split["feature_cols"]
    assert len(split["X_train"]) + len(split["X_test"]) == len(model_input)


def test_split_raises_without_target(params):
    bad = pd.DataFrame({"SEQN": [1, 2], "RIDAGEYR": [40, 50]})
    with pytest.raises(ValueError):
        split_data(bad, params)


def test_full_modeling_flow_with_threshold(model_input, params):
    split = split_data(model_input, params)
    models = train_models(split, params)
    assert {"logistic_regression", "random_forest", "gradient_boosting"}.issubset(set(models))

    evaluation = evaluate_models(models, split)
    # PR-AUC presente en la comparacion
    assert "pr_auc" in evaluation["per_model"]["logistic_regression"]

    final = select_and_finalize(models, evaluation, split, params)
    bundle = final["model_bundle"]
    assert "model" in bundle and "feature_cols" in bundle
    assert "threshold" in bundle and 0.0 <= bundle["threshold"] <= 1.0
    assert 0.0 <= final["metrics"]["metrics"]["roc_auc"] <= 1.0
    assert len(final["predictions"]) == len(split["X_test"])
    assert final["confusion_matrix"].shape == (2, 2)


def test_selection_metric_is_respected(model_input, params):
    split = split_data(model_input, params)
    models = train_models(split, params)
    evaluation = evaluate_models(models, split)
    final = select_and_finalize(models, evaluation, split, params)
    assert final["metrics"]["selection_metric"] == "f1"
