"""API FastAPI para servir el modelo de riesgo de diabetes (feature/c).

Endpoints:
    GET  /health       estado del servicio
    GET  /metrics      métricas del modelo entrenado
    GET  /features     features que espera el modelo
    GET  /model-info   nombre y versión del modelo
    POST /predict      predicción individual

Disclaimer: el modelo es una herramienta analítica/educativa basada en datos
públicos de NHANES. NO es un diagnóstico clínico.
"""
from __future__ import annotations

import json
import os
import pickle
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = Path(os.getenv("MODEL_PATH", "data/06_models/model.pkl"))
METRICS_PATH = Path(os.getenv("METRICS_PATH", "data/08_reporting/metrics.json"))

app = FastAPI(
    title="DiabetesNHANES API",
    description="Predicción de riesgo de diabetes con datos NHANES. Uso educativo.",
    version="1.0.0",
)

_bundle: dict[str, Any] | None = None


def _load_bundle() -> dict[str, Any]:
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise HTTPException(
                status_code=503,
                detail=f"Modelo no encontrado en {MODEL_PATH}. Ejecuta 'kedro run' primero.",
            )
        with open(MODEL_PATH, "rb") as fh:
            _bundle = pickle.load(fh)
    return _bundle


class PredictRequest(BaseModel):
    RIDAGEYR: float
    RIAGENDR: int
    BMXBMI: float
    LBXGH: float
    LBXGLU: float
    INDFMPIR: float | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "RIDAGEYR": 55,
                "RIAGENDR": 1,
                "BMXBMI": 31.5,
                "LBXGH": 6.8,
                "LBXGLU": 130,
                "INDFMPIR": 2.1,
            }
        }
    }


class PredictResponse(BaseModel):
    prediction: int
    label: str
    probability: float
    model_version: str


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model_loaded": MODEL_PATH.exists()}


@app.get("/metrics")
def metrics() -> dict[str, Any]:
    if not METRICS_PATH.exists():
        raise HTTPException(status_code=503, detail="Métricas no disponibles. Ejecuta el pipeline.")
    return json.loads(METRICS_PATH.read_text())


@app.get("/features")
def features() -> dict[str, Any]:
    bundle = _load_bundle()
    return {"features": bundle["feature_cols"], "n_features": len(bundle["feature_cols"])}


@app.get("/model-info")
def model_info() -> dict[str, Any]:
    bundle = _load_bundle()
    return {
        "model_name": bundle.get("model_name"),
        "model_version": bundle.get("model_version", "v1.0.0"),
        "n_features": len(bundle["feature_cols"]),
    }


def _build_row(payload: dict[str, Any], bundle: dict[str, Any]) -> pd.DataFrame:
    """Construye una fila con TODAS las features del modelo.

    Las features provistas en el payload se usan tal cual; el resto se rellena con
    la media del training set (almacenada en el bundle).
    """
    means = bundle.get("feature_means", {})
    row = {col: means.get(col, 0.0) for col in bundle["feature_cols"]}
    for k, v in payload.items():
        if v is not None and k in row:
            row[k] = v
    return pd.DataFrame([row])[bundle["feature_cols"]]


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    bundle = _load_bundle()
    X = _build_row(req.model_dump(), bundle)
    model = bundle["model"]
    proba = float(model.predict_proba(X)[:, 1][0])
    pred = int(proba >= 0.5)
    return PredictResponse(
        prediction=pred,
        label="riesgo_diabetes" if pred == 1 else "sin_riesgo",
        probability=round(proba, 4),
        model_version=bundle.get("model_version", "v1.0.0"),
    )
