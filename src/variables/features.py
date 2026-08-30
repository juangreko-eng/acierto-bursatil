"""
Cálculo de variables de precio y volumen/liquidez (v1).
Ver references/diccionario-datos.md para el detalle de cada variable.

Cada función es pura: recibe un DataFrame OHLCV de UNA acción (columnas
Open, High, Low, Close, Volume, indexado por fecha) y devuelve una Serie
o un DataFrame con columnas nuevas, alineado al mismo índice.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Variables de precio
# ---------------------------------------------------------------------------

def retornos(close: pd.Series, ventanas=(1, 5, 10, 20, 60, 120)) -> pd.DataFrame:
    """Retorno simple sobre cada ventana en `ventanas`."""
    out = {f"retorno_{w}": close.pct_change(w) for w in ventanas}
    return pd.DataFrame(out, index=close.index)


def distancia_52_semanas(close: pd.Series, ruedas_anio: int = 252) -> pd.DataFrame:
    """% de distancia frente al máximo y mínimo de las últimas ~252 ruedas."""
    max_52 = close.rolling(ruedas_anio, min_periods=20).max()
    min_52 = close.rolling(ruedas_anio, min_periods=20).min()
    return pd.DataFrame({
        "dist_max_52s": close / max_52 - 1,
        "dist_min_52s": close / min_52 - 1,
    }, index=close.index)


def medias_moviles(close: pd.Series, ventanas=(5, 20, 60, 120)) -> pd.DataFrame:
    out = {}
    for w in ventanas:
        sma = close.rolling(w, min_periods=max(2, w // 2)).mean()
        out[f"sma_{w}"] = sma
        out[f"dist_sma_{w}"] = close / sma - 1
    return pd.DataFrame(out, index=close.index)


def rsi(close: pd.Series, periodo: int = 14) -> pd.Series:
    delta = close.diff()
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)
    avg_gan = ganancia.ewm(alpha=1 / periodo, min_periods=periodo, adjust=False).mean()
    avg_per = perdida.ewm(alpha=1 / periodo, min_periods=periodo, adjust=False).mean()
    rs = avg_gan / avg_per.replace(0, np.nan)
    valor = 100 - 100 / (1 + rs)
    return valor.rename("rsi")


def macd(close: pd.Series, rapida: int = 12, lenta: int = 26, señal: int = 9) -> pd.DataFrame:
    ema_rapida = close.ewm(span=rapida, adjust=False).mean()
    ema_lenta = close.ewm(span=lenta, adjust=False).mean()
    linea_macd = ema_rapida - ema_lenta
    linea_señal = linea_macd.ewm(span=señal, adjust=False).mean()
    return pd.DataFrame({
        "macd": linea_macd,
        "macd_señal": linea_señal,
        "macd_hist": linea_macd - linea_señal,
    }, index=close.index)


def volatilidad(close: pd.Series, ventana: int = 20) -> pd.Series:
    """Desviación estándar de retornos diarios sobre la ventana dada."""
    ret = close.pct_change()
    valor = ret.rolling(ventana, min_periods=max(5, ventana // 2)).std()
    return valor.rename(f"vol_{ventana}")


def momentum_12_1(close: pd.Series) -> pd.Series:
    """
    Factor clásico de momentum de mediano plazo: retorno de los últimos 12
    meses (~252 ruedas) EXCLUYENDO el último mes (~21 ruedas), para evitar
    el efecto de reversión de corto plazo que sí contamina un momentum de
    12 meses "puro". Requiere ~273 ruedas de historia para tener un primer
    valor válido.
    """
    valor = close.shift(21).pct_change(231)
    return valor.rename("momentum_12_1")


def atr(high: pd.Series, low: pd.Series, close: pd.Series, ventana: int = 14) -> pd.Series:
    """Rango verdadero promedio (Average True Range)."""
    close_prev = close.shift(1)
    tr = pd.concat([
        high - low,
        (high - close_prev).abs(),
        (low - close_prev).abs(),
    ], axis=1).max(axis=1)
    valor = tr.rolling(ventana, min_periods=max(2, ventana // 2)).mean()
    return valor.rename("atr")


def maxima_caida_reciente(close: pd.Series, ventana: int = 60) -> pd.Series:
    """Drawdown máximo dentro de la ventana reciente (valor negativo o cero)."""
    max_movil = close.rolling(ventana, min_periods=5).max()
    drawdown = close / max_movil - 1
    valor = drawdown.rolling(ventana, min_periods=5).min()
    return valor.rename(f"max_caida_{ventana}")


def tendencia_relativa(close: pd.Series, close_indice: pd.Series, ventana: int = 20) -> pd.Series:
    """Retorno de la acción menos retorno del índice (p.ej. COLCAP) en la misma ventana."""
    ret_accion = close.pct_change(ventana)
    ret_indice = close_indice.reindex(close.index).pct_change(ventana)
    valor = ret_accion - ret_indice
    return valor.rename(f"tendencia_relativa_{ventana}")


# ---------------------------------------------------------------------------
# Variables de volumen y liquidez
# ---------------------------------------------------------------------------

def volumen_promedio(volume: pd.Series, ventanas=(5, 20, 60)) -> pd.DataFrame:
    out = {f"vol_prom_{w}": volume.rolling(w, min_periods=max(2, w // 2)).mean() for w in ventanas}
    return pd.DataFrame(out, index=volume.index)


def variacion_anormal_volumen(volume: pd.Series, ventana: int = 20) -> pd.Series:
    """z-score del volumen frente a su media/desviación móvil."""
    media = volume.rolling(ventana, min_periods=max(5, ventana // 2)).mean()
    desv = volume.rolling(ventana, min_periods=max(5, ventana // 2)).std()
    valor = (volume - media) / desv.replace(0, np.nan)
    return valor.rename("volumen_zscore")


def ruedas_sin_negociacion(volume: pd.Series, ventana: int = 60) -> pd.Series:
    """Número de ruedas con volumen cero dentro de la ventana."""
    sin_negociacion = (volume == 0).astype(int)
    valor = sin_negociacion.rolling(ventana, min_periods=1).sum()
    return valor.rename(f"ruedas_sin_neg_{ventana}")


def valor_promedio_negociado(close: pd.Series, volume: pd.Series, ventana: int = 20) -> pd.Series:
    valor_diario = close * volume
    valor = valor_diario.rolling(ventana, min_periods=max(2, ventana // 2)).mean()
    return valor.rename(f"valor_negociado_{ventana}")


def facilidad_entrada_salida(volume: pd.Series, close: pd.Series, ventana: int = 20) -> pd.Series:
    """
    Score simplificado de liquidez (0 a 1, más alto = más fácil entrar/salir):
    inverso del coeficiente de variación del valor negociado diario.

    Aproximación provisional mientras se obtiene el spread real de Trii
    (ver references/fuentes-colombia.md) — no reemplaza un dato de spread real.
    """
    valor_diario = close * volume
    media = valor_diario.rolling(ventana, min_periods=max(2, ventana // 2)).mean()
    desv = valor_diario.rolling(ventana, min_periods=max(2, ventana // 2)).std()
    cv = desv / media.replace(0, np.nan)
    cv_relleno = cv.fillna(cv.median())
    valor = 1 / (1 + cv_relleno)
    return valor.rename("facilidad_entrada_salida")


# ---------------------------------------------------------------------------
# Ensamblador
# ---------------------------------------------------------------------------

def construir_features(df: pd.DataFrame, close_indice: pd.Series = None) -> pd.DataFrame:
    """
    Recibe un DataFrame con columnas Open, High, Low, Close, Volume
    (indexado por fecha) para UNA acción, y devuelve un DataFrame con
    todas las variables v1 del diccionario de datos, alineadas al mismo índice.

    `close_indice` es opcional: serie de cierre de un índice de referencia
    (p.ej. COLCAP) para calcular tendencia_relativa.
    """
    close = df["Close"]
    partes = [
        retornos(close),
        distancia_52_semanas(close),
        medias_moviles(close),
        rsi(close).to_frame(),
        macd(close),
        volatilidad(close).to_frame(),
        atr(df["High"], df["Low"], close).to_frame(),
        maxima_caida_reciente(close).to_frame(),
        momentum_12_1(close).to_frame(),
        volumen_promedio(df["Volume"]),
        variacion_anormal_volumen(df["Volume"]).to_frame(),
        ruedas_sin_negociacion(df["Volume"]).to_frame(),
        valor_promedio_negociado(close, df["Volume"]).to_frame(),
        facilidad_entrada_salida(df["Volume"], close).to_frame(),
    ]
    if close_indice is not None:
        partes.append(tendencia_relativa(close, close_indice).to_frame())

    return pd.concat(partes, axis=1)
