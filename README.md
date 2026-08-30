# ACierto Bursátil

Sistema de análisis semanal de acciones colombianas (BVC). No predice precios exactos: clasifica cada acción según probabilidad de alcanzar un objetivo de retorno antes de un límite de pérdida, dentro de un horizonte máximo de 20 ruedas.

## Qué entrega cada semana

1. **Ranking de oportunidades** — todas las acciones elegibles, ordenadas por puntaje compuesto.
2. **Señal individual** — comprar / compra moderada / mantener / esperar / vender / no elegible, por acción.
3. **Portafolio sugerido** — máximo 3 acciones, con % recomendado y efectivo permitido entre 0–100%.

Ver `references/marco-metodologico.md` para el detalle completo.

## Estado del proyecto

- [x] Definición de objetivo, perfil de operación y universo candidato
- [x] Metodología de etiquetado (triple barrera) y validación (walk-forward)
- [x] Estructura del repositorio
- [x] Variables v1 de precio, volumen y liquidez (`src/variables/features.py`, con tests)
- [x] Etiquetado por triple barrera (`src/backtesting/triple_barrera.py`, con tests)
- [x] Modelos de referencia: comprar y mantener, momentum, cruce de medias (`src/modelos/baseline.py`)
- [x] Regresión logística (`src/modelos/logistic_model.py`)
- [x] Modelos candidatos: Random Forest, XGBoost (`src/modelos/candidatos.py`, aún sin validar — ver criterios de aprobación)
- [x] Script de evaluación rápida (`src/backtesting/evaluar_simple.py`) — un solo corte train/test para iterar rápido; **no** reemplaza el walk-forward
- [ ] Diccionario de datos v1 (borrador en `references/diccionario-datos.md`, pendiente de validar disponibilidad real)
- [x] Prueba de disponibilidad de datos con las 5 acciones piloto (`src/datos/`) — corrida con datos reales, ver `references/fuentes-colombia.md`
- [ ] Obtención de costos reales de Trii (comisiones, IVA, deslizamiento)
- [x] Motor de backtesting walk-forward (`src/backtesting/walk_forward.py` + `correr_walk_forward.py`) — reentrena periódicamente sin mezclar pasado y futuro, verificado con test dedicado anti-fuga de información; guarda cada predicción en `predictions/` para trazabilidad
- [x] Costos reales de Trii (`src/backtesting/costos.py`) — 0.25% de comisión + 19% de IVA por lado, confirmado con Trii 2026-08-30. Deslizamiento aún sin estimar (asumido 0%, ver aviso al correr el script)
- [x] Estrategia de factores — momentum 12-1 con rebalanceo mensual (`src/backtesting/estrategia_factores.py` + driver) — enfoque alternativo al de triple barrera, sin riesgo de sobreajuste al periodo de prueba (ver bitácora de experimentos)
- [ ] Generador de reporte semanal

## Estructura

```
acierto-bursatil/
├── SKILL.md                    # Resumen operativo del proyecto
├── config/
│   └── colombia-mvp.yaml       # Parámetros, universo, reglas de portafolio
├── references/
│   ├── marco-metodologico.md   # Qué se predice, cómo se etiqueta, cómo se valida
│   ├── fuentes-colombia.md     # Fuentes de datos gratuitas y su estado de verificación
│   ├── diccionario-datos.md    # Variables v1 (precio/volumen) y v2 (fundamentales/macro)
│   └── reglas-portafolio.md    # Fórmula de ranking, reglas de portafolio, costos netos
├── src/
│   ├── datos/                  # Descarga y limpieza de precios, volumen, macro
│   ├── variables/               # Cálculo de features (RSI, MACD, medias, etc.)
│   ├── modelos/                 # Modelos de referencia y candidatos
│   ├── backtesting/             # Motor walk-forward, triple barrera
│   └── reportes/                # Generación del ranking / señal / portafolio semanal
├── tests/
├── predictions/                 # Registro inmutable de cada predicción (trazabilidad)
└── reports/                     # Reportes semanales generados
```

## Principios que no se negocian (criterios de aprobación, sección 10 del documento original)

- Todo se mide **neto de costos** (comisión, IVA, deslizamiento).
- Nunca se mezclan datos pasados y futuros (walk-forward estricto).
- Un modelo complejo solo se adopta si supera consistentemente a la regresión logística y a las reglas simples.
- La tasa de acierto sola no basta: importa la asimetría entre ganancias y pérdidas.
- Cada predicción debe quedar trazable en `predictions/`, sin modificarse después de emitida.
