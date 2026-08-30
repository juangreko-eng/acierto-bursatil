import numpy as np
import pandas as pd
import pytest

from src.variables.features import retornos, rsi, medias_moviles, construir_features


def _serie_precios(n=300, seed=0):
    rng = np.random.default_rng(seed)
    pasos = rng.normal(0, 0.01, n)
    precios = 100 * np.exp(np.cumsum(pasos))
    fechas = pd.bdate_range("2023-01-02", periods=n)
    return pd.Series(precios, index=fechas, name="Close")


def test_retornos_basico():
    close = pd.Series([100, 110, 121], index=pd.bdate_range("2024-01-01", periods=3))
    r = retornos(close, ventanas=(1,))
    assert r["retorno_1"].iloc[1] == pytest.approx(0.10)
    assert r["retorno_1"].iloc[2] == pytest.approx(0.10)


def test_rsi_en_rango():
    close = _serie_precios()
    valores = rsi(close).dropna()
    assert (valores >= 0).all() and (valores <= 100).all()


def test_medias_moviles_columnas():
    close = _serie_precios()
    df = medias_moviles(close, ventanas=(5, 20))
    assert {"sma_5", "sma_20", "dist_sma_5", "dist_sma_20"}.issubset(df.columns)


def test_construir_features_no_rompe():
    n = 300
    fechas = pd.bdate_range("2023-01-02", periods=n)
    close = _serie_precios(n)
    df = pd.DataFrame({
        "Open": close.shift(1).fillna(close.iloc[0]),
        "High": close * 1.01,
        "Low": close * 0.99,
        "Close": close,
        "Volume": np.random.default_rng(1).integers(1000, 50000, n),
    }, index=fechas)

    features = construir_features(df)
    assert len(features) == n
    assert "rsi" in features.columns
    assert "vol_prom_20" in features.columns
