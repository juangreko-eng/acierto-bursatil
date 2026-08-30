"""
Modelos candidatos — ver references/marco-metodologico.md.

IMPORTANTE: ningún modelo de este archivo está aprobado para producción.
Un modelo candidato solo se adopta si supera consistentemente a
RegresionLogistica (logistic_model.py) y a las reglas simples de
baseline.py, evaluado siempre vía src/backtesting/. Ver "Criterios para
aprobar el modelo" en references/marco-metodologico.md.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from .base import ModeloBase

try:
    from xgboost import XGBClassifier, XGBRegressor
    _XGBOOST_DISPONIBLE = True
except ImportError:
    _XGBOOST_DISPONIBLE = False


class RandomForest(ModeloBase):
    nombre = "random_forest"

    def __init__(self, n_estimators: int = 300, max_depth: int = 5, random_state: int = 42):
        self._clasificador = RandomForestClassifier(
            n_estimators=n_estimators, max_depth=max_depth,
            random_state=random_state, n_jobs=-1,
        )
        self._regresor = RandomForestRegressor(
            n_estimators=n_estimators, max_depth=max_depth,
            random_state=random_state, n_jobs=-1,
        )
        self._columnas = None

    def fit(self, features: pd.DataFrame, etiquetas: pd.DataFrame) -> "RandomForest":
        datos = features.join(etiquetas[["etiqueta", "retorno_realizado"]]).dropna()
        if datos.empty:
            raise ValueError("No hay filas completas (features + etiquetas) para entrenar.")

        self._columnas = features.columns.tolist()
        X = datos[self._columnas]
        y_clas = (datos["etiqueta"] == 1).astype(int)
        y_reg = datos["retorno_realizado"]

        self._clasificador.fit(X, y_clas)
        self._regresor.fit(X, y_reg)
        return self

    def predecir(self, features: pd.DataFrame) -> pd.DataFrame:
        if self._columnas is None:
            raise RuntimeError("Llama a fit() antes de predecir().")

        filas_validas = features[self._columnas].dropna()
        prob = self._clasificador.predict_proba(filas_validas)[:, 1]
        retorno = self._regresor.predict(filas_validas)

        resultado = pd.DataFrame(
            {"probabilidad_exito": prob, "retorno_esperado": retorno},
            index=filas_validas.index,
        )
        return resultado.reindex(features.index)


class XGBoost(ModeloBase):
    nombre = "xgboost"

    def __init__(self, n_estimators: int = 300, max_depth: int = 4,
                 learning_rate: float = 0.05, random_state: int = 42):
        if not _XGBOOST_DISPONIBLE:
            raise ImportError("xgboost no está instalado. Ejecuta: pip install xgboost")

        self._clasificador = XGBClassifier(
            n_estimators=n_estimators, max_depth=max_depth,
            learning_rate=learning_rate, random_state=random_state,
            eval_metric="logloss",
        )
        self._regresor = XGBRegressor(
            n_estimators=n_estimators, max_depth=max_depth,
            learning_rate=learning_rate, random_state=random_state,
        )
        self._columnas = None

    def fit(self, features: pd.DataFrame, etiquetas: pd.DataFrame) -> "XGBoost":
        datos = features.join(etiquetas[["etiqueta", "retorno_realizado"]]).dropna()
        if datos.empty:
            raise ValueError("No hay filas completas (features + etiquetas) para entrenar.")

        self._columnas = features.columns.tolist()
        X = datos[self._columnas]
        y_clas = (datos["etiqueta"] == 1).astype(int)
        y_reg = datos["retorno_realizado"]

        self._clasificador.fit(X, y_clas)
        self._regresor.fit(X, y_reg)
        return self

    def predecir(self, features: pd.DataFrame) -> pd.DataFrame:
        if self._columnas is None:
            raise RuntimeError("Llama a fit() antes de predecir().")

        filas_validas = features[self._columnas].dropna()
        prob = self._clasificador.predict_proba(filas_validas)[:, 1]
        retorno = self._regresor.predict(filas_validas)

        resultado = pd.DataFrame(
            {"probabilidad_exito": prob, "retorno_esperado": retorno},
            index=filas_validas.index,
        )
        return resultado.reindex(features.index)
