"""Nodos del pipeline de reporting (feature/c).

Convierte los artefactos del modelado en reportes visuales para el dashboard y la
documentación final.
"""
from __future__ import annotations

import logging

import matplotlib

matplotlib.use("Agg")  # backend sin display, necesario en Docker/CI
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)


def plot_confusion_matrix(cm_df: pd.DataFrame):
    """Renderiza la matriz de confusión como figura."""
    fig, ax = plt.subplots(figsize=(4.5, 4))
    im = ax.imshow(cm_df.values, cmap="Blues")
    ax.set_xticks(range(len(cm_df.columns)), labels=cm_df.columns)
    ax.set_yticks(range(len(cm_df.index)), labels=cm_df.index)
    ax.set_xlabel("Predicho")
    ax.set_ylabel("Real")
    ax.set_title("Matriz de confusión")
    for i in range(cm_df.shape[0]):
        for j in range(cm_df.shape[1]):
            ax.text(
                j, i, int(cm_df.values[i, j]), ha="center", va="center", color="black"
            )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    return fig


def plot_feature_importance(fi_df: pd.DataFrame):
    """Renderiza el top-15 de importancia de variables."""
    top = fi_df.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.barh(top["feature"], top["importance"], color="#2b6cb0")
    ax.set_title("Importancia de variables (top 15)")
    ax.set_xlabel("Importancia")
    fig.tight_layout()
    return fig
