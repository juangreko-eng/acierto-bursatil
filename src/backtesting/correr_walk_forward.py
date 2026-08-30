"""
Corre el motor de validación walk-forward completo sobre el universo
piloto, y guarda cada predicción individual en predictions/ para
trazabilidad (ver predictions/README.md).

A diferencia de evaluar_simple.py (un solo corte train/test) y
barrer_horizontes.py, este SÍ es el motor de validación que exige
references/marco-metodologico.md: reentrena periódicamente usando solo
información que hubiera estado disponible en ese momento, nunca mezcla
pasado y futuro. Los resultados de esto son los que de verdad cuentan
para los criterios de aprobación del modelo.

Uso:
    python src/backtesting/correr_walk_forward.py
    python src/backtesting/correr_walk_forward.py --horizonte 30
    python src/backtesting/correr_walk_forward.py --frac-test 0.3
"""

import argparse
from pathlib import Path
import sys

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.variables.features import construir_features
from src.backtesting.triple_barrera import etiquetar_triple_barrera
from src.backtesting.evaluar_simple import descargar_precios, COLUMNAS_NO_FEATURE
from src.backtesting.walk_forward import correr_walk_forward
from src.modelos.baseline import ComprarYMantener, Momentum, CruceMediasMoviles
from src.modelos.logistic_model import RegresionLogistica

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "colombia-mvp.yaml"


def construir_dataset_completo(tickers, objetivo_pct, limite_pct, horizonte):
    datasets = []
    for ticker in tickers:
        df_precios = descargar_precios(ticker)
        if df_precios.empty:
            print(f"  {ticker}: sin datos, se omite")
            continue
        features = construir_features(df_precios)
        vol_referencia = features["vol_20"].median()
        etiquetas = etiquetar_triple_barrera(
            df_precios["Close"], objetivo_pct=objetivo_pct, limite_pct=limite_pct,
            horizonte=horizonte, volatilidad=features["vol_20"], vol_referencia=vol_referencia,
        )
        datos = features.join(etiquetas)
        datos.index = pd.MultiIndex.from_product([[ticker], datos.index], names=["ticker", "fecha"])
        datasets.append(datos)
        print(f"  {ticker}: {len(df_precios)} ruedas")

    if not datasets:
        sys.exit("No se pudo construir el dataset de ningún ticker.")

    return pd.concat(datasets).sort_index(level="fecha")


def resumir(predicciones: pd.DataFrame, nombre_modelo: str) -> dict:
    de_este_modelo = predicciones[predicciones["modelo"] == nombre_modelo]
    decide_comprar = de_este_modelo["probabilidad_exito"] > 0.5
    señales = de_este_modelo[decide_comprar]
    aciertos = señales[señales["etiqueta_real"] == 1]
    fallos = señales[señales["etiqueta_real"] == -1]
    no_neutrales = señales[señales["etiqueta_real"] != 0]

    tasa_acierto = (no_neutrales["etiqueta_real"] == 1).mean() if len(no_neutrales) else float("nan")
    retorno_prom_señal = señales["retorno_real"].mean() if len(señales) else float("nan")
    retorno_prom_aciertos = aciertos["retorno_real"].mean() if len(aciertos) else float("nan")
    retorno_prom_fallos = fallos["retorno_real"].mean() if len(fallos) else float("nan")
    ratio = (
        abs(retorno_prom_aciertos / retorno_prom_fallos)
        if retorno_prom_fallos and pd.notna(retorno_prom_fallos) and retorno_prom_fallos != 0
        else float("nan")
    )

    return {
        "modelo": nombre_modelo,
        "n_bloques_reentrenados": int(de_este_modelo["fecha_corte_entrenamiento"].nunique()),
        "n_señales_compra": int(decide_comprar.sum()),
        "n_total_observaciones": len(de_este_modelo),
        "tasa_acierto_no_neutral": tasa_acierto,
        "retorno_prom_si_compra": retorno_prom_señal,
        "retorno_prom_todas": de_este_modelo["retorno_real"].mean(),
        "ratio_ganancia_perdida": ratio,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--horizonte", type=int, default=None,
                         help="Horizonte en ruedas (por defecto, el de config/colombia-mvp.yaml)")
    parser.add_argument("--frac-test", type=float, default=0.5,
                         help="Fracción final del historial a usar como periodo de validación walk-forward")
    args = parser.parse_args()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tickers = config["universo_piloto"]
    barreras = config["barreras"]
    horizonte = args.horizonte or barreras["limite_temporal_ruedas"]
    objetivo_pct = barreras["objetivo_positivo_pct"] / 100
    limite_pct = barreras["limite_negativo_pct"] / 100

    print(f"Descargando y preparando datos (horizonte={horizonte} ruedas) para: {', '.join(tickers)}")
    datos = construir_dataset_completo(tickers, objetivo_pct, limite_pct, horizonte)

    fechas_unicas = datos.index.get_level_values("fecha").unique().sort_values()
    fecha_inicio_test = fechas_unicas[int(len(fechas_unicas) * (1 - args.frac_test))]
    print(f"\nPeriodo de validación walk-forward: desde {fecha_inicio_test.date()} "
          f"({args.frac_test:.0%} más reciente del historial disponible)\n")

    columnas_features = [c for c in datos.columns if c not in COLUMNAS_NO_FEATURE]

    modelos = [ComprarYMantener, Momentum, CruceMediasMoviles, RegresionLogistica]
    resumen_filas = []
    todas_las_predicciones = []

    for Modelo in modelos:
        nombre = Modelo().nombre
        print(f"Corriendo walk-forward para: {nombre}...")
        predicciones = correr_walk_forward(
            datos, Modelo, columnas_features, fecha_inicio_test,
            paso_ruedas=20, min_filas_train=500,
        )
        if predicciones.empty:
            print(f"  {nombre}: sin predicciones (no hubo suficiente historia de entrenamiento)")
            continue
        todas_las_predicciones.append(predicciones)
        resumen_filas.append(resumir(predicciones, nombre))

    if not resumen_filas:
        sys.exit("Ningún modelo generó predicciones — revisa min_filas_train y fecha_inicio_test.")

    tabla = pd.DataFrame(resumen_filas).set_index("modelo")
    pd.set_option("display.float_format", lambda x: f"{x:.3f}")
    print("\n" + tabla.to_string())

    reports_dir = Path(__file__).resolve().parents[2] / "reports"
    reports_dir.mkdir(exist_ok=True)
    tabla.to_csv(reports_dir / "walk_forward_resumen.csv")

    predictions_dir = Path(__file__).resolve().parents[2] / "predictions"
    predictions_dir.mkdir(exist_ok=True)
    todas = pd.concat(todas_las_predicciones)
    marca_tiempo = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    ruta_predicciones = predictions_dir / f"walk_forward_{marca_tiempo}.csv"
    todas.to_csv(ruta_predicciones)

    print(f"\nResumen guardado en {reports_dir / 'walk_forward_resumen.csv'}")
    print(f"Predicciones individuales guardadas en {ruta_predicciones}")


if __name__ == "__main__":
    main()
