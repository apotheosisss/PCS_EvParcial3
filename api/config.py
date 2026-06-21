"""Configuración de la API leída desde variables de entorno.

Mantiene compatibilidad con las variables ya usadas (`MODEL_PATH`, `METRICS_PATH`)
y añade las nuevas con valores por defecto sensatos. Todas las rutas son relativas
al directorio de trabajo (la raíz del proyecto), igual que el resto del sistema.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


def _split_origins(raw: str) -> tuple[str, ...]:
    return tuple(o.strip() for o in raw.split(",") if o.strip())


@dataclass(frozen=True)
class Settings:
    project_name: str = os.getenv("PROJECT_NAME", "DiabetesNHANES")
    api_version: str = "1.0.0"

    # --- Artefactos del pipeline Kedro ---
    model_path: Path = Path(os.getenv("MODEL_PATH", "data/06_models/model.pkl"))
    metrics_path: Path = Path(os.getenv("METRICS_PATH", "data/08_reporting/metrics.json"))
    model_comparison_path: Path = Path(
        os.getenv("MODEL_COMPARISON_PATH", "data/08_reporting/model_comparison.csv")
    )
    confusion_matrix_path: Path = Path(
        os.getenv("CONFUSION_MATRIX_PATH", "data/08_reporting/confusion_matrix.csv")
    )
    feature_importance_path: Path = Path(
        os.getenv("FEATURE_IMPORTANCE_PATH", "data/08_reporting/feature_importance.csv")
    )
    predictions_path: Path = Path(
        os.getenv("PREDICTIONS_PATH", "data/07_model_output/predictions.csv")
    )
    model_input_path: Path = Path(
        os.getenv("MODEL_INPUT_PATH", "data/05_model_input/model_input.csv")
    )
    feature_metadata_path: Path = Path(
        os.getenv("FEATURE_METADATA_PATH", "data/05_model_input/feature_metadata.json")
    )
    thresholds_path: Path = Path(
        os.getenv("THRESHOLDS_PATH", "data/01_raw/umbrales_diabetes.csv")
    )
    reporting_dir: Path = Path(os.getenv("REPORTING_DIR", "data/08_reporting"))

    # --- Dominio ---
    id_col: str = "SEQN"
    target_col: str = "diabetes_target"

    # --- Predicción ---
    decision_threshold: float = float(os.getenv("DECISION_THRESHOLD", "0.5"))
    risk_band_low: float = float(os.getenv("RISK_BAND_LOW", "0.33"))
    risk_band_high: float = float(os.getenv("RISK_BAND_HIGH", "0.66"))
    max_batch_rows: int = int(os.getenv("MAX_BATCH_ROWS", "1000"))

    # --- CORS ---
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: _split_origins(
            os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:5173,http://localhost:8501",
            )
        )
    )

    disclaimer: str = (
        "Resultado educativo basado en datos públicos NHANES. "
        "No reemplaza un diagnóstico clínico."
    )


@lru_cache
def get_settings() -> Settings:
    """Settings como singleton cacheado (apto para usarse como dependencia FastAPI)."""
    return Settings()
