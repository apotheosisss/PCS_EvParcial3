# Guía de despliegue (feature/c)

## Local
```bash
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
python scripts/make_sample_model_input.py   # o esperar dato real de feature/b
kedro run
uvicorn api.main:app --reload                # API en :8000
streamlit run dashboards/streamlit_app.py    # dashboard en :8501
```

## Docker
```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```
Servicios: `kedro-etl` (genera artefactos), `api` (:8000), `dashboard` (:8501), `db` (postgres :5432).
