# Arquitectura del proyecto

El proyecto usa Kedro para ordenar el flujo de datos desde fuentes NHANES crudas hasta artefactos de modelamiento, API y dashboard.

```text
NHANES XPT + archivos propios
        |
        v
data/01_raw/
        |
        v
catalog.yml
        |
        v
pipeline ingestion
        |
        +--> data/02_intermediate/ingestion_audit.csv
        +--> data/02_intermediate/nhanes_sources_summary.csv
        +--> data/diabetes_nhanes.db
        |
        v
pipeline cleaning + feature_engineering
        |
        v
data/05_model_input/model_input.csv
        |
        v
pipeline modeling + reporting
        |
        +--> data/06_models/model.pkl
        +--> data/07_model_output/predictions.csv
        +--> data/08_reporting/metrics.json
        +--> data/08_reporting/confusion_matrix.png
        |
        v
FastAPI + Streamlit + Docker
```

## Responsabilidad de `feature/a`

La rama `feature/a` deja lista la base de ingesta:

- Define fuentes NHANES en `conf/base/catalog.yml`.
- Define archivos esperados y columnas obligatorias en `conf/base/parameters.yml`.
- Descarga datos XPT con `scripts/download_nhanes.py`.
- Valida columnas mínimas requeridas por dataset.
- Genera reportes de auditoría en CSV.
- Persiste auditoría de ejecución en SQLite.
- Documenta variables clave para que `feature/b` pueda limpiar y unir datos.

## Fuentes de entrada

| Dataset | Archivo | Uso |
| --- | --- | --- |
| `nhanes_demo_raw` | `DEMO_L.xpt` | Datos demográficos. |
| `nhanes_diq_raw` | `DIQ_L.xpt` | Cuestionario de diabetes. |
| `nhanes_bmx_raw` | `BMX_L.xpt` | Medidas corporales. |
| `nhanes_ghb_raw` | `GHB_L.xpt` | Hemoglobina glicosilada. |
| `nhanes_glu_raw` | `GLU_L.xpt` | Glucosa en ayunas. |
| `nhanes_paq_raw` | `PAQ_L.xpt` | Actividad física. |
| `nhanes_slq_raw` | `SLQ_L.xpt` | Sueño. |
| `nhanes_bpxo_raw` | `BPXO_L.xpt` | Presión arterial. |
| `diabetes_thresholds` | `umbrales_diabetes.csv` | Umbrales educativos para variables clínicas. |

## Auditoría de ingesta

El pipeline `ingestion` registra por cada fuente:

- `run_id`
- `execution_timestamp`
- `dataset_key`
- `dataset_name`
- `rows`
- `columns`
- `missing_values`
- `required_columns`
- `missing_required_columns`
- `status`

La auditoría se guarda en `data/02_intermediate/ingestion_audit.csv` y en la tabla SQLite `ingestion_audit` dentro de `data/diabetes_nhanes.db`.

## Ejecución

```bash
python scripts/download_nhanes.py
kedro run --pipeline ingestion
pytest tests/test_ingestion.py
```
