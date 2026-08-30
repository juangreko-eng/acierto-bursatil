"""
Motor de validación walk-forward (ver references/marco-metodologico.md,
sección "Validación histórica").

Nunca mezcla datos pasados y futuros: para cada bloque de fechas de
prueba, entrena solo con lo que hubiera estado disponible hasta el día
anterior a ese bloque, predice ese bloque, avanza, reentrena, repite.
Cada predicción queda registrada individualmente para trazabilidad.
"""

import pandas as pd


def correr_walk_forward(
    datos: pd.DataFrame,
    Modelo,
    columnas_features: list,
    fecha_inicio_test,
    paso_ruedas: int = 20,
    min_filas_train: int = 500,
) -> pd.DataFrame:
    """
    `datos`: DataFrame con MultiIndex (ticker, fecha); columnas de
             features + etiqueta + retorno_realizado.
    `Modelo`: clase que implementa ModeloBase (se instancia una vez por bloque).
    `fecha_inicio_test`: primera fecha desde la cual se empieza a evaluar;
                          todo lo anterior se usa únicamente como historia
                          inicial de entrenamiento.
    `paso_ruedas`: cada cuántas ruedas de calendario se reentrena el modelo
                   (p.ej. 20 ≈ reentrenar mensualmente).
    `min_filas_train`: mínimo de filas completas de entrenamiento
                        requeridas para intentar un bloque; si no se
                        cumple, ese bloque se salta (no genera predicción).

    Devuelve un DataFrame de predicciones individuales, una fila por
    (ticker, fecha) evaluado, con columnas: probabilidad_exito,
    retorno_esperado, etiqueta_real, retorno_real, modelo,
    fecha_corte_entrenamiento.
    """
    datos = datos.sort_index(level="fecha")
    fechas = datos.index.get_level_values("fecha")

    fechas_test_unicas = fechas[fechas >= pd.Timestamp(fecha_inicio_test)].unique()
    fechas_test_unicas = fechas_test_unicas.sort_values()

    resultados = []
    inicio_bloque = 0
    while inicio_bloque < len(fechas_test_unicas):
        fin_bloque = min(inicio_bloque + paso_ruedas, len(fechas_test_unicas))
        fechas_bloque = fechas_test_unicas[inicio_bloque:fin_bloque]
        fecha_corte = fechas_bloque[0]

        train = datos[fechas < fecha_corte]
        bloque = datos[fechas.isin(fechas_bloque)]

        train_completo = train.dropna(subset=columnas_features + ["etiqueta", "retorno_realizado"])
        if len(train_completo) < min_filas_train:
            inicio_bloque = fin_bloque
            continue

        modelo = Modelo()
        modelo.fit(train[columnas_features], train[["etiqueta", "retorno_realizado"]])
        pred = modelo.predecir(bloque[columnas_features])

        registro = bloque[["etiqueta", "retorno_realizado"]].join(pred).dropna()
        registro = registro.rename(columns={
            "etiqueta": "etiqueta_real",
            "retorno_realizado": "retorno_real",
        })
        registro["fecha_corte_entrenamiento"] = fecha_corte
        registro["modelo"] = modelo.nombre
        resultados.append(registro)

        inicio_bloque = fin_bloque

    if not resultados:
        return pd.DataFrame()

    return pd.concat(resultados).sort_index(level="fecha")
