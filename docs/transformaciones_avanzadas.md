# Transformaciones avanzadas y optimización (IEE 1.2.1)

Este documento evidencia el uso de técnicas avanzadas de Pandas/NumPy optimizadas
para gran escala, exigidas por el indicador **IEE 1.2.1**. El código vive en
[`src/nhanes_diabetes/utils/transforms.py`](../src/nhanes_diabetes/utils/transforms.py)
y se ejecuta sobre datos reales con
[`scripts/advanced_transforms_demo.py`](../scripts/advanced_transforms_demo.py).

Reproducir:

```bash
python scripts/advanced_transforms_demo.py
```

## Resultados medidos (model_input real: 8 149 filas × 44 columnas)

| Técnica | Función | Resultado sobre datos reales |
|---|---|---|
| Optimización de memoria | `optimize_dtypes` | **2.74 MB → 0.76 MB (−72.2 %)** |
| Broadcasting (z-score) | `broadcast_zscore` | Estandariza 4 columnas en una operación matricial |
| Pivot / tabla dinámica | `pivot_prevalence` | Prevalencia por obesidad × grupo etario |
| Reshape (melt) | `reshape_long` | 8 149×44 → 16 298×3 (formato largo) |
| Chunking | `chunked_group_mean` | Media por grupo con memoria constante |

## Detalle y justificación técnica

### 1. Optimización de memoria — `optimize_dtypes`
Downcast vectorizado de tipos: `int64→int8/16/32`, `float64→float32`, y columnas de
texto de baja cardinalidad a `category`. Se elige el tipo más pequeño que preserva el
rango, sin pérdida de información. **Impacto medido: −72 % de memoria**, lo que permite
procesar volúmenes mayores en la misma RAM y acelera operaciones posteriores por mejor
uso de caché.

### 2. Broadcasting — `broadcast_zscore`
La estandarización `(X − μ) / σ` se calcula de una sola vez sobre la matriz `M×N`;
los vectores `μ` y `σ` (`1×N`) se **difunden** contra la matriz. Evita bucles por fila
y `.apply` por columna: es vectorización pura de NumPy, órdenes de magnitud más rápida.

### 3. Pivot / tabla dinámica — `pivot_prevalence`
`pivot_table` con agregación vectorizada. Ejemplo real:

```
age_group_age_45_64      0      1
has_obesity
0                    0.104  0.141
1                    0.224  0.321
```

Lectura de negocio: la prevalencia de `diabetes_target` sube de **10.4 %** (no obeso,
joven) a **32.1 %** (obeso, 45–64) — un gradiente coherente con la literatura clínica.

### 4. Reshape (wide → long) — `reshape_long`
`melt` transforma el formato ancho a largo (`variable`, `valor`), ideal para graficar
múltiples biomarcadores en una sola figura facetada o alimentar herramientas long-form.

### 5. Chunking — `chunked_group_mean`
Lectura del CSV por *chunks* con acumulación online de sumas y conteos por grupo. La
memoria es **O(grupos)** en vez de **O(filas)**, lo que permite agregar archivos que no
caben en RAM. Ejemplo: IMC medio por sexo calculado sin cargar el archivo completo.

## Relación con el pipeline
Estas utilidades son transversales: `optimize_dtypes` es aplicable tras la ingesta de
los XPT para reducir la huella de memoria del `merged`, y `broadcast_zscore` refleja el
mismo principio de escalado que el `StandardScaler` dentro del `Pipeline` de modelado
(ajustado solo con train para evitar fuga de datos).
