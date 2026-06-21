"""Endpoints de estadísticas poblacionales (vista ejecutiva)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..artifacts import ArtifactStore, get_store
from ..config import Settings, get_settings
from ..schemas import DistributionResponse, SummaryResponse
from ..services import stats_service

router = APIRouter(prefix="/stats", tags=["estadisticas"])


@router.get("/summary", response_model=SummaryResponse)
def summary(
    store: ArtifactStore = Depends(get_store),
    s: Settings = Depends(get_settings),
) -> SummaryResponse:
    return SummaryResponse(**stats_service.summary(store, s))


@router.get("/distribution", response_model=DistributionResponse)
def distribution(
    by: str = Query("age_group", description="age_group | bmi_category | RIAGENDR | columna existente"),
    store: ArtifactStore = Depends(get_store),
    s: Settings = Depends(get_settings),
) -> DistributionResponse:
    try:
        return DistributionResponse(**stats_service.distribution(store, s, by))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
