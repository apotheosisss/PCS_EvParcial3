"""Paquete de la API REST de NHANES Diabetes Risk (feature/c).

Arquitectura modular:
    config      -> configuración por entorno (rutas, CORS, umbrales)
    artifacts   -> capa de acceso a datos con caché (bundle, métricas, CSVs)
    schemas     -> contratos Pydantic (request/response)
    services    -> lógica de negocio (predicción, stats, metadatos, reporting)
    routers     -> endpoints HTTP agrupados por recurso
    main        -> app factory + `app` listo para `uvicorn api.main:app`

Disclaimer: herramienta analítica/educativa basada en datos públicos NHANES.
NO es un diagnóstico clínico.
"""
