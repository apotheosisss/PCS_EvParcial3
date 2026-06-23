"""Nodos del pipeline de modelado (feature/c) — version mejorada.

Mejoras (ver plan de mejora):
  - Pipeline con imputacion + escalado (ajustados solo con train -> sin fuga).
  - Balance de clases configurable: class_weight | smote | smoteenn.
  - Seleccion del mejor modelo por metrica configurable (f1 | pr_auc | roc_auc | recall).
  - Umbral de decision optimizado (max F1 sobre probabilidades OOF de train via CV).
  - Tuning opcional de hiperparametros (RandomizedSearchCV + StratifiedKFold).
  - Evaluacion con PR-AUC ademas de las metricas base.
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.feature_selection import SelectFromModel
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_predict,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

ID_COL = "SEQN"
TARGET = "diabetes_target"


def split_data(model_input: pd.DataFrame, params: dict[str, Any]) -> dict[str, Any]:
    """Separa en train/test estratificado por el target."""
    if TARGET not in model_input.columns:
        raise ValueError(f"'{TARGET}' no esta en model_input.")

    feature_cols = [c for c in model_input.columns if c not in (ID_COL, TARGET)]
    X = model_input[feature_cols]
    y = model_input[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=params.get("test_size", 0.2),
        random_state=params.get("random_state", 42),
        stratify=y,
    )
    logger.info("Split: train=%d test=%d features=%d", len(X_train), len(X_test), len(feature_cols))
    return {
        "X_train": X_train, "X_test": X_test,
        "y_train": y_train, "y_test": y_test,
        "feature_cols": feature_cols,
    }


# --------------------------------------------------------------------------- #
# Construccion de pipelines (imputer + scaler + [sampler] + clf)
# --------------------------------------------------------------------------- #
def _param_distributions() -> dict[str, dict]:
    """Rejillas pequenas para RandomizedSearchCV (prefijo clf__)."""
    return {
        "logistic_regression": {"clf__C": [0.01, 0.1, 1.0, 10.0]},
        "random_forest": {
            "clf__n_estimators": [200, 300, 500],
            "clf__max_depth": [None, 8, 16],
            "clf__min_samples_leaf": [1, 2, 5],
        },
        "gradient_boosting": {
            "clf__learning_rate": [0.05, 0.1, 0.2],
            "clf__max_iter": [200, 400],
            "clf__max_depth": [None, 3, 6],
        },
        "xgboost": {
            "clf__max_depth": [3, 6, 9],
            "clf__learning_rate": [0.05, 0.1, 0.2],
            "clf__n_estimators": [200, 400],
        },
        "lightgbm": {
            "clf__num_leaves": [31, 63],
            "clf__learning_rate": [0.05, 0.1],
            "clf__n_estimators": [200, 400],
        },
        "catboost": {
            "clf__depth": [4, 6, 8],
            "clf__learning_rate": [0.05, 0.1],
        },
    }


def _base_estimators(
    params: dict[str, Any], use_class_weight: bool, scale_pos_weight: float = 1.0
) -> dict[str, Any]:
    rs = params.get("random_state", 42)
    cw = "balanced" if use_class_weight else None
    est: dict[str, Any] = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight=cw),
        "random_forest": RandomForestClassifier(
            n_estimators=300, class_weight=cw, random_state=rs, n_jobs=-1
        ),
        "gradient_boosting": HistGradientBoostingClassifier(
            class_weight=cw, random_state=rs
        ),
    }
    # Modelos de boosting externos (import perezoso: se omiten si no estan instalados).
    try:
        from xgboost import XGBClassifier
        est["xgboost"] = XGBClassifier(
            n_estimators=300, learning_rate=0.1, max_depth=6,
            scale_pos_weight=scale_pos_weight if use_class_weight else 1.0,
            eval_metric="logloss", tree_method="hist", random_state=rs, n_jobs=-1,
        )
    except ImportError:
        logger.warning("xgboost no instalado; se omite ese modelo")
    try:
        from lightgbm import LGBMClassifier
        est["lightgbm"] = LGBMClassifier(
            n_estimators=300, learning_rate=0.1, class_weight=cw,
            random_state=rs, n_jobs=-1, verbose=-1,
        )
    except ImportError:
        logger.warning("lightgbm no instalado; se omite ese modelo")
    try:
        from catboost import CatBoostClassifier
        est["catboost"] = CatBoostClassifier(
            iterations=300, learning_rate=0.1, depth=6, random_seed=rs, verbose=False,
            auto_class_weights="Balanced" if use_class_weight else None,
        )
    except ImportError:
        logger.warning("catboost no instalado; se omite ese modelo")
    return est


def _make_pipeline(estimator, params: dict[str, Any], balance_method: str):
    """Pipeline imputer(+scaler)(+sampler)+clf. Usa imblearn si hay sampling."""
    pre = [("imputer", SimpleImputer(strategy="median"))]
    if params.get("scale_features", True):
        pre.append(("scaler", StandardScaler()))

    # Seleccion automatica de features (parsimonia): conserva las top-N por
    # importancia de un RandomForest. Evita el ruido de la cola de baja importancia.
    max_features = params.get("max_features")
    if params.get("feature_selection", False) and max_features:
        rs = params.get("random_state", 42)
        selector = SelectFromModel(
            RandomForestClassifier(n_estimators=100, random_state=rs, n_jobs=-1),
            max_features=int(max_features), threshold=-np.inf,
        )
        pre.append(("selector", selector))

    if balance_method in ("smote", "smoteenn"):
        from imblearn.combine import SMOTEENN
        from imblearn.over_sampling import SMOTE
        from imblearn.pipeline import Pipeline as ImbPipeline

        rs = params.get("random_state", 42)
        sampler = SMOTE(random_state=rs) if balance_method == "smote" else SMOTEENN(random_state=rs)
        return ImbPipeline(pre + [("sampler", sampler), ("clf", estimator)])

    return Pipeline(pre + [("clf", estimator)])


def train_models(split: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
    """Entrena los pipelines; tuning opcional con RandomizedSearchCV."""
    balance_method = params.get("balance_method", "class_weight")
    use_cw = balance_method == "class_weight"
    rs = params.get("random_state", 42)
    cv_folds = int(params.get("cv_folds", 5))
    tune = bool(params.get("tune_hyperparams", False))

    y = split["y_train"]
    n_pos = max(int((y == 1).sum()), 1)
    n_neg = int((y == 0).sum())
    scale_pos_weight = n_neg / n_pos
    estimators = _base_estimators(params, use_cw, scale_pos_weight)
    grids = _param_distributions()
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=rs)
    tune_cv = StratifiedKFold(n_splits=min(3, cv_folds), shuffle=True, random_state=rs)
    fitted = {}

    for name, est in estimators.items():
        pipe = _make_pipeline(est, params, balance_method)
        if tune and name in grids:
            search = RandomizedSearchCV(
                pipe, grids[name], n_iter=min(8, _grid_size(grids[name])),
                scoring="f1", cv=tune_cv, random_state=rs, n_jobs=-1, refit=True,
            )
            search.fit(split["X_train"], split["y_train"])
            fitted[name] = search.best_estimator_
            logger.info("Tuned %s -> %s (f1_cv=%.4f)", name, search.best_params_, search.best_score_)
        else:
            pipe.fit(split["X_train"], split["y_train"])
            fitted[name] = pipe
            logger.info("Modelo entrenado: %s (balance=%s)", name, balance_method)
    return fitted


def _grid_size(grid: dict) -> int:
    n = 1
    for v in grid.values():
        n *= len(v)
    return n


# --------------------------------------------------------------------------- #
# Evaluacion
# --------------------------------------------------------------------------- #
def _metrics_at(y, proba, threshold: float) -> dict[str, float]:
    pred = (proba >= threshold).astype(int)
    return {
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "precision": round(float(precision_score(y, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y, proba)), 4),
        "pr_auc": round(float(average_precision_score(y, proba)), 4),
    }


def evaluate_models(models: dict[str, Any], split: dict[str, Any]) -> dict[str, Any]:
    """Evalua cada modelo en test (umbral 0.5 para la tabla comparativa)."""
    comparison = {}
    for name, model in models.items():
        proba = model.predict_proba(split["X_test"])[:, 1]
        comparison[name] = _metrics_at(split["y_test"], proba, 0.5)
    comparison_df = pd.DataFrame(comparison).T.reset_index(names="model")
    logger.info("Comparacion (umbral 0.5):\n%s", comparison_df.to_string(index=False))
    return {"comparison": comparison_df, "per_model": comparison}


def _best_threshold(y_true, proba) -> float:
    """Umbral que maximiza F1 sobre la curva precision-recall."""
    prec, rec, thr = precision_recall_curve(y_true, proba)
    f1 = (2 * prec * rec) / (prec + rec + 1e-12)
    # thr tiene len-1 respecto a prec/rec; alinear
    best_idx = int(np.nanargmax(f1[:-1])) if len(thr) else 0
    return float(thr[best_idx]) if len(thr) else 0.5


def _conformal_qhat(scores: np.ndarray, alpha: float) -> float:
    """Quantil de conformidad (split-conformal / LAC) para cobertura 1-alpha."""
    n = len(scores)
    if n == 0:
        return 1.0
    level = min(1.0, np.ceil((n + 1) * (1 - alpha)) / n)
    return float(np.quantile(scores, level, method="higher"))


def select_and_finalize(
    models: dict[str, Any], evaluation: dict[str, Any], split: dict[str, Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    """Elige el mejor modelo, lo CALIBRA (holdout), fija umbral y aplica conformal."""
    metric = params.get("selection_metric", "f1")
    rs = params.get("random_state", 42)
    calibrate = bool(params.get("calibrate", True))
    cal_method = params.get("calibration_method", "isotonic")
    alpha = float(params.get("conformal_alpha", 0.1))
    per_model = evaluation["per_model"]

    best_name = max(per_model, key=lambda m: per_model[m].get(metric, 0.0))
    best_base = models[best_name]
    feature_cols = split["feature_cols"]
    X_train, y_train = split["X_train"], split["y_train"]
    X_test, y_test = split["X_test"], split["y_test"]
    logger.info("Mejor modelo por %s: %s", metric, best_name)

    # Holdout de calibracion desde train (sin CV anidado -> rapido y sin fuga).
    X_fit, X_cal, y_fit, y_cal = train_test_split(
        X_train, y_train, test_size=0.3, random_state=rs, stratify=y_train
    )
    base_fit = clone(best_base).fit(X_fit, y_fit)
    if calibrate:
        final_model = CalibratedClassifierCV(FrozenEstimator(base_fit), method=cal_method).fit(X_cal, y_cal)
        logger.info("Modelo calibrado (%s) sobre holdout", cal_method)
    else:
        final_model = base_fit

    # Umbral optimo + conformidad sobre el holdout de calibracion (out-of-sample del fit).
    cal_full = final_model.predict_proba(X_cal)
    threshold = _best_threshold(y_cal.values, cal_full[:, 1])
    logger.info("Umbral optimo (max F1 holdout): %.4f", threshold)
    yc = y_cal.values.astype(int)
    cal_scores = 1.0 - cal_full[np.arange(len(yc)), yc]
    qhat = _conformal_qhat(cal_scores, alpha)

    # Metricas finales en test (modelo calibrado).
    proba_full = final_model.predict_proba(X_test)
    proba = proba_full[:, 1]
    metrics_05 = _metrics_at(y_test, proba, 0.5)
    metrics_opt = _metrics_at(y_test, proba, threshold)
    brier = round(float(brier_score_loss(y_test, proba)), 4)

    yte = y_test.values.astype(int)
    in_set = (1.0 - proba_full) <= qhat
    covered = float(in_set[np.arange(len(yte)), yte].mean())
    avg_set_size = float(in_set.sum(axis=1).mean())

    preds = pd.DataFrame({
        "y_true": y_test.values,
        "y_pred": (proba >= threshold).astype(int),
        "probability": np.round(proba, 4),
    })
    cm = confusion_matrix(y_test, (proba >= threshold).astype(int))
    cm_df = pd.DataFrame(cm, index=["real_0", "real_1"], columns=["pred_0", "pred_1"])

    perm = permutation_importance(
        final_model, X_test, y_test, n_repeats=3, random_state=rs, scoring="roc_auc", n_jobs=-1
    )
    fi_df = (
        pd.DataFrame({"feature": feature_cols, "importance": np.round(perm.importances_mean, 4)})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    metrics = {
        "best_model": best_name,
        "selection_metric": metric,
        "decision_threshold": round(threshold, 4),
        "calibrated": calibrate,
        "calibration_method": cal_method if calibrate else None,
        "brier_score": brier,
        "conformal_alpha": alpha,
        "conformal_coverage": round(covered, 4),
        "conformal_avg_set_size": round(avg_set_size, 4),
        "metrics": metrics_opt,
        "metrics_threshold_0.5": metrics_05,
        "all_models": per_model,
        "n_features": len(feature_cols),
    }
    bundle = {
        "model": final_model,
        "model_name": best_name,
        "feature_cols": feature_cols,
        "feature_means": X_train.mean().to_dict(),
        "threshold": round(threshold, 4),
        "calibrated": calibrate,
        "conformal_qhat": round(qhat, 4),
        "conformal_alpha": alpha,
        "model_version": "v3.0.0",
    }
    return {
        "model_bundle": bundle,
        "metrics": metrics,
        "comparison": evaluation["comparison"],
        "predictions": preds,
        "confusion_matrix": cm_df,
        "feature_importance": fi_df,
    }
