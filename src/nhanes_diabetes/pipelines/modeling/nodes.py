"""Nodos del pipeline de modelado (feature/c).

Entrena varios clasificadores baseline para diabetes_target, los compara y guarda
el mejor modelo junto con sus metadatos de features.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)

ID_COL = "SEQN"
TARGET = "diabetes_target"


def split_data(
    model_input: pd.DataFrame, params: dict[str, Any]
) -> dict[str, Any]:
    """Separa el dataset en train/test estratificado por el target.

    Devuelve un diccionario con los arrays y la lista de columnas de feature, para
    que el resto de nodos no dependa del orden de columnas.
    """
    if TARGET not in model_input.columns:
        raise ValueError(
            f"'{TARGET}' no está en model_input. ¿feature/b ya entregó el dataset? "
            "Ver docs/CONTRATO_FEATURE_B.md"
        )

    feature_cols = [c for c in model_input.columns if c not in (ID_COL, TARGET)]
    X = model_input[feature_cols]
    y = model_input[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=params.get("test_size", 0.2),
        random_state=params.get("random_state", 42),
        stratify=y,
    )
    logger.info(
        "Split: train=%d test=%d features=%d", len(X_train), len(X_test), len(feature_cols)
    )
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "feature_cols": feature_cols,
    }


def train_models(split: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Entrena los clasificadores baseline definidos en el Notion."""
    rs = params.get("random_state", 42)
    models = {
        "logistic_regression": LogisticRegression(
            max_iter=1000, class_weight="balanced"
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, class_weight="balanced", random_state=rs
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=rs),
    }
    for name, model in models.items():
        model.fit(split["X_train"], split["y_train"])
        logger.info("Modelo entrenado: %s", name)
    return models


def _metrics(model, X, y) -> dict[str, float]:
    pred = model.predict(X)
    proba = (
        model.predict_proba(X)[:, 1]
        if hasattr(model, "predict_proba")
        else pred.astype(float)
    )
    return {
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "precision": round(float(precision_score(y, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y, proba)), 4),
    }


def evaluate_models(
    models: dict[str, Any], split: dict[str, Any]
) -> dict[str, Any]:
    """Evalúa cada modelo en el test set y arma la tabla de comparación."""
    comparison = {}
    for name, model in models.items():
        comparison[name] = _metrics(model, split["X_test"], split["y_test"])
    comparison_df = pd.DataFrame(comparison).T.reset_index(names="model")
    logger.info("Comparación de modelos:\n%s", comparison_df.to_string(index=False))
    return {"comparison": comparison_df, "per_model": comparison}


def select_and_finalize(
    models: dict[str, Any],
    evaluation: dict[str, Any],
    split: dict[str, Any],
) -> dict[str, Any]:
    """Elige el mejor modelo por ROC-AUC y produce todos los artefactos finales."""
    per_model = evaluation["per_model"]
    best_name = max(per_model, key=lambda m: per_model[m]["roc_auc"])
    best_model = models[best_name]
    feature_cols = split["feature_cols"]
    logger.info("Mejor modelo: %s (roc_auc=%.4f)", best_name, per_model[best_name]["roc_auc"])

    # Predicciones sobre el test set
    X_test, y_test = split["X_test"], split["y_test"]
    proba = best_model.predict_proba(X_test)[:, 1]
    preds = pd.DataFrame(
        {
            "y_true": y_test.values,
            "y_pred": best_model.predict(X_test),
            "probability": np.round(proba, 4),
        }
    )

    # Matriz de confusión
    cm = confusion_matrix(y_test, best_model.predict(X_test))
    cm_df = pd.DataFrame(
        cm, index=["real_0", "real_1"], columns=["pred_0", "pred_1"]
    )

    # Feature importance (o coeficientes)
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
    elif hasattr(best_model, "coef_"):
        importances = np.abs(best_model.coef_[0])
    else:
        importances = np.zeros(len(feature_cols))
    fi_df = (
        pd.DataFrame({"feature": feature_cols, "importance": np.round(importances, 4)})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    metrics = {
        "best_model": best_name,
        "metrics": per_model[best_name],
        "all_models": per_model,
        "n_features": len(feature_cols),
    }

    # Bundle del modelo: lo que necesitan la API y el dashboard
    bundle = {
        "model": best_model,
        "model_name": best_name,
        "feature_cols": feature_cols,
        "feature_means": split["X_train"].mean().to_dict(),
        "model_version": "v1.0.0",
    }

    return {
        "model_bundle": bundle,
        "metrics": metrics,
        "comparison": evaluation["comparison"],
        "predictions": preds,
        "confusion_matrix": cm_df,
        "feature_importance": fi_df,
    }
