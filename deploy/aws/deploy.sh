#!/bin/bash
# =============================================================================
# deploy.sh — despliegue de DiabetesNHANES en la instancia EC2
# Ejecutar DENTRO de la instancia, en la raiz del repo clonado.
#
# Estrategia (aprendida en pruebas locales): el ETL con tuning de 6 modelos es
# intensivo en memoria. Para no saturar la instancia, corremos el ETL primero de
# forma controlada y LUEGO levantamos API + frontend, que solo leen artefactos.
# =============================================================================
set -euxo pipefail

cd "$(dirname "$0")/../.."

# 1) Config por variables de entorno
[ -f .env ] || cp .env.example .env

# 2) Descargar datos NHANES reales (o generar muestra si falla la red)
docker run --rm -v "$PWD":/app -w /app python:3.11-slim bash -c \
  "pip install -q requests pandas pyreadstat && python scripts/download_nhanes.py" \
  || echo "Descarga fallo; el ETL usara la muestra si existe."

# 3) ETL: construye artefactos (model.pkl, metrics, reportes) en data/
docker compose -f docker/docker-compose.yml build kedro-etl
docker compose -f docker/docker-compose.yml run --rm kedro-etl

# 4) Servicios de producto: API (8000) + frontend (8501) + db
docker compose -f docker/docker-compose.yml up -d --build api frontend db

echo "----------------------------------------------------------------"
echo " Despliegue OK. Accesos (reemplaza <IP> por la IP publica EC2):"
echo "   API .... http://<IP>:8000/docs"
echo "   Dashboard http://<IP>:8501"
echo " Recuerda abrir 8000 y 8501 en el Security Group."
echo "----------------------------------------------------------------"
