"""Endpoints de reporting: métricas y artefactos de evaluación."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from ..artifacts import ArtifactStore, get_store
from ..config import Settings, get_settings
from ..schemas import (
    ConfusionMatrixResponse,
    FeatureImportanceResponse,
    ModelComparisonResponse,
)
from ..services import reporting_service

router = APIRouter(tags=["reporting"])

_REPORT_IMAGES = {"confusion_matrix", "feature_importance"}


@router.get("/metrics")
def metrics(store: ArtifactStore = Depends(get_store)) -> dict[str, Any]:
    """Métricas del modelo entrenado (`metrics.json`), tal cual."""
    return store.metrics()


@router.get("/model-comparison", response_model=ModelComparisonResponse)
def model_comparison(store: ArtifactStore = Depends(get_store)) -> ModelComparisonResponse:
    return ModelComparisonResponse(**reporting_service.comparison(store))


@router.get("/confusion-matrix", response_model=ConfusionMatrixResponse)
def confusion_matrix(store: ArtifactStore = Depends(get_store)) -> ConfusionMatrixResponse:
    return ConfusionMatrixResponse(**reporting_service.confusion_matrix(store))


@router.get("/feature-importance", response_model=FeatureImportanceResponse)
def feature_importance(
    top: int | None = Query(None, ge=1, le=200, description="Limita al top-N"),
    store: ArtifactStore = Depends(get_store),
) -> FeatureImportanceResponse:
    return FeatureImportanceResponse(**reporting_service.feature_importance(store, top))


@router.get("/report/{name}.png")
def report_image(name: str, s: Settings = Depends(get_settings)) -> FileResponse:
    """Sirve las figuras PNG de reporting (descarga / fallback visual)."""
    if name not in _REPORT_IMAGES:
        raise HTTPException(404, f"Imagen no disponible. Opciones: {sorted(_REPORT_IMAGES)}")
    path = s.reporting_dir / f"{name}.png"
    if not path.exists():
        raise HTTPException(503, f"Figura no generada: {path}. Ejecuta el pipeline de reporting.")
    return FileResponse(path, media_type="image/png", filename=f"{name}.png")
