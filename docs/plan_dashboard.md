# Plan de implementación — Dashboard web (Next.js + shadcn/ui)

> Front-end web que consume la API FastAPI (`docs/api_docs.md`, `docs/plan_api.md`)
> y reproduce las tres vistas del proyecto: **Ejecutiva**, **Técnica** y **Operativa**
> (`docs/manual_usuario.md`), con enfoque **educativo, no diagnóstico**.
>
> Rama: `feature/dashboard`. Convive con el dashboard Streamlit existente
> (`dashboards/`) sin reemplazarlo: es una alternativa web moderna.

---

## 0. Decisiones de arquitectura

| Decisión | Elección | Motivo |
|----------|----------|--------|
| Framework | Next.js (App Router) | Lo crea el comando `--template next`; SSR + file routing |
| UI | shadcn/ui (preset `b6G4E4Ia9`) | Componentes accesibles + tema preconfigurado del preset |
| Ubicación | `frontend/` (subcarpeta del repo) | Monorepo simple; Python en la raíz, web aislado |
| Datos | TanStack Query + fetch tipado | Caché, estados loading/error, refetch; ideal para filtros y formularios |
| Gráficos | Recharts (vía shadcn `chart`) | Integrado con shadcn; barras/heatmap sin librería extra |
| Estilos | Tailwind (incluido por shadcn) | Tokens del preset |
| Estado API base | `NEXT_PUBLIC_API_BASE_URL` | Configurable por entorno (`.env.local`) |

**CORS**: la API ya permite `http://localhost:3000` (ver `CORS_ORIGINS` en `.env.example`).
Si el front corre en otro puerto, agregarlo ahí.

---

## 1. Scaffolding (Fase 0)

```bash
# Desde la raíz del repo, en la rama feature/dashboard
mkdir frontend && cd frontend
npx shadcn@latest init --preset b6G4E4Ia9 --template next
```

El comando crea el proyecto Next.js con el preset (tema, fuentes, `components.json`,
Tailwind y utilidades base). Tras inicializar, agregar los componentes que usaremos:

```bash
npx shadcn@latest add card table tabs button input label select badge \
  separator skeleton alert sonner chart dialog form
```

Dependencias adicionales:
```bash
npm install @tanstack/react-query
```

Crear `frontend/.env.local`:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

> Si el `init` pregunta por sobrescribir, mantener el preset; no commitear `node_modules`
> (verificar que el `.gitignore` generado lo excluya, y añadir `frontend/.next`).

---

## 2. Capa de acceso a la API (Fase 1)

Tipos TypeScript espejo de `api/schemas.py` y un cliente fetch tipado.

`frontend/lib/types.ts` — interfaces:
```ts
export interface Health { status: string; model_loaded: boolean; metrics_loaded: boolean; model_version: string | null }
export interface ModelInfo { model_name: string | null; model_version: string; n_features: number }
export interface FeatureMeta { name: string; label: string; dtype: string; user_facing: boolean; is_derived: boolean; default: number | null; min: number | null; max: number | null; unit: string | null }
export interface FeaturesResponse { n_features: number; feature_names: string[]; features: FeatureMeta[] }
export interface Threshold { variable: string; op: string; value: number; description: string | null }
export interface Metrics { best_model: string; metrics: ModelScores; all_models: Record<string, ModelScores>; n_features: number }
export interface ModelScores { accuracy: number; precision: number; recall: number; f1: number; roc_auc: number }
export interface ModelComparisonRow extends ModelScores { model: string }
export interface ConfusionMatrix { labels: string[]; index: string[]; columns: string[]; matrix: number[][] }
export interface FeatureImportance { feature: string; importance: number }
export interface Summary { n_participants: number; n_positive: number | null; n_negative: number | null; positive_rate: number | null }
export interface DistributionBucket { key: string; count: number; positive_rate: number | null }
export interface PredictResult { prediction: number; label: string; probability: number; risk_band: string; threshold: number; model_version: string }
```

`frontend/lib/api.ts` — wrapper:
- `apiFetch<T>(path, init?)` que arma la URL con `NEXT_PUBLIC_API_BASE_URL`, parsea JSON
  y lanza un error con `detail` cuando `!res.ok` (mapea `503` a un estado "modelo no listo").
- Funciones por endpoint: `getHealth`, `getModelInfo`, `getFeatures`, `getThresholds`,
  `getMetrics`, `getModelComparison`, `getConfusionMatrix`, `getFeatureImportance`,
  `getSummary`, `getDistribution(by)`, `postPredict(payload)`, `postPredictBatch(items)`,
  `getPredictions(limit, offset)`.

`frontend/lib/query.tsx` — `QueryClientProvider` (client component) montado en el layout.

---

## 3. App shell / layout (Fase 2)

`frontend/app/layout.tsx`:
- Providers: QueryClient + theme (del preset) + `<Toaster />` (sonner).
- Shell: **sidebar** con navegación (Ejecutiva / Técnica / Operativa) + **header** con
  título, badge de versión del modelo (`/model-info`) e indicador de salud (`/health`).
- **Banner de disclaimer** global (shadcn `Alert`): "Resultado educativo… no reemplaza
  diagnóstico clínico".

`frontend/app/page.tsx`: redirige a `/ejecutiva`.

Componentes de layout: `components/layout/sidebar.tsx`, `header.tsx`, `disclaimer.tsx`.
Componentes base reutilizables: `components/kpi-card.tsx`, `components/states.tsx`
(Skeleton de carga + Alert de error/“modelo no listo” para el caso 503).

---

## 4. Vista Ejecutiva (Fase 3) — `app/ejecutiva/page.tsx`

Consume: `GET /stats/summary`, `GET /stats/distribution?by=...`.

- **KPIs** (`KpiCard`): nº participantes, % con diabetes (`positive_rate`), positivos/negativos.
- **Distribuciones** (Recharts `BarChart`) con un `Select` para alternar `by`:
  `age_group | bmi_category | RIAGENDR`. Cada barra muestra `count` y, en tooltip,
  `positive_rate`.
- Estados: Skeleton mientras carga; Alert si la API responde 503.

---

## 5. Vista Técnica (Fase 4) — `app/tecnica/page.tsx`

Consume: `GET /metrics`, `/model-comparison`, `/confusion-matrix`, `/feature-importance`, `/model-info`.

- **Tarjetas de métricas** del mejor modelo (accuracy, precision, recall, f1, roc_auc).
- **Tabla comparativa** de modelos (shadcn `Table`), resaltando `best_model`.
- **Matriz de confusión**: grid 2×2 estilo heatmap (color por magnitud) usando
  `matrix`/`labels`/`index`. Fallback: `GET /report/confusion_matrix.png`.
- **Importancia de variables**: `BarChart` horizontal (top-N con `?top=15`).

---

## 6. Vista Operativa (Fase 5) — `app/operativa/page.tsx`

Consume: `GET /features`, `GET /thresholds`, `POST /predict`, `POST /predict/batch`, `GET /predictions`.

- **Simulador (formulario dinámico)**: construir inputs a partir de `/features`
  filtrando `user_facing === true`; usar `min`/`max`/`unit`/`label`/`default` para
  etiquetar y validar (shadcn `Form` + `Input`/`Select`). Al enviar → `POST /predict`;
  mostrar resultado con `Badge` de `risk_band` (bajo/medio/alto) y `probability`.
  Mostrar los `/thresholds` como referencia clínica junto a los campos.
- **Predicción por lote**: subir CSV / pegar JSON → `POST /predict/batch`; tabla de
  resultados + botón **descargar CSV**.
- **Muestra de predicciones**: tabla paginada desde `GET /predictions?limit=&offset=`
  (`y_true`, `y_pred`, `probability`) con descarga CSV.

---

## 7. Robustez, pulido y entrega (Fase 6)

- **Estados**: loading (Skeleton), error y vacío para cada query; mensaje claro en 503
  ("Ejecuta `kedro run` para generar el modelo").
- **Responsive** y **dark mode** (del preset).
- **Accesibilidad**: labels en inputs, foco visible, contraste (shadcn ya ayuda).
- **Calidad**: `npm run lint`, `npm run build` deben pasar.
- **Docker (opcional)**: nuevo servicio `web` en `docker/docker-compose.yml`
  (Node 20-alpine, `npm run build && npm start`, puerto 3000, `depends_on: api`),
  con `NEXT_PUBLIC_API_BASE_URL` apuntando al servicio `api`.
- **Docs**: actualizar `docs/manual_usuario.md` (mencionar el dashboard web) y crear
  `frontend/README.md` (cómo correr: `npm run dev`).

---

## 8. Estructura de carpetas objetivo

```
frontend/
  app/
    layout.tsx              # shell, providers, disclaimer
    page.tsx                # -> /ejecutiva
    ejecutiva/page.tsx
    tecnica/page.tsx
    operativa/page.tsx
  components/
    ui/                     # shadcn (generado)
    layout/{sidebar,header,disclaimer}.tsx
    kpi-card.tsx
    states.tsx              # loading / error / 503
    charts/{distribution-bar,importance-bar,confusion-matrix}.tsx
    predict-form.tsx
    batch-predict.tsx
    predictions-table.tsx
  lib/
    api.ts                  # cliente fetch tipado
    types.ts                # tipos espejo de api/schemas.py
    query.tsx               # QueryClientProvider
    utils.ts                # (cn, formato, csv)
  .env.local               # NEXT_PUBLIC_API_BASE_URL
```

---

## 9. Mapa endpoint → componente (resumen)

| Endpoint | Vista | Componente |
|----------|-------|------------|
| `GET /health`, `/model-info` | Global | header |
| `GET /stats/summary` | Ejecutiva | KpiCard |
| `GET /stats/distribution?by=` | Ejecutiva | DistributionBar |
| `GET /metrics`, `/model-comparison` | Técnica | métricas + tabla |
| `GET /confusion-matrix` | Técnica | ConfusionMatrix |
| `GET /feature-importance` | Técnica | ImportanceBar |
| `GET /features`, `/thresholds` | Operativa | PredictForm |
| `POST /predict`, `/predict/batch` | Operativa | PredictForm / BatchPredict |
| `GET /predictions` | Operativa | PredictionsTable |

---

## 10. Orden de ejecución sugerido

1. Fase 0 — scaffolding (init + componentes + env). *Verificar `npm run dev` arranca.*
2. Fase 1 — `lib/types.ts`, `lib/api.ts`, `lib/query.tsx`.
3. Fase 2 — layout, sidebar, header (health/model-info), disclaimer.
4. Fase 3 — Ejecutiva (la más simple; valida la cadena front↔API end-to-end).
5. Fase 4 — Técnica.
6. Fase 5 — Operativa (la más interactiva).
7. Fase 6 — pulido, Docker y docs.

**Prerrequisito en cada fase**: tener la API corriendo (`uvicorn api.main:app --reload`)
con artefactos generados (`kedro run` o `python scripts/make_sample_model_input.py` + `kedro run`).
