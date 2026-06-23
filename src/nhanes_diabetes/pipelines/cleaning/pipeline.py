"""Pipeline de limpieza NHANES (feature/b)."""
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (
    build_etl_audit,
    clean_and_impute,
    merge_nhanes_tables,
    replace_special_codes_with_nan,
    save_etl_audit,
    validate_ranges,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                merge_nhanes_tables,
                inputs=[
                    "nhanes_demo_raw",
                    "nhanes_diq_raw",
                    "nhanes_bmx_raw",
                    "nhanes_ghb_raw",
                    "nhanes_glu_raw",
                    "nhanes_paq_raw",
                    "nhanes_slq_raw",
                    "nhanes_bpxo_raw",
                    "params:cleaning",
                ],
                outputs="nhanes_merged",
                name="merge_nhanes_tables",
            ),
            node(
                replace_special_codes_with_nan,
                inputs=["nhanes_merged", "params:cleaning"],
                outputs="nhanes_no_codes",
                name="replace_special_codes_with_nan",
            ),
            node(
                validate_ranges,
                inputs=["nhanes_no_codes", "params:cleaning"],
                outputs="nhanes_ranged",
                name="validate_ranges",
            ),
            node(
                clean_and_impute,
                inputs=["nhanes_ranged", "params:cleaning"],
                outputs="nhanes_clean",
                name="clean_and_impute",
            ),
            node(
                build_etl_audit,
                inputs=["nhanes_merged", "nhanes_clean", "params:cleaning"],
                outputs="etl_audit",
                name="build_etl_audit",
            ),
            node(
                save_etl_audit,
                inputs=["etl_audit", "params:cleaning"],
                outputs="sqlite_etl_audit_status",
                name="save_etl_audit",
            ),
        ]
    )
