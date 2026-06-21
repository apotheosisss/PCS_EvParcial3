# Dashboard web — NHANES Diabetes Risk

Front-end Next.js (App Router) + shadcn/ui que consume la API FastAPI del proyecto
(`api/main.py`). Reproduce las tres vistas: **Ejecutiva**, **Técnica** y **Operativa**.

> Uso educativo basado en datos NHANES. No reemplaza un diagnóstico clínico.

## Requisitos

- Node.js 20+ (probado con Node 24).
- La API corriendo: desde la raíz del repo `uvicorn api.main:app --reload` (puerto 8000)
  con los artefactos generados (`kedro run` o `python scripts/make_sample_model_input.py`).

## Configuración

Crea `frontend/.env.local` con la URL base de la API:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

La API ya permite CORS para `http://localhost:3000`, `http://localhost:5173` y
`http://localhost:8501` (ver `CORS_ORIGINS` en `.env.example` de la raíz). Si sirves
el front en otro origen, agrégalo ahí.

## Desarrollo

```bash
cd frontend
npm install        # solo la primera vez
npm run dev        # http://localhost:3000
```

## Build de producción

```bash
npm run build
npm run start
```

## Scripts útiles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Build de producción |
| `npm run start` | Sirve el build |
| `npm run lint` | ESLint |
| `npm run typecheck` | Chequeo de tipos (`tsc --noEmit`) |

## Estructura

```
app/                      rutas (App Router)
  ejecutiva/  tecnica/  operativa/
components/
  layout/                 shell: sidebar, header, disclaimer
  views/                  componentes por vista (charts, formularios, tablas)
  ui/                     componentes shadcn (preset radix-lyra)
  kpi-card.tsx  states.tsx
lib/
  api.ts                  cliente HTTP tipado
  types.ts                tipos espejo de api/schemas.py
  queries.ts              hooks de TanStack Query
  providers.tsx           QueryClient + Toaster
  format.ts               formato y exportación CSV
```

## Mapa vista → endpoints

- **Ejecutiva**: `GET /stats/summary`, `GET /stats/distribution`
- **Técnica**: `GET /metrics`, `/model-comparison`, `/confusion-matrix`, `/feature-importance`
- **Operativa**: `GET /features`, `/thresholds`, `POST /predict`, `/predict/batch`, `GET /predictions`
- **Global**: `GET /health`, `/model-info`

Atajo: presiona `d` para alternar modo claro/oscuro.
