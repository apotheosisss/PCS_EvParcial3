# Imagen base para Kedro ETL + API (feature/c)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 8000

# Por defecto levanta la API; el servicio kedro-etl sobreescribe el command en compose
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
