# API REST — DiabetesNHANES (feature/c)

FastAPI. Levantar: `uvicorn api.main:app --reload` → docs en `http://localhost:8000/docs`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio y si el modelo está cargado |
| GET | `/metrics` | Métricas del modelo entrenado |
| GET | `/features` | Lista de features que espera el modelo |
| GET | `/model-info` | Nombre y versión del modelo |
| POST | `/predict` | Predicción individual |

## POST /predict
Payload:
```json
{"RIDAGEYR":55,"RIAGENDR":1,"BMXBMI":31.5,"LBXGH":6.8,"LBXGLU":130,"INDFMPIR":2.1}
```
Respuesta:
```json
{"prediction":1,"label":"riesgo_diabetes","probability":0.87,"model_version":"v1.0.0"}
```
Las features no provistas se rellenan con la media del training set (almacenada en el bundle).
