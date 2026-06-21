"""Endpoints de predicción: individual, por lote y muestra de predicciones."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..artifacts import ArtifactStore, get_store
from ..config import Settings, get_settings
from ..schemas import (
    BatchPredictItem,
    BatchPredictRequest,
    BatchPredictResponse,
    PredictionsResponse,
    PredictRequest,
    PredictResponse,
)
from ..services import model_service

router = APIRouter(tags=["prediccion"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    req: PredictRequest,
    store: ArtifactStore = Depends(get_store),
    s: Settings = Depends(get_settings),
) -> PredictResponse:
    results, version = model_service.predict([req.model_dump()], store, s)
    return PredictResponse(**results[0], threshold=s.decision_threshold, model_version=version)


@router.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(
    req: BatchPredictRequest,
    store: ArtifactStore = Depends(get_store),
    s: Settings = Depends(get_settings),
) -> BatchPredictResponse:
    if len(req.items) > s.max_batch_rows:
        raise HTTPException(
            status_code=413,
            detail=f"Máximo {s.max_batch_rows} filas por lote (recibidas {len(req.items)}).",
        )
    results, version = model_service.predict(req.items, store, s)
    return BatchPredictResponse(
        n=len(results),
        threshold=s.decision_threshold,
        model_version=version,
        results=[BatchPredictItem(**r) for r in results],
    )


@router.get("/predictions", response_model=PredictionsResponse)
def predictions(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    store: ArtifactStore = Depends(get_store),
) -> PredictionsResponse:
    """Muestra paginada de predicciones del test set (`predictions.csv`)."""
    df = store.predictions()
    page = df.iloc[offset : offset + limit]
    return PredictionsResponse(
        total=int(len(df)),
        limit=limit,
        offset=offset,
        items=page.to_dict(orient="records"),
    )
