# src/modelos

Todos los modelos comparten la interfaz `ModeloBase` (`base.py`): `fit(features, etiquetas)`
y `predecir(features)`, devolviendo `probabilidad_exito` y `retorno_esperado`.

- `baseline.py` — modelos de referencia (reglas fijas, no ML): comprar y mantener,
  momentum, cruce de medias móviles.
- `logistic_model.py` — regresión logística. El primer modelo "de verdad";
  cualquier candidato debe superarlo de forma consistente.
- `candidatos.py` — Random Forest y XGBoost. **Ninguno de los dos está aprobado
  para producción** — solo se adoptan si superan consistentemente a la regresión
  logística y a las reglas simples, evaluado vía `src/backtesting/` y cumpliendo
  todos los criterios de aprobación de `references/marco-metodologico.md`.

Pendiente: LightGBM como alternativa a XGBoost (mencionado en el documento
original pero no implementado todavía).
