"""
Modelos de referencia (baseline) — ver references/marco-metodologico.md.

Estos no se "entrenan" en el sentido de machine learning: son reglas fijas.
Se exponen con la misma interfaz (ModeloBase) para poder compararlos
apples-to-apples contra los modelos candidatos en el motor de backtesting.
Un modelo candidato solo se adopta si supera a estos de forma consistente.
"""

import pandas as pd

from .base import ModeloBase


class ComprarYMantener(ModeloBase):
    """Siempre 'compra' (probabilidad de éxito = 1.0); el retorno esperado
    es el promedio histórico observado."""

    nombre = "comprar_y_mantener"

    def __init__(self):
        self._retorno_promedio = 0.0

    def fit(self, features: pd.DataFrame, etiquetas: pd.DataFrame) -> "ComprarYMantener":
        self._retorno_promedio = float(etiquetas["retorno_realizado"].mean() or 0.0)
        return self

    def predecir(self, features: pd.DataFrame) -> pd.DataFrame:
        n = len(features)
        return pd.DataFrame({
            "probabilidad_exito": [1.0] * n,
            "retorno_esperado": [self._retorno_promedio] * n,
        }, index=features.index)


class Momentum(ModeloBase):
    """Compra si el retorno de `ventana` ruedas fue positivo."""

    nombre = "momentum"

    def __init__(self, ventana: int = 20):
        self.ventana = ventana
        self._retorno_promedio_positivo = 0.0

    def fit(self, features: pd.DataFrame, etiquetas: pd.DataFrame) -> "Momentum":
        col = f"retorno_{self.ventana}"
        positivos = etiquetas.loc[features[col] > 0, "retorno_realizado"]
        self._retorno_promedio_positivo = float(positivos.mean()) if len(positivos) else 0.0
        return self

    def predecir(self, features: pd.DataFrame) -> pd.DataFrame:
        col = f"retorno_{self.ventana}"
        señal = (features[col] > 0).astype(float)
        return pd.DataFrame({
            "probabilidad_exito": 0.5 + 0.5 * señal,
            "retorno_esperado": señal * self._retorno_promedio_positivo,
        }, index=features.index)


class CruceMediasMoviles(ModeloBase):
    """Compra si la media móvil corta está por encima de la larga."""

    nombre = "cruce_medias_moviles"

    def __init__(self, corta: int = 20, larga: int = 60):
        self.corta = corta
        self.larga = larga
        self._retorno_promedio_cruce = 0.0

    def fit(self, features: pd.DataFrame, etiquetas: pd.DataFrame) -> "CruceMediasMoviles":
        col_c, col_l = f"sma_{self.corta}", f"sma_{self.larga}"
        cruce_alcista = features[col_c] > features[col_l]
        positivos = etiquetas.loc[cruce_alcista, "retorno_realizado"]
        self._retorno_promedio_cruce = float(positivos.mean()) if len(positivos) else 0.0
        return self

    def predecir(self, features: pd.DataFrame) -> pd.DataFrame:
        col_c, col_l = f"sma_{self.corta}", f"sma_{self.larga}"
        señal = (features[col_c] > features[col_l]).astype(float)
        return pd.DataFrame({
            "probabilidad_exito": 0.5 + 0.5 * señal,
            "retorno_esperado": señal * self._retorno_promedio_cruce,
        }, index=features.index)
