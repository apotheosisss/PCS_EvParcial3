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

Fe