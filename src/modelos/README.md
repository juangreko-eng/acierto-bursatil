# src/modelos

Modelos de referencia y candidatos (ver `references/marco-metodologico.md`).

- Referencia: comprar y mantener, momentum de 20 ruedas, cruce de medias móviles, regresión logística.
- Candidatos: Random Forest, XGBoost/LightGBM, regresión de retorno, clasificador de triple barrera.

Cada modelo debe exponer dos salidas: clasificación (probabilidad de éxito) y regresión (retorno esperado a 20 ruedas). Un modelo candidato solo se adopta si supera de forma consistente a la regresión logística y a las reglas simples, evaluado siempre vía `src/backtesting/`.
