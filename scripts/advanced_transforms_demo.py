"""Demostracion ejecutable de transformaciones avanzadas sobre datos reales NHANES.

Corre las utilidades de src/nhanes_diabetes/utils/transforms.py sobre el model_input
y reporta el impacto en memoria y ejemplos de cada tecnica. Evidencia del indicador
IEE 1.2.1.

Uso:
    python scripts/advanced_transforms_demo.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nhanes_diabetes.utils.transforms import (  # noqa: E402
    broadcast_zscore,
    chunked_group_mean,
    memory_usage_mb,
    optimize_dtypes,
    pivot_prevalence,
    reshape_long,
)

CSV = Path("data/05_model_input/model_input.csv")


def main() -> None:
    if not CSV.exists():
        raise SystemExit(
            f"No existe {CSV}. Corre 'kedro run' o "
            "'python scripts/make_sample_model_input.py' primero."
        )

    df = pd.read_csv(CSV)
    print(f"Dataset: {df.shape[0]} filas x {df.shape[1]} columnas\n")

    # 1) Optimizacion de memoria (downcast + category) --------------------------
    before = memory_usage_mb(df)
    df_opt = optimize_dtypes(df)
    after = memory_usage_mb(df_opt)
    print("== 1. Optimizacion de memoria ==")
    print(f"   antes:  {before:7.3f} MB")
    print(f"   despues:{after:7.3f} MB")
    print(f"   ahorro: {(1 - after / before) * 100:5.1f}%\n")

    # 2) Broadcasting (z-score vectorizado) ------------------------------------
    num_cols = [c for c in ("RIDAGEYR", "BMXBMI", "LBXGH", "LBXGLU") if c in df.columns]
    if num_cols:
        z = broadcast_zscore(df, num_cols)
        print("== 2. Broadcasting (z-score) ==")
        print(z[[f"{c}_z" for c in num_cols]].describe().round(2).to_string(), "\n")

    # 3) Pivot (prevalencia por dimensiones) -----------------------------------
    if {"has_obesity", "age_group_age_45_64", "diabetes_target"}.issubset(df.columns):
        piv = pivot_prevalence(df, index="has_obesity", columns="age_group_age_45_64")
        print("== 3. Pivot: prevalencia diabetes_target por obesidad x edad 45-64 ==")
        print(piv.to_string(), "\n")

    # 4) Reshape (wide -> long) ------------------------------------------------
    if num_cols:
        long = reshape_long(df, id_vars=["diabetes_target"], value_vars=num_cols)
        print("== 4. Reshape (melt) ==")
        print(f"   {df.shape} -> long {long.shape}")
        print(long.head(3).to_string(index=False), "\n")

    # 5) Chunking (media por grupo con memoria constante) ----------------------
    if "RIAGENDR" in df.columns and "BMXBMI" in df.columns:
        means = chunked_group_mean(CSV, group_col="RIAGENDR", value_col="BMXBMI",
                                   chunksize=500)
        print("== 5. Chunking: IMC medio por sexo (lectura por chunks) ==")
        print(means.round(2).to_string(), "\n")

    print("[OK] Demostracion completa.")


if __name__ == "__main__":
    main()
