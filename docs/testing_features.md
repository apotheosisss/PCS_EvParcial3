# Testing de features del sistema

Fecha de ejecución: 2026-06-13

Este documento registra las pruebas realizadas sobre las features principales del proyecto **NHANES Diabetes Risk**. El objetivo fue validar que la ingesta, modelamiento, reporting, API, dashboard y configuración Docker sean ejecutables de forma integrada.

## Resumen ejecutivo

| Feature | Estado | Evidencia |
| --- | --- | --- |
| Descarga de datos NHANES | OK | `python scripts/download_nhanes.py` descargó/validó los archivos esperados. |
| Dataset sintético de modelamiento | OK | `python scripts/make_sample_model_input.py` generó `model_input.csv` con 2000 filas. |
| Tests automatizados | OK | `pytest` ejecutó 8 tests exitosos. |
| Pipeline Kedro completo | OK | `kedro run` ejecutó 8/8 nodos correctamente. |
| Ingesta y auditoría | OK | Se generaron `ingestion_audit.csv`, `nhanes_sources_summary.csv` y `diabetes_nhanes.db`. |
| Modelamiento | OK | Se entrenaron 3 modelos y se seleccionó `random_forest`. |
| Reporting | OK | Se generaron métricas, comparación, matriz de confusión e importancia de variables. |
| API FastAPI | OK | Endpoints `/health`, `/features`, `/model-info`, `/metrics` y `/predict` respondieron 200. |
| Dashboard Streamlit | OK parcial | Compilación Python exitosa; validación visual requiere levantar Streamlit manualmente. |
| Docker Compose | OK con advertencia | `docker compose config` validó servicios; Docker mostró warning por permiso local de config. |

## Comandos ejecutados

### 1. Generación de dataset de ejemplo

```bash
python scripts/make_sample_model_input.py
```

Resultado:

```text
[OK] data\05_model_input\model_input.csv -> 2000 filas, target positivo=39.9%
```

Este dataset permite probar `feature/c` mientras `feature/b` entrega el dataset real.

### 2. Tests automatizados

```bash
pytest
```

Resultado:

```text
collected 8 items
tests/test_ingestion.py .....    [ 62%]
tests/test_model.py ...          [100%]
8 passed
```

Cobertura funcional validada:

- Validación de columnas obligatorias en ingesta.
- Resumen de fuentes NHANES.
- Escritura de auditoría SQLite.
- División train/test.
- Entrenamiento de modelos.
- Evaluación y selección de modelo final.

### 3. Pipeline Kedro completo

```bash
kedro run
```

Resultado:

```text
Pipeline execution completed successfully
Completed 8 out of 8 tasks
```

Nodos ejecutados:

```text
build_ingestion_reports
split_data
save_ingestion_audit
train_models
evaluate_models
select_and_finalize
plot_confusion_matrix
plot_feature_importance
```

## Resultados por feature

### Feature: ingesta NHANES

Entradas validadas:

```text
DEMO_L.xpt
DIQ_L.xpt
BMX_L.xpt
GHB_L.xpt
GLU_L.xpt
PAQ_L.xpt
SLQ_L.xpt
BPXO_L.xpt
umbrales_diabetes.csv
```

Artefactos generados:

```text
data/02_intermediate/ingestion_audit.csv
data/02_intermediate/nhanes_sources_summary.csv
data/diabetes_nhanes.db
```

Primeras fuentes auditadas:

```text
DEMO_L -> 11933 filas, 27 columnas, status ok
DIQ_L  -> 11744 filas, 9 columnas, status ok
```

Estado: OK.

### Feature: modelamiento

Modelos entrenados:

```text
logistic_regression
random_forest
gradient_boosting
```

Mejor modelo seleccionado:

```text
random_forest
```

Métricas del mejor modelo:

| Métrica | Valor |
| --- | ---: |
| Accuracy | 0.9450 |
| Precision | 1.0000 |
| Recall | 0.8616 |
| F1 | 0.9257 |
| ROC-AUC | 0.9312 |

Comparación:

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| logistic_regression | 0.9450 | 1.0000 | 0.8616 | 0.9257 | 0.9214 |
| random_forest | 0.9450 | 1.0000 | 0.8616 | 0.9257 | 0.9312 |
| gradient_boosting | 0.9425 | 0.9928 | 0.8616 | 0.9226 | 0.9246 |

Estado: OK.

### Feature: reporting

Artefactos generados:

```text
data/08_reporting/metrics.json
data/08_reporting/model_comparison.csv
data/08_reporting/confusion_matrix.csv
data/08_reporting/confusion_matrix.png
data/08_reporting/feature_importance.csv
data/08_reporting/feature_importance.png
```

Estado: OK.

### Feature: API FastAPI

Prueba ejecutada con `fastapi.testclient.TestClient`.

Endpoints validados:

| Endpoint | Estado | Resultado esperado |
| --- | --- | --- |
| `GET /health` | 200 | Servicio activo y modelo disponible. |
| `GET /features` | 200 | Retorna 11 features. |
| `GET /model-info` | 200 | Retorna `random_forest`, versión `v1.0.0`. |
| `GET /metrics` | 200 | Retorna métricas del modelo. |
| `POST /predict` | 200 | Retorna predicción y probabilidad. |

Payload usado:

```json
{
  "RIDAGEYR": 55,
  "RIAGENDR": 1,
  "BMXBMI": 31.5,
  "LBXGH": 6.8,
  "LBXGLU": 130,
  "INDFMPIR": 2.1
}
```

Respuesta:

```json
{
  "prediction": 1,
  "label": "riesgo_diabetes",
  "probability": 0.7533,
  "model_version": "v1.0.0"
}
```

Estado: OK.

### Feature: dashboard Streamlit

Validación ejecutada:

```bash
python -m compileall src api dashboards scripts
```

Resultado:

```text
Compilación exitosa de dashboards/streamlit_app.py
```

El dashboard depende de ejecución interactiva con:

```bash
streamlit run dashboards/streamlit_app.py
```

Estado: OK parcial. La sintaxis y dependencias de importación compilan correctamente; la validación visual debe realizarse abriendo Streamlit en navegador.

### Feature: Docker

Validación ejecutada:

```bash
docker compose -f docker/docker-compose.yml config
```

Servicios detectados:

```text
kedro-etl
api
dashboard
db
```

Estado: OK con advertencia.

Observación:

```text
Docker mostró warning por acceso denegado a C:\Users\madzm\.docker\config.json,
pero el comando finalizó con código 0 y generó la configuración compuesta.
```

## Artefactos principales verificados

```text
data/06_models/model.pkl
data/07_model_output/predictions.csv
data/08_reporting/metrics.json
data/08_reporting/model_comparison.csv
data/08_reporting/confusion_matrix.png
data/08_reporting/feature_importance.png
data/02_intermediate/ingestion_audit.csv
data/02_intermediate/nhanes_sources_summary.csv
data/diabetes_nhanes.db
```

## Limitaciones del testing

- El dataset de modelamiento usado fue sintético, generado con `scripts/make_sample_model_input.py`.
- La validación visual del dashboard no se hizo en navegador dentro de esta prueba automatizada.
- No se ejecutó `docker compose up --build` para levantar contenedores completos; solo se validó la configuración con `docker compose config`.
- Los datos y artefactos bajo `data/` no se versionan por `.gitignore`.

## Conclusión

El sistema queda validado funcionalmente para el flujo actual:

```text
descarga/preparación de datos -> ingesta -> auditoría -> modelamiento -> reporting -> API -> dashboard/docker configurados
```

La siguiente validación recomendada es reemplazar el dataset sintético por el `model_input.csv` real de `feature/b` y repetir:

```bash
kedro run
pytest
uvicorn api.main:app --reload
streamlit run dashboards/streamlit_app.py
docker compose -f docker/docker-compose.yml up --build
```
