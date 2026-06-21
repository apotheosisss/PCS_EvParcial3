# Plan de API — NHANES Diabetes Risk

> Plan para evolucionar la API REST (FastAPI) de modo que un front-end web pueda
> consumirla y resolver lo que el proyecto busca: **explorar y comunicar el riesgo
> de diabetes** estimado a partir de datos NHANES, con un enfoque **educativo, no
> diagnóstico**.
>
> Este documento describe (1) lo que la API expone hoy, (2) lo que un front necesita,
> (3) los endpoints propuestos con sus contratos, y (4) un orden de implementación.

---

## 1. Qué resuelve el proyecto y qué front tiene sentido

El pipeline Kedro va de NHANES crudo → `model_input.csv` → modelo entrenado →
artefactos de reporting. El manual de usuario ya define tres vistas (hoy en
Streamlit) que el front web debe poder reproducir:

| Vista | Necesidad | Datos que requiere de la API |
|-------|-----------|------------------------------|
| **Ejecutiva** | KPIs y distribuciones poblacionales | nº participantes, % con `diabetes_target=1`, distribuciones por edad / sexo / IMC |
| **Técnica** | Calidad del modelo | métricas del mejor modelo, comparación de modelos, matriz de confusión, importancia de variables |
| **Operativa** | Uso individual y tabla | features esperadas + metadatos, predicción individual, predicción por lote, descarga CSV, umbrales educativos |

La API debe servir **todo en JSON** (no solo PNG) para que el front renderice sus
propios gráficos y formularios. Las imágenes (`.png`) siguen disponibles como
fallback/descarga.

---

## 2. Estado actual de la API (`api/main.py`)

| Método | Ruta | Estado | Observación |
|--------|------|--------|-------------|
| GET | `/health` | ✅ existe | `{status, model_loaded}` |
| GET | `/metrics` | ✅ existe | devuelve `metrics.json` crudo |
| GET | `/features` | ✅ existe | lista `feature_cols` + `n_features` |
| GET | `/model-info` | ✅ existe | `model_name`, `model_version`, `n_features` |
| POST | `/predict` | ✅ existe | predicción individual; rellena features faltantes con la media |

**Limitaciones para un front:**

- No hay **CORS** habilitado → un front en otro origen (p. ej. `localhost:3000`) no
  puede llamar a la API.
- `/features` no entrega **metadatos** (tipo, rango, si es ingresable por el usuario,
  default) → el front no puede construir un formulario automáticamente.
- No hay endpoints JSON para **matriz de confusión**, **importancia de variables**,
  **comparación de modelos** ni **predicciones** (existen como CSV/PNG en `data/08_reporting/`).
- No hay **agregaciones poblacionales** (KPIs/distribuciones) para la vista ejecutiva.
- No hay **predicción por lote** (CSV) ni endpoint para descargar resultados.
- `/predict` no devuelve el **umbral de decisión** ni la **banda de riesgo** (bajo/medio/alto),
  útiles para comunicar el resultado.

---

## 3. Endpoints propuestos

Se mantiene el prefijo plano actual y, para lo nuevo, se agrupa bajo recursos claros.
Todos los endpoints nuevos leen de artefactos que **ya genera el pipeline**
(`data/05_model_input/`, `data/06_models/`, `data/08_reporting/`), así que no
requieren reentrenar nada.

### 3.1. Operación / salud (ya existe, se amplía)

#### `GET /health`
Sin cambios. Añadir `model_version` y `metrics_loaded` al payload:
```json
{ "status": "ok", "model_loaded": true, "metrics_loaded": true, "model_version": "v1.0.0" }
```

#### `GET /model-info`
Sin cambios funcionales. Documenta el bundle: `model_name`, `model_version`, `n_features`.

---

### 3.2. Metadatos del modelo (para construir formularios)

#### `GET /features` — **ampliar a metadatos**
Hoy devuelve solo nombres. Propuesta: enriquecer con metadatos por feature, tomando
de `feature_metadata.json` (opcional de feature/b, §5 del contrato) o infiriéndolos
del bundle (`feature_means`) y del diccionario de datos / umbrales.

```json
{
  "n_features": 8,
  "features": [
    {
      "name": "RIDAGEYR",
      "label": "Edad (años)",
      "dtype": "float",
      "user_facing": true,
      "default": 50,
      "min": 0, "max": 120,
      "unit": "años"
    },
    {
      "name": "bmi_category",
      "label": "Categoría IMC (derivada)",
      "dtype": "int",
      "user_facing": false,
      "default": 1
    }
  ]
}
```
- `user_facing` permite al front mostrar solo los campos que una persona puede
  ingresar; el resto se rellena con `default`/media (igual que hace `_build_row`).
- `min`/`max`/`unit` permiten validar y etiquetar inputs.

#### `GET /thresholds`
Sirve los umbrales educativos (`data/01_raw/umbrales_diabetes.csv`) para que el front
muestre referencias clínicas junto a los inputs.
```json
{ "thresholds": [ { "variable": "LBXGH", "op": ">=", "value": 6.5, "description": "A1C compatible con diabetes" } ] }
```

---

### 3.3. Reporting / desempeño del modelo (vista Técnica)

#### `GET /metrics` — se mantiene
Devuelve `metrics.json`: `best_model`, `metrics` (accuracy/precision/recall/f1/roc_auc),
`all_models`, `n_features`.

#### `GET /model-comparison`
Sirve `model_comparison.csv` como JSON para tabla/gráfico comparativo.
```json
{ "models": [ { "model": "random_forest", "accuracy": 0.945, "precision": 1.0, "recall": 0.8616, "f1": 0.9257, "roc_auc": 0.9312 } ] }
```

#### `GET /confusion-matrix`
Sirve `confusion_matrix.csv` como JSON (no solo PNG):
```json
{ "labels": ["0", "1"], "matrix": [[TN, FP], [FN, TP]] }
```

#### `GET /feature-importance?top=15`
Sirve `feature_importance.csv` ordenado, con parámetro `top` opcional:
```json
{ "importances": [ { "feature": "LBXGH", "importance": 0.41 } ] }
```

#### `GET /report/{artifact}.png`  *(opcional, fallback)*
Devuelve las imágenes (`confusion_matrix`, `feature_importance`) como `image/png`
para descarga/visualización directa.

---

### 3.4. Datos poblacionales (vista Ejecutiva)

#### `GET /stats/summary`
Agrega sobre `data/05_model_input/model_input.csv` los KPIs de cabecera:
```json
{
  "n_participants": 2000,
  "positive_rate": 0.399,
  "n_positive": 798,
  "n_negative": 1202
}
```

#### `GET /stats/distribution?by=age_group`
Distribución de una variable (y opcionalmente cruzada con el target) para gráficos:
```json
{
  "by": "age_group",
  "buckets": [
    { "key": "30-44", "count": 540, "positive_rate": 0.21 },
    { "key": "45-64", "count": 870, "positive_rate": 0.48 }
  ]
}
```
Variables soportadas inicialmente: `age_group`, `RIAGENDR` (sexo), `bmi_category`.

> Nota de privacidad: estas agregaciones nunca exponen filas individuales con `SEQN`;
> solo conteos y tasas. El dataset es público NHANES, pero se mantiene el criterio.

---

### 3.5. Predicción (vista Operativa)

#### `POST /predict` — se mantiene, se enriquece la respuesta
Request actual (igual):
```json
{ "RIDAGEYR": 55, "RIAGENDR": 1, "BMXBMI": 31.5, "LBXGH": 6.8, "LBXGLU": 130, "INDFMPIR": 2.1 }
```
Respuesta propuesta (añade banda y umbral, conservando los campos actuales):
```json
{
  "prediction": 1,
  "label": "riesgo_diabetes",
  "probability": 0.7533,
  "risk_band": "alto",
  "threshold": 0.5,
  "model_version": "v1.0.0"
}
```
`risk_band` derivado de la probabilidad (p. ej. `<0.33 bajo`, `<0.66 medio`, `>=0.66 alto`).

#### `POST /predict/batch`
Recibe una lista de registros (o un CSV vía `multipart/form-data`) y devuelve un
arreglo de predicciones, para la tabla y la descarga de la vista operativa.
```json
{ "items": [ { "RIDAGEYR": 55, "BMXBMI": 31.5, "LBXGH": 6.8, "LBXGLU": 130 } ] }
```
→
```json
{ "results": [ { "prediction": 1, "probability": 0.75, "risk_band": "alto" } ], "n": 1 }
```
Límite de tamaño (p. ej. máx. 1000 filas) para evitar abusos.

#### `GET /predictions?limit=100&offset=0`  *(opcional)*
Sirve `data/07_model_output/predictions.csv` (test set: `y_true`, `y_pred`,
`probability`) paginado, para una tabla de ejemplo en la vista operativa.

---

## 4. Aspectos transversales

### 4.1. CORS
Habilitar `CORSMiddleware` con orígenes configurables por entorno:
```python
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])
```

### 4.2. Manejo de errores
- `503` cuando falta `model.pkl` o `metrics.json` (ya se hace para algunos).
- `422` validación de payload (Pydantic, automático).
- Respuesta de error uniforme `{ "detail": "..." }` (estándar FastAPI).

### 4.3. Versionado y disclaimer
- Mantener `version="1.0.0"` en la app y `model_version` en cada respuesta de predicción.
- Incluir en `/health` o en un `GET /` un **disclaimer** explícito: *resultado
  educativo basado en NHANES, no reemplaza diagnóstico clínico*.
- (Opcional) Prefijar las rutas con `/api/v1` para futuras versiones sin romper el front.

### 4.4. Carga de artefactos
- Reutilizar `_load_bundle()` (cache en memoria) y aplicar el mismo patrón de carga
  perezosa + cache a `metrics.json`, CSVs de reporting y `model_input.csv`.
- Los CSV de reporting son pequeños: cargar bajo demanda y cachear.

### 4.5. Rendimiento
- `/stats/*` agregan sobre `model_input.csv` (≈2000 filas hoy): trivial en memoria.
- `/predict/batch` vectoriza con un solo `predict_proba` sobre el DataFrame completo.

---

## 5. Contrato resumido para el front

| Vista | Endpoints que consume |
|-------|------------------------|
| Ejecutiva | `GET /stats/summary`, `GET /stats/distribution?by=...` |
| Técnica | `GET /metrics`, `GET /model-comparison`, `GET /confusion-matrix`, `GET /feature-importance` |
| Operativa | `GET /features`, `GET /thresholds`, `POST /predict`, `POST /predict/batch`, `GET /predictions` |
| Global | `GET /health`, `GET /model-info` |

Con esto el front (React/Vite o Next.js) puede:
1. Arrancar pidiendo `/health` + `/model-info` (estado y versión).
2. Construir el formulario de predicción dinámicamente desde `/features` + `/thresholds`.
3. Renderizar KPIs y gráficos con `/stats/*` y los endpoints de reporting.
4. Ejecutar predicciones individuales y por lote, y exportar resultados.

---

## 6. Orden de implementación sugerido

1. **Habilitar CORS** y `GET /` con disclaimer. *(desbloquea cualquier front)*
2. **Endpoints de reporting JSON**: `/model-comparison`, `/confusion-matrix`,
   `/feature-importance`. *(reutilizan CSVs existentes)*
3. **`/features` con metadatos** + `/thresholds`. *(habilita formularios)*
4. **`/stats/summary` y `/stats/distribution`**. *(vista ejecutiva)*
5. **`/predict` enriquecido** (`risk_band`, `threshold`) y **`/predict/batch`**.
6. **`/predictions` paginado** y endpoints PNG opcionales.
7. Tests (`tests/test_api.py`) para cada endpoint nuevo, siguiendo el patrón
   `fastapi.testclient.TestClient` ya usado en el proyecto.

> Todo lo propuesto se apoya en artefactos que el pipeline Kedro ya produce; no
> requiere cambios en `feature/b` ni reentrenamiento. Si feature/b entrega
> `feature_metadata.json`, `/features` lo usa directamente; si no, se infiere.
