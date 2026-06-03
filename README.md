# NHANES Diabetes Risk 

Proyecto desarrollado para la **Evaluación Parcial N°3** de la asignatura **Programación para la Ciencia de Datos — SCY1101**.

Este repositorio implementa una solución **end-to-end de ciencia de datos** utilizando **Kedro**, orientada al análisis y predicción de riesgo de **diabetes/prediabetes** a partir de datos públicos de **NHANES 08/2021–08/2023**.

El proyecto integra múltiples fuentes de datos, ejecuta un pipeline ETL automatizado, realiza limpieza y transformación de variables clínicas, entrena modelos de Machine Learning, expone resultados mediante una API, visualiza métricas en un dashboard interactivo y permite ejecución reproducible mediante Docker.

---

## 1. Resumen del proyecto

El objetivo principal del proyecto es construir un flujo profesional de ciencia de datos capaz de:

1. Ingerir datos oficiales de NHANES.
2. Integrar múltiples fuentes de datos clínicas, demográficas y complementarias.
3. Limpiar datos faltantes, duplicados, códigos especiales y valores fuera de rango.
4. Crear variables derivadas útiles para modelamiento.
5. Entrenar modelos predictivos para estimar riesgo de diabetes/prediabetes.
6. Comparar modelos mediante métricas de clasificación.
7. Visualizar resultados en un dashboard interactivo.
8. Exponer resultados mediante una API REST.
9. Ejecutar el sistema completo usando Docker.
10. Evidenciar buenas prácticas de trabajo colaborativo con Git.

---

## 2. Problema de negocio / análisis

La diabetes y la prediabetes son condiciones metabólicas asociadas a múltiples factores: edad, composición corporal, presión arterial, glucosa, hemoglobina glicosilada, hábitos de vida y antecedentes médicos.

Este proyecto busca responder la siguiente pregunta:

> ¿Es posible construir un pipeline reproducible que permita estimar riesgo de diabetes o prediabetes usando datos públicos de salud poblacional?

El sistema no debe entenderse como una herramienta diagnóstica médica, sino como un ejercicio académico de análisis predictivo y ciencia de datos reproducible.

---

## 3. Objetivos

### Objetivo general

Desarrollar una solución end-to-end en Kedro para integrar, procesar, modelar y visualizar datos de NHANES relacionados con diabetes y factores de riesgo metabólico.

### Objetivos específicos

* Integrar al menos tres fuentes de datos diferentes.
* Construir un pipeline ETL automatizado.
* Aplicar limpieza robusta de datos clínicos.
* Validar esquemas y controlar errores.
* Crear variables derivadas relevantes para análisis.
* Entrenar y comparar modelos de clasificación.
* Generar visualizaciones interactivas diferenciadas por audiencia.
* Exponer métricas y predicciones mediante API REST.
* Containerizar la solución con Docker y docker-compose.
* Documentar arquitectura, instalación, uso y despliegue.
* Aplicar flujo colaborativo con ramas, commits, pull requests e issues.

---

## 4. Fuente principal de datos

La fuente principal utilizada es **NHANES — National Health and Nutrition Examination Survey**, correspondiente al ciclo:

```text
NHANES 08/2021–08/2023
```

Se selecciona este ciclo porque permite trabajar con datos recientes y consistentes dentro de una misma temporalidad, evitando mezclar metodologías entre ciclos diferentes.

---

## 5. Fuentes de datos integradas

Para cumplir con el requisito de integración de múltiples fuentes, el proyecto trabaja con tres tipos de fuentes:

### Fuente 1: Archivos NHANES oficiales

Archivos en formato `.XPT` descargados desde NHANES:

| Archivo      | Categoría     | Descripción                                    |
| ------------ | ------------- | ---------------------------------------------- |
| `DEMO_L.XPT` | Demographics  | Información demográfica de participantes       |
| `BMX_L.XPT`  | Examination   | Medidas corporales: peso, altura, BMI, cintura |
| `DIQ_L.XPT`  | Questionnaire | Cuestionario de diabetes                       |
| `GHB_L.XPT`  | Laboratory    | Hemoglobina glicosilada / HbA1c                |
| `GLU_L.XPT`  | Laboratory    | Glucosa en ayunas                              |
| `BPQ_L.XPT`  | Questionnaire | Antecedentes de presión arterial y colesterol  |
| `PAQ_L.XPT`  | Questionnaire | Actividad física                               |
| `SMQ_L.XPT`  | Questionnaire | Tabaquismo                                     |

### Fuente 2: Archivo CSV/Excel complementario

Archivo creado por el equipo:

```text
data/01_raw/clinical_thresholds.csv
```

Este archivo contiene umbrales usados para clasificación y análisis:

| Variable           |    Umbral | Descripción       |
| ------------------ | --------: | ----------------- |
| HbA1c normal       |     < 5.7 | Bajo riesgo       |
| HbA1c prediabetes  |   5.7–6.4 | Riesgo intermedio |
| HbA1c diabetes     |    >= 6.5 | Alto riesgo       |
| BMI sobrepeso      |     >= 25 | Sobrepeso         |
| BMI obesidad       |     >= 30 | Obesidad          |
| Sueño insuficiente | < 7 horas | Riesgo conductual |

### Fuente 3: Base de datos SQL

Base SQLite o PostgreSQL utilizada para registrar:

```text
data/nhanes_project.db
```

Tablas internas:

| Tabla                    | Descripción                          |
| ------------------------ | ------------------------------------ |
| `etl_audit_log`          | Registro de ejecución del pipeline   |
| `processed_participants` | Datos limpios y transformados        |
| `model_predictions`      | Predicciones generadas por el modelo |
| `model_metrics`          | Métricas históricas de modelos       |

---

## 6. Arquitectura general

El sistema sigue una arquitectura modular basada en Kedro:

```text
┌────────────────────┐
│  Fuentes de datos  │
│ NHANES / CSV / SQL │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Pipeline Kedro    │
│  Ingestion         │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Cleaning          │
│  Validación        │
│  Nulos / Outliers  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Feature Engineering│
│ Target / Variables │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│  Modeling          │
│  ML / Métricas     │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Reporting          │
│ Métricas / Gráficos│
└──────┬───────┬─────┘
       │       │
       ▼       ▼
┌──────────┐ ┌────────────┐
│ FastAPI  │ │ Streamlit  │
│ API REST │ │ Dashboard  │
└──────────┘ └────────────┘
```

---

## 7. Estructura del repositorio

```text
nhanes-diabetes-risk/
│
├── conf/
│   ├── base/
│   │   ├── catalog.yml
│   │   ├── parameters.yml
│   │   └── logging.yml
│   └── local/
│       └── credentials.yml
│
├── data/
│   ├── 01_raw/
│   ├── 02_intermediate/
│   ├── 03_primary/
│   ├── 04_feature/
│   ├── 05_model_input/
│   ├── 06_models/
│   ├── 07_model_output/
│   └── 08_reporting/
│
├── src/
│   └── nhanes_diabetes/
│       ├── pipelines/
│       │   ├── ingestion/
│       │   ├── cleaning/
│       │   ├── feature_engineering/
│       │   ├── modeling/
│       │   └── reporting/
│       ├── settings.py
│       └── pipeline_registry.py
│
├── dashboards/
│   └── streamlit_app.py
│
├── api/
│   └── main.py
│
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.dashboard
│   ├── Dockerfile.api
│   └── docker-compose.yml
│
├── docs/
│   ├── arquitectura.md
│   ├── api_docs.md
│   ├── guia_despliegue.md
│   ├── manual_usuario.md
│   ├── modelo.md
│   └── evidencias_git.md
│
├── tests/
│   ├── test_ingestion.py
│   ├── test_cleaning.py
│   ├── test_features.py
│   └── test_modeling.py
│
├── repo/
│   ├── git_log.txt
│   ├── branches.txt
│   ├── issues.png
│   └── pull_requests.png
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── pyproject.toml
└── Makefile
```

---

## 8. Variables principales

### Identificador de unión

Todas las tablas NHANES se integran mediante:

```text
SEQN
```

`SEQN` corresponde al identificador único del participante dentro del ciclo NHANES.

### Variables demográficas

| Variable   | Descripción               |
| ---------- | ------------------------- |
| `RIDAGEYR` | Edad del participante     |
| `RIAGENDR` | Sexo                      |
| `RIDRETH3` | Grupo racial/étnico       |
| `DMDEDUC2` | Nivel educacional         |
| `INDFMPIR` | Indicador ingreso-pobreza |

### Variables corporales

| Variable   | Descripción               |
| ---------- | ------------------------- |
| `BMXWT`    | Peso                      |
| `BMXHT`    | Altura                    |
| `BMXBMI`   | Índice de masa corporal   |
| `BMXWAIST` | Circunferencia de cintura |

### Variables metabólicas

| Variable | Descripción                          |
| -------- | ------------------------------------ |
| `LBXGH`  | Hemoglobina glicosilada / HbA1c      |
| `LBXGLU` | Glucosa                              |
| `DIQ010` | Diagnóstico reportado de diabetes    |
| `DIQ160` | Diagnóstico reportado de prediabetes |

### Variables conductuales

| Variable | Descripción                   |
| -------- | ----------------------------- |
| `PAQ`    | Actividad física              |
| `SMQ`    | Tabaquismo                    |
| `BPQ`    | Antecedentes cardiovasculares |

---

## 9. Definición del target

El proyecto permite dos estrategias de modelamiento.

### Estrategia A: Diabetes autoinformada

Se crea un target binario usando el cuestionario de diabetes:

```text
diabetes_flag = 1 si DIQ010 indica diagnóstico de diabetes
diabetes_flag = 0 en caso contrario
```

### Estrategia B: Riesgo metabólico derivado

Se crea una variable de riesgo combinando HbA1c y glucosa:

```text
diabetes_risk =
    0 → bajo riesgo
    1 → prediabetes / riesgo intermedio
    2 → diabetes / riesgo alto
```

La estrategia final seleccionada para el modelo principal es:

```text
diabetes_risk
```

Esto permite trabajar un problema multiclase más interesante y clínicamente interpretable.

---

## 10. Pipeline Kedro

El proyecto está dividido en cinco pipelines principales.

---

### 10.1 Pipeline de ingesta

Nombre Kedro:

```bash
kedro run --pipeline ingestion
```

Responsabilidades:

* Leer archivos `.XPT` de NHANES.
* Leer archivo CSV/Excel de umbrales clínicos.
* Leer o inicializar base SQL.
* Validar existencia de archivos.
* Registrar logs de carga.
* Guardar datasets en `data/02_intermediate`.

Entradas:

```text
data/01_raw/DEMO_L.XPT
data/01_raw/BMX_L.XPT
data/01_raw/DIQ_L.XPT
data/01_raw/GHB_L.XPT
data/01_raw/GLU_L.XPT
data/01_raw/BPQ_L.XPT
data/01_raw/clinical_thresholds.csv
```

Salidas:

```text
data/02_intermediate/demo_raw.parquet
data/02_intermediate/bmx_raw.parquet
data/02_intermediate/diq_raw.parquet
data/02_intermediate/ghb_raw.parquet
data/02_intermediate/glu_raw.parquet
data/02_intermediate/bpq_raw.parquet
```

---

### 10.2 Pipeline de limpieza

Nombre Kedro:

```bash
kedro run --pipeline cleaning
```

Responsabilidades:

* Eliminar duplicados por `SEQN`.
* Convertir códigos especiales a `NaN`.
* Validar rangos mínimos y máximos.
* Eliminar columnas con exceso de nulos.
* Imputar variables numéricas.
* Imputar variables categóricas.
* Generar reporte de calidad de datos.

Códigos tratados como faltantes:

```text
7, 9, 77, 99, 777, 999, 7777, 9999
```

Salidas:

```text
data/03_primary/participants_clean.parquet
data/08_reporting/missing_values_report.csv
data/08_reporting/cleaning_summary.json
```

---

### 10.3 Pipeline de feature engineering

Nombre Kedro:

```bash
kedro run --pipeline feature_engineering
```

Responsabilidades:

* Unir tablas limpias por `SEQN`.
* Crear target `diabetes_risk`.
* Crear categorías de BMI.
* Crear grupos etarios.
* Crear indicador de obesidad abdominal.
* Crear variables de riesgo metabólico.
* Codificar variables categóricas.
* Escalar variables numéricas.

Features derivadas:

| Feature                | Descripción                   |
| ---------------------- | ----------------------------- |
| `age_group`            | Grupo etario                  |
| `bmi_category`         | Normal, sobrepeso, obesidad   |
| `waist_risk`           | Riesgo por cintura            |
| `hba1c_category`       | Normal, prediabetes, diabetes |
| `glucose_category`     | Normal, elevada, alta         |
| `metabolic_risk_score` | Puntaje simple de riesgo      |
| `diabetes_risk`        | Target final                  |

Salidas:

```text
data/04_feature/features.parquet
data/05_model_input/model_input.parquet
```

---

### 10.4 Pipeline de modelamiento

Nombre Kedro:

```bash
kedro run --pipeline modeling
```

Responsabilidades:

* Separar train/test.
* Entrenar modelos base.
* Comparar rendimiento.
* Guardar modelo ganador.
* Generar métricas.
* Exportar predicciones.
* Guardar matriz de confusión.
* Guardar importancia de variables.

Modelos utilizados:

| Modelo              | Descripción                      |
| ------------------- | -------------------------------- |
| Logistic Regression | Modelo base interpretable        |
| Random Forest       | Modelo no lineal robusto         |
| Gradient Boosting   | Modelo avanzado para comparación |

Métricas calculadas:

| Métrica          | Uso                              |
| ---------------- | -------------------------------- |
| Accuracy         | Rendimiento global               |
| Precision        | Control de falsos positivos      |
| Recall           | Control de falsos negativos      |
| F1-score         | Balance entre precision y recall |
| ROC-AUC          | Separabilidad del modelo         |
| Confusion Matrix | Análisis de errores              |

Salidas:

```text
data/06_models/model.pkl
data/06_models/preprocessor.pkl
data/08_reporting/model_metrics.json
data/08_reporting/model_comparison.csv
data/08_reporting/confusion_matrix.png
data/08_reporting/feature_importance.csv
```

---

### 10.5 Pipeline de reporting

Nombre Kedro:

```bash
kedro run --pipeline reporting
```

Responsabilidades:

* Consolidar métricas.
* Generar gráficos finales.
* Preparar archivos usados por dashboard.
* Exportar resumen ejecutivo.
* Registrar predicciones en base SQL.

Salidas:

```text
data/08_reporting/executive_summary.json
data/08_reporting/dashboard_dataset.parquet
data/08_reporting/model_report.html
```

---

## 11. Ejecución completa del proyecto

Para ejecutar el flujo completo:

```bash
kedro run
```

Para ejecutar pipelines por separado:

```bash
kedro run --pipeline ingestion
kedro run --pipeline cleaning
kedro run --pipeline feature_engineering
kedro run --pipeline modeling
kedro run --pipeline reporting
```

---

## 12. Instalación local

### 12.1 Crear entorno virtual

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

En macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 12.2 Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 12.3 Validar instalación

```bash
kedro info
pytest
```

---

## 13. Variables de entorno

Crear un archivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

Contenido esperado:

```env
PROJECT_NAME=nhanes-diabetes-risk
ENVIRONMENT=local

DATA_PATH=data
DATABASE_URL=sqlite:///data/nhanes_project.db

API_HOST=0.0.0.0
API_PORT=8000

DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8501

LOG_LEVEL=INFO
MODEL_NAME=diabetes_risk_model
```

---

## 14. Dashboard interactivo

El dashboard está desarrollado en Streamlit.

Ejecución local:

```bash
streamlit run dashboards/streamlit_app.py
```

URL local:

```text
http://localhost:8501
```

### Vistas disponibles

#### Vista Ejecutiva

Orientada a usuarios no técnicos.

Incluye:

* Total de participantes analizados.
* Distribución de riesgo de diabetes.
* Porcentaje de prediabetes.
* Porcentaje de diabetes.
* Factores de riesgo principales.
* Conclusiones generales.

#### Vista Técnica

Orientada a analistas, docentes o equipo de ciencia de datos.

Incluye:

* Métricas por modelo.
* Matriz de confusión.
* Comparación de algoritmos.
* Importancia de variables.
* Calidad de datos.
* Distribución de nulos.
* Análisis de desbalance de clases.

#### Vista Operativa

Orientada a exploración de casos.

Incluye:

* Filtros por edad, sexo, BMI y riesgo.
* Tabla interactiva de participantes.
* Predicción individual simulada.
* Variables más relevantes por caso.

---

## 15. API REST

La API está desarrollada con FastAPI.

Ejecución local:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

URL local:

```text
http://localhost:8000
```

Documentación automática:

```text
http://localhost:8000/docs
```

### Endpoints disponibles

#### Health check

```http
GET /health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "nhanes-diabetes-risk-api"
}
```

#### Métricas del modelo

```http
GET /metrics
```

Respuesta esperada:

```json
{
  "model": "RandomForestClassifier",
  "accuracy": 0.84,
  "precision": 0.81,
  "recall": 0.79,
  "f1_score": 0.80
}
```

#### Importancia de variables

```http
GET /features
```

Respuesta esperada:

```json
[
  {
    "feature": "LBXGH",
    "importance": 0.31
  },
  {
    "feature": "BMXBMI",
    "importance": 0.18
  }
]
```

#### Predicción individual

```http
POST /predict
```

Ejemplo de entrada:

```json
{
  "age": 52,
  "sex": "Male",
  "bmi": 31.2,
  "waist": 104.5,
  "hba1c": 6.1,
  "glucose": 112,
  "physical_activity": "low",
  "smoking_status": "former"
}
```

Ejemplo de salida:

```json
{
  "prediction": "prediabetes",
  "risk_class": 1,
  "probability": 0.72,
  "model": "RandomForestClassifier"
}
```

---

## 16. Docker

El proyecto incluye Docker para ejecución reproducible.

### 16.1 Construir servicios

```bash
docker compose -f docker/docker-compose.yml build
```

### 16.2 Levantar proyecto completo

```bash
docker compose -f docker/docker-compose.yml up
```

Servicios incluidos:

| Servicio    |         Puerto | Descripción                        |
| ----------- | -------------: | ---------------------------------- |
| `kedro-etl` |              - | Ejecuta pipeline ETL               |
| `api`       |           8000 | API REST con FastAPI               |
| `dashboard` |           8501 | Dashboard Streamlit                |
| `db`        | 5432 / interno | Base de datos si se usa PostgreSQL |

### 16.3 Detener servicios

```bash
docker compose -f docker/docker-compose.yml down
```

### 16.4 Reconstruir desde cero

```bash
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up --build
```

---

## 17. Testing

El proyecto incluye pruebas automatizadas con `pytest`.

Ejecutar todas las pruebas:

```bash
pytest
```

Ejecutar pruebas con salida detallada:

```bash
pytest -v
```

Pruebas consideradas:

| Archivo             | Validación                                      |
| ------------------- | ----------------------------------------------- |
| `test_ingestion.py` | Verifica carga de fuentes                       |
| `test_cleaning.py`  | Verifica limpieza de nulos y duplicados         |
| `test_features.py`  | Verifica creación de target y features          |
| `test_modeling.py`  | Verifica entrenamiento y generación de métricas |

---

## 18. Logging

El proyecto utiliza logging para registrar eventos relevantes:

* Inicio y fin de pipelines.
* Cantidad de registros cargados.
* Cantidad de registros eliminados.
* Nulos detectados.
* Errores de esquema.
* Métricas de modelos.
* Exportación de resultados.

Archivo de configuración:

```text
conf/base/logging.yml
```

Ejemplo de log:

```text
INFO - Starting cleaning pipeline
INFO - DEMO records loaded: 11933
WARNING - Missing values detected in BMXBMI
INFO - Model trained successfully
ERROR - Required column SEQN not found
```

---

## 19. Validación de esquemas

Cada tabla debe cumplir una estructura mínima antes de ser procesada.

Ejemplo para `DEMO_L`:

```text
SEQN
RIDAGEYR
RIAGENDR
RIDRETH3
```

Ejemplo para `BMX_L`:

```text
SEQN
BMXBMI
BMXWT
BMXHT
BMXWAIST
```

Ejemplo para `GHB_L`:

```text
SEQN
LBXGH
```

Si una columna crítica no existe, el pipeline detiene la ejecución y registra el error en el log.

---

## 20. Manejo de errores

El pipeline considera errores frecuentes:

| Error                   | Tratamiento                          |
| ----------------------- | ------------------------------------ |
| Archivo no encontrado   | Mensaje claro y detención controlada |
| Columna crítica ausente | Validación de esquema                |
| Duplicados por `SEQN`   | Eliminación controlada               |
| Códigos especiales      | Conversión a `NaN`                   |
| Exceso de nulos         | Eliminación o imputación             |
| Outliers clínicos       | Revisión por rango                   |
| Error de entrenamiento  | Registro en log y detención          |

---

## 21. Buenas prácticas contra fuga de información

Para evitar data leakage:

* No se usa directamente el target como predictor.
* Variables derivadas del target se excluyen del entrenamiento.
* La imputación y escalado se ajustan solo con train.
* El split train/test se realiza antes del preprocesamiento final.
* El pipeline de transformación se guarda junto al modelo.
* Las métricas se calculan únicamente sobre test.

---

## 22. Consideraciones sobre datos desbalanceados

El problema puede presentar desbalance entre clases.

Medidas consideradas:

* Comparar distribución de clases.
* Usar `class_weight="balanced"` cuando aplique.
* Reportar `precision`, `recall` y `f1-score`, no solo `accuracy`.
* Analizar matriz de confusión.
* Evaluar ajuste de umbral si se trabaja clasificación binaria.
* Revisar desempeño por clase.

---

## 23. Flujo de Git utilizado

El proyecto utiliza una estrategia tipo Git Flow simplificada.

### Ramas principales

| Rama        | Uso                                                |
| ----------- | -------------------------------------------------- |
| `main`      | Versión estable final                              |
| `develop`   | Rama de integración                                |
| `feature/a` | ETL, Kedro, limpieza, features, modelos y tests    |
| `feature/b` | Dashboard, API, Docker, documentación y evidencias |

### Flujo aplicado

```text
feature/a ─┐
           ├──> develop ───> main
feature/b ─┘
```

Ninguna feature se integra directamente a `main`.

Primero se realiza Pull Request hacia `develop`, luego se prueba la integración completa y finalmente se libera una versión estable hacia `main`.

---

## 24. Responsabilidades por rama

### `feature/a`

Responsable de:

* Configuración Kedro.
* Catálogo de datos.
* Pipeline de ingesta.
* Pipeline de limpieza.
* Pipeline de transformación.
* Modelamiento.
* Métricas.
* Tests de datos y modelos.

### `feature/b`

Responsable de:

* Dashboard Streamlit.
* API FastAPI.
* Dockerfiles.
* docker-compose.
* README.
* Documentación técnica.
* Evidencias Git.
* Manual de usuario.
* Guía de despliegue.

---

## 25. Convención de commits

Se utiliza convención semántica:

```text
feat: nueva funcionalidad
fix: corrección de error
docs: documentación
test: pruebas
chore: configuración
refactor: mejora interna
```

Ejemplos:

```bash
git commit -m "feat(ingestion): load NHANES XPT datasets"
git commit -m "feat(cleaning): handle missing values and outliers"
git commit -m "feat(features): create diabetes risk target"
git commit -m "feat(modeling): train baseline classifiers"
git commit -m "feat(dashboard): add executive and technical views"
git commit -m "feat(api): expose metrics and prediction endpoints"
git commit -m "chore(docker): add compose orchestration"
git commit -m "docs(readme): add installation and deployment guide"
git commit -m "test(modeling): validate model metrics output"
```

---

## 26. Pull Requests esperados

### PR 1

```text
feature/a → develop
```

Título:

```text
feat: add Kedro ETL and modeling pipelines
```

Incluye:

* Ingesta.
* Limpieza.
* Feature engineering.
* Modelamiento.
* Métricas.
* Tests.

### PR 2

```text
feature/b → develop
```

Título:

```text
feat: add dashboard API Docker and documentation
```

Incluye:

* Streamlit.
* FastAPI.
* Docker.
* Documentación.
* Evidencias.

### PR 3

```text
develop → main
```

Título:

```text
release: final NHANES diabetes risk project
```

Incluye:

* Proyecto integrado.
* Validaciones ejecutadas.
* Evidencia de funcionamiento.
* Tag final `v1.0.0`.

---

## 27. Comandos Git principales

Crear ramas:

```bash
git checkout -b develop
git checkout -b feature/a
git checkout -b feature/b
```

Actualizar feature desde develop:

```bash
git checkout feature/a
git fetch origin
git merge origin/develop
```

Subir cambios:

```bash
git add .
git commit -m "feat(scope): message"
git push origin feature/a
```

Integración final:

```bash
git checkout develop
git pull origin develop

pytest
kedro run

git checkout main
git pull origin main
git merge develop
git tag -a v1.0.0 -m "Entrega final Evaluación Parcial 3"
git push origin main
git push origin v1.0.0
```

---

## 28. Evidencias Git

La carpeta `repo/` contiene evidencia del trabajo colaborativo:

```text
repo/git_log.txt
repo/branches.txt
repo/issues.png
repo/pull_requests.png
repo/merge_history.png
```

Generar log:

```bash
git log --oneline --graph --all --decorate > repo/git_log.txt
```

Generar listado de ramas:

```bash
git branch -a > repo/branches.txt
```

---

## 29. Makefile

El proyecto incluye comandos simplificados.

```bash
make install
make test
make run
make dashboard
make api
make docker-up
make docker-down
```

Ejemplo de uso:

```bash
make install
make test
make run
make dashboard
```

---

## 30. Reproducibilidad

Para asegurar reproducibilidad:

* Se utiliza Kedro como estructura de proyecto.
* El catálogo de datos está versionado.
* Los parámetros del modelo están en `parameters.yml`.
* Las rutas están centralizadas en `catalog.yml`.
* Las variables sensibles se gestionan mediante `.env`.
* Docker permite ejecutar el sistema en otro equipo.
* Los modelos y métricas se guardan como artefactos.
* Los pipelines pueden ejecutarse de forma independiente.
* Las pruebas automatizadas validan el funcionamiento mínimo.

---

## 31. Resultados esperados

Al finalizar una ejecución completa, deben generarse:

```text
data/03_primary/participants_clean.parquet
data/04_feature/features.parquet
data/05_model_input/model_input.parquet
data/06_models/model.pkl
data/06_models/preprocessor.pkl
data/08_reporting/model_metrics.json
data/08_reporting/model_comparison.csv
data/08_reporting/confusion_matrix.png
data/08_reporting/feature_importance.csv
data/08_reporting/dashboard_dataset.parquet
```

---

## 32. Ejemplo de métricas esperadas

Las métricas pueden variar según limpieza, variables seleccionadas y split de entrenamiento.

Ejemplo referencial:

```json
{
  "model": "RandomForestClassifier",
  "accuracy": 0.84,
  "precision_macro": 0.79,
  "recall_macro": 0.76,
  "f1_macro": 0.77,
  "roc_auc": 0.86
}
```

---

## 33. Limitaciones

Este proyecto tiene fines académicos.

Limitaciones principales:

* Los datos corresponden a una encuesta poblacional.
* El modelo no reemplaza evaluación médica.
* Algunas variables son autoinformadas.
* Puede existir desbalance de clases.
* La disponibilidad de variables depende del ciclo NHANES.
* El modelo depende de la calidad del preprocesamiento.
* No se realiza inferencia clínica real.

---

## 34. Mejoras futuras

Posibles mejoras:

* Integrar más ciclos NHANES.
* Comparar periodo pre-pandemia vs post-pandemia.
* Agregar modelos más avanzados como XGBoost o LightGBM.
* Implementar calibración de probabilidades.
* Agregar explainability con SHAP.
* Implementar tracking de experimentos con MLflow.
* Desplegar en Azure, Render o Railway.
* Agregar CI/CD con GitHub Actions.
* Agregar base PostgreSQL real.
* Incorporar monitoreo de drift de datos.

---

## 35. Guía rápida de ejecución

### Opción 1: Ejecución local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

kedro run
streamlit run dashboards/streamlit_app.py
uvicorn api.main:app --reload
```

### Opción 2: Ejecución con Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

### Opción 3: Solo pruebas

```bash
pytest -v
```

---

## 36. Presentación del proyecto

La defensa del proyecto considera:

1. Problema y objetivo.
2. Fuentes de datos integradas.
3. Arquitectura técnica.
4. Pipeline Kedro.
5. Limpieza y validación.
6. Feature engineering.
7. Modelos y métricas.
8. Dashboard por audiencias.
9. API REST.
10. Docker y despliegue.
11. Flujo Git colaborativo.
12. Lecciones aprendidas.
13. Mejoras futuras.

---

## 37. Equipo de trabajo

| Integrante   | Rol                                         |
| ------------ | ------------------------------------------- |
| Integrante 1 | ETL, Kedro, limpieza y modelamiento         |
| Integrante 2 | Dashboard, API, Docker y documentación      |
| Integrante 3 | Testing, QA, Git, presentación y evidencias |

---

## 38. Estado del proyecto

```text
Estado: En desarrollo
Versión: v1.0.0 académica
Asignatura: SCY1101 Programación para la Ciencia de Datos
Evaluación: Parcial N°3
```

---

## 39. Licencia y uso

Este proyecto fue desarrollado con fines académicos.

Los datos utilizados pertenecen a fuentes públicas de NHANES. El código del proyecto se entrega únicamente como evidencia de aprendizaje en programación para ciencia de datos, pipelines reproducibles, visualización, colaboración con Git y despliegue con Docker.

---

## 40. Cierre

Este proyecto demuestra un flujo profesional de ciencia de datos desde la ingesta hasta el despliegue. La solución integra datos reales, procesamiento automatizado, modelamiento predictivo, visualización interactiva, API, pruebas, documentación técnica, control de versiones y ejecución reproducible mediante Docker.

El resultado final es una arquitectura modular, defendible y alineada con buenas prácticas de desarrollo de proyectos de datos.
