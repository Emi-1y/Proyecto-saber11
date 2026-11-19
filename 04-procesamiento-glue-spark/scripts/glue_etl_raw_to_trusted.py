import sys
import os
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, LongType

args = getResolvedOptions(sys.argv, ["JOB_NAME", "S3_BUCKET_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bucket = args["S3_BUCKET_NAME"]
raw_base = f"s3://{bucket}/raw"
trusted_output = f"s3://{bucket}/trusted/saber11_unified"

print("--- INICIANDO GLUE ETL JOB: Raw a Trusted ---")

# 1. Leer Fuente RDS (Resultados 2019-2020 y Maestras)
path_rds_res = f"{raw_base}/fuente=rds/*/*resultados*.csv"
path_rds_col = f"{raw_base}/fuente=rds/*/*dim_colegios*.csv"
path_rds_mun = f"{raw_base}/fuente=rds/*/*dim_municipios*.csv"

df_rds_res = spark.read.option("header", "true").option("inferSchema", "true").csv(path_rds_res)
df_rds_col = spark.read.option("header", "true").option("inferSchema", "true").csv(path_rds_col)
df_rds_mun = spark.read.option("header", "true").option("inferSchema", "true").csv(path_rds_mun)

# Eliminar de resultados cualquier columna que provenga de los maestros para evitar ambigüedades
cols_colegio = [c for c in df_rds_col.columns if c != "cole_cod_dane_establecimiento"]
df_rds_res_clean = df_rds_res.drop(*cols_colegio)
cols_municipio = ["cole_mcpio_ubicacion", "cole_cod_depto_ubicacion", "cole_depto_ubicacion"]
df_rds_res_clean = df_rds_res_clean.drop(*cols_municipio)

df_rds_enriquecido = df_rds_res_clean.join(
    df_rds_col,
    on="cole_cod_dane_establecimiento",
    how="left"
).join(
    df_rds_mun.select(
        F.col("cod_municipio").alias("cole_cod_mcpio_ubicacion"),
        F.col("nom_municipio").alias("cole_mcpio_ubicacion"),
        F.col("cod_depto").alias("cole_cod_depto_ubicacion"),
        F.col("nom_depto").alias("cole_depto_ubicacion")
    ),
    on="cole_cod_mcpio_ubicacion",
    how="left"
)

# 2. Leer Fuente EC2 (2021-2022)
path_ec2 = f"{raw_base}/fuente=ec2/*/*.csv"
df_ec2 = spark.read.option("header", "true").option("inferSchema", "true").csv(path_ec2)

# 3. Leer Fuente API (2023)
path_api = f"{raw_base}/fuente=api/*/*saber11*.json"
df_api = spark.read.option("multiline", "true").json(path_api)

# 4. Homologar columnas y esquemas para el UNION
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

def seleccionar_columnas(df):
    exprs = []
    for c in target_columns:
        if c in df.columns:
            exprs.append(F.col(c))
        else:
            exprs.append(F.lit(None).alias(c))
    return df.select(exprs)

df_rds_sel = seleccionar_columnas(df_rds_enriquecido)
df_ec2_sel = seleccionar_columnas(df_ec2)
df_api_sel = seleccionar_columnas(df_api)

df_union = df_rds_sel.unionByName(df_ec2_sel).unionByName(df_api_sel)

# 5. Limpieza, tipificación y deduplicación
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
    .withColumn("cole_codigo_icfes", F.col("cole_codigo_icfes").cast(LongType())) \
    .withColumn("fami_estratovivienda", F.coalesce(F.col("fami_estratovivienda"), F.lit("NO_REPORTADO"))) \
    .withColumn("fami_educacionpadre", F.coalesce(F.col("fami_educacionpadre"), F.lit("NO_REPORTADO"))) \
    .withColumn("fami_educacionmadre", F.coalesce(F.col("fami_educacionmadre"), F.lit("NO_REPORTADO")))

print(f"Total registros consolidados: {df_clean.count()}")

# 6. Escribir a S3 Trusted en formato Parquet particionado por periodo
print(f"Escribiendo en Parquet en {trusted_output} particionado por periodo...")
df_clean.write \
    .mode("overwrite") \
    .partitionBy("periodo") \
    .parquet(trusted_output)

print("--- GLUE ETL JOB COMPLETADO EXITOSAMENTE ---")
job.commit()
