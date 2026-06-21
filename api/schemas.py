"""Contratos Pydantic (request/response) de la API.

`protected_namespaces=()` silencia el aviso de Pydantic v2 por los campos que
empiezan con `model_` (p. ej. `model_version`, `model_name`).
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

_NO_PROTECT = {"protected_namespaces": ()}


# --------------------------------------------------------------------------- #
# Estado / metadatos generales
# --------------------------------------------------------------------------- #
class RootResponse(BaseModel):
    name: str
    version: str
    disclaimer: str
    docs: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    metrics_loaded: bool
    model_version: str | None = None

    model_config = _NO_PROTECT


class ModelInfoResponse(BaseModel):
    model_name: str | None
    model_version: str
    n_features: int

    model_config = _NO_PROTECT


# --------------------------------------------------------------------------- #
# Features y umbrales
# --------------------------------------------------------------------------- #
class FeatureMeta(BaseModel):
    name: str
    label: str
    dtype: str
    user_facing: bool
    is_derived: bool
    default: float | None = None
    min: float | None = None
    max: float | None = None
    unit: str | None = None


class FeaturesResponse(BaseModel):
    n_features: int
    feature_names: list[str]
    features: list[FeatureMeta]


class ThresholdItem(BaseModel):
    variable: str
    op: str
    value: float
    description: str | None = None


class ThresholdsResponse(BaseModel):
    thresholds: list[ThresholdItem]


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #
class ModelComparisonResponse(BaseModel):
    models: list[dict[str, Any]]


class ConfusionMatrixResponse(BaseModel):
    labels: list[str]
    index: list[str]
    columns: list[str]
    matrix: list[list[int]]


class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    importances: list[FeatureImportanceItem]


# --------------------------------------------------------------------------- #
# Estadísticas poblacionales
# --------------------------------------------------------------------------- #
class SummaryResponse(BaseModel):
    n_participants: int
    n_positive: int | None = None
    n_negative: int | None = None
    positive_rate: float | None = None


class DistributionBucket(BaseModel):
    key: str
    count: int
    positive_rate: float | None = None


class DistributionResponse(BaseModel):
    by: str
    buckets: list[DistributionBucket]


# --------------------------------------------------------------------------- #
# Predicción
# --------------------------------------------------------------------------- #
class PredictRequest(BaseModel):
    RIDAGEYR: float
    RIAGENDR: int
    BMXBMI: float
    LBXGH: float
    LBXGLU: float
    INDFMPIR: float | None = None
    BMXWAIST: float | None = None
    RIDRETH3: float | None = None

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
    risk_band: str
    threshold: float
    model_version: str

    model_config = _NO_PROTECT


class BatchPredictRequest(BaseModel):
    items: list[dict[str, float | int | None]] = Field(
        ...,
        min_length=1,
        description="Lista de registros; cada uno mapea feature -> valor.",
        json_schema_extra={
            "example": {
                "items": [
                    {"RIDAGEYR": 55, "RIAGENDR": 1, "BMXBMI": 31.5,
                     "LBXGH": 6.8, "LBXGLU": 130, "INDFMPIR": 2.1},
                    {"RIDAGEYR": 30, "RIAGENDR": 2, "BMXBMI": 22.0,
                     "LBXGH": 5.1, "LBXGLU": 90, "INDFMPIR": 3.5},
                ]
            }
        },
    )


class BatchPredictItem(BaseModel):
    prediction: int
    label: str
    probability: float
    risk_band: str


class BatchPredictResponse(BaseModel):
    n: int
    threshold: float
    model_version: str
    results: list[BatchPredictItem]

    model_config = _NO_PROTECT


class PredictionsResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[dict[str, Any]]
