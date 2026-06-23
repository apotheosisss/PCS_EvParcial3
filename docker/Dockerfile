# Imagen base para Kedro ETL + API (feature/c)
FROM python:3.11-slim

WORKDIR /app

# libgomp1: runtime OpenMP requerido por LightGBM / XGBoost en imágenes slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 8000

# Por defecto levanta la API; el servicio kedro-etl sobreescribe el command en compose
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
