"""
Barrido de horizontes — responde empíricamente: ¿20 ruedas es el horizonte
correcto para la triple barrera?

Corre el mismo pipeline de evaluar_simple.py pero probando varios
horizontes, para ver cómo cambia el comportamiento según cuánto tiempo se
le da a cada operación para resolverse. Los precios y las variables de
precio/volumen NO dependen del horizonte, así que se descargan y calculan
una sola vez; solo se recalculan las etiquetas y se reentrena por cada
horizonte — así corre rápido.

Uso:
    python src/backtesting/barrer_horizontes.py
"""

from pathlib import Path
import sys

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.variables.features import construir_features
from src.backtesting.triple_barrera import etiquetar_triple_barrera
from src.backtesting.evaluar_simple import (
    descargar_precios, dividir_train_test, evaluar_modelo, COLUMNAS_NO_FEATURE,
)
from src.modelos.baseline import ComprarYMantener
from src.modelos.logistic_model import RegresionLogistica

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "colombia-mvp.yaml"
HORIZONTES_A_PROBAR = [5, 10, 15, 20, 30, 40]


def main():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tickers = config["universo_piloto"]
    barreras = config["barreras"]
    objetivo_pct = barreras["objetivo_positivo_pct"] / 100
    limite_pct = barreras["limite_negativo_pct"] / 100

    print(f"Descargando precios una sola vez para: {', '.join(tickers)}")
    precios_y_features = {}
    for ticker in tickers:
        df_precios = descargar_precios(ticker)
        if df_precios.empty:
            print(f"  {ticker}: sin datos, se omite")
            continue
        features = construir_features(df_precios)
        precios_y_features[ticker] = (df_precios, features)
        print(f"  {ticker}: {len(df_precios)} ruedas")

    if not precios_y_features:
        sys.exit("No se pudo construir el dataset de ningún ticker.")

    filas_resumen = []
    for horizonte in HORIZONTES_A_PROBAR:
        print(f"Procesando horizonte = {horizonte} ruedas...")
        datasets = []
        for ticker, (df_precios, features) in precios_y_features.items():
            vol_referencia = features["vol_20"].median()
            etiquetas = etiquetar_triple_barrera(
                df_precios["Close"], objetivo_pct=objetivo_pct, limite_pct=limite_pct,
                horizonte=horizonte, volatilidad=features["vol_20"], vol_referencia=vol_referencia,
            )
            datos = features.join(etiquetas)
            datos.index = pd.MultiIndex.from_product([[ticker], datos.index], names=["ticker", "fecha"])
            datasets.append(datos)

        datos = pd.concat(datasets).sort_index(level="fecha")
        columnas_features = [c for c in datos.columns if c not in COLUMNAS_NO_FEATURE]
        train, test, _ = dividir_train_test(datos, frac_test=0.2)

        # % de observaciones que no tocan ninguna barrera, antes de cualquier modelo.
        pct_neutral = (test["etiqueta"] == 0).mean()

        for Modelo in (ComprarYMantener, RegresionLogistica):
            resultado = evaluar_modelo(Modelo(), train, test, columnas_features)
            resultado["horizonte"] = horizonte
            resultado["pct_neutral_en_test"] = pct_neutral
            filas_resumen.append(resultado)

    tabla = pd.DataFrame(filas_resumen).set_index(["horizonte", "modelo"])
    pd.set_option("display.float_format", lambda x: f"{x:.3f}")
    columnas_a_mostrar = [
        "pct_neutral_en_test", "n_señales_compra", "tasa_acierto_no_neutral",
        "retorno_prom_si_compra", "ratio_ganancia_perdida",
    ]
    print("\n" + tabla[columnas_a_mostrar].to_string())

    out_path = Path(__file__).resolve().parents[2] / "reports" / "barrido_horizontes.csv"
    tabla.to_csv(out_path)
    print(f"\nResultado guardado en {out_path}")


if __name__ == "__main__":
    main()
