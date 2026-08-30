import numpy as np
import pandas as pd

from src.variables.features import construir_features
from src.backtesting.triple_barrera import etiquetar_triple_barrera
from src.backtesting.walk_forward import correr_walk_forward
from src.modelos.baseline import ComprarYMantener
from src.modelos.logistic_model import RegresionLogistica

COLUMNAS_NO_FEATURE = (
    "etiqueta", "retorno_realizado", "ruedas_hasta_evento",
    "objetivo_usado", "limite_usado",
)


def _precios_sinteticos(n, seed):
    rng = np.random.default_rng(seed)
    pasos = rng.normal(0.0003, 0.015, n)
    close = pd.Series(100 * np.exp(np.cumsum(pasos)), index=pd.bdate_range("2015-01-05", periods=n))
    return pd.DataFrame({
        "Open": close.shift(1).fillna(close.iloc[0]),
        "High": close * 1.01,
        "Low": close * 0.99,
        "Close": close,
        "Volume": rng.integers(5000, 100000, n),
    }, index=close.index)


def _dataset(ticker, n, seed, horizonte=20):
    df = _precios_sinteticos(n, seed)
    features = construir_features(df)
    vol_ref = features["vol_20"].median()
    etiquetas = etiquetar_triple_barrera(
        df["Close"], horizonte=horizonte, volatilidad=features["vol_20"], vol_referencia=vol_ref,
    )
    datos = features.join(etiquetas)
    datos.index = pd.MultiIndex.from_product([[ticker], datos.index], names=["ticker", "fecha"])
    return datos


def _dataset_combinado():
    datos = pd.concat([
        _dataset("A", 1200, seed=1),
        _dataset("B", 1000, seed=2),
    ]).sort_index(level="fecha")
    columnas_features = [c for c in datos.columns if c not in COLUMNAS_NO_FEATURE]
    fechas_unicas = datos.index.get_level_values("fecha").unique().sort_values()
    fecha_inicio_test = fechas_unicas[int(len(fechas_unicas) * 0.7)]
    return datos, columnas_features, fecha_inicio_test


def test_walk_forward_no_filtra_informacion_futura():
    """
    La garantía más importante del motor: en cada bloque, el entrenamiento
    nunca debe haber visto una fecha igual o posterior a la que se le pide
    predecir en ese bloque.
    """
    datos, columnas_features, fecha_inicio_test = _dataset_combinado()

    fechas_train_vistas = []

    class RegresionLogisticaInstrumentada(RegresionLogistica):
        def fit(self, features, etiquetas):
            fechas_train_vistas.append(features.index.get_level_values("fecha").max())
            return super().fit(features, etiquetas)

    pred = correr_walk_forward(
        datos, RegresionLogisticaInstrumentada, columnas_features,
        fecha_inicio_test, paso_ruedas=20, min_filas_train=200,
    )

    assert not pred.empty

    cortes_unicos = sorted(pred["fecha_corte_entrenamiento"].unique())
    assert len(fechas_train_vistas) == len(cortes_unicos)

    for max_vista, corte in zip(fechas_train_vistas, cortes_unicos):
        assert max_vista < corte, (
            f"Fuga de información: el entrenamiento vio hasta {max_vista}, "
            f"pero se usó para predecir el bloque que empieza en {corte}"
        )

    # Ninguna predicción individual debe caer antes de la fecha de corte de su propio bloque.
    for fecha_corte, grupo in pred.groupby("fecha_corte_entrenamiento"):
        fechas_predichas = grupo.index.get_level_values("fecha")
        assert (fechas_predichas >= fecha_corte).all()


def test_walk_forward_produce_predicciones_para_baseline():
    datos, columnas_features, fecha_inicio_test = _dataset_combinado()
    pred = correr_walk_forward(
        datos, ComprarYMantener, columnas_features,
        fecha_inicio_test, paso_ruedas=20, min_filas_train=200,
    )
    assert not pred.empty
    assert {"probabilidad_exito", "retorno_esperado", "etiqueta_real",
            "retorno_real", "modelo", "fecha_corte_entrenamiento"}.issubset(pred.columns)


def test_walk_forward_respeta_min_filas_train():
    """Con un mínimo de filas de entrenamiento imposible de alcanzar, no debe producir nada."""
    datos, columnas_features, fecha_inicio_test = _dataset_combinado()
    pred = correr_walk_forward(
        datos, ComprarYMantener, columnas_features,
        fecha_inicio_test, paso_ruedas=20, min_filas_train=10_000_000,
    )
    assert pred.empty
