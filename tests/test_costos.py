import pytest

from src.backtesting.costos import costo_redondo_pct, retorno_neto


def test_costo_redondo_con_numeros_de_trii():
    # 0.25% de comisión + 19% de IVA, en cada lado (compra y venta)
    costo = costo_redondo_pct(comision_pct=0.0025, iva_pct=0.19)
    assert costo == pytest.approx(0.005950, abs=1e-6)


def test_retorno_neto_resta_el_costo_redondo():
    bruto = 0.01  # 1%
    neto = retorno_neto(bruto, comision_pct=0.0025, iva_pct=0.19)
    assert neto == pytest.approx(0.01 - 0.005950, abs=1e-6)


def test_retorno_neto_con_deslizamiento():
    bruto = 0.01
    neto_sin_deslizamiento = retorno_neto(bruto, comision_pct=0.0025, iva_pct=0.19)
    neto_con_deslizamiento = retorno_neto(bruto, comision_pct=0.0025, iva_pct=0.19, deslizamiento_pct=0.002)
    assert neto_con_deslizamiento < neto_sin_deslizamiento
    assert neto_sin_deslizamiento - neto_con_deslizamiento == pytest.approx(0.002, abs=1e-6)
