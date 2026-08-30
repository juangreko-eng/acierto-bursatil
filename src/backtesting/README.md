# src/backtesting

`triple_barrera.py` implementa el etiquetado de `references/marco-metodologico.md`:
para cada rueda, mira hasta 20 ruedas hacia adelante y clasifica según qué
barrera se toca primero (objetivo, límite, o ninguna = neutral). Soporta
ajuste de las barreras por volatilidad.

Pendiente: el motor walk-forward propiamente dicho (entrenar con historia
hasta una fecha, predecir, avanzar, reentrenar — sin mezclar nunca pasado
y futuro) que orqueste `src/variables`, este etiquetado y `src/modelos`,
y registre cada predicción en `predictions/` para trazabilidad. También
falta controlar aquí: fuga de información futura, survivorship bias,
dividendos/eventos corporativos, sobreajuste de parámetros al periodo de
prueba, y precios no ejecutables — ver el checklist completo en
`references/marco-metodologico.md`.
