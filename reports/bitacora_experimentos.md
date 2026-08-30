# Bitácora de experimentos

Registro de hallazgos clave conforme se van corriendo pruebas. El objetivo
es que las conclusiones no se pierdan en el historial de conversación —
cada entrada debe ser suficiente para entender qué se probó, qué se
encontró, y qué implica para el proyecto.

---

## 2026-08-30

### 1. Disponibilidad de datos — universo piloto original (GEA)

Se probó con Ecopetrol, Bancolombia preferencial, Grupo Argos, Cementos
Argos y Celsia. **Descartado**: 4 de esas 5 son del GEA, actualmente en
pleno desenroque accionario (canjes de acciones, cambios de razón social —
Bancolombia/Sura ahora aparece como "Grupo Cibest"). Su comportamiento de
precio del último año es incomparable con su historia previa.

### 2. Universo piloto corregido (no-GEA, más líquidas)

Nuevo piloto: Ecopetrol, ISA, Grupo Energía Bogotá, Corficolombiana,
Terpel — las 5 no-GEA más líquidas por valor negociado (fuente:
TradingView). Los 4 primeros dieron buena disponibilidad histórica.
**Terpel quedó marcado con alerta**: 25.7% de sus ruedas tienen volumen
cero — candidata a excluirse en el filtro de liquidez mensual real.

### 3. Evaluación de un solo corte (horizonte=20, prueba 2021-2025)

Ningún modelo (momentum, cruce de medias, regresión logística) le ganó a
comprar-y-mantener. Llevó a la pregunta: ¿20 ruedas es el horizonte
correcto?

### 4. Barrido de horizontes (5, 10, 15, 20, 30, 40 ruedas)

La tasa de acierto de la regresión logística sube con el horizonte:
33.8% (h=5) → 48.4% (h=40), superando a comprar-y-mantener a partir de
~horizonte 25-30. **Caveat importante**: probar 6 horizontes contra el
mismo periodo de prueba y quedarse con el mejor es, técnicamente,
sobreajustar el horizonte a ese periodo — necesita confirmarse con
walk-forward antes de tomarlo como definitivo.

### 5. Walk-forward completo, horizonte=30, umbral=0.5

163 bloques de reentrenamiento, 2014-2026, verificado sin fuga de
información futura (test dedicado en `tests/test_walk_forward.py`).
Regresión logística **sí** superó a las reglas simples en tasa de acierto
(48.7% vs. 44.0%) y retorno bruto (+0.33% vs. +0.05%) — la primera
confirmación robusta (no de un solo corte) de que el modelo aporta algo.

### 6. Costos reales de Trii: 0.25% de comisión + 19% IVA por lado

Costo de ida y vuelta ≈ 0.595%. Aplicado al resultado del punto 5:
**ningún modelo sobrevive neto de costos.** Regresión logística queda en
-0.27% (la menos mala; comprar-y-mantener queda en -0.54%). Deslizamiento
todavía no estimado — el neto real podría ser peor.

### 7. Umbral de convicción más alto (0.7 en vez de 0.5)

Hipótesis: operar solo las señales de mayor probabilidad debería mejorar
el resultado neto al pagar costos menos veces. **Resultado: lo contrario.**
Con umbral 0.7 (solo 56 señales en 12 años): tasa de acierto cae a 36.5%,
retorno neto cae a -1.85%, ratio ganancia/pérdida cae por debajo de 1
(0.88 — ahora pierde más de lo que gana). Esto sugiere que la probabilidad
que reporta el modelo **no está bien calibrada**: mayor "confianza"
declarada no corresponde a mayor probabilidad real de éxito. Muestra
pequeña (56 casos), así que parte de esto podría ser ruido — pero la
dirección contraria a la esperada es una señal real a investigar, no un
resultado a ignorar.

**Estado actual del proyecto**: ningún modelo probado hasta ahora es
rentable neto de costos con el universo, horizonte y variables actuales.
La regresión logística es consistentemente la menos mala. Próximas líneas
de investigación razonables: revisar la calibración de probabilidades del
modelo, agregar variables fundamentales/macro (v2), o evaluar los modelos
candidatos (Random Forest, XGBoost) bajo el mismo protocolo walk-forward.
