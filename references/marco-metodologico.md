# Marco metodológico

## Qué predice el modelo

No un precio exacto — eso genera una falsa sensación de precisión. Se usa un esquema de **triple barrera** sobre las 20 ruedas posteriores a cada señal:

- **Objetivo positivo:** ~+3%, después de costos.
- **Límite negativo:** ~-2% (inicial).
- **Límite temporal:** 20 ruedas.

| Resultado | Clasificación |
|---|---|
| Alcanza +3% antes de caer -2% | Oportunidad exitosa |
| Cae -2% antes de alcanzar +3% | Oportunidad fallida |
| No toca ninguna barrera en 20 ruedas | Resultado neutral |

Los porcentajes se ajustan por volatilidad: no tiene sentido exigirle el mismo movimiento a Ecopetrol que a una acción mucho menos volátil.

Además, el modelo estima:

- Retorno esperado a 20 ruedas.
- Probabilidad de alcanzar el objetivo.
- Probabilidad de tocar el límite de pérdida.
- Caída máxima probable.
- Tiempo estimado para que ocurra el movimiento.

## Modelos que se comparan

No se empieza por una red neuronal — primero hay que establecer si existe capacidad predictiva real.

**Modelos de referencia (baseline):**
- Comprar y mantener.
- Momentum de 20 ruedas.
- Cruce de medias móviles.
- Regresión logística.

**Modelos candidatos:**
- Random Forest.
- XGBoost o LightGBM.
- Regresión para estimar retorno.
- Modelo clasificador de triple barrera.

Cada modelo cumple dos funciones: **clasificación** (probabilidad de alcanzar el objetivo antes del stop) y **regresión** (retorno esperado en las siguientes 20 ruedas). Un modelo complejo solo se aprueba si supera consistentemente a la regresión logística y a las reglas simples.

> **Riesgo a vigilar:** con ~12-15 acciones en el universo y horizontes de 20 ruedas, el número de observaciones independientes en walk-forward es bajo. Random Forest y XGBoost tienden a sobreajustar en ese régimen (pocas filas, muchas variables correlacionadas). Definir desde ya un mínimo de señales por acción antes de confiar en la tasa de acierto.

## Validación histórica (walk-forward)

1. Entrenar con información histórica disponible hasta una fecha.
2. Predecir las siguientes 20 ruedas.
3. Registrar el resultado sin modificarlo.
4. Avanzar temporalmente.
5. Reentrenar y repetir.

Nunca se mezclan aleatoriamente datos pasados y futuros. También se controla:

- Información futura introducida accidentalmente.
- Estados financieros usados antes de su publicación.
- Acciones eliminadas retrospectivamente (survivorship bias).
- Dividendos y eventos corporativos.
- Sobreajuste y selección de parámetros basada en el periodo de prueba.
- Ruedas sin negociación.
- Precios que no habrían permitido ejecutar realmente una orden.

## Criterios para aprobar el modelo

La versión inicial no pasa a portafolio simulado hasta cumplir **simultáneamente**:

- Resultado positivo después de costos.
- Mejor desempeño que el modelo base.
- Desempeño favorable en datos no utilizados para entrenar.
- Drawdown compatible con riesgo medio.
- Resultados no concentrados en una sola acción.
- Resultados no explicados por una sola época excepcional.
- Mínimo suficiente de operaciones.
- Estabilidad ante pequeños cambios de parámetros.
- Trazabilidad completa de cada predicción.

La tasa de acierto sola no es suficiente: un sistema puede acertar 70% de las veces y perder dinero si sus pérdidas son mucho mayores que sus ganancias.

## Elegibilidad de una acción (filtro de liquidez, aplicado cada mes)

Una acción es elegible únicamente si:

- Tuvo negociación suficiente durante los últimos 60 días.
- No presenta demasiadas ruedas sin operación.
- Permite entrar o salir de una posición razonable sin alterar materialmente el precio.
- Tiene información histórica suficiente.
- No está sometida a una OPA, suspensión u otro evento que vuelva incomparable su comportamiento.

> **Riesgo a vigilar:** incluso los nombres grandes (Ecopetrol, Bancolombia) tienen volumen bajo frente a mercados desarrollados, y varios del universo candidato (Mineros, GEB, Corficolombiana) pueden tener ruedas sin negociación con frecuencia. Vale la pena simular este filtro cuanto antes para saber con cuántos nombres se va a trabajar en la práctica.
