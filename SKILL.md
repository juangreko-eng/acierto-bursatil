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

## Cómo retomar esto en una conversación nueva

Este proyecto no vive en la memoria de Claude entre conversaciones — vive en este repositorio. Para pedir una recomendación:

1. En tu computador, corre el script vigente (a 2026-08-30, el más prometedor es `python src\backtesting\estrategia_factores_driver.py`; el motor de clasificación por triple barrera sigue disponible en `python src\backtesting\correr_walk_forward.py --horizonte 30`).
2. Copia el resultado completo de la terminal.
3. En una conversación nueva con Claude, pega ese resultado y menciona este repositorio (`github.com/juangreko-eng/acierto-bursatil`). Pide: *"con este resultado, dame el ranking, la señal individual por acción, y el portafolio sugerido, siguiendo las reglas de este proyecto."*
4. Claude debe armar los tres productos usando las reglas de `references/reglas-portafolio.md` (máximo 3 acciones, máx. 40% en una, efectivo permitido 0-100%).

**Estado honesto a 2026-08-30** (ver `reports/bitacora_experimentos.md` para el detalle): ningún modelo probado supera los costos de transacción de forma consistente todavía. La estrategia de factores (momentum 12-1) es la más prometedora, pero su ventaja histórica está bastante concentrada en la racha alcista de la BVC de 2024-2025 — cualquier recomendación que salga de ahí hoy debe presentarse como exploratoria, no como una señal confirmada.

### Sugerencia: crea un Proyecto de Claude para esto

Si usas claude.ai, puedes crear un **Proyecto** llamado "ACierto Bursátil" y pegar esto en sus instrucciones personalizadas — así cualquier chat nuevo dentro de ese Proyecto ya tiene el contexto, sin que tengas que reexplicar nada:

```
Proyecto: ACierto Bursátil — github.com/juangreko-eng/acierto-bursatil

Analiza acciones colombianas (BVC) y da: 1) ranking de oportunidades,
2) señal individual por acción (comprar/mantener/esperar/vender),
3) portafolio sugerido (máx. 3 acciones, reglas en
references/reglas-portafolio.md del repositorio).

Cuando el usuario pegue el resultado de correr un script del repositorio
(evaluar_simple.py, correr_walk_forward.py, o
estrategia_factores_driver.py), interpreta los resultados y arma los tres
productos de arriba.

Estado a 2026-08-30: ningún modelo probado supera los costos de
transacción de forma consistente todavía. La estrategia de factores
(momentum 12-1) es la más prometedora, pero su ventaja está concentrada
en la racha alcista BVC 2024-2025 — trátala como pista, no como señal
confirmada. Sé honesto sobre esto en cualquier recomendación.
```
