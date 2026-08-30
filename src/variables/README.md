# src/variables

Cálculo de features a partir de los datos crudos de `src/datos/`.

`features.py` implementa las variables v1 de `references/diccionario-datos.md`
(precio, volumen, liquidez). Cada función es pura: recibe una Serie o
DataFrame de precios/volumen de UNA acción y devuelve las columnas nuevas,
alineadas al mismo índice de fechas. `construir_features(df)` las junta todas.

Pendiente: variables v2 (fundamentales, macro, informativas) cuando se
aborde la segunda iteración.
