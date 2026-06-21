# API REST — DiabetesNHANES (feature/c)

FastAPI con arquitectura modular. Levantar:
`uvicorn api.main:app --reload` → docs interactivas en `http://localhost:8000/docs`.

> Herramienta analítica/educativa basada en datos públicos NHANES. **No es un
> diagnóstico clínico.**

## Estructura del paquete `api/`

```
api/
  config.py        configuración por entorno (rutas, CORS, umbrales)
  artifacts.py     acceso a artefactos del pipeline con caché (503 si faltan)
  schemas.py       contratos Pydantic
  services/        lógica de negocio (model, metadata, reporting, stats)
  routers/         endpoints HTTP por recurso
  main.py          app factory + `app` (uvicorn api.main:app)
```

## Endpoints

| Grupo | Método | Ruta | Descripción |
|-------|--------|------|-------------|
| estado | GET | `/` | Nombre, versión y disclaimer |
| estado | GET | `/health` | Estado del servicio, modelo y métricas cargados |
| modelo | GET | `/model-info` | Nombre y versión del modelo |
| modelo | GET | `/features` | Features esperadas + metadatos (tipo, rango, default, user_facing) |
| modelo | GET | `/thresholds` | Umbrales clínicos educativos |
| reporting | GET | `/metrics` | Métricas del modelo entrenado |
| reporting | GET | `/model-comparison` | Comparación de modelos |
| reporting | GET | `/confusion-matrix` | Matriz de confusión (JSON) |
| reporting | GET | `/feature-importance?top=N` | Importancia de variables (JSON) |
| reporting | GET | `/report/{name}.png` | Figura PNG (`confusion_matrix` \| `feature_importance`) |
| estadísticas | GET | `/stats/summary` | KPIs poblacionales (n, % diabetes) |
| estadísticas | GET | `/stats/distribution?by=...` | Distribución por `age_group` \| `bmi_category` \| `RIAGENDR` |
| predicción | POST | `/predict` | Predicción individual |
| predicción | POST | `/predict/batch` | Predicción por lote |
| predicción | GET | `/predictions?limit=&offset=` | Muestra paginada del test set |

## POST /predict
Payload (las features faltantes se rellenan con la media del training set):
```json
{"RIDAGEYR":55,"RIAGENDR":1,"BMXBMI":31.5,"LBXGH":6.8,"LBXGLU":130,"INDFMPIR":2.1}
```
Respuesta:
```json
{"prediction":1,"label":"riesgo_diabetes","probability":0.7533,"risk_band":"alto","threshold":0.5,"model_version":"v1.0.0"}
```

## POST /predict/batch
```json
{"items":[{"RIDAGEYR":55,"RIAGENDR":1,"BMXBMI":31.5,"LBXGH":6.8,"LBXGLU":130},
          {"RIDAGEYR":30,"RIAGENDR":2,"BMXBMI":22.0,"LBXGH":5.1,"LBXGLU":90}]}
```
→
```json
{"n":2,"threshold":0.5,"model_version":"v1.0.0",
 "results":[{"prediction":1,"label":"riesgo_diabetes","probability":0.76,"risk_band":"alto"},
            {"prediction":0,"label":"sin_riesgo","probability":0.04,"risk_band":"bajo"}]}
```

## Códigos de estado
- `200` OK · `400` parámetro inválido (p. ej. `by` no soportado) · `413` lote demasiado grande
- `422` validación del payload · `503` artefacto/modelo aún no generado (`kedro run`)

## Configuración (variables de entorno, opcionales)
`CORS_ORIGINS`, `DECISION_THRESHOLD`, `RISK_BAND_LOW`, `RISK_BAND_HIGH`,
`MAX_BATCH_ROWS`, además de las rutas `*_PATH`. Ver `.env.example` y `docs/plan_api.md`.

## Consumo desde un front
- Estado/arranque: `GET /health` + `GET /model-info`.
- Formulario dinámico: `GET /features` + `GET /thresholds`.
- Vista ejecutiva: `GET /stats/summary` + `GET /stats/distribution`.
- Vista técnica: `GET /metrics`, `/model-comparison`, `/confusion-matrix`, `/feature-importance`.
- Vista operativa: `POST /predict`, `POST /predict/batch`, `GET /predictions`.

CORS está habilitado; configura el origen del front en `CORS_ORIGINS`.
