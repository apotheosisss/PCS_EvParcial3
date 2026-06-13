"""Genera un model_input.csv de MUESTRA para desarrollar feature/c sin esperar a
feature/b.

Reproduce el contrato definido en docs/CONTRATO_FEATURE_B.md: una fila por SEQN,
features numéricas sin nulos y diabetes_target construido con la regla del Notion.

NO es dato real de NHANES — es sintético, solo para que el pipeline de modelado,
la API y el dashboard sean ejecutables de punta a punta. Cuando feature/b entregue
el archivo real, este script deja de usarse.

Uso:
    python scripts/make_sample_model_input.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("data/05_model_input/model_input.csv")
N = 2000
SEED = 42


def main() -> None:
    rng = np.random.default_rng(SEED)

    seqn = np.arange(100000, 100000 + N)
    age = rng.integers(18, 80, N)
    sex = rng.integers(1, 3, N)            # 1=hombre, 2=mujer
    race = rng.integers(1, 7, N)
    pir = np.round(rng.uniform(0, 5, N), 2)
    bmi = np.round(rng.normal(28, 6, N).clip(15, 60), 1)
    waist = np.round(bmi * 2.6 + rng.normal(0, 8, N), 1)
    a1c = np.round(rng.normal(5.6, 1.1, N).clip(4, 14), 1)
    glucose = np.round(rng.normal(100, 25, N).clip(60, 300), 0)
    diq010_pos = rng.random(N) < 0.10      # ~10% diagnóstico reportado

    # Regla del Notion para el target
    target = ((diq010_pos) | (a1c >= 6.5) | (glucose >= 126)).astype(int)

    df = pd.DataFrame(
        {
            "SEQN": seqn,
            "RIDAGEYR": age,
            "RIAGENDR": sex,
            "RIDRETH3": race,
            "INDFMPIR": pir,
            "BMXBMI": bmi,
            "BMXWAIST": waist,
            "LBXGH": a1c,
            "LBXGLU": glucose,
            "has_obesity": (bmi >= 30).astype(int),
            "high_a1c": (a1c >= 6.5).astype(int),
            "high_fasting_glucose": (glucose >= 126).astype(int),
            "diabetes_target": target,
        }
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"[OK] {OUT} -> {len(df)} filas, target positivo={target.mean():.1%}")


if __name__ == "__main__":
    main()
