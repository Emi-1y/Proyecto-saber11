# 04 - Procesamiento ETL: Raw a Trusted con AWS Glue y Apache Spark

## 1. Objetivo
Transformar, limpiar, estandarizar y unificar los datos provenientes de las tres fuentes ubicadas en `s3://.../raw/` hacia la zona `s3://.../trusted/` (Bronze a Silver). El job realiza cruces relacionales con las tablas maestras, homologa esquemas, tipifica columnas numéricas y escribe los datos consolidados en formato columnar **Apache Parquet particionado por periodo**.

---

## 2. Requisitos Previos
- Datos disponibles en la zona `raw/` de S3.
- Rol IAM `LabRole` (o rol para AWS Glue con políticas de acceso a S3 y CloudWatch Logs).
- Script PySpark probado con muestra en local o directamente en AWS Glue Job.

---

## 3. Comandos Exactos Numerados

### Paso 1: Probar la transformación en local con PySpark
Ejecutar el pipeline de validación y limpieza en la máquina de desarrollo:
```bash
python 04-procesamiento-glue-spark/scripts/local_spark_raw_to_trusted.py
```

### Paso 2: Subir el script ETL al bucket de scripts en S3
```bash
aws s3 cp 04-procesamiento-glue-spark/scripts/glue_etl_raw_to_trusted.py \
    s3://saber11-datalake-TUNOMBRE/scripts/glue_etl_raw_to_trusted.py
```

### Paso 3: Crear el Job de AWS Glue (Spark)
```bash
aws glue create-job \
    --name saber11-raw-to-trusted \
    --role LabRole \
    --command '{"Name": "glueetl", "ScriptLocation": "s3://saber11-datalake-TUNOMBRE/scripts/glue_etl_raw_to_trusted.py", "PythonVersion": "3"}' \
    --glue-version "4.0" \
    --number-of-workers 2 \
    --worker-type "G.1X" \
    --default-arguments '{"--enable-metrics": "true", "--job-language": "python", "--TempDir": "s3://saber11-datalake-TUNOMBRE/temp/"}' \
    --region us-east-1
```

### Paso 4: Ejecutar el Glue Job
```bash
JOB_RUN_ID=$(aws glue start-job-run --job-name saber11-raw-to-trusted --query 'JobRunId' --output text --region us-east-1)
echo "Ejecutando Job Run ID: $JOB_RUN_ID"
```

### Paso 5: Monitorear el estado del Job hasta finalizar
```bash
aws glue get-job-run --job-name saber11-raw-to-trusted --run-id $JOB_RUN_ID --query 'JobRun.JobRunState' --output text --region us-east-1
```

### Paso 6: Verificar la salida en S3 Trusted
```bash
aws s3 ls s3://saber11-datalake-TUNOMBRE/trusted/saber11_unified/
```

---

## 4. Resultado Esperado
- Datos consolidados de todos los periodos (2019 a 2023+) en un único dataset unificado.
- Formato columnar Parquet con compresión Snappy.
- Directorios particionados por periodo: `periodo=20194/`, `periodo=20204/`, `periodo=20214/`, `periodo=20224/`, `periodo=20234/`.
- Limpieza de valores nulos y nombres normalizados.

---

## 5. Evidencias (Pantallazos)
<!-- Adjuntar capturas en ../evidencias/ -->
- `evidencias/04_glue_job_success.png`: Consola de AWS Glue mostrando el Job Run en estado `SUCCEEDED`.
- `evidencias/04_s3_trusted_parquet_partitions.png`: Vista en consola de S3 con las particiones Parquet generadas.
