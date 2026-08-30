import numpy as np
import pandas as pd

from src.variables.features import momentum_12_1
from src.backtesting.estrategia_factores import construir_dataset_mensual, simular_cartera


def _precios_sinteticos(n, seed, drift=0.0003):
    rng = np.random.default_rng(seed)
    pasos = rng.normal(drift, 0.015, n)
    return pd.Series(100 * np.exp(np.cumsum(pasos)), index=pd.bdate_range("2015-01-05", periods=n))


def _dataset_mensual_sintetico():
    tickers_close = {
        "A": _precios_sinteticos(2500, seed=1, drift=0.0010),  # ganador estructural
        "B": _precios_sinteticos(2500, seed=2, drift=0.0002),
        "C": _precios_sinteticos(2500, seed=3, drift=-0.0002),
        "D": _precios_sinteticos(2500, seed=4, drift=0.0000),
        "E": _precios_sinteticos(2500, seed=5, drift=-0.0005),  # perdedor estructural
    }
    datasets = [construir_dataset_mensual(t, momentum_12_1(c), c) for t, c in tickers_close.items()]
    return pd.concat(datasets).sort_index(level="fecha_mes")


def test_momentum_no_usa_informacion_futura():
    """El momentum reportado en una fecha debe ser idéntico si se recalcula
    truncando la serie de precios exactamente en esa fecha."""
    close = _precios_sinteticos(1500, seed=1)
    momentum_completo = momentum_12_1(close)

    fecha_prueba = close.index[800]
    momentum_reportado = momentum_completo.loc[fecha_prueba]

    precios_truncados = close[close.index <= fecha_prueba]
    momentum_recalculado = momentum_12_1(precios_truncados).iloc[-1]

    assert abs(momentum_reportado - momentum_recalculado) < 1e-9


def test_dataset_mensual_indice_unico():
    datos = _dataset_mensual_sintetico()
    assert datos.index.is_unique


def test_ranking_identifica_ganador_estructural():
    """Con drifts claramente distintos, el ticker con mejor drift debe ser
    seleccionado en una mayoría clara de los meses."""
    datos = _dataset_mensual_sintetico()
    resultado = simular_cartera(datos, top_k=2, costo_redondo_pct=0.0)

    meses_con_a = resultado["tickers"].str.contains("A").sum()
    assert meses_con_a > len(resultado) * 0.5


def test_costos_reducen_retorno_neto():
    datos = _dataset_mensual_sintetico()
    resultado = simular_cartera(datos, top_k=2, costo_redondo_pct=0.006)
    assert (resultado["retorno_cartera_neto"] <= resultado["retorno_cartera_bruto"] + 1e-9).all()


def test_turnover_cero_si_cartera_no_cambia():
    datos = _dataset_mensual_sintetico()
    resultado = simular_cartera(datos, top_k=2, costo_redondo_pct=0.0)
    meses_sin_cambio = resultado[(resultado["n_entradas"] == 0) & (resultado["n_salidas"] == 0)]
    assert (meses_sin_cambio["turnover_pct"] == 0).all()
