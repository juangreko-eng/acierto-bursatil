# src/datos

Ingesta y limpieza de datos crudos.

- `test_disponibilidad.py` — prueba de disponibilidad histórica vía yfinance para el universo piloto (ver `references/fuentes-colombia.md`).
- Pendiente: `precios_bvc.py` (descarga y cacheo diario de OHLCV para todo el universo candidato), `macro.py` (TRM, tasas, IPC desde Banco de la República / DANE), `filtro_liquidez.py` (aplica el filtro mensual de elegibilidad de `marco-metodologico.md`).

Los datos crudos descargados **no** se versionan en Git (ver `.gitignore`); solo el código que los genera.

## Cómo se conecta con el resto del pipeline

```
src/datos            -> precios OHLCV crudos por acción (DataFrame con columnas Open, High, Low, Close, Volume)
src/variables         -> construir_features(df) convierte eso en variables (RSI, medias, volumen, etc.)
src/backtesting       -> etiquetar_triple_barrera(close) convierte el precio en etiquetas (éxito/fallo/neutral)
src/modelos           -> cada modelo hace fit(features, etiquetas) y predecir(features)
```
