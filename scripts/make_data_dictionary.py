"""Genera data/01_raw/diccionario_variables.xlsx (fuente Excel propia, Notion §2).

Documenta las variables NHANES usadas por el proyecto y las features derivadas que
crea feature/b. Reproducible: regenera el archivo cada vez que se ejecuta.

Uso:
    python scripts/make_data_dictionary.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

OUT = Path("data/01_raw/diccionario_variables.xlsx")

VARIABLES = [
    # variable, fuente, tipo, unidad, descripcion, uso
    ("SEQN", "DEMO_L", "id", "-", "Respondent sequence number", "Llave de union"),
    ("RIDAGEYR", "DEMO_L", "numerica", "anios", "Edad en anios (top-coded a 80)", "feature"),
    ("RIAGENDR", "DEMO_L", "categorica", "1=H 2=M", "Sexo", "feature"),
    ("RIDRETH3", "DEMO_L", "categorica", "codigo", "Grupo racial/etnico", "feature (one-hot)"),
    ("INDFMPIR", "DEMO_L", "numerica", "ratio", "Ratio ingreso/pobreza (0-5)", "feature"),
    ("DIQ010", "DIQ_L", "categorica", "1=Si 2=No 3=Borderline", "Diabetes reportada", "target source"),
    ("BMXBMI", "BMX_L", "numerica", "kg/m2", "Indice de masa corporal", "feature"),
    ("BMXWAIST", "BMX_L", "numerica", "cm", "Circunferencia de cintura", "feature"),
    ("BMXWT", "BMX_L", "numerica", "kg", "Peso", "feature opcional"),
    ("BMXHT", "BMX_L", "numerica", "cm", "Estatura", "feature opcional"),
    ("LBXGH", "GHB_L", "numerica", "%", "Hemoglobina glicosilada A1C", "target source + feature"),
    ("LBXGLU", "GLU_L", "numerica", "mg/dL", "Glucosa plasmatica en ayunas", "target source + feature"),
]

DERIVED = [
    ("diabetes_target", "feature/b", "binaria", "0/1", "1 si DIQ010==1 o LBXGH>=6.5 o LBXGLU>=126", "TARGET"),
    ("age_group", "feature/b", "categorica", "tramo", "Tramo etario (18-44/45-64/65+)", "feature (one-hot)"),
    ("bmi_category", "feature/b", "categorica", "clase", "underweight/normal/overweight/obese", "feature (one-hot)"),
    ("has_obesity", "feature/b", "binaria", "0/1", "BMXBMI >= 30", "feature"),
    ("high_a1c", "feature/b", "binaria", "0/1", "LBXGH >= 6.5", "feature"),
    ("high_fasting_glucose", "feature/b", "binaria", "0/1", "LBXGLU >= 126", "feature"),
    ("income_group", "feature/b", "categorica", "tramo", "Tramo de INDFMPIR", "feature (one-hot)"),
    ("physical_activity_level", "feature/b", "categorica", "nivel", "Derivada de PAQ (si disponible)", "feature (one-hot)"),
    ("sleep_risk_category", "feature/b", "categorica", "clase", "Derivada de SLQ (si disponible)", "feature (one-hot)"),
]

COLUMNS = ["variable", "fuente", "tipo", "unidad", "descripcion", "uso"]
DISCLAIMER = (
    "diabetes_target es una aproximacion analitica/educativa basada en datos "
    "disponibles; NO reemplaza un diagnostico clinico."
)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df_src = pd.DataFrame(VARIABLES, columns=COLUMNS)
    df_der = pd.DataFrame(DERIVED, columns=COLUMNS)
    df_note = pd.DataFrame({"nota": [DISCLAIMER]})
    with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
        df_src.to_excel(writer, sheet_name="variables_nhanes", index=False)
        df_der.to_excel(writer, sheet_name="features_derivadas", index=False)
        df_note.to_excel(writer, sheet_name="disclaimer", index=False)
    print(f"[OK] {OUT} -> {len(df_src)} variables, {len(df_der)} derivadas")


if __name__ == "__main__":
    main()
