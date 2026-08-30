import pandas as pd

from src.backtesting.correr_walk_forward import resumir


def test_resumir_incluye_retorno_neto_menor_al_bruto():
    predicciones = pd.DataFrame({
        "modelo": ["mi_modelo"] * 4,
        "probabilidad_exito": [0.8, 0.7, 0.9, 0.2],  # la última no es señal de compra
        "etiqueta_real": [1, -1, 1, 0],
        "retorno_real": [0.03, -0.02, 0.03, 0.0],
        "fecha_corte_entrenamiento": pd.to_datetime(["2024-01-01"] * 4),
    })

    costos = {"comision_pct": 0.0025, "iva_pct": 0.19, "deslizamiento_pct": None}
    resultado = resumir(predicciones, "mi_modelo", costos)

    assert resultado["n_señales_compra"] == 3
    assert resultado["retorno_prom_si_compra_neto"] < resultado["retorno_prom_si_compra_bruto"]
    # La diferencia entre bruto y neto debe ser exactamente el costo redondo (~0.595%).
    diferencia = resultado["retorno_prom_si_compra_bruto"] - resultado["retorno_prom_si_compra_neto"]
    assert abs(diferencia - 0.005950) < 1e-6
