#!/usr/bin/env python3
"""
local_spark_raw_to_trusted.py
-----------------------------
Ejecuta el procesamiento ETL Raw -> Trusted localmente con Apache Spark (PySpark),
leyendo desde 02-fuentes-datos/data/ y guardando en 04-procesamiento-glue-spark/data/trusted/
o directamente hacia S3 si las credenciales están configuradas.
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, LongType

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(base_dir, "02-fuentes-datos", "data")
    output_dir = os.path.join(base_dir, "04-procesamiento-glue-spark", "data", "trusted", "saber11_unified")

    print("Iniciando sesión local de Apache Spark...")
    spark = SparkSession.builder \
        .appName("Saber11-Local-RawToTrusted") \
        .master("local[*]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # 1. Leer RDS
    rds_res = os.path.join(data_dir, "rds", "resultados_2019_2020.csv")
    rds_col = os.path.join(data_dir, "rds", "dim_colegios.csv")
    rds_mun = os.path.join(data_dir, "rds", "dim_municipios.csv")

    df_res = spark.read.option("header", "true").option("inferSchema", "true").csv(rds_res)
    df_col = spark.read.option("header", "true").option("inferSchema", "true").csv(rds_col)
    df_mun = spark.read.option("header", "true").option("inferSchema", "true").csv(rds_mun)

    df_rds = df_res.join(
        df_col.select(
            "cole_cod_dane_establecimiento", "cole_codigo_icfes", "cole_nombre_establecimiento",
            "cole_genero", "cole_naturaleza", "cole_calendario", "cole_bilingue", "cole_caracter",
            "cole_area_ubicacion", "cole_jornada", "cole_cod_mcpio_ubicacion"
        ),
        on="cole_cod_dane_establecimiento",
        how="left"
    ).join(
        df_mun.select(
            F.col("cod_municipio").alias("cole_cod_mcpio_ubicacion"),
            F.col("nom_municipio").alias("cole_mcpio_ubicacion"),
            F.col("cod_depto").alias("cole_cod_depto_ubicacion"),
            F.col("nom_depto").alias("cole_depto_ubicacion")
        ),
        on="cole_cod_mcpio_ubicacion",
        how="left"
    )

    # 2. Leer EC2
    ec2_2021 = os.path.join(data_dir, "ec2", "saber11_2021.csv")
    ec2_2022 = os.path.join(data_dir, "ec2", "saber11_2022.csv")
    df_ec2 = spark.read.option("header", "true").option("inferSchema", "true").csv([ec2_2021, ec2_2022])

    # 3. Leer API
    api_2023 = os.path.join(data_dir, "api", "saber11_2023.json")
    df_api = spark.read.option("multiline", "true").json(api_2023)

    target_columns = [
        "estu_consecutivo", "periodo", "estu_tipodocumento", "estu_genero", "estu_fechanacimiento",
        "fami_estratovivienda", "fami_educacionpadre", "fami_educacionmadre",
        "fami_tieneinternet", "fami_tienecomputador",
        "cole_cod_dane_establecimiento", "cole_codigo_icfes", "cole_nombre_establecimiento",
        "cole_genero", "cole_naturaleza", "cole_calendario", "cole_bilingue", "cole_caracter",
        "cole_area_ubicacion", "cole_jornada", "cole_cod_mcpio_ubicacion",
        "cole_mcpio_ubicacion", "cole_cod_depto_ubicacion", "cole_depto_ubicacion",
        "punt_lectura_critica", "punt_matematicas", "punt_c_naturales", "punt_sociales_ciudadanas",
        "punt_ingles", "desemp_ingles", "punt_global", "percentil_global"
    ]

    def sel_cols(df):
        exprs = []
        for c in target_columns:
            if c in df.columns:
                exprs.append(F.col(c))
            else:
                exprs.append(F.lit(None).alias(c))
        return df.select(exprs)

    df_union = sel_cols(df_rds).unionByName(sel_cols(df_ec2)).unionByName(sel_cols(df_api))

    df_clean = df_union.dropDuplicates(["estu_consecutivo"]) \
        .withColumn("periodo", F.col("periodo").cast(IntegerType())) \
        .withColumn("punt_lectura_critica", F.col("punt_lectura_critica").cast(IntegerType())) \
        .withColumn("punt_matematicas", F.col("punt_matematicas").cast(IntegerType())) \
        .withColumn("punt_c_naturales", F.col("punt_c_naturales").cast(IntegerType())) \
        .withColumn("punt_sociales_ciudadanas", F.col("punt_sociales_ciudadanas").cast(IntegerType())) \
        .withColumn("punt_ingles", F.col("punt_ingles").cast(IntegerType())) \
        .withColumn("punt_global", F.col("punt_global").cast(IntegerType())) \
        .withColumn("percentil_global", F.col("percentil_global").cast(IntegerType())) \
        .withColumn("cole_cod_dane_establecimiento", F.col("cole_cod_dane_establecimiento").cast(LongType())) \
        .withColumn("fami_estratovivienda", F.coalesce(F.col("fami_estratovivienda"), F.lit("NO_REPORTADO"))) \
        .withColumn("fami_educacionpadre", F.coalesce(F.col("fami_educacionpadre"), F.lit("NO_REPORTADO"))) \
        .withColumn("fami_educacionmadre", F.coalesce(F.col("fami_educacionmadre"), F.lit("NO_REPORTADO")))

    total = df_clean.count()
    print(f"\n[OK] Datos unificados exitosamente. Total registros: {total}")
    print("\nDistribución por periodo:")
    df_clean.groupBy("periodo").count().orderBy("periodo").show()

    print(f"Escribiendo dataset en Parquet particionado en: {output_dir}")
    os.makedirs(os.path.dirname(output_dir), exist_ok=True)
    df_clean.write.mode("overwrite").partitionBy("periodo").parquet(output_dir)

    print("\nProcesamiento Spark local completado con éxito.")
    spark.stop()

if __name__ == "__main__":
    main()
