"""Pipeline de modelado (feature/c)."""
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    evaluate_models,
    select_and_finalize,
    split_data,
    train_models,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                split_data,
                inputs=["model_input", "params:modeling"],
                outputs="data_split",
                name="split_data",
            ),
            node(
                train_models,
                inputs=["data_split", "params:modeling"],
                outputs="trained_models",
                name="train_models",
            ),
            node(
                evaluate_models,
                inputs=["trained_models", "data_split"],
                outputs="evaluation",
                name="evaluate_models",
            ),
            node(
                select_and_finalize,
                inputs=["trained_models", "evaluation", "data_split"],
                outputs={
                    "model_bundle": "model_bundle",
                    "metrics": "model_metrics",
                    "comparison": "model_comparison",
                    "predictions": "model_predictions",
                    "confusion_matrix": "confusion_matrix_data",
                    "feature_importance": "feature_importance",
                },
                name="select_and_finalize",
            ),
        ]
    )
