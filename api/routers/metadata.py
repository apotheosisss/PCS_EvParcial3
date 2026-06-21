"""Endpoints de metadatos del modelo: info, features y umbrales."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..artifacts import ArtifactStore, get_store
from ..schemas import FeaturesResponse, ModelInfoResponse, ThresholdsResponse
from ..services import metadata_service

router = APIRouter(tags=["modelo"])


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info(store: ArtifactStore = Depends(get_store)) -> ModelInfoResponse:
    bundle = store.bundle()
    return ModelInfoResponse(
        model_name=bundle.get("model_name"),
        model_version=bundle.get("model_version", "v1.0.0"),
        n_features=len(bundle["feature_cols"]),
    )


@router.get("/features", response_model=FeaturesResponse)
def features(store: ArtifactStore = Depends(get_store)) -> FeaturesResponse:
    return FeaturesResponse(**metadata_service.build_features(store))


@router.get("/thresholds", response_model=ThresholdsResponse)
def thresholds(store: ArtifactStore = Depends(get_store)) -> ThresholdsResponse:
    return ThresholdsResponse(**metadata_service.get_thresholds(store))
