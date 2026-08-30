# Fuentes de datos — Colombia

Estado a 2026-08-30. "Verificado" significa que se confirmó que la fuente existe y publica el dato relevante; no significa que ya se haya probado la descarga histórica programática completa.

## Precios y volumen (BVC)

| Fuente | Estado | Notas |
|---|---|---|
| Yahoo Finance (`.CL` suffix) | Verificado — cubre todo el universo candidato | Tickers confirmados: `ECOPETROL.CL`, `BCOLOMBIA.CL`/`PFBCOLOM.CL`, `GRUPOSURA.CL`/`PFGRUPSURA.CL`, `GRUPOARGOS.CL`/`PFGRUPOARG.CL`, `CEMARGOS.CL`/`PFCEMARGOS.CL`, `ISA.CL`, `CELSIA.CL`, `GEB.CL`, `CORFICOLCF.CL`/`PFCORFICOL.CL`, `TERPEL.CL`, `MINEROS.CL`, `PFDAVVNDA.CL`. Acceso gratuito vía librería `yfinance` (wrapper no oficial, sin API key). Precios en COP. |
| Sitio oficial BVC | Sin verificar | La página de emisores muestra precios y volumen, pero no está confirmado que exista una vía gratuita, histórica y automatizable con suficiente alcance. No asumir que hay una API pública disponible. |
| Trii | Pendiente | Fuente de ejecución, no necesariamente de datos históricos masivos. |
| Investing.com / Bolsamania | Disponible manualmente | Útil como verificación cruzada puntual, no como fuente automatizada primaria (scraping tiene implicaciones de términos de servicio). |

**Caveat importante:** la cobertura de Yahoo para tickers latinoamericanos de baja liquidez a veces tiene huecos (días faltantes, ajustes por dividendos poco claros, profundidad histórica limitada en los nombres menos líquidos). Todo lo que venga de ahí debe pasar por el mismo checklist de validación de `marco-metodologico.md` (ruedas sin negociación, precios no ejecutables) antes de usarse para entrenar o evaluar modelos.

## Variables macroeconómicas

| Variable | Fuente | Estado |
|---|---|---|
| TRM, tasa de política monetaria | Portal de Estadísticas del Banco de la República | Verificado — series históricas descargables |
| IPC / inflación | DANE | Verificado — series oficiales publicadas |
| Precio del petróleo | Fuentes internacionales (EIA, Investing.com, etc.) | Pendiente de fijar fuente única |
| Riesgo país (EMBI Colombia) | JP Morgan / Banco de la República | Pendiente de verificar disponibilidad gratuita histórica |
| S&P 500, tasas EE.UU. | Yahoo Finance / FRED | Verificado — ambas fuentes tienen históricos gratuitos y accesibles vía API/librería |

## Variables informativas / información relevante de emisores

| Fuente | Estado | Notas |
|---|---|---|
| Superintendencia Financiera de Colombia | Sin verificar profundidad de acceso automatizado | Es la fuente oficial de información relevante (resultados, cambios de junta, dividendos, OPA, litigios). Convertir esto en variable estructurada es, en la práctica, un mini-proyecto de NLP — se recomienda tratarlo como iteración separada, fuera de la v1. |

## Nota sobre el GEA y el desenroque accionario (2026-08-30)

Las acciones del Grupo Empresarial Antioqueño (GEA) — Grupo Cibest (entidad
que agrupa lo que antes era Bancolombia/Grupo Sura, renombrada tras la
reestructuración), Grupo Argos, Cementos Argos, Grupo Sura y Celsia — vienen
desenrocando sus participaciones cruzadas históricas. Esto genera eventos
corporativos (canjes de acciones, OPAs, cambios de razón social) que vuelven
su comportamiento de precio del último año incomparable con su historia
previa, exactamente el tipo de situación que el filtro de elegibilidad de
`marco-metodologico.md` busca excluir ("no está sometida a una OPA,
suspensión u otro evento que vuelva incomparable su comportamiento").

Por eso el universo piloto se cambió a las 5 acciones **no-GEA** más líquidas
de la BVC por valor negociado diario (fuente: ranking de TradingView,
consultado 2026-08-30): Ecopetrol, ISA, Grupo Energía Bogotá, Corficolombiana
y Terpel. El resto del universo candidato (incluyendo las acciones del GEA)
se mantiene en `config/colombia-mvp.yaml` para la v1 completa, pero deberá
pasar por un filtro adicional de "sin evento corporativo material reciente"
antes de incluirse en cualquier entrenamiento o backtesting.

## Resultados reales de la prueba de disponibilidad (2026-08-30)

Corrida contra el universo piloto no-GEA (`src/datos/test_disponibilidad.py`), con datos reales de Yahoo Finance:

| Ticker | Desde | Ruedas | % días sin volumen | Lectura |
|---|---|---|---|---|
| ECOPETROL.CL | 2007-11-28 | 4.853 | 6.8% | Sólida |
| ISA.CL | 2001-08-21 | 6.488 | 12.9% | Buena, historia larga |
| GEB.CL | 2009-10-07 | 4.368 | 7.1% | Sólida |
| CORFICOLCF.CL | 2007-04-03 | 5.023 | 7.2% | Sólida |
| TERPEL.CL | 2014-08-19 | 3.102 | **25.7%** | ⚠️ Ver nota abajo |

**Nota sobre Terpel:** aunque aparece 5ª en el ranking de liquidez de TradingView por *valor total negociado*, una de cada cuatro ruedas tiene volumen cero — probablemente porque ese valor lo explican operaciones grandes y esporádicas (bloques) más que actividad diaria constante. Antes de incluir Terpel en cualquier entrenamiento o backtesting, debe pasar por el filtro de liquidez mensual de `marco-metodologico.md`; es candidata a quedar excluida la mayoría de los meses, o a ser reemplazada por otra acción no-GEA (p.ej. Mineros o Banco de Bogotá, siguientes en el ranking de liquidez).

## Próximos pasos de esta sección

1. Ejecutar `src/datos/test_disponibilidad.py` contra las 5 acciones piloto para confirmar profundidad histórica real, huecos y calidad de los datos vía `yfinance`.
2. Confirmar con el Banco de la República y el DANE el formato exacto de descarga (CSV/API) para automatizar la ingesta.
3. Decidir fuente única para petróleo y riesgo país antes de construir `src/variables/macro.py`.
