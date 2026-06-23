# Manual de usuario (feature/c)

## Dashboard web (Next.js + shadcn/ui)
Front-end moderno en `frontend/` que consume la API FastAPI. Tres vistas:
- **Ejecutiva**: KPIs (participantes, % diabetes) y distribuciones por edad/IMC/sexo.
- **Técnica**: métricas, comparación de modelos, matriz de confusión e importancia de variables.
- **Operativa**: simulador de predicción, predicción por lote (CSV/JSON) y tabla de predicciones.

Levantar (requiere la API en `:8000`): `cd frontend && npm install && npm run dev` → `http://localhost:3000`.
Ver `frontend/README.md`.

## Dashboard (Streamlit)
- **Ejecutiva**: KPIs (participantes, % diabetes), distribuciones por edad/sexo/IMC.
- **Técnica**: métricas, matriz de confusión, comparación de modelos, importancia de variables.
- **Operativa**: filtros, tabla, **simulador de predicción** y descarga CSV.

## API
Ver `docs/api_docs.md`. El simulador del dashboard y `/predict` usan el mismo modelo.

> Resultado educativo basado en datos NHANES. No reemplaza evaluación médica.
