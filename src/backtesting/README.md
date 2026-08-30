# src/backtesting

Motor de validación walk-forward y etiquetado por triple barrera (ver `references/marco-metodologico.md`).

Debe controlar explícitamente: fuga de información futura, uso de estados financieros antes de su publicación, survivorship bias, dividendos/eventos corporativos, sobreajuste de parámetros al periodo de prueba, ruedas sin negociación y precios no ejecutables.

Salida esperada: por cada predicción histórica, registrar resultado (éxito/fallo/neutral), retorno neto realizado y metadatos suficientes para trazabilidad en `predictions/`.
