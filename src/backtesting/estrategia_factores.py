"""
Estrategia de factores: momentum de mediano plazo (12 meses, excluyendo el
último), con rebalanceo mensual. Ver reports/bitacora_experimentos.md
(entrada 2026-08-30, "Umbral de convicción") para el razonamiento detrás
de este cambio de enfoque.

A diferencia de la clasificación diaria por triple barrera, esto es un
enfoque de "ranking": cada fin de mes se ordenan las acciones del universo
por su momentum, se seleccionan las top-K, y se mantienen hasta el
siguiente rebalanceo. El costo de transacción solo se cobra sobre el
turnover real (posiciones que entran o salen), no sobre las que se
mantienen — así una estrategia de bajo turnover no se penaliza de más.

Al ser una regla fija (no se "entrena" con datos), no tiene el riesgo de
sobreajuste al periodo de prueba que sí tienen los modelos de
clasificación — se puede evaluar sobre toda la historia disponible.
"""

import pandas as pd


def construir_dataset_mensual(ticker: str, momentum: pd.Series, close: pd.Series) -> pd.DataFrame:
    """
    `momentum`: serie diaria del factor (usa solo información pasada en
                cada fecha — no hay fuga por construcción).
    `close`: serie diaria de cierre, para calcular el retorno del mes
             siguiente al momento del rebalanceo.

    Devuelve un DataFrame mensual (fin de mes) con MultiIndex
    (ticker, fecha_mes) y columnas: momentum (al cierre de ese mes),
    retorno_fwd (retorno realizado del mes SIGUIENTE — lo que se sabría
    si se hubiera comprado al cierre de este mes y vendido al cierre del
    próximo).
    """
    cierre_mensual = close.resample("ME").last()
    momentum_mensual = momentum.resample("ME").last()
    retorno_fwd = cierre_mensual.pct_change().shift(-1)

    datos = pd.DataFrame({"momentum": momentum_mensual, "retorno_fwd": retorno_fwd})
    datos.index = pd.MultiIndex.from_product([[ticker], datos.index], names=["ticker", "fecha_mes"])
    return datos


def simular_cartera(
    datos_mensual: pd.DataFrame,
    top_k: int = 3,
    costo_redondo_pct: float = 0.0,
) -> pd.DataFrame:
    """
    Cada mes: rankea por momentum entre los tickers con dato válido ese
    mes, selecciona el top_k, calcula el retorno de cartera equiponderada
    del mes siguiente, y cobra costos solo sobre el turnover respecto al
    mes anterior (fracción de la cartera que cambió).

    Devuelve un DataFrame indexado por fecha_mes con el detalle de cada
    rebalanceo mensual.
    """
    fechas = datos_mensual.index.get_level_values("fecha_mes").unique().sort_values()

    cartera_anterior = set()
    filas = []
    for fecha in fechas:
        corte = datos_mensual.xs(fecha, level="fecha_mes")
        corte_valido = corte.dropna(subset=["momentum", "retorno_fwd"])
        if len(corte_valido) < top_k:
            continue

        seleccion = corte_valido.sort_values("momentum", ascending=False).head(top_k)
        tickers_actuales = set(seleccion.index)

        entradas = tickers_actuales - cartera_anterior
        salidas = cartera_anterior - tickers_actuales
        turnover_pct = (len(entradas) + len(salidas)) / (2 * top_k)

        retorno_bruto = seleccion["retorno_fwd"].mean()
        retorno_neto = retorno_bruto - turnover_pct * costo_redondo_pct

        filas.append({
            "fecha_mes": fecha,
            "tickers": ", ".join(sorted(tickers_actuales)),
            "n_entradas": len(entradas),
            "n_salidas": len(salidas),
            "turnover_pct": turnover_pct,
            "retorno_cartera_bruto": retorno_bruto,
            "retorno_cartera_neto": retorno_neto,
        })

        cartera_anterior = tickers_actuales

    return pd.DataFrame(filas).set_index("fecha_mes")
