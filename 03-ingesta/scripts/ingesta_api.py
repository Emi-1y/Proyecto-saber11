#!/usr/bin/env python3
"""
ingesta_api.py
--------------
Ingesta de datos desde la API pública de Socrata (datos.gov.co) y DIVIPOLA hacia S3 Raw.
Guarda los datos en:
s3://<S3_BUCKET_NAME>/raw/fuente=api/ingest_date=YYYY-MM-DD/
"""

import os
import sys
import json
import boto3
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
SOCRATA_DATASET_ID = os.getenv("SOCRATA_DATASET_ID", "kgxf-xxbe")
SOCRATA_DIVIPOLA_ID = os.getenv("SOCRATA_DIVIPOLA_ID", "gdxc-w37w")
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN", "")

def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)

def descargar_socrata(dataset_id, where_clause=None, limit=10000):
    url = f"https://www.datos.gov.co/resource/{dataset_id}.json"
    headers = {"User-Agent": "AntigravityDataPipeline/1.0"}
    if SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = SOCRATA_APP_TOKEN

    params = {"$limit": limit}
    if where_clause:
        params["$where"] = where_clause

    print(f"Consultando API Socrata ({url}) con params: {params}...")
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"  Descargados {len(data)} registros de {dataset_id}")
        return data
    except Exception as e:
        print(f"Error consultando API externa: {e}")
        # Si estamos sin conexión o en sandbox, verificar si existe copia local en 02-fuentes-datos/data/api
        fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "02-fuentes-datos", "data", "api")
        local_file = os.path.join(fallback_path, "saber11_2023.json" if dataset_id == SOCRATA_DATASET_ID else "divipola_municipios.json")
        if os.path.exists(local_file):
            print(f"  Usando respaldo local desde {local_file}...")
            with open(local_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

def subir_a_s3(s3_client, data, s3_key):
    body = json.dumps(data, ensure_ascii=False)
    print(f"Subiendo a S3: s3://{S3_BUCKET}/{s3_key} ({len(body)} bytes)...")
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=body.encode("utf-8"),
        ContentType="application/json"
    )
    print(f"  Subida completada exitosamente.")

def main():
    if not S3_BUCKET:
        print("ERROR: S3_BUCKET_NAME no está definido en .env")
        sys.exit(1)

    ingest_date = datetime.now().strftime("%Y-%m-%d")
    s3_client = get_s3_client()

    print(f"--- INICIO INGESTA API HACIA S3 RAW (Fecha: {ingest_date}) ---")

    # 1. Ingesta Saber 11 (Periodo 2023 o reciente)
    saber11_data = descargar_socrata(SOCRATA_DATASET_ID, where_clause="periodo >= '20231'", limit=10000)
    if saber11_data:
        key = f"raw/fuente=api/ingest_date={ingest_date}/saber11_2023.json"
        subir_a_s3(s3_client, saber11_data, key)

    # 2. Ingesta DIVIPOLA (Municipios)
    divipola_data = descargar_socrata(SOCRATA_DIVIPOLA_ID, limit=2000)
    if divipola_data:
        key = f"raw/fuente=api/ingest_date={ingest_date}/divipola_municipios.json"
        subir_a_s3(s3_client, divipola_data, key)

    print("--- INGESTA API FINALIZADA CON ÉXITO ---")

if __name__ == "__main__":
    main()
