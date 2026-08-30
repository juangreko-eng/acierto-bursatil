import numpy as np
import pandas as pd

from src.variables.features import construir_features
from src.backtesting.triple_barrera import etiquetar_triple_barrera


def _precios_sinteticos(n=500, seed=1):
    rng = np.random.default_rng(seed)
    pasos = rng.normal(0.0003, 0.015, n)
    close = pd.Series(100 * np.exp(np.cumsum(pasos)), index=pd.bdate_range("2018-01-02", periods=n))
    return pd.DataFrame({
        "Open": close.shift(1).fillna(close.iloc[0]),
        "High": close * 1.01,
        "Low": close * 0.99,
        "Close": close,
        "Volume": rng.integers(5000, 100000, n),
    }, index=close.index)


def test_horizonte_corto_tiene_mas_neutrales_que_horizonte_largo():
    """Con menos tiempo para resolverse, más observaciones deberían quedar neutrales."""
    df = _precios_sinteticos()
    features = construir_features(df)
    vol_ref = features["vol_20"].median()

    etiquetas_cortas = etiquetar_triple_barrera(
        df["Close"], objetivo_pct=0.03, limite_pct=-0.02, horizonte=5,
        volatilidad=features["vol_20"], vol_referencia=vol_ref,
    )
    etiquetas_largas = etiquetar_triple_barrera(
        df["Close"], objetivo_pct=0.03, limite_pct=-0.02, horizonte=40,
        volatilidad=features["vol_20"], vol_referencia=vol_ref,
    )

    pct_neutral_corto = (etiquetas_cortas["etiqueta"] == 0).mean()
    pct_neutral_largo = (etiquetas_largas["etiqueta"] == 0).mean()

    assert pct_neutral_corto > pct_neutral_largo
