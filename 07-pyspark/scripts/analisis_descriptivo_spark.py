#!/usr/bin/env python3
"""
07 - Analítica Descriptiva con PySpark: Resultados Saber 11
-----------------------------------------------------------
Procesa el dataset unificado en S3 Trusted (Parquet), ejecuta análisis
estadísticos univariados y multivariados (correlaciones de Pearson,
análisis de brechas socioeconómicas y geográficas), y exporta los
resultados refinados a S3 Refined en formato Parquet y CSV resumen.
"""

import os
import sys
import argparse
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.stat import Correlation
from pyspark.ml.feature import VectorAssembler

def main():
    parser = argparse.ArgumentParser(description="Analítica Descriptiva PySpark Saber 11")
    parser.add_argument("--bucket", default="saber11-datalake-885601272401", help="Bucket S3")
    parser.add_argument("--local", action="store_true", help="Ejecutar en modo local con datos de muestra")
    args, _ = parser.parse_known_args()

    spark = SparkSession.builder \
        .appName("Saber11-Analytics-PySpark") \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    if args.local:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        input_path = os.path.join(base_dir, "04-procesamiento-glue-spark", "data", "trusted", "saber11_unified")
        output_refined = os.path.join(base_dir, "07-pyspark", "data", "refined")
    else:
        input_path = f"s3://{args.bucket}/trusted/saber11_unified/"
        output_refined = f"s3://{args.bucket}/refined"

    print(f"=== INICIANDO ANALÍTICA PYSPARK ===")
    print(f"Leyendo dataset desde: {input_path}")
    
    df = spark.read.parquet(input_path)
    total_filas = df.count()
    print(f"Total registros cargados: {total_filas:,}")

    # 1. Resumen Estadístico Univariado de Puntajes
    areas = ["punt_lectura_critica", "punt_matematicas", "punt_c_naturales", "punt_sociales_ciudadanas", "punt_ingles", "punt_global"]
    print("\n--- 1. ESTADÍSTICAS DESCRIPTIVAS POR ÁREA Y GLOBAL ---")
    df.select(areas).describe().show()

    # 2. Matriz de Correlación de Pearson
    print("\n--- 2. MATRIZ DE CORRELACIÓN DE PEARSON ENTRE PRUEBAS ---")
    assembler = VectorAssembler(inputCols=areas, outputCol="features")
    df_vector = assembler.transform(df.select(areas).dropna())
    matriz_corr = Correlation.corr(df_vector, "features", "pearson").head()
    print("Áreas:", areas)
    print("Matriz de correlación:")
    print(matriz_corr[0])

    # 3. Brecha Oficial vs No Oficial
    print("\n--- 3. BRECHA OFICIAL VS NO OFICIAL ---")
    df_brecha_oficial = df.groupBy("periodo", "cole_naturaleza").agg(
        F.count("*").alias("total_estudiantes"),
        F.round(F.avg("punt_global"), 2).alias("prom_global"),
        F.round(F.stddev("punt_global"), 2).alias("std_global"),
        F.round(F.avg("punt_matematicas"), 2).alias("prom_matematicas"),
        F.round(F.avg("punt_lectura_critica"), 2).alias("prom_lectura"),
        F.round(F.avg("punt_ingles"), 2).alias("prom_ingles")
    ).orderBy("periodo", "cole_naturaleza")
    df_brecha_oficial.show(truncate=False)

    # 4. Brecha Digital (Computador e Internet)
    print("\n--- 4. BRECHA DIGITAL (COMPUTADOR E INTERNET) ---")
    df_brecha_tic = df.groupBy("fami_tieneinternet", "fami_tienecomputador").agg(
        F.count("*").alias("total_evaluados"),
        F.round(F.avg("punt_global"), 2).alias("prom_global"),
        F.round(F.avg("punt_matematicas"), 2).alias("prom_matematicas"),
        F.round(F.avg("punt_lectura_critica"), 2).alias("prom_lectura")
    ).orderBy(F.desc("prom_global"))
    df_brecha_tic.show()

    # 5. Ranking Departamental
    print("\n--- 5. RANKING DEPARTAMENTAL ---")
    df_ranking_deptos = df.groupBy("cole_depto_ubicacion").agg(
        F.count("*").alias("total_estudiantes"),
        F.round(F.avg("punt_global"), 2).alias("prom_global"),
        F.round(F.stddev("punt_global"), 2).alias("std_global"),
        F.round(F.max("punt_global"), 2).alias("max_global"),
        F.round(F.min("punt_global"), 2).alias("min_global")
    ).orderBy(F.desc("prom_global"))
    df_ranking_deptos.show(15, truncate=False)

    # 6. Desempeño en Inglés por Municipios (Top y Bottom)
    print("\n--- 6. TOP MUNICIPIOS EN INGLÉS ---")
    df_muni_ingles = df.groupBy("cole_mcpio_ubicacion", "cole_depto_ubicacion").agg(
        F.count("*").alias("total_evaluados"),
        F.round(F.avg("punt_ingles"), 2).alias("prom_ingles"),
        F.round(F.sum(F.when(F.col("desemp_ingles").isin("B1", "B+"), 1).otherwise(0)) * 100.0 / F.count("*"), 2).alias("pct_b1_bmas")
    ).filter(F.col("total_evaluados") >= 50).orderBy(F.desc("prom_ingles"))
    df_muni_ingles.show(10, truncate=False)

    # 7. Exportar resultados a capa Refined (Parquet)
    print(f"\n--- 7. EXPORTANDO CAPA REFINED A S3: {output_refined} ---")
    df_brecha_oficial.write.mode("overwrite").parquet(f"{output_refined}/brecha_oficial/")
    df_brecha_tic.write.mode("overwrite").parquet(f"{output_refined}/brecha_digital/")
    df_ranking_deptos.write.mode("overwrite").parquet(f"{output_refined}/ranking_departamental/")
    df_muni_ingles.write.mode("overwrite").parquet(f"{output_refined}/municipios_ingles/")

    print("=== ANÁLISIS PYSPARK FINALIZADO CON ÉXITO ===")
    spark.stop()

if __name__ == "__main__":
    main()
