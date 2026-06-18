"""Pipeline de feature engineering NHANES (feature/b)."""
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    build_feature_metadata,
    create_derived_features,
    create_diabetes_target,
    encode_categorical_variables,
    select_final_features,
    validate_model_input,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                create_diabetes_target,
                inputs=["nhanes_clean", "params:features"],
                outputs="nhanes_targeted",
                name="create_diabetes_target",
            ),
            node(
                create_derived_features,
                inputs=["nhanes_targeted", "params:features"],
                outputs="nhanes_features",
                name="create_derived_features",
            ),
            node(
                encode_categorical_variables,
                inputs=["nhanes_features", "params:features"],
                outputs="nhanes_encoded",
                name="encode_categorical_variables",
            ),
            node(
                select_final_features,
                inputs=["nhanes_encoded", "params:features"],
                outputs="nhanes_selected",
                name="select_final_features",
            ),
            node(
                build_feature_metadata,
                inputs=["nhanes_selected", "params:features"],
                outputs="feature_metadata",
                name="build_feature_metadata",
            ),
            node(
                validate_model_input,
                inputs="nhanes_selected",
                outputs="model_input",
                name="validate_model_input",
            ),
        ]
    )
