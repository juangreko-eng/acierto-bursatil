"""
Prueba de disponibilidad de datos — sección 12 del documento original.

Descarga histórico diario (OHLCV) de las 5 acciones piloto vía yfinance
y reporta profundidad histórica, huecos y calidad básica de los datos,
para decidir si Yahoo Finance es una fuente suficiente para la v1.

Uso:
    pip install yfinance pandas pyyaml
    python src/datos/test_disponibilidad.py
"""

from pathlib import Path
import sys

import pandas as pd
import yaml

try:
    import yfinance as yf
except ImportError:
    sys.exit("Falta yfinance. Instala con: pip install yfinance")

CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "colombia-mvp.yaml"


def cargar_universo_piloto() -> list[str]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["universo_piloto"]


def evaluar_ticker(ticker: str) -> dict:
    data = yf.download(ticker, period="max", interval="1d", progress=False, auto_adjust=False)

    if data.empty:
        return {
            "ticker": ticker,
            "disponible": False,
            "primera_fecha": None,
            "ultima_fecha": None,
            "n_ruedas": 0,
            "ruedas_sin_volumen": None,
            "gap_max_dias_habiles": None,
        }

    n_ruedas = len(data)
    primera_fecha = data.index.min().date()
    ultima_fecha = data.index.max().date()

    ruedas_sin_volumen = int((data["Volume"] == 0).sum()) if "Volume" in data else None

    dias_habiles = pd.bdate_range(primera_fecha, ultima_fecha)
    gap_max = None
    if len(dias_habiles) > 0:
        presentes = set(data.index.normalize())
        faltantes_consecutivos = 0
        max_consecutivos = 0
        for dia in dias_habiles:
            if dia not in presentes:
                faltantes_consecutivos += 1
                max_consecutivos = max(max_consecutivos, faltantes_consecutivos)
            else:
                faltantes_consecutivos = 0
        gap_max = max_consecutivos

    return {
        "ticker": ticker,
        "disponible": True,
        "primera_fecha": primera_fecha,
        "ultima_fecha": ultima_fecha,
        "n_ruedas": n_ruedas,
        "ruedas_sin_volumen": ruedas_sin_volumen,
        "gap_max_dias_habiles": gap_max,
    }


def main():
    universo = cargar_universo_piloto()
    resultados = [evaluar_ticker(t) for t in universo]

    df = pd.DataFrame(resultados)
    print(df.to_string(index=False))

    out_path = Path(__file__).resolve().parents[2] / "reports" / "disponibilidad_datos.csv"
    out_path.parent.mkdir(exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\nResultado guardado en {out_path}")


if __name__ == "__main__":
    main()
