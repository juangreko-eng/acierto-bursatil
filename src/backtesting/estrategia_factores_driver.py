"""
Corre la estrategia de factores (momentum 12-1, rebalanceo mensual) sobre
el universo piloto, con costos reales de Trii, y la compara contra un
benchmark equiponderado simple (todas las acciones del universo, mismo
peso, sin selección).

Uso:
    python src/backtesting/estrategia_factores_driver.py
    python src/backtesting/estrategia_factores_driver.py --top-k 3
"""

import argparse
from pathlib import Path
import sys

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.variables.features import momentum_12_1
from src.backtesting.evaluar_simple import descargar_precios
from src.backtesting.costos import costo_redondo_pct
from src.backtesting.estrategia_factores import construir_dataset_mensual, simular_cartera

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "colombia-mvp.yaml"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=3,
                         help="Número de acciones en la cartera (por defecto 3, según reglas-portafolio.md)")
    args = parser.parse_args()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tickers = config["universo_piloto"]
    costos = config["costos"]
    costo_ida_vuelta = costo_redondo_pct(
        comision_pct=costos["comision_pct"], iva_pct=costos["iva_pct"],
        deslizamiento_pct=costos.get("deslizamiento_pct") or 0.0,
    )

    print(f"Descargando precios para: {', '.join(tickers)}")
    datasets = []
    for ticker in tickers:
        df_precios = descargar_precios(ticker)
        if df_precios.empty:
            print(f"  {ticker}: sin datos, se omite")
            continue
        momentum = momentum_12_1(df_precios["Close"])
        datasets.append(construir_dataset_mensual(ticker, momentum, df_precios["Close"]))
        print(f"  {ticker}: {len(df_precios)} ruedas")

    if not datasets:
        sys.exit("No se pudo construir el dataset de ningún ticker.")

    datos_mensual = pd.concat(datasets).sort_index(level="fecha_mes")

    resultado = simular_cartera(datos_mensual, top_k=args.top_k, costo_redondo_pct=costo_ida_vuelta)
    if resultado.empty:
        sys.exit("No hubo suficientes tickers con dato válido en ningún mes para formar cartera.")

    # Benchmark: equiponderado de TODO el universo, cada mes, sin selección
    # (compara "elegir top_k por momentum" contra "tener un poco de todo").
    benchmark_mensual = datos_mensual.groupby("fecha_mes")["retorno_fwd"].mean()
    resultado["retorno_benchmark"] = benchmark_mensual.reindex(resultado.index)

    n_meses = len(resultado)
    prom_bruto = resultado["retorno_cartera_bruto"].mean()
    prom_neto = resultado["retorno_cartera_neto"].mean()
    prom_benchmark = resultado["retorno_benchmark"].mean()
    turnover_prom = resultado["turnover_pct"].mean()

    # Retorno compuesto (geométrico) de todo el periodo, neto de costos.
    compuesto_neto = (1 + resultado["retorno_cartera_neto"]).prod() - 1
    compuesto_benchmark = (1 + resultado["retorno_benchmark"]).prod() - 1

    print(f"\nMeses evaluados: {n_meses}  (desde {resultado.index.min().date()} "
          f"hasta {resultado.index.max().date()})")
    print(f"Costo de ida y vuelta usado: {costo_ida_vuelta:.4%}")
    print(f"Turnover promedio mensual: {turnover_prom:.1%}\n")

    print(f"Retorno mensual promedio — cartera (bruto):     {prom_bruto:.4%}")
    print(f"Retorno mensual promedio — cartera (neto):      {prom_neto:.4%}")
    print(f"Retorno mensual promedio — benchmark (bruto):   {prom_benchmark:.4%}\n")

    print(f"Retorno TOTAL compuesto del periodo — cartera (neto):  {compuesto_neto:.2%}")
    print(f"Retorno TOTAL compuesto del periodo — benchmark:       {compuesto_benchmark:.2%}")

    out_path = Path(__file__).resolve().parents[2] / "reports" / "estrategia_factores.csv"
    resultado.to_csv(out_path)
    print(f"\nDetalle mes a mes guardado en {out_path}")

    # --- Chequeo 1: ¿el resultado depende de una sola época excepcional? ---
    resultado["año"] = resultado.index.year
    por_año = resultado.groupby("año").apply(
        lambda g: pd.Series({
            "retorno_cartera_neto": (1 + g["retorno_cartera_neto"]).prod() - 1,
            "retorno_benchmark": (1 + g["retorno_benchmark"]).prod() - 1,
            "n_meses": len(g),
        }),
        include_groups=False,
    )
    print("\n=== Retorno compuesto por año — cartera (neto) vs. benchmark ===")
    pd.set_option("display.float_format", lambda x: f"{x:.2%}" if abs(x) < 50 else f"{x:.1f}")
    print(por_año.to_string())

    años_cartera_gana = (por_año["retorno_cartera_neto"] > por_año["retorno_benchmark"]).sum()
    print(f"\nAños en que la cartera superó al benchmark: {años_cartera_gana} de {len(por_año)}")

    # --- Chequeo 2: ¿el resultado depende de una sola acción? ---
    conteo_tickers = pd.Series(
        [t for lista in resultado["tickers"] for t in lista.split(", ")]
    ).value_counts()
    print("\n=== Cuántos meses fue seleccionada cada acción ===")
    print((conteo_tickers / n_meses).apply(lambda x: f"{x:.1%}").to_string())


if __name__ == "__main__":
    main()
