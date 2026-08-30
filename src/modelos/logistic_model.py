"""
Regresión logística — el primer modelo "de verdad" (no una regla fija).

Ver references/marco-metodologico.md: un modelo candidato (Random Forest,
XGBoost/LightGBM) solo se adopta si supera a este de forma consistente,
además de superar a las reglas simples de src/modelos/baseline.py.
"""

import pandas as pd
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import StandardScaler

from .base import ModeloBase


class RegresionLogistica(ModeloBase):
    nombre = "regresion_logistica"

    def __init__(self, **kwargs_logistica):
        self._scaler = StandardScaler()
        self._clasificador = LogisticRegression(max_iter=1000, **kwargs_logistica)
        self._regresor = LinearRegression()
        self._columnas = None

    def fit(self, features: pd.DataFrame, etiquetas: pd.DataFrame) -> "RegresionLogistica":
        datos = features.join(etiquetas[["etiqueta", "retorno_realizado"]]).dropna()
        if datos.empty:
            raise ValueError("No hay filas completas (features + etiquetas) para entrenar.")

        self._columnas = features.columns.tolist()
        X = self._scaler.fit_transform(datos[self._columnas])
        y_clas = (datos["etiqueta"] == 1).astype(int)  # éxito vs. no-éxito
        y_reg = datos["retorno_realizado"]

        self._clasificador.fit(X, y_clas)
        self._regresor.fit(X, y_reg)
        return self

    def predecir(self, features: pd.DataFrame) -> pd.DataFrame:
        if self._columnas is None:
            raise RuntimeError("Llama a fit() antes de predecir().")

        filas_validas = features[self._columnas].dropna()
        X = self._scaler.transform(filas_validas)

        prob = self._clasificador.predict_proba(X)[:, 1]
        retorno = self._regresor.predict(X)

        resultado = pd.DataFrame(
            {"probabilidad_exito": prob, "retorno_esperado": retorno},
            index=filas_validas.index,
        )
        return resultado.reindex(features.index)
