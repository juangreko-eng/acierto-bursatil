# Señales, ranking y reglas de portafolio

## A. Señal individual

Cada acción elegible recibe un registro como este (ejemplo):

| Campo | Resultado |
|---|---|
| Acción | Celsia |
| Señal | Compra moderada |
| Horizonte | 20 ruedas |
| Probabilidad de alcanzar objetivo | 66% |
| Retorno esperado neto | 3.8% |
| Riesgo de tocar límite negativo | 24% |
| Confianza de los datos | 82/100 |
| Razones principales | Momentum, volumen y fortaleza relativa |
| Riesgo principal | Liquidez |
| Estado | Elegible |

**Escala de señales:**

- **Comprar:** expectativa neta positiva y criterios completos.
- **Compra moderada:** resultado favorable, pero con riesgo o confianza intermedia.
- **Mantener:** posición existente que conserva una expectativa favorable.
- **Esperar:** información insuficiente o ventaja estadística pequeña.
- **Vender/reducir:** expectativa negativa o activación de regla de salida.
- **No elegible:** problemas de liquidez o calidad de información.

> **Pendiente de definir:** la regla exacta para calcular "Confianza de los datos" (por ejemplo: % de ruedas sin negociación + antigüedad del dato + cobertura fundamental). Sin una fórmula explícita, este campo corre el riesgo de volverse subjetivo.

## B. Ranking

No se ordena únicamente por probabilidad de subida. Puntaje compuesto:

```
Puntaje = 0.40 * P_exito + 0.25 * R_esperado + 0.20 * F_tendencia + 0.15 * L_liquidez - Penalizacion_riesgo
```

Los componentes se normalizan entre 0 y 100. Los pesos son hipótesis iniciales — deben validarse con backtesting, no asumirse como definitivos.

## C. Portafolio sugerido

- Máximo tres acciones.
- Máximo 40% en una sola acción.
- Máximo 60% en un mismo sector.
- Efectivo permitido entre 0% y 100%.
- No invertir por obligación si ninguna acción supera el umbral.
- Tamaño de posición ajustado por volatilidad.
- Ninguna posición si los costos eliminan la rentabilidad esperada.
- No incluir dos clases de la misma compañía salvo justificación.

La posibilidad de recomendar 100% efectivo es fundamental: un modelo obligado a escoger siempre tres acciones terminaría inventando oportunidades.

## Costos reales (pendiente de obtener de Trii)

- Comisión fija o variable.
- IVA.
- Costos de compra.
- Costos de venta.
- Eventuales cargos adicionales.
- Tamaño mínimo económicamente eficiente.

**Retorno neto:**

```
R_n = (Valor de venta - Costo de compra - Comisiones - Impuestos - Deslizamiento) / Costo total de compra
```

La meta de 2–3% siempre se entiende como rentabilidad **después de costos estimados**.
