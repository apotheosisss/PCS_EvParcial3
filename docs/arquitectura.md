# Arquitectura (feature/c)

```
NHANES XPT (feature/a)
        │ ingesta + catálogo Kedro
        ▼
limpieza + features (feature/b)  ──►  data/05_model_input/model_input.csv
        │                                  (contrato: docs/CONTRATO_FEATURE_B.md)
        ▼
pipeline modeling (feature/c) ─► model.pkl, predictions, metrics
        ▼
pipeline reporting (feature/c) ─► confusion_matrix.png, feature_importance.png
        ▼
   ┌─────────────┬──────────────┐
   ▼             ▼              ▼
API FastAPI   Dashboard       Docker compose
(/predict)    Streamlit       (etl, api, dashboard, db)
```

Paquete: `nhanes_diabetes`. Pipelines registrados vía `find_pipelines()`.
