# Diccionario de datos — borrador v1

Este es un primer borrador organizativo de las variables de la sección 5 del documento original. Pendiente de validar cada fila contra la disponibilidad real confirmada por `src/datos/test_disponibilidad.py` y de fijar nombre técnico de columna, tipo de dato y frecuencia de actualización.

## v1 — Variables de precio

| Variable | Descripción | Fuente | Estado |
|---|---|---|---|
| Retornos de 1, 5, 10, 20, 60, 120 ruedas | Retorno simple sobre esas ventanas | Yahoo Finance (`yfinance`) | Por calcular |
| Distancia al máximo/mínimo de 52 semanas | % respecto al extremo de las últimas 52 semanas | Derivada de precio | Por calcular |
| Medias móviles 5/20/60/120 | Media móvil simple o exponencial | Derivada de precio | Por calcular |
| RSI | Índice de fuerza relativa | Derivada de precio | Por calcular |
| MACD | Convergencia/divergencia de medias móviles | Derivada de precio | Por calcular |
| Volatilidad | Desviación estándar de retornos (ventana a definir) | Derivada de precio | Por calcular |
| Rango verdadero promedio (ATR) | Volatilidad intradía promedio | Derivada de OHLC | Por calcular |
| Máxima caída reciente | Drawdown máximo en ventana reciente | Derivada de precio | Por calcular |
| Tendencia relativa frente al índice | Retorno de la acción vs. índice BVC/COLCAP | Derivada de precio + índice | Pendiente fuente del índice |

## v1 — Variables de volumen y liquidez

| Variable | Descripción | Fuente | Estado |
|---|---|---|---|
| Volumen diario | Acciones negociadas por rueda | Yahoo Finance | Por calcular |
| Volumen promedio 5/20/60 ruedas | Media móvil de volumen | Derivada | Por calcular |
| Variación anormal de volumen | Desviación respecto al promedio | Derivada | Por calcular |
| Número de ruedas sin negociación | Conteo de días sin operación en ventana | Derivada | Por calcular |
| Valor promedio negociado | Volumen × precio promedio | Derivada | Por calcular |
| Aproximación al spread | Estimación indirecta (sin book de órdenes) | Derivada / pendiente método | Pendiente definir metodología |
| Facilidad estimada de entrada y salida | Score compuesto de liquidez | Derivada | Pendiente definir fórmula |

## v2 — Variables fundamentales (segunda iteración)

Crecimiento de ingresos, EBITDA, utilidad neta, endeudamiento, ROE, flujo de caja, P/U, precio/valor en libros, EV/EBITDA, dividend yield, cambio trimestral y anual de resultados.

*Fuente pendiente de definir — reportes financieros de emisores / Superintendencia Financiera.*

## v2 — Variables macroeconómicas (segunda iteración)

TRM, tasa de política monetaria, inflación, precio del petróleo, riesgo país, comportamiento del S&P 500, tasas de EE.UU.

*Fuentes confirmadas: Banco de la República (TRM, tasas), DANE (IPC). Ver `fuentes-colombia.md`.*

## v2 — Variables informativas (segunda iteración, requiere NLP)

Publicación de resultados, cambios de junta o administración, dividendos, adquisiciones o desinversiones, endeudamiento relevante, litigios materiales, OPA, cambios regulatorios.

*Fuente: información relevante de emisores, Superintendencia Financiera. Tratar como proyecto separado — no bloquea la v1.*
