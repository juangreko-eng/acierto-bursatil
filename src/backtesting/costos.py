"""
Costos reales de transacción (ver references/reglas-portafolio.md, sección
"Costos reales"). El retorno neto es el que de verdad importa — el bruto
sistemáticamente sobreestima lo que se gana en la práctica.

    R_n = retorno_bruto - comisión_compra - comisión_venta - deslizamiento

Trii cobra comisión + IVA sobre esa comisión, en cada lado de la operación
(compra y venta). El deslizamiento (impacto de mercado al ejecutar) todavía
no se ha estimado con datos reales — ver el TODO en config/colombia-mvp.yaml.
Mientras tanto se asume 0%, lo que significa que estos números son
optimistas: el neto real probablemente sea peor, no mejor.
"""

import pandas as pd


def costo_redondo_pct(comision_pct: float, iva_pct: float, deslizamiento_pct: float = 0.0) -> float:
    """
    Costo total (%) de abrir y cerrar una posición: comisión + IVA sobre la
    comisión, cobrada en cada lado (compra y venta), más deslizamiento
    estimado (0% por defecto — pendiente de dato real).
    """
    comision_con_iva = comision_pct * (1 + iva_pct)
    return 2 * comision_con_iva + deslizamiento_pct


def retorno_neto(retorno_bruto, comision_pct: float, iva_pct: float, deslizamiento_pct: float = 0.0):
    """
    Resta el costo de ida y vuelta al retorno bruto. Acepta un float o una
    pd.Series de retornos brutos (aplica el mismo costo fijo a cada fila —
    válido mientras el costo no dependa del tamaño de la operación).
    """
    return retorno_bruto - costo_redondo_pct(comision_pct, iva_pct, deslizamiento_pct)
