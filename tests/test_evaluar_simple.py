import numpy as np
import pandas as pd

from src.backtesting.evaluar_simple import (
    construir_dataset, dividir_train_test, evaluar_modelo, COLUMNAS_NO_FEATURE,
)
from src.modelos.baseline import ComprarYMantener, Momentum, CruceMediasMoviles
from src.modelos.logistic_model import RegresionLogistica


def _precios_sinteticos(n, seed):
    rng = np.random.default_rng(seed)
    pasos = rng.normal(0.0003, 0.015, n)
    close = pd.Series(100 * np.exp(np.cumsum(pasos)), index=pd.bdate_range("2015-01-05", periods=n))
    return pd.DataFrame({
        "Open": close.shift(1).fillna(close.iloc[0]),
        "High": close * 1.01,
        "Low": close * 0.99,
        "Close": close,
        "Volume": rng.integers(5000, 100000, n),
    }, index=close.index)


def test_multi_ticker_no_choca_fechas():
    """Varios tickers con historia distinta no deben producir índices duplicados."""
    datasets = [
        construir_dataset("TICKERA", _precios_sinteticos(600, seed=1), horizonte=20),
        construir_dataset("TICKERB", _precios_sinteticos(500, seed=2), horizonte=20),
    ]
    datos = pd.concat(datasets)
    assert datos.index.is_unique


def test_comprar_y_mantener_siempre_compra():
    datasets = [construir_dataset("TICKERA", _precios_sinteticos(600, seed=1), horizonte=20)]
    datos = pd.concat(datasets).sort_index(level="fecha")
    columnas_features = [c for c in datos.columns if c not in COLUMNAS_NO_FEATURE]
    train, test, _ = dividir_train_test(datos, frac_test=0.2)

    resultado = evaluar_modelo(ComprarYMantener(), train, test, columnas_features)
    assert resultado["n_señales_compra"] == resultado["n_total_observaciones"]


def test_evaluacion_completa_no_rompe():
    datasets = [
        construir_dataset("TICKERA", _precios_sinteticos(700, seed=1), horizonte=20),
        construir_dataset("TICKERB", _precios_sinteticos(650, seed=2), horizonte=20),
    ]
    datos = pd.concat(datasets).sort_index(level="fecha")
    columnas_features = [c for c in datos.columns if c not in COLUMNAS_NO_FEATURE]
    train, test, _ = dividir_train_test(datos, frac_test=0.2)

    for Modelo in (ComprarYMantener, Momentum, CruceMediasMoviles, RegresionLogistica):
        resultado = evaluar_modelo(Modelo(), train, test, columnas_features)
        assert resultado["n_total_observaciones"] > 0
