"""Tests de las transformaciones avanzadas (IEE 1.2.1)."""
import numpy as np
import pandas as pd
import pytest

from nhanes_diabetes.utils.transforms import (
    broadcast_zscore,
    chunked_group_mean,
    memory_usage_mb,
    optimize_dtypes,
    pivot_prevalence,
    reshape_long,
)


@pytest.fixture
def df() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 400
    return pd.DataFrame(
        {
            "SEQN": np.arange(n),
            "RIDAGEYR": rng.integers(18, 80, n),
            "BMXBMI": rng.normal(28, 6, n).round(1),
            "has_obesity": rng.integers(0, 2, n),
            "grupo": rng.integers(0, 2, n),
            "diabetes_target": rng.integers(0, 2, n),
        }
    )


def test_optimize_dtypes_reduces_memory(df):
    optimized = optimize_dtypes(df)
    assert memory_usage_mb(optimized) < memory_usage_mb(df)
    # No pierde filas ni columnas
    assert optimized.shape == df.shape


def test_broadcast_zscore_is_standardized(df):
    out = broadcast_zscore(df, ["RIDAGEYR", "BMXBMI"])
    assert abs(out["RIDAGEYR_z"].mean()) < 1e-9
    assert abs(out["BMXBMI_z"].std() - 1.0) < 0.05


def test_pivot_prevalence_shape(df):
    piv = pivot_prevalence(df, index="has_obesity", columns="grupo")
    assert piv.shape[0] <= 2 and piv.shape[1] <= 2


def test_reshape_long_row_count(df):
    long = reshape_long(df, id_vars=["SEQN"], value_vars=["RIDAGEYR", "BMXBMI"])
    assert len(long) == 2 * len(df)
    assert set(long["variable"].unique()) == {"RIDAGEYR", "BMXBMI"}


def test_chunked_group_mean_matches_full(df, tmp_path):
    csv = tmp_path / "d.csv"
    df.to_csv(csv, index=False)
    chunked = chunked_group_mean(csv, "grupo", "BMXBMI", chunksize=50)
    full = df.groupby("grupo")["BMXBMI"].mean()
    for k in full.index:
        assert abs(chunked[k] - full[k]) < 1e-6
