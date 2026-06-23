<p align="center">
  <img src="assets/banner.png" alt="NHANES Diabetes Risk banner" width="100%">
</p>

<p align="center">
  <img src="assets/logo.png" alt="NHANES Diabetes Risk logo" width="120">
</p>

<h1 align="center">NHANES Diabetes Risk</h1>

<p align="center">
  Proyecto académico de ciencia de datos con Kedro para analizar factores asociados a diabetes y riesgo metabólico usando datos públicos de NHANES.
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="Kedro" src="https://img.shields.io/badge/Kedro-1.x-ffc900?style=for-the-badge">
  <img alt="Pandas" src="https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas&logoColor=white">
  <img alt="scikit-learn" src="https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white">
</p>

---

## About

**NHANES Diabetes Risk** organiza un flujo reproducible para integrar, limpiar, transformar, modelar y visualizar datos de salud poblacional del ciclo **NHANES August 2021-August 2023**. El foco del proyecto es construir una base técnica clara para análisis de riesgo de diabetes, integrando datos demográficos, cuestionarios, mediciones corporales, resultados de laboratorio y fuentes auxiliares propias.

El repositorio fue desarrollado para la **Evaluación Parcial N°3** de la asignatura **Programación para la Ciencia de Datos - SCY1101**.

> Este proyecto tiene fines académicos y analíticos. No es una herramienta diagnóstica ni reemplaza evaluación médica profesional.

## Objetivo Del Proyecto

Desarrollar un pipeline profesional con **Kedro** para analizar factores asociados a diabetes y entrenar modelos predictivos usando datos públicos de NHANES.

Objetivo analítico:

```text
Predecir o clasificar riesgo/estado de diabetes en participantes de NHANES usando variables demográficas, antropométricas, cuestionarios de salud y biomarcadores clínicos.
```

Variable objetivo sugerida:

```text
diabetes_target
0 = sin evidencia de diabetes
1 = diabetes reportada o alto riesgo metabólico según variables disponibles
```

La variable `diabetes_target` se construye como una aproximación educativa/analítica usando:

```text
DIQ010  -> diagnóstico médico de diabetes reportado.
LBXGH   -> hemoglobina glicosilada / A1C.
LBXGLU  -> glucosa plasmática en ayunas.
```

Reglas sugeridas:

```text
diabetes_target = 1 si:
- DIQ010 == 1
- o LBXGH >= 6.5
- o LBXGLU >= 126

diabetes_target = 0 si no cumple criterios anteriores.
```

> Los umbrales de A1C y glucosa se usan como referencia educativa. Esta clasificación no debe interpretarse como diagnóstico clínico real.

## Estado Del Proyecto

| Área | Estado | Detalle |
| --- | --- | --- |
| Estructura Kedro | Disponible | Proyecto configurado con `pyproject.toml`, `conf/` y paquete en `src/`. |
| Descarga de datos | Disponible | Script `scripts/download_nhanes.py` para obtener archivos `.xpt`. |
| Catálogo de datos | Disponible | Datasets NHANES registrados en `conf/base/catalog.yml`. |
| Parámetros | Disponible | URL base, archivos esperados, target y llave de unión en `parameters.yml`. |
| Ingesta | Rama `feature/a` | Carga de fuentes NHANES, CSV/Excel propio y auditoría. |
| Limpieza/features | Rama `feature/b` | Unión por `SEQN`, limpieza, target y dataset modelable. |
| Modelamiento/producto | Rama `feature/c` | Modelos, métricas, dashboard, API, Docker y documentación final. |

## Fuentes De Datos

Los datos provienen de **NHANES - National Health and Nutrition Examination Survey**, programa público del National Center for Health Statistics.

### Fuente 1: NHANES Oficial En Formato XPT

| Archivo | Categoría | Uso principal |
| --- | --- | --- |
| `DEMO_L.xpt` | Demographics | Edad, sexo, raza/etnia, ingresos y pesos muestrales. |
| `DIQ_L.xpt` | Questionnaire | Diabetes reportada, variable `DIQ010`. |
| `BMX_L.xpt` | Examination | BMI, peso, altura y medidas corporales. |
| `GHB_L.xpt` | Laboratory | Hemoglobina glicosilada, variable `LBXGH`. |
| `GLU_L.xpt` | Laboratory | Glucosa plasmática en ayunas, variable `LBXGLU`. |
| `PAQ_L.xpt` | Questionnaire | Actividad física. |
| `SLQ_L.xpt` | Questionnaire | Sueño. |
| `BPXO_L.xpt` | Examination | Presión arterial. |

Llave de integración:

```text
SEQN
```

### Fuente 2: Archivos Propios CSV/Excel

Archivos sugeridos:

```text
data/01_raw/diccionario_variables.xlsx
data/01_raw/umbrales_diabetes.csv
```

Ejemplo de `umbrales_diabetes.csv`:

```csv
variable,criterio,valor,descripcion
LBXGH,>=,6.5,A1C compatible con diabetes
LBXGLU,>=,126,Glucosa ayunas compatible con diabetes
BMXBMI,>=,30,Obesidad
RIDAGEYR,>=,45,Edad de mayor riesgo
```

### Fuente 3: Base SQLite/PostgreSQL

Base sugerida:

```text
data/diabetes_nhanes.db
```

Usos esperados:

- Auditoría del ETL.
- Fecha de ejecución.
- Cantidad de filas procesadas.
- Nulos antes y después de limpieza.
- Métricas del modelo.
- Predicciones generadas.

## Arquitectura

```text
NHANES Public Data + CSV/Excel propio + SQLite/PostgreSQL
        |
        v
scripts/download_nhanes.py
        |
        v
data/01_raw/
        |
        v
Kedro Data Catalog
        |
        v
Pipelines
  - ingestion
  - cleaning
  - feature_engineering
  - modeling
  - reporting
        |
        v
Artifacts
  - data/02_intermediate/
  - data/03_primary/
  - data/04_feature/
  - data/05_model_input/
  - data/06_models/
  - data/07_model_output/
  - data/08_reporting/
        |
        v
Dashboard Streamlit + API FastAPI + Docker
```

## Estructura Del Repositorio

```text
.
|-- assets/
|   |-- banner.png
|   `-- logo.png
|-- conf/
|   |-- base/
|   |   |-- catalog.yml
|   |   |-- logging.yml
|   |   `-- parameters.yml
|   `-- local/
|-- data/
|   |-- 01_raw/
|   |-- 02_intermediate/
|   |-- 03_primary/
|   |-- 04_feature/
|   |-- 05_model_input/
|   |-- 06_models/
|   |-- 07_model_output/
|   `-- 08_reporting/
|-- dashboards/
|   `-- streamlit_app.py
|-- api/
|   `-- main.py
|-- docker/
|   |-- Dockerfile
|   |-- Dockerfile.dashboard
|   `-- docker-compose.yml
|-- docs/
|-- notebooks/
|-- scripts/
|   `-- download_nhanes.py
|-- src/
|   `-- nhanes_diabetes/
|       |-- pipeline_registry.py
|       |-- settings.py
|       `-- pipelines/
|-- tests/
|-- .env.example
|-- .gitignore
|-- pyproject.toml
|-- README.md
`-- requirements.txt
```

## Instalación

Crear y activar entorno virtual:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instalar dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Validar Kedro:

```bash
kedro info
```

## Uso Rápido

Descargar los archivos NHANES:

```bash
python scripts/download_nhanes.py
```

Ejecutar el proyecto Kedro:

```bash
kedro run
```

Ejecutar el paquete como comando:

```bash
nhanes-diabetes
```

Generar dataset de ejemplo para modelamiento:

```bash
python scripts/make_sample_model_input.py
```

Levantar API de predicción:

```bash
uvicorn api.main:app --reload
```

Levantar dashboard:

```bash
streamlit run dashboards/streamlit_app.py
```

Despliegue completo con Docker:

```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

## Configuración Kedro

Los datasets crudos están definidos en:

```text
conf/base/catalog.yml
```

Los parámetros centrales están en:

```text
conf/base/parameters.yml
```

Parámetros destacados:

```yaml
nhanes_base_url: "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles"
target_column: "diabetes_target"
merge_key: "SEQN"
```

## Variables Relevantes

| Variable | Descripción |
| --- | --- |
| `SEQN` | Identificador único de participante. |
| `RIDAGEYR` | Edad. |
| `RIAGENDR` | Sexo. |
| `RIDRETH3` | Grupo racial/étnico. |
| `INDFMPIR` | Ratio ingreso/pobreza. |
| `BMXBMI` | Índice de masa corporal. |
| `BMXWT` | Peso. |
| `BMXHT` | Estatura. |
| `BMXWAIST` | Circunferencia de cintura. |
| `DIQ010` | Diagnóstico reportado de diabetes. |
| `LBXGH` | Hemoglobina glicosilada HbA1c. |
| `LBXGLU` | Glucosa plasmática en ayunas. |
| `PAQ_*` | Variables de actividad física. |
| `SLQ_*` | Variables de sueño. |
| `BPXO_*` | Variables de presión arterial. |

Features derivadas recomendadas:

```text
age_group
bmi_category
has_obesity
high_a1c
high_fasting_glucose
physical_activity_level
sleep_risk_category
income_group
diabetes_target
```

## Modelamiento

Modelos recomendados:

```text
LogisticRegression
RandomForestClassifier
GradientBoostingClassifier
```

Métricas mínimas:

```text
accuracy
precision
recall
f1-score
roc-auc
confusion matrix
classification report
```

Como el target puede estar desbalanceado, se debe revisar especialmente `precision`, `recall`, `f1-score`, matriz de confusión, curva ROC y curva precision-recall. También debe documentarse si se aplicó `class_weight="balanced"`, ajuste de umbral o comparación entre modelos.

## Dashboard Recomendado

Vista ejecutiva:

- Total de participantes analizados.
- Porcentaje estimado de `diabetes_target`.
- Distribución por edad, sexo e IMC.
- Top variables asociadas al modelo.

Vista técnica:

- Matriz de confusión.
- Accuracy, precision, recall y F1-score.
- ROC-AUC y curva precision-recall.
- Comparación de modelos.
- Feature importance.

Vista operativa:

- Filtros por edad, sexo, IMC, actividad física y sueño.
- Tabla de registros procesados.
- Simulador de predicción individual.
- Descarga de resultados en CSV.

## API REST Recomendada

Endpoints mínimos:

```text
GET /health
GET /metrics
GET /features
GET /model-info
POST /predict
```

Ejemplo de payload:

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

Respuesta esperada:

```json
{
  "prediction": 1,
  "label": "riesgo_diabetes",
  "probability": 0.87,
  "model_version": "v1.0.0"
}
```

## Docker

Servicios sugeridos:

```text
kedro-etl
api
dashboard
db
```

Variables de entorno sugeridas en `.env.example`:

```text
PROJECT_NAME=DiabetesNHANES
MODEL_PATH=data/06_models/model.pkl
DATABASE_URL=sqlite:///data/diabetes_nhanes.db
API_PORT=8000
DASHBOARD_PORT=8501
```

## Flujo Git Recomendado

El repositorio usa una estrategia Git Flow simplificada:

| Rama | Propósito |
| --- | --- |
| `main` | Versión final estable. |
| `develop` | Integración del equipo. |
| `feature/a` | Ingesta, estructura Kedro y fuentes de datos. |
| `feature/b` | Limpieza, transformación y dataset modelable. |
| `feature/c` | Modelamiento, dashboard, API, Docker y documentación final. |

Flujo correcto:

```text
feature/a -> develop
feature/b -> develop
feature/c -> develop
develop   -> main
```

No se debe integrar una rama `feature/*` directamente a `main`.

## División Por Ramas

### Integrante 1 - `feature/a`

Responsable de Kedro, ingesta y arquitectura base.

Tareas principales:

- Crear el proyecto Kedro y estructura de carpetas.
- Configurar `catalog.yml` y `parameters.yml`.
- Descargar o preparar archivos NHANES XPT.
- Cargar `DEMO_L`, `DIQ_L`, `BMX_L`, `GHB_L`, `GLU_L` y fuentes adicionales.
- Crear lectura de CSV/Excel propio.
- Crear base SQLite/PostgreSQL de auditoría.
- Validar columnas obligatorias.
- Crear pipeline de ingesta.
- Documentar fuentes de datos.

Archivos esperados:

```text
src/nhanes_diabetes/pipelines/ingestion/
conf/base/catalog.yml
conf/base/parameters.yml
data/01_raw/
data/diabetes_nhanes.db
docs/diccionario_datos.md
tests/test_ingestion.py
```

### Integrante 2 - `feature/b`

Responsable de limpieza, transformación y feature engineering.

Tareas principales:

- Unir tablas NHANES usando `SEQN`.
- Limpiar códigos especiales.
- Tratar nulos y duplicados.
- Validar rangos.
- Crear `diabetes_target`.
- Crear variables derivadas.
- Codificar variables categóricas.
- Normalizar variables numéricas.
- Guardar dataset final en `data/05_model_input/`.

Archivos esperados:

```text
src/nhanes_diabetes/pipelines/cleaning/
src/nhanes_diabetes/pipelines/feature_engineering/
data/02_intermediate/
data/03_primary/
data/04_feature/
data/05_model_input/model_input.csv
tests/test_cleaning.py
tests/test_features.py
```

### Integrante 3 - `feature/c`

Responsable de modelamiento, dashboard, API, Docker y documentación final.

Tareas principales:

- Entrenar modelos.
- Evaluar métricas.
- Guardar modelo entrenado y predicciones.
- Crear visualizaciones.
- Crear dashboard Streamlit.
- Crear API FastAPI.
- Crear Dockerfile y `docker-compose.yml`.
- Completar README, documentación final y evidencias Git.

Archivos esperados:

```text
src/nhanes_diabetes/pipelines/modeling/
src/nhanes_diabetes/pipelines/reporting/
data/06_models/model.pkl
data/07_model_output/predictions.csv
data/08_reporting/metrics.json
data/08_reporting/model_comparison.csv
data/08_reporting/confusion_matrix.png
data/08_reporting/feature_importance.csv
dashboards/streamlit_app.py
api/main.py
docker/Dockerfile
docker/docker-compose.yml
README.md
docs/modelo.md
docs/arquitectura.md
docs/manual_usuario.md
docs/guia_despliegue.md
docs/evidencias_git.md
```

## Issues Sugeridas

```text
#1 Configurar proyecto Kedro base
#2 Configurar catalog.yml
#3 Descargar y cargar archivos NHANES XPT
#4 Crear diccionario de variables y umbrales
#5 Crear base SQLite de auditoría
#6 Unir tablas por SEQN
#7 Limpiar códigos especiales y nulos
#8 Crear diabetes_target
#9 Crear variables derivadas
#10 Generar dataset model_input
#11 Entrenar modelos baseline
#12 Evaluar modelos y guardar métricas
#13 Crear dashboard Streamlit
#14 Crear API FastAPI
#15 Crear Docker y docker-compose
#16 Crear tests automatizados
#17 Completar README
#18 Crear documentación técnica
#19 Preparar evidencias Git
#20 Preparar presentación final
```

## Convención De Commits

```text
feat: nueva funcionalidad
fix: corrección
docs: documentación
test: pruebas
chore: configuración
refactor: mejora interna
```

Ejemplos:

```bash
git commit -m "feat(ingestion): load NHANES XPT datasets"
git commit -m "feat(cleaning): handle missing values and invalid codes"
git commit -m "feat(features): create diabetes target"
git commit -m "feat(modeling): train baseline classifiers"
git commit -m "feat(dashboard): add diabetes analytics dashboard"
git commit -m "docs(readme): add installation and execution guide"
git commit -m "chore(docker): add compose services"
```

## Checklist Para El 100%

### ETL Y Kedro

- [ ] Proyecto Kedro creado.
- [ ] `catalog.yml` configurado.
- [ ] Múltiples fuentes integradas.
- [ ] Archivos NHANES XPT cargados.
- [ ] CSV/Excel propio usado.
- [ ] SQLite/PostgreSQL usado para auditoría o resultados.
- [ ] Tablas unidas por `SEQN`.
- [ ] Nulos tratados.
- [ ] Duplicados tratados.
- [ ] Outliers o rangos inválidos tratados.
- [ ] Dataset `model_input` generado.

### Modelamiento

- [ ] Mínimo 2 modelos entrenados.
- [ ] Comparación de métricas.
- [ ] Matriz de confusión.
- [ ] ROC-AUC o curva PR.
- [ ] Feature importance.
- [ ] Modelo guardado.
- [ ] Predicciones guardadas.

### Dashboard

- [ ] Vista ejecutiva.
- [ ] Vista técnica.
- [ ] Vista operativa.
- [ ] Filtros interactivos.
- [ ] KPIs.
- [ ] Métricas del modelo.
- [ ] Gráficos de distribución.
- [ ] Simulador de predicción.

### Git

- [ ] `main` estable.
- [ ] `develop` integración.
- [ ] `feature/a` para ingesta.
- [ ] `feature/b` para limpieza/features.
- [ ] `feature/c` para modelo/producto.
- [ ] Pull Requests.
- [ ] Issues.
- [ ] Commits claros.
- [ ] Evidencias exportadas.

### Docker Y Despliegue

- [ ] Dockerfile.
- [ ] `docker-compose.yml`.
- [ ] `.env.example`.
- [ ] Servicio API.
- [ ] Servicio dashboard.
- [ ] Servicio ETL.
- [ ] Guía de despliegue.

### Documentación

- [ ] README completo.
- [ ] Arquitectura.
- [ ] Diccionario de datos.
- [ ] Guía de instalación.
- [ ] Guía de uso.
- [ ] Documentación API.
- [ ] Explicación del modelo.
- [ ] Evidencias Git.

## Presentación De 15 Minutos

```text
Min 0-1: Problema y objetivo del proyecto.
Min 1-3: Fuente NHANES y variables usadas.
Min 3-5: Arquitectura Kedro y flujo ETL.
Min 5-7: Limpieza, transformación y target diabetes.
Min 7-9: Modelos y métricas.
Min 9-11: Dashboard Streamlit.
Min 11-12: API y Docker.
Min 12-14: Git Flow, branches, PRs e issues.
Min 14-15: Cierre, limitaciones y mejoras futuras.
```

Frase para defender Git:

```text
Trabajamos con una estrategia Git Flow simplificada. main se mantuvo como rama estable de entrega, develop como rama de integración, y cada integrante trabajó en una rama feature separada. feature/a concentró la ingesta y arquitectura Kedro, feature/b la limpieza y transformación de datos, y feature/c el modelamiento, dashboard, API, Docker y documentación final. Ninguna rama feature se integró directamente a main; todas pasaron primero por Pull Request hacia develop, donde se probaron antes de liberar la versión final.
```

## Buenas Prácticas

- No versionar datos crudos ni procesados.
- Mantener credenciales fuera del repositorio.
- Documentar cambios relevantes en commits pequeños.
- Ejecutar validaciones antes de integrar a `develop`.
- Separar trabajo técnico por ramas `feature/*`.

## Reproducibilidad

El proyecto concentra rutas y parámetros en configuración Kedro para que el flujo pueda repetirse en otros equipos. Los datos descargados se guardan bajo `data/01_raw/`, pero esa carpeta se mantiene fuera de Git para evitar subir archivos pesados o sensibles.

## Limitaciones

- NHANES es una encuesta poblacional y no una historia clínica individual.
- Algunas variables son autoinformadas.
- El target `diabetes_target` es una aproximación analítica basada en reglas y variables disponibles.
- Las métricas finales dependerán de la calidad de limpieza, features, modelamiento y balance de clases.

## Licencia Y Uso

Repositorio académico para práctica de ciencia de datos reproducible con Kedro, Python y fuentes públicas de salud. Los datos pertenecen a NHANES/NCHS/CDC y deben utilizarse respetando sus condiciones oficiales de uso.
