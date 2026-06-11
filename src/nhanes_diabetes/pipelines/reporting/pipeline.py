"""Pipeline de reporting (feature/c)."""
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import plot_confusion_matrix, plot_feature_importance


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                plot_confusion_matrix,
                inputs="confusion_matrix_data",
                outputs="confusion_matrix_plot",
                name="plot_confusion_matrix",
            ),
            node(
                plot_feature_importance,
                inputs="feature_importance",
                outputs="feature_importance_plot",
                name="plot_feature_importance",
            ),
        ]
    )
