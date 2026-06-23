# Dashboard web — NHANES Diabetes Risk

Front-end Next.js (App Router) + shadcn/ui que consume la API FastAPI del proyecto
(`api/main.py`). Reproduce las tres vistas: **Ejecutiva**, **Técnica** y **Operativa**.

> Uso educativo basado en datos NHANES. No reemplaza un diagnóstico clínico.

## Requisitos

- Node.js 20+ (probado con Node 24) y Python con las dependencias de la raíz instaladas.
- Artefactos del modelo generados (`kedro run` o `python scripts/make_sample_model_input.py` + `kedro run`).

## Configuración

Crea `frontend/.env.local` con la URL base de la API:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

El front se sirve en el puerto **5173** (no 3000) porque está en la allowlist de CORS
de la API (`CORS_ORIGINS` en `.env.example` de la raíz) y evita choques con otros
servicios locales en 3000. Si lo sirves en otro origen, agrégalo a `CORS_ORIGINS`.

## Desarrollo (front + API juntos)

```bash
cd frontend
npm install        # solo la primera vez
npm run dev        # levanta Next (:5173) y uvicorn (:8000) a la vez
```

Abre `http://localhost:5173`. `npm run dev` usa `concurrently`:
- `dev:web` → `next dev -p 5173`
- `dev:api` → `uvicorn api.main:app --reload` (desde la raíz del repo, :8000)

Para correr solo uno: `npm run dev:web` o `npm run dev:api`.

## Build de producción

```bash
npm run build
npm run start
```

## Scripts útiles

| Script | Descripción |
|--------|-------------|
| `npm run dev` | Next (:5173) + uvicorn (:8000) en paralelo |
| `npm run dev:web` | Solo Next (:5173) |
| `npm run dev:api` | Solo la API (uvicorn :8000) |
| `npm run build` | Build de producción |
| `npm run start` | Sirve el build (:5173) |
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
