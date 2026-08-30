import pandas as pd

from src.backtesting.triple_barrera import etiquetar_triple_barrera


def test_toca_objetivo_primero():
    # Precio sube 5% en la rueda 2, por encima del objetivo de 3%.
    precios = [100, 100.5, 105, 104, 103]
    fechas = pd.bdate_range("2024-01-01", periods=len(precios))
    close = pd.Series(precios, index=fechas)

    resultado = etiquetar_triple_barrera(close, objetivo_pct=0.03, limite_pct=-0.02, horizonte=4)
    assert resultado["etiqueta"].iloc[0] == 1
    assert resultado["ruedas_hasta_evento"].iloc[0] == 2


def test_toca_limite_primero():
    precios = [100, 99, 97, 98, 99]
    fechas = pd.bdate_range("2024-01-01", periods=len(precios))
    close = pd.Series(precios, index=fechas)

    resultado = etiquetar_triple_barrera(close, objetivo_pct=0.03, limite_pct=-0.02, horizonte=4)
    assert resultado["etiqueta"].iloc[0] == -1


def test_resultado_neutral():
    precios = [100, 100.2, 100.5, 100.3, 100.4]
    fechas = pd.bdate_range("2024-01-01", periods=len(precios))
    close = pd.Series(precios, index=fechas)

    resultado = etiquetar_triple_barrera(close, objetivo_pct=0.03, limite_pct=-0.02, horizonte=4)
    assert resultado["etiqueta"].iloc[0] == 0


def test_sin_historia_futura_da_nan():
    precios = [100, 101, 102]
    fechas = pd.bdate_range("2024-01-01", periods=len(precios))
    close = pd.Series(precios, index=fechas)

    resultado = etiquetar_triple_barrera(close, horizonte=20)
    # La última rueda no tiene ninguna rueda futura -> NaN
    assert pd.isna(resultado["etiqueta"].iloc[-1])
