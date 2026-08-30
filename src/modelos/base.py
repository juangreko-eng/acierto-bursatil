"""
Interfaz común para todos los modelos (referencia y candidatos).

Cada modelo cumple dos funciones (ver references/marco-metodologico.md):
    - Clasificación: probabilidad de alcanzar el objetivo antes del stop.
    - Regresión: retorno esperado durante las siguientes 20 ruedas.
"""

from abc import ABC, abstractmethod
import pandas as pd


class ModeloBase(ABC):
    nombre: str = "modelo_base"

    @abstractmethod
    def fit(self, features: pd.DataFrame, etiquetas: pd.DataFrame) -> "ModeloBase":
        """
        `features`  : DataFrame de src/variables/features.py (una fila por rueda).
        `etiquetas` : DataFrame de src/backtesting/triple_barrera.py, alineado
                      al mismo índice (columnas: etiqueta, retorno_realizado, ...).
        """
        raise NotImplementedError

    @abstractmethod
    def predecir(self, features: pd.DataFrame) -> pd.DataFrame:
        """
        Devuelve un DataFrame indexado igual que `features` con columnas:
            probabilidad_exito : float en [0, 1]
            retorno_esperado   : float (retorno neto esperado a 20 ruedas)
        """
        raise NotImplementedError
