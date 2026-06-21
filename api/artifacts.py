"""Capa de acceso a los artefactos del pipeline, con caché en memoria.

Todos los endpoints leen sus datos desde aquí. Si un artefacto no existe (p. ej.
el pipeline aún no se ha ejecutado) se lanza `ArtifactUnavailable`, que la app
traduce a un HTTP 503 uniforme.
"""
from __future__ import annotations

import json
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from .config import Settings, get_settings


class ArtifactUnavailable(Exception):
    """El artefacto solicitado no existe todavía en disco."""

    def __init__(self, path: Path | str, hint: str = "") -> None:
        self.path = str(path)
        self.hint = hint or "Ejecuta 'kedro run' para generar los artefactos."
        super().__init__(f"Artefacto no disponible: {self.path}. {self.hint}")


class ArtifactStore:
    """Lee y cachea los artefactos del pipeline para servirlos por la API."""

    def __init__(self, settings: Settings) -> None:
        self._s = settings
        self._cache: dict[str, Any] = {}

    # -- utilidades --------------------------------------------------------
    def clear_cache(self) -> None:
        self._cache.clear()

    @staticmethod
    def _require(path: Path) -> Path:
        if not Path(path).exists():
            raise ArtifactUnavailable(path)
        return Path(path)

    def _csv(self, key: str, path: Path) -> pd.DataFrame:
        if key not in self._cache:
            self._cache[key] = pd.read_csv(self._require(path))
        return self._cache[key].copy()  # copia: el caller nunca muta la caché

    # -- modelo ------------------------------------------------------------
    def bundle(self) -> dict[str, Any]:
        if "bundle" not in self._cache:
            with open(self._require(self._s.model_path), "rb") as fh:
                self._cache["bundle"] = pickle.load(fh)
        return self._cache["bundle"]

    def model_loaded(self) -> bool:
        return Path(self._s.model_path).exists()

    # -- reporting ---------------------------------------------------------
    def metrics(self) -> dict[str, Any]:
        if "metrics" not in self._cache:
            text = self._require(self._s.metrics_path).read_text(encoding="utf-8")
            self._cache["metrics"] = json.loads(text)
        return self._cache["metrics"]

    def metrics_available(self) -> bool:
        return Path(self._s.metrics_path).exists()

    def model_comparison(self) -> pd.DataFrame:
        return self._csv("model_comparison", self._s.model_comparison_path)

    def confusion_matrix(self) -> pd.DataFrame:
        return self._csv("confusion_matrix", self._s.confusion_matrix_path)

    def feature_importance(self) -> pd.DataFrame:
        return self._csv("feature_importance", self._s.feature_importance_path)

    def predictions(self) -> pd.DataFrame:
        return self._csv("predictions", self._s.predictions_path)

    # -- datos / metadatos -------------------------------------------------
    def model_input(self) -> pd.DataFrame:
        return self._csv("model_input", self._s.model_input_path)

    def thresholds(self) -> pd.DataFrame:
        return self._csv("thresholds", self._s.thresholds_path)

    def feature_metadata(self) -> dict[str, Any] | None:
        """Metadata opcional de feature/b; devuelve None si no fue entregada."""
        path = Path(self._s.feature_metadata_path)
        if not path.exists():
            return None
        if "feature_metadata" not in self._cache:
            self._cache["feature_metadata"] = json.loads(
                path.read_text(encoding="utf-8")
            )
        return self._cache["feature_metadata"]


@lru_cache
def get_store() -> ArtifactStore:
    """ArtifactStore como singleton (apto como dependencia FastAPI)."""
    return ArtifactStore(get_settings())
