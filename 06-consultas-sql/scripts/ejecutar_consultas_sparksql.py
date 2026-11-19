#!/usr/bin/env python3
"""
06 - Ejecución de Consultas Analíticas con Apache SparkSQL
-----------------------------------------------------------
Este script ejecuta las 8 preguntas de negocio utilizando el motor SparkSQL
sobre la tabla unificada en formato Parquet (S3 Trusted o local).
Registra tiempos de ejecución exactos, número de registros procesados y
genera el log de evidencias para comparación con Amazon Athena y Hive en EMR.
"""

import os
import sys
import time
import argparse
from pyspark.sql import SparkSession

CONSULTAS_SPARKSQL = [
    (
        "1. Ranking de Departamentos por Puntaje Global Promedio",
        """
        SELECT 
            cole_depto_ubicacion AS departamento,
            COUNT(*) AS total_estudiantes,
            ROUND(AVG(punt_global), 2) AS promedio_global,
            ROUND(STDDEV(punt_global), 2) AS desv_global,
            MAX(punt_global) AS max_global,
            MIN(punt_global) AS min_global
        FROM saber11_unified
        GROUP BY cole_depto_ubicacion
        ORDER BY promedio_global DESC
        LIMIT 10
        """
    ),
    (
        "2. Brecha de Puntaje entre Colegios Oficiales y No Oficiales",
        """
        SELECT 
            periodo,
            cole_naturaleza,
            COUNT(*) AS total_estudiantes,
            ROUND(AVG(punt_global), 2) AS promedio_global,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
            ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
            ROUND(AVG(punt_ingles), 2) AS prom_ingles
        FROM saber11_unified
        GROUP BY periodo, cole_naturaleza
        ORDER BY periodo ASC, cole_naturaleza ASC
        """
    ),
    (
        "3. Impacto Socioeconómico (Estrato vs Matemáticas y Global)",
        """
        SELECT 
            fami_estratovivienda AS estrato,
            COUNT(*) AS total_evaluados,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
            ROUND(AVG(punt_global), 2) AS prom_global
        FROM saber11_unified
        GROUP BY fami_estratovivienda
        ORDER BY prom_global DESC
        """
    ),
    (
        "4. Evolución del Puntaje Promedio por Periodo y Área",
        """
        SELECT 
            periodo,
            COUNT(*) AS total_evaluados,
            ROUND(AVG(punt_global), 2) AS prom_global,
            ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
            ROUND(AVG(punt_ingles), 2) AS prom_ingles
        FROM saber11_unified
        GROUP BY periodo
        ORDER BY periodo ASC
        """
    ),
    (
        "5. Municipios con Mejores Resultados en Inglés (Top Bilingüismo)",
        """
        SELECT 
            cole_mcpio_ubicacion AS municipio,
            cole_depto_ubicacion AS departamento,
            COUNT(*) AS total_estudiantes,
            ROUND(AVG(punt_ingles), 2) AS prom_ingles,
            ROUND(SUM(CASE WHEN desemp_ingles IN ('B1', 'B+') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_bilingue
        FROM saber11_unified
        GROUP BY cole_mcpio_ubicacion, cole_depto_ubicacion
        HAVING COUNT(*) >= 50
        ORDER BY prom_ingles DESC
        LIMIT 10
        """
    ),
    (
        "6. Diferencias entre Zona Urbana y Rural",
        """
        SELECT 
            cole_area_ubicacion AS zona,
            COUNT(*) AS total_estudiantes,
            ROUND(AVG(punt_global), 2) AS prom_global,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
            ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
            ROUND(AVG(punt_ingles), 2) AS prom_ingles
        FROM saber11_unified
        GROUP BY cole_area_ubicacion
        """
    ),
    (
        "7. Brecha Digital: Acceso a Internet y Computador",
        """
        SELECT 
            fami_tieneinternet AS tiene_internet,
            fami_tienecomputador AS tiene_computador,
            COUNT(*) AS total_evaluados,
            ROUND(AVG(punt_global), 2) AS prom_global,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas
        FROM saber11_unified
        GROUP BY fami_tieneinternet, fami_tienecomputador
        ORDER BY prom_global DESC
        """
    ),
    (
        "8. Calidad de Datos: Monitoreo de Nulos e Inconsistencias",
        """
        SELECT 
            COUNT(*) AS total_filas,
            ROUND(SUM(CASE WHEN fami_estratovivienda IS NULL OR fami_estratovivienda = 'NO_REPORTADO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_estrato,
            ROUND(SUM(CASE WHEN fami_educacionpadre IS NULL OR fami_educacionpadre = 'NO_REPORTADO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_educ_padre,
            ROUND(SUM(CASE WHEN fami_tieneinternet IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_internet
        FROM saber11_unified
        """
    )
]

def main():
    parser = argparse.ArgumentParser(description="Ejecutor SparkSQL Saber 11")
    parser.add_argument("--bucket", default="saber11-datalake-885601272401", help="Bucket S3")
    parser.add_argument("--input-path", default="", help="Ruta de entrada Parquet personalizada")
    args, _ = parser.parse_known_args()

    spark = SparkSession.builder \
        .appName("Saber11-SparkSQL-Analytics") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    # Determinar ruta del dataset
    if args.input_path:
        input_path = args.input_path
    else:
        # Intentar ruta local de muestra o S3
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        local_sample = os.path.join(base_dir, "04-procesamiento-glue-spark", "data", "trusted", "saber11_unified")
        if os.path.exists(local_sample):
            input_path = local_sample
        else:
            input_path = f"s3://{args.bucket}/trusted/saber11_unified/"

    print("=" * 75)
    print("EJECUTANDO CONSULTAS ANALÍTICAS CON APACHE SPARKSQL")
    print(f"Dataset de entrada: {input_path}")
    print("=" * 75)

    # Cargar Parquet y registrar Vista Temporal SQL
    t0_load = time.time()
    df = spark.read.parquet(input_path)
    df.createOrReplaceTempView("saber11_unified")
    total_registros = df.count()
    load_time = round(time.time() - t0_load, 2)
    print(f"✓ Vista temporal 'saber11_unified' registrada: {total_registros:,} registros en {load_time}s\n")

    benchmark_records = []
    
    for idx, (titulo, sql_query) in enumerate(CONSULTAS_SPARKSQL, 1):
        print(f"\n>>> [Consulta {idx}/8] {titulo}")
        t0 = time.time()
        res_df = spark.sql(sql_query)
        # Forzar acción para medir tiempo real de cómputo Spark
        filas = res_df.collect()
        duracion = round(time.time() - t0, 3)
        res_df.show(truncate=False)
        print(f"⏱ Tiempo de ejecución SparkSQL: {duracion} segundos ({len(filas)} filas retornadas)")
        benchmark_records.append((titulo, duracion, len(filas)))

    print("\n" + "=" * 75)
    print("RESUMEN DE TIEMPOS DE RESPUESTA - SPARKSQL")
    print("=" * 75)
    for titulo, duracion, n_filas in benchmark_records:
        print(f"- {titulo[:50]:<50} | {duracion:>6.3f} seg | {n_filas:>3} filas")

    spark.stop()

if __name__ == "__main__":
    main()
