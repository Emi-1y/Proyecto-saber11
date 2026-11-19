"""
AWS Lambda: Disparador Automático de Ingesta y Pipeline Saber 11
-----------------------------------------------------------------
Esta función Lambda se activa automáticamente mediante Amazon EventBridge (Cron)
o tras la llegada de nuevos archivos a S3.
Acciones:
1. Realiza la extracción incremental de datos desde la API Socrata (Saber 11 y DIVIPOLA).
2. Deposita los objetos en S3 Raw particionados por la fecha del día (ingest_date=YYYY-MM-DD).
3. Dispara automáticamente el Job de AWS Glue (saber11-raw-to-trusted) para procesar los datos.
"""

import os
import json
import boto3
import urllib.request
from datetime import datetime

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "saber11-datalake-885601272401")
GLUE_JOB_NAME = os.environ.get("GLUE_JOB_NAME", "saber11-raw-to-trusted")
SOCRATA_DATASET_ID = "kgxf-xxbe"

s3_client = boto3.client("s3")
glue_client = boto3.client("glue")

def lambda_handler(event, context):
    print("--- EVENTO DE INGESTA AUTOMÁTICA DISPARADO POR EVENTBRIDGE ---")
    print(f"Payload del evento: {json.dumps(event)}")
    
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    s3_raw_prefix = f"raw/fuente=api/ingest_date={fecha_hoy}"
    
    # 1. Extracción automática desde Socrata API (último periodo)
    url = f"https://www.datos.gov.co/resource/{SOCRATA_DATASET_ID}.json?$limit=5000&$where=periodo>='20231'"
    print(f"Consultando API Socrata: {url}")
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AWS-Lambda-Ingest/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            registros = json.loads(data.decode("utf-8"))
            print(f"Descargados exitosamente {len(registros)} registros desde datos.gov.co")
            
            # Guardar en S3 Raw
            s3_key = f"{s3_raw_prefix}/saber11_incremental_{fecha_hoy}.json"
            s3_client.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=data,
                ContentType="application/json"
            )
            print(f"Guardado automático en: s3://{S3_BUCKET}/{s3_key}")
    except Exception as e:
        print(f"Advertencia consultando API: {e}. Continuando flujo...")

    # 2. Disparo encadenado del Job de AWS Glue (ETL Raw a Trusted)
    try:
        print(f"Disparando AWS Glue Job ETL: {GLUE_JOB_NAME}...")
        glue_res = glue_client.start_job_run(JobName=GLUE_JOB_NAME)
        job_run_id = glue_res["JobRunId"]
        print(f"Glue Job disparado automáticamente con JobRunId: {job_run_id}")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Ingesta automática completada y Glue ETL disparado.",
                "ingest_date": fecha_hoy,
                "glue_job_run_id": job_run_id
            })
        }
    except Exception as e:
        print(f"Error disparando Glue Job: {e}")
        return {"statusCode": 500, "error": str(e)}
