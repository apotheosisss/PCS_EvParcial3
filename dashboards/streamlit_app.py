"""Dashboard Streamlit — DiabetesNHANES (feature/c).

Tres vistas según el Notion:
    - Ejecutiva: KPIs y distribuciones.
    - Técnica:   métricas del modelo, matriz de confusión, comparación, importancia.
    - Operativa: filtros, tabla, simulador de predicción y descarga CSV.

Uso educativo. No es un diagnóstico clínico.
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path("data")
MODEL_INPUT = DATA / "05_model_input/model_input.csv"
MODEL_PATH = DATA / "06_models/model.pkl"
METRICS = DATA / "08_reporting/metrics.json"
COMPARISON = DATA / "08_reporting/model_comparison.csv"
CONF_PNG = DATA / "08_reporting/confusion_matrix.png"
FI_PNG = DATA / "08_reporting/feature_importance.png"

st.set_page_config(page_title="DiabetesNHANES", layout="wide")


@st.cache_data
def load_df() -> pd.DataFrame | None:
    return pd.read_csv(MODEL_INPUT) if MODEL_INPUT.exists() else None


@st.cache_resource
def load_bundle() -> dict | None:
    if MODEL_PATH.exists():
        with open(MODEL_PATH, "rb") as fh:
            return pickle.load(fh)
    return None


df = load_df()
bundle = load_bundle()

st.title("🩺 DiabetesNHANES — Dashboard")
st.caption(
    "Herramienta analítica/educativa con datos públicos NHANES 2021–2023. "
    "**No reemplaza un diagnóstico clínico.**"
)

if df is None:
    st.warning(
        "No existe `data/05_model_input/model_input.csv`. "
        "Genera la muestra con `python scripts/make_sample_model_input.py` "
        "o espera el entregable de feature/b."
    )
    st.stop()

vista = st.sidebar.radio("Vista", ["Ejecutiva", "Técnica", "Operativa"])

# ============================================================ Ejecutiva
if vista == "Ejecutiva":
    st.header("Vista ejecutiva")
    c1, c2, c3 = st.columns(3)
    c1.metric("Participantes", f"{len(df):,}")
    if "diabetes_target" in df:
        c2.metric("% diabetes_target", f"{df['diabetes_target'].mean():.1%}")
    if "RIDAGEYR" in df:
        c3.metric("Edad media", f"{df['RIDAGEYR'].mean():.0f}")

    cols = st.columns(3)
    if "RIDAGEYR" in df:
        cols[0].subheader("Distribución por edad")
        cols[0].bar_chart(df["RIDAGEYR"].value_counts(bins=10).sort_index())
    if "RIAGENDR" in df:
        cols[1].subheader("Distribución por sexo")
        cols[1].bar_chart(df["RIAGENDR"].value_counts())
    if "BMXBMI" in df:
        cols[2].subheader("Distribución por IMC")
        cols[2].bar_chart(df["BMXBMI"].value_counts(bins=10).sort_index())

# ============================================================ Técnica
elif vista == "Técnica":
    st.header("Vista técnica")
    if METRICS.exists():
        m = json.loads(METRICS.read_text())
        st.subheader(f"Mejor modelo: {m.get('best_model')}")
        met = m.get("metrics", {})
        cols = st.columns(len(met) or 1)
        for col, (k, v) in zip(cols, met.items()):
            col.metric(k, v)
    else:
        st.info("Aún no hay métricas. Ejecuta `kedro run`.")

    cc = st.columns(2)
    if CONF_PNG.exists():
        cc[0].subheader("Matriz de confusión")
        cc[0].image(str(CONF_PNG))
    if FI_PNG.exists():
        cc[1].subheader("Importancia de variables")
        cc[1].image(str(FI_PNG))

    if COMPARISON.exists():
        st.subheader("Comparación de modelos")
        st.dataframe(pd.read_csv(COMPARISON), use_container_width=True)

# ============================================================ Operativa
else:
    st.header("Vista operativa")
    st.subheader("Filtros")
    fdf = df.copy()
    f = st.columns(3)
    if "RIDAGEYR" in df:
        lo, hi = int(df.RIDAGEYR.min()), int(df.RIDAGEYR.max())
        r = f[0].slider("Edad", lo, hi, (lo, hi))
        fdf = fdf[fdf.RIDAGEYR.between(*r)]
    if "RIAGENDR" in df:
        sx = f[1].multiselect("Sexo", sorted(df.RIAGENDR.unique()), sorted(df.RIAGENDR.unique()))
        fdf = fdf[fdf.RIAGENDR.isin(sx)]
    if "BMXBMI" in df:
        lo, hi = float(df.BMXBMI.min()), float(df.BMXBMI.max())
        rb = f[2].slider("IMC", lo, hi, (lo, hi))
        fdf = fdf[fdf.BMXBMI.between(*rb)]

    st.write(f"Registros filtrados: **{len(fdf):,}**")
    st.dataframe(fdf.head(500), use_container_width=True)
    st.download_button(
        "Descargar CSV", fdf.to_csv(index=False).encode(), "registros_filtrados.csv"
    )

    st.divider()
    st.subheader("🔮 Simulador de predicción individual")
    if bundle is None:
        st.info("No hay modelo entrenado. Ejecuta `kedro run --pipeline modeling`.")
    else:
        s = st.columns(3)
        age = s[0].number_input("Edad (RIDAGEYR)", 18, 100, 55)
        sex = s[0].selectbox("Sexo (RIAGENDR)", [1, 2])
        bmi = s[1].number_input("IMC (BMXBMI)", 10.0, 60.0, 31.5)
        a1c = s[1].number_input("HbA1c (LBXGH)", 4.0, 15.0, 6.8)
        glu = s[2].number_input("Glucosa (LBXGLU)", 50.0, 400.0, 130.0)
        pir = s[2].number_input("Ingreso/pobreza (INDFMPIR)", 0.0, 5.0, 2.1)
        if st.button("Predecir", type="primary"):
            means = bundle.get("feature_means", {})
            row = {c: means.get(c, 0.0) for c in bundle["feature_cols"]}
            row.update(
                {
                    "RIDAGEYR": age, "RIAGENDR": sex, "BMXBMI": bmi,
                    "LBXGH": a1c, "LBXGLU": glu, "INDFMPIR": pir,
                }
            )
            X = pd.DataFrame([row])[bundle["feature_cols"]]
            proba = float(bundle["model"].predict_proba(X)[:, 1][0])
            pred = int(proba >= 0.5)
            if pred:
                st.error(f"⚠️ Riesgo de diabetes — probabilidad {proba:.1%}")
            else:
                st.success(f"✅ Sin riesgo — probabilidad {proba:.1%}")
            st.caption("Resultado educativo, no diagnóstico clínico.")
