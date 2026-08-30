# ACierto Bursátil — Resumen operativo

## Objetivo

Analizar semanalmente un universo de acciones de la Bolsa de Valores de Colombia (BVC) y entregar tres productos: ranking de oportunidades, señal individual por acción, y portafolio sugerido de máximo tres posiciones. Horizonte máximo por operación: 20 ruedas (~1 mes). Objetivo indicativo: retorno neto de 2–3%, con riesgo medio.

El sistema **no** promete resultados ni predice un precio exacto. Mide, de forma objetiva y auditable, la capacidad de acierto de un modelo frente a reglas simples (buy & hold, momentum, cruce de medias).

## Alcance de la v1

- Mercado: solo BVC. NU, Amazon y otros valores internacionales quedan para un módulo global posterior.
- Variables: precio, volumen y liquidez. Fundamentales, macro e informativas quedan para una segunda iteración (ver `references/diccionario-datos.md`).
- Ejecución: manual, vía Trii. Sin operación automática.
- Validación: portafolio simulado antes de cualquier capital real.

## Cómo se clasifica cada operación (triple barrera)

Durante las 20 ruedas posteriores a cada señal:

| Resultado | Clasificación |
|---|---|
| Alcanza ~+3% (ajustado por volatilidad) antes de caer ~-2% | Oportunidad exitosa |
| Cae ~-2% antes de alcanzar ~+3% | Oportunidad fallida |
| No toca ninguna barrera en 20 ruedas | Resultado neutral |

Detalle completo en `references/marco-metodologico.md`.

## Reglas de portafolio (resumen)

- Máximo 3 acciones, máximo 40% en una sola, máximo 60% en un mismo sector.
- Efectivo permitido entre 0% y 100% — el sistema puede recomendar no invertir.
- Tamaño de posición ajustado por volatilidad; sin posición si los costos eliminan la rentabilidad esperada.

Detalle completo en `references/reglas-portafolio.md`.

## Antes de pasar a producción

Un modelo no avanza a portafolio simulado hasta cumplir simultáneamente los criterios de la sección "Criterios para aprobar el modelo" en `references/marco-metodologico.md` — desempeño neto positivo, superioridad frente al modelo base, estabilidad fuera de muestra, drawdown compatible con riesgo medio, resultados no concentrados en una sola acción ni en una sola época, y trazabilidad completa.
