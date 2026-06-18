# Diccionario de datos

Este documento resume las variables principales usadas en el proyecto **NHANES Diabetes Risk**. Las fuentes corresponden al ciclo NHANES August 2021-August 2023.

## Llave de integración

| Variable | Fuente | Descripción |
| --- | --- | --- |
| `SEQN` | Todas las tablas NHANES | Identificador único del participante. Se usa como llave para unir datasets. |

## Variables demográficas

| Variable | Fuente | Descripción |
| --- | --- | --- |
| `RIDAGEYR` | `DEMO_L.xpt` | Edad del participante en años. |
| `RIAGENDR` | `DEMO_L.xpt` | Sexo reportado en NHANES. |
| `RIDRETH3` | `DEMO_L.xpt` | Grupo racial/étnico. |
| `INDFMPIR` | `DEMO_L.xpt` | Ratio ingreso familiar/pobreza. |

## Cuestionario de diabetes

| Variable | Fuente | Descripción |
| --- | --- | --- |
| `DIQ010` | `DIQ_L.xpt` | Respuesta sobre diagnóstico médico reportado de diabetes. |

## Medidas corporales

| Variable | Fuente | Descripción |
| --- | --- | --- |
| `BMXBMI` | `BMX_L.xpt` | Índice de masa corporal. |
| `BMXWT` | `BMX_L.xpt` | Peso corporal. |
| `BMXHT` | `BMX_L.xpt` | Estatura. |
| `BMXWAIST` | `BMX_L.xpt` | Circunferencia de cintura. |

## Laboratorio

| Variable | Fuente | Descripción |
| --- | --- | --- |
| `LBXGH` | `GHB_L.xpt` | Hemoglobina glicosilada HbA1c. |
| `LBXGLU` | `GLU_L.xpt` | Glucosa plasmática en ayunas. |

## Variables complementarias

| Grupo | Fuente | Uso |
| --- | --- | --- |
| `PAQ_*` | `PAQ_L.xpt` | Variables de actividad física. |
| `SLQ_*` | `SLQ_L.xpt` | Variables de sueño. |
| `BPXO_*` | `BPXO_L.xpt` | Variables de presión arterial. |

## Umbrales educativos

Archivo: `data/01_raw/umbrales_diabetes.csv`

| Variable | Criterio | Valor | Descripción |
| --- | --- | --- | --- |
| `LBXGH` | `>=` | `6.5` | A1C compatible con diabetes para uso analítico educativo. |
| `LBXGLU` | `>=` | `126` | Glucosa en ayunas compatible con diabetes para uso analítico educativo. |
| `BMXBMI` | `>=` | `30` | Obesidad según IMC. |
| `RIDAGEYR` | `>=` | `45` | Edad de mayor riesgo metabólico. |

## Variable objetivo sugerida

`feature/b` debe construir `diabetes_target` como aproximación analítica:

```text
diabetes_target = 1 si DIQ010 == 1 o LBXGH >= 6.5 o LBXGLU >= 126
diabetes_target = 0 en caso contrario
```

Esta variable no reemplaza diagnóstico médico. Su uso es académico y exploratorio.
