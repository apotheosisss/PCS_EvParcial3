"""Pipeline de ingesta NHANES."""
from kedro.pipeline import Pipeline, node, pipeline

from .nodes import build_ingestion_reports, save_ingestion_audit


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                build_ingestion_reports,
                inputs=[
                    "nhanes_demo_raw",
                    "nhanes_diq_raw",
                    "nhanes_bmx_raw",
                    "nhanes_ghb_raw",
                    "nhanes_glu_raw",
                    "nhanes_paq_raw",
                    "nhanes_slq_raw",
                    "nhanes_bpxo_raw",
                    "diabetes_thresholds",
                    "params:ingestion",
                ],
                outputs=["ingestion_audit", "nhanes_sources_summary"],
                name="build_ingestion_reports",
            ),
            node(
                save_ingestion_audit,
                inputs=["ingestion_audit", "params:ingestion"],
                outputs="sqlite_ingestion_audit_status",
                name="save_ingestion_audit",
            ),
        ]
    )
