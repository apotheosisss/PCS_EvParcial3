"""App factory de la API FastAPI (feature/c).

Levantar:
    uvicorn api.main:app --reload      ->  docs en http://localhost:8000/docs

Endpoints (agrupados en routers):
    estado        GET  /                 raíz + disclaimer
                  GET  /health           estado del servicio
    modelo        GET  /model-info       nombre y versión del modelo
                  GET  /features         features esperadas + metadatos
                  GET  /thresholds       umbrales clínicos educativos
    reporting     GET  /metrics          métricas del modelo
                  GET  /model-comparison comparación de modelos
                  GET  /confusion-matrix matriz de confusión (JSON)
                  GET  /feature-importance importancia de variables (JSON)
                  GET  /report/{name}.png figura PNG (descarga)
    estadisticas  GET  /stats/summary    KPIs poblacionales
                  GET  /stats/distribution distribución por variable
    prediccion    POST /predict          predicción individual
                  POST /predict/batch    predicción por lote
                  GET  /predictions      muestra de predicciones del test set

Disclaimer: herramienta analítica/educativa basada en datos públicos NHANES.
NO es un diagnóstico clínico.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .artifacts import ArtifactUnavailable
from .config import get_settings
from .routers import health, metadata, predict, reporting, stats
from .schemas import RootResponse


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title=f"{s.project_name} API",
        version=s.api_version,
        description=(
            "Predicción y analítica de riesgo de diabetes con datos NHANES.\n\n"
            f"⚠️ {s.disclaimer}"
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(s.cors_origins),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(ArtifactUnavailable)
    async def _artifact_unavailable(request: Request, exc: ArtifactUnavailable) -> JSONResponse:
        # 503: el servicio está vivo pero el modelo/artefacto aún no se ha generado.
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.get("/", response_model=RootResponse, tags=["estado"])
    def root() -> RootResponse:
        return RootResponse(
            name=f"{s.project_name} API",
            version=s.api_version,
            disclaimer=s.disclaimer,
            docs="/docs",
        )

    for module in (health, metadata, reporting, stats, predict):
        app.include_router(module.router)

    return app


app = create_app()
