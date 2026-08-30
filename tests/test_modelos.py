import numpy as np
import pandas as pd

from src.variables.features import construir_features
from src.backtesting.triple_barrera import etiquetar_triple_barrera
from src.modelos.baseline import ComprarYMantener, Momentum, CruceMediasMoviles
from src.modelos.logistic_model import RegresionLogistica


def _dataset_sintetico(n=400, seed=7):
    rng = np.random.default_rng(seed)
    pasos = rng.normal(0.0003, 0.015, n)
    close = pd.Series(100 * np.exp(np.cumsum(pasos)), index=pd.bdate_range("2022-01-03", periods=n))
    df = pd.DataFrame({
        "Open": close.shift(1).fillna(close.iloc[0]),
        "High": close * 1.01,
        "Low": close * 0.99,
        "Close": close,
        "Volume": rng.integers(5000, 100000, n),
    }, index=close.index)
    return df


def test_baseline_predecir_no_rompe():
    df = _dataset_sintetico()
    features = construir_features(df)
    etiquetas = etiquetar_triple_barrera(df["Close"], horizonte=20)

    for Modelo in (ComprarYMantener, Momentum, CruceMediasMoviles):
        modelo = Modelo()
        modelo.fit(features, etiquetas)
        pred = modelo.predecir(features)
        assert {"probabilidad_exito", "retorno_esperado"}.issubset(pred.columns)
        assert len(pred) == len(features)


def test_regresion_logistica_entrena_y_predice():
    df = _dataset_sintetico()
    features = construir_features(df)
    etiquetas = etiquetar_triple_barrera(df["Close"], horizonte=20)

    modelo = RegresionLogistica()
    modelo.fit(features, etiquetas)
    pred = modelo.predecir(features)

    probs = pred["probabilidad_exito"].dropna()
    assert (probs >= 0).all() and (probs <= 1).all()
