"""
Etiquetado por triple barrera (ver references/marco-metodologico.md).

Para cada fecha t, mira hacia adelante hasta `horizonte` ruedas y clasifica
según qué barrera se toca primero:
    1  -> Oportunidad exitosa (toca +objetivo antes que -límite)
   -1  -> Oportunidad fallida (toca -límite antes que +objetivo)
    0  -> Resultado neutral (no toca ninguna barrera dentro del horizonte)
"""

import numpy as np
import pandas as pd


def etiquetar_triple_barrera(
    close: pd.Series,
    objetivo_pct: float = 0.03,
    limite_pct: float = -0.02,
    horizonte: int = 20,
    volatilidad: pd.Series = None,
    vol_referencia: float = None,
) -> pd.DataFrame:
    """
    Devuelve un DataFrame indexado igual que `close` con columnas:
        etiqueta             : 1 / -1 / 0 (NaN si no hay suficiente historia futura)
        retorno_realizado    : retorno simple en el punto donde se resuelve la barrera
        ruedas_hasta_evento  : cuántas ruedas tomó resolverse
        objetivo_usado / limite_usado: barreras efectivamente usadas ese día

    Si se pasan `volatilidad` (p.ej. la serie vol_20 de features.py) y
    `vol_referencia` (la volatilidad "típica" del universo), las barreras
    se escalan por vol_actual / vol_referencia, acotado entre 0.3x y 3x —
    así no se le exige el mismo movimiento a una acción muy volátil que a
    una poco volátil.
    """
    n = len(close)
    valores = close.to_numpy(dtype=float)
    fechas = close.index

    etiquetas = np.full(n, np.nan)
    retornos_realizados = np.full(n, np.nan)
    ruedas_evento = np.full(n, np.nan)
    objetivos_usados = np.full(n, objetivo_pct)
    limites_usados = np.full(n, limite_pct)

    if volatilidad is not None and vol_referencia:
        escala = (volatilidad.reindex(fechas) / vol_referencia).clip(lower=0.3, upper=3.0)
        escala = escala.fillna(1.0).to_numpy()
        objetivos_usados = objetivo_pct * escala
        limites_usados = limite_pct * escala

    for i in range(n):
        fin = min(i + horizonte, n - 1)
        if fin <= i:
            continue  # no queda suficiente historia futura para resolver la barrera

        precio_entrada = valores[i]
        ventana = valores[i + 1: fin + 1]
        if len(ventana) == 0 or precio_entrada == 0 or np.isnan(precio_entrada):
            continue

        retornos_ventana = ventana / precio_entrada - 1
        obj = objetivos_usados[i]
        lim = limites_usados[i]

        toca_objetivo = np.where(retornos_ventana >= obj)[0]
        toca_limite = np.where(retornos_ventana <= lim)[0]

        idx_objetivo = toca_objetivo[0] if len(toca_objetivo) else None
        idx_limite = toca_limite[0] if len(toca_limite) else None

        if idx_objetivo is not None and (idx_limite is None or idx_objetivo <= idx_limite):
            etiquetas[i] = 1
            retornos_realizados[i] = retornos_ventana[idx_objetivo]
            ruedas_evento[i] = idx_objetivo + 1
        elif idx_limite is not None:
            etiquetas[i] = -1
            retornos_realizados[i] = retornos_ventana[idx_limite]
            ruedas_evento[i] = idx_limite + 1
        else:
            etiquetas[i] = 0
            retornos_realizados[i] = retornos_ventana[-1]
            ruedas_evento[i] = len(ventana)

    return pd.DataFrame({
        "etiqueta": etiquetas,
        "retorno_realizado": retornos_realizados,
        "ruedas_hasta_evento": ruedas_evento,
        "objetivo_usado": objetivos_usados,
        "limite_usado": limites_usados,
    }, index=fechas)
