"""
Evaluación rápida con un solo corte temporal (train/test) — para iterar
rápido mientras se construye el motor walk-forward completo (ver el
checklist pendiente en README.md).

IMPORTANTE: esto NO es el motor de validación definitivo. Un solo corte
train/test es más rápido de correr pero menos riguroso que el walk-forward
(entrenar → predecir → avanzar → reentrenar) exigido en
references/marco-metodologico.md. Sirve para ver si el pipeline completo
funciona de punta a punta y para iterar rápido en variables/modelos; no
uses estos resultados todavía para decidir si un modelo se aprueba.

Uso:
    pip install yfinance pandas pyyaml scikit-learn
    python src/backtesting/evaluar_simple.py
"""

from pathlib import Path
import sys

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.variables.features import construir_features
from src.backtesting.triple_barrera import etiquetar_triple_barrera
from src.modelos.baseline import ComprarYMantener, Momentum, CruceMediasMoviles
from src.modelos.logistic_model import RegresionLogistica

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "colombia-mvp.yaml"

COLUMNAS_NO_FEATURE = (
    "etiqueta", "retorno_realizado", "ruedas_hasta_evento",
    "objetivo_usado", "limite_usado",
)


def descargar_precios(ticker: str, period: str = "max") -> pd.DataFrame:
    import yfinance as yf
    df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=False)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna()


def construir_dataset(ticker: str, df_precios: pd.DataFrame,
                       objetivo_pct: float = 0.03, limite_pct: float = -0.02,
                       horizonte: int = 20) -> pd.DataFrame:
    """
    Features + etiquetas para UN ticker. El índice queda como MultiIndex
    (ticker, fecha) para poder juntar varias acciones sin que se choquen
    fechas repetidas entre ellas.
    """
    features = construir_features(df_precios)

    # Ajuste de barreras por volatilidad usando la propia mediana histórica
    # del ticker como referencia (simplificación inicial — ver nota en
    # references/marco-metodologico.md sobre ajuste cross-sectional).
    vol_referencia = features["vol_20"].median()
    etiquetas = etiquetar_triple_barrera(
        df_precios["Close"], objetivo_pct=objetivo_pct, limite_pct=limite_pct,
        horizonte=horizonte, volatilidad=features["vol_20"], vol_referencia=vol_referencia,
    )

    datos = features.join(etiquetas)
    datos.index = pd.MultiIndex.from_product([[ticker], datos.index], names=["ticker", "fecha"])
    return datos


def dividir_train_test(datos: pd.DataFrame, frac_test: float = 0.2):
    """
    Corte cronológico: usa el percentil (1 - frac_test) de las fechas
    presentes en el dataset combinado como frontera. Todo lo anterior es
    train, todo lo posterior es test — sin mezclar pasado y futuro.
    """
    fechas = datos.index.get_level_values("fecha")
    fechas_unicas = fechas.unique().sort_values()
    fecha_corte = fechas_unicas[int(len(fechas_unicas) * (1 - frac_test))]
    train = datos[fechas < fecha_corte]
    test = datos[fechas >= fecha_corte]
    return train, test, fecha_corte


def evaluar_modelo(modelo, train: pd.DataFrame, test: pd.DataFrame, columnas_features: list) -> dict:
    modelo.fit(train[columnas_features], train[["etiqueta", "retorno_realizado"]])
    pred = modelo.predecir(test[columnas_features])

    comparado = test[["etiqueta", "retorno_realizado"]].join(pred).dropna()
    decide_comprar = comparado["probabilidad_exito"] > 0.5

    señales = comparado[decide_comprar]
    no_neutrales = señales[señales["etiqueta"] != 0]

    tasa_acierto = (no_neutrales["etiqueta"] == 1).mean() if len(no_neutrales) else float("nan")
    retorno_prom_señal = señales["retorno_realizado"].mean() if len(señales) else float("nan")
    retorno_prom_todas = comparado["retorno_realizado"].mean()

    return {
        "modelo": modelo.nombre,
        "n_señales_compra": int(decide_comprar.sum()),
        "n_total_observaciones": len(comparado),
        "tasa_acierto_no_neutral": tasa_acierto,
        "retorno_prom_si_compra": retorno_prom_señal,
        "retorno_prom_todas": retorno_prom_todas,
    }


def main():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tickers = config["universo_piloto"]
    barreras = config["barreras"]

    print(f"Descargando y preparando datos para: {', '.join(tickers)}")
    datasets = []
    for ticker in tickers:
        df_precios = descargar_precios(ticker)
        if df_precios.empty:
            print(f"  {ticker}: sin datos, se omite")
            continue
        datasets.append(construir_dataset(
            ticker, df_precios,
            objetivo_pct=barreras["objetivo_positivo_pct"] / 100,
            limite_pct=barreras["limite_negativo_pct"] / 100,
            horizonte=barreras["limite_temporal_ruedas"],
        ))
        print(f"  {ticker}: {len(df_precios)} ruedas procesadas")

    if not datasets:
        sys.exit("No se pudo construir el dataset de ningún ticker.")

    datos = pd.concat(datasets).sort_index(level="fecha")
    columnas_features = [c for c in datos.columns if c not in COLUMNAS_NO_FEATURE]

    train, test, fecha_corte = dividir_train_test(datos, frac_test=0.2)
    print(f"\nCorte train/test en {fecha_corte.date()} — train: {len(train)} filas, test: {len(test)} filas\n")

    modelos = [
        ComprarYMantener(),
        Momentum(),
        CruceMediasMoviles(),
        RegresionLogistica(),
    ]

    resultados = [evaluar_modelo(m, train, test, columnas_features) for m in modelos]
    tabla = pd.DataFrame(resultados).set_index("modelo")
    pd.set_option("display.float_format", lambda x: f"{x:.3f}")
    print(tabla)

    out_path = Path(__file__).resolve().parents[2] / "reports" / "evaluacion_simple.csv"
    tabla.to_csv(out_path)
    print(f"\nResultado guardado en {out_path}")


if __name__ == "__main__":
    main()
