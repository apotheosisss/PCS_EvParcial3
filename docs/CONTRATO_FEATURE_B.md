# Contrato de datos: Feature B → Feature C

> Documento para quien desarrolla **feature/b** (limpieza, transformación y feature
> engineering). Define **exactamente** qué debe entregar para que **feature/c**
> (modelado, dashboard, API) funcione sin fricción.
>
> Mientras este entregable no exista, feature/c trabaja contra un dataset de muestra
> generado por `scripts/make_sample_model_input.py`.

---

## 1. Entregable principal

| Ítem | Valor |
|------|-------|
| Archivo | `data/05_model_input/model_input.csv` |
| Entrada en catálogo | `model_input` (ya registrada en `conf/base/catalog.yml`) |
| Formato | CSV, UTF-8, separador `,`, header en la primera fila |
| Granularidad | **una fila por participante** (`SEQN` único, sin duplicados) |
| Origen | Unión por `SEQN` de DEMO_L, DIQ_L, BMX_L, GHB_L, GLU_L (+ opcionales) |

Feature C lee este archivo con la entrada de catálogo `model_input`. **No cambies el
nombre ni la ruta** sin avisar, porque rompe el pipeline de modelado, la API y el dashboard.

---

## 2. Columnas obligatorias

### 2.1. Variable objetivo

| Columna | Tipo | Reglas |
|---------|------|--------|
| `diabetes_target` | int (0/1) | **Sin nulos.** Construida según la regla del Notion (ver §3). Ambas clases presentes. |

### 2.2. Identificador (se conserva pero NO se usa como feature)

| Columna | Tipo |
|---------|------|
| `SEQN` | int — identificador del participante |

### 2.3. Columnas de features (todas las demás)

Todo lo que **no** sea `SEQN` ni `diabetes_target` se trata como feature. Requisitos:

- **Sin valores nulos** (imputados durante la limpieza).
- **Solo numéricas**: las categóricas deben venir ya codificadas (one-hot o label encoding).
- **Numéricas escaladas** (StandardScaler o equivalente) — opcional pero recomendado.
- Sin columnas constantes ni 100 % correlacionadas (rompen feature importance).

Set mínimo de features esperado (según Notion §5 / §2):

```
RIDAGEYR        edad
RIAGENDR        sexo (codificado)
RIDRETH3        grupo racial/étnico (codificado)
INDFMPIR        ratio ingreso/pobreza
BMXBMI          índice de masa corporal
BMXWAIST        circunferencia de cintura
LBXGH           HbA1c
LBXGLU          glucosa en ayunas
age_group       (derivada, codificada)
bmi_category    (derivada, codificada)
has_obesity     (0/1)
high_a1c        (0/1)
high_fasting_glucose (0/1)
```

> ⚠️ Si una feature aparece en `model_input.csv` también debería poder llegar por la
> API. Para las features derivadas que el usuario final no puede ingresar (p. ej.
> `bmi_category`), feature C las deriva internamente o las rellena con su media.

---

## 3. Regla de construcción de `diabetes_target` (del Notion)

```
diabetes_target = 1 si:
    DIQ010 == 1            (diagnóstico reportado)
    o LBXGH  >= 6.5        (A1C compatible con diabetes)
    o LBXGLU >= 126        (glucosa en ayunas compatible con diabetes)

diabetes_target = 0 en caso contrario
```

> **Disclaimer obligatorio (incluir en README):** `diabetes_target` es una
> aproximación analítica/educativa basada en datos disponibles; **no reemplaza un
> diagnóstico clínico**.

---

## 4. Códigos especiales NHANES a limpiar (antes de imputar)

NHANES usa códigos que **no** son valores reales y deben convertirse a `NaN` antes de imputar:

| Código | Significado | Variables típicas |
|--------|-------------|--------------------|
| `7`, `9` | Refused / Don't know (preguntas de 1 dígito como `DIQ010`) | cuestionarios |
| `77`, `99` | Refused / Don't know (2 dígitos) | cuestionarios |
| `.` / vacío | No aplica / faltante | todas |

`DIQ010`: 1=Sí, 2=No, 3=Borderline, 7=Refused, 9=Don't know → trata 7/9 como nulo.

---

## 5. Metadatos opcionales (suman puntos, recomendado)

Si puedes, entrega además:

- `data/05_model_input/feature_metadata.json` con, por cada feature:
  `{ "name", "dtype", "is_derived", "user_facing", "default" }`.
  Si no lo entregas, feature C lo infiere automáticamente.
- Registro en la base de auditoría `data/diabetes_nhanes.db` (tabla `etl_audit`):
  filas procesadas, nulos antes/después por tabla.

---

## 6. Checklist de aceptación (Definition of Done de feature/b)

- [ ] `data/05_model_input/model_input.csv` existe y abre con `pandas.read_csv`.
- [ ] `SEQN` único, sin filas duplicadas.
- [ ] `diabetes_target` presente, sin nulos, con ambas clases (0 y 1).
- [ ] Cero nulos en columnas de feature.
- [ ] Todas las features son numéricas (sin `object`/strings).
- [ ] Códigos 7/9/77/99 ya tratados (no aparecen como valores válidos).
- [ ] PR `feature/b → develop` mergeado **antes** de que feature/c haga su merge.

Cuando esto se cumpla, feature/c ejecuta:

```bash
git checkout feature/c
git fetch origin
git merge origin/develop      # trae model_input.csv real
kedro run --pipeline modeling
```

y reemplaza automáticamente el dataset de muestra por el real.
