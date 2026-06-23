"""Endpoint de salud del servicio."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..artifacts import ArtifactStore, get_store
from ..schemas import HealthResponse

router = APIRouter(tags=["estado"])


@router.get("/health", response_model=HealthResponse)
def health(store: ArtifactStore = Depends(get_store)) -> HealthResponse:
    version: str | None = None
    if store.model_loaded():
        try:
            version = store.bundle().get("model_version", "v1.0.0")
        except Exception:  # bundle ilegible: el servicio sigue vivo
            version = None
    return HealthResponse(
        status="ok",
        model_loaded=store.model_loaded(),
        metrics_loaded=store.metrics_available(),
        model_version=version,
    )
