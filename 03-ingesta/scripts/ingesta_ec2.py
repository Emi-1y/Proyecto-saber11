#!/usr/bin/env python3
"""
ingesta_ec2.py
--------------
Ingesta de archivos CSV generados o almacenados en la instancia EC2 hacia S3 Raw.
Guarda los datos en:
s3://<S3_BUCKET_NAME>/raw/fuente=ec2/ingest_date=YYYY-MM-DD/
"""

import os
import sys
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)

def subir_archivo(s3_client, local_path, s3_key):
    print(f"Subiendo {local_path} -> s3://{S3_BUCKET}/{s3_key}...")
    s3_client.upload_file(local_path, S3_BUCKET, s3_key)
    print(f"  Completado exitosamente.")

def main():
    if not S3_BUCKET:
        print("ERROR: S3_BUCKET_NAME no está definido en .env")
        sys.exit(1)

    ingest_date = datetime.now().strftime("%Y-%m-%d")
    s3_client = get_s3_client()

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ec2_data_dir = os.path.join(base_dir, "02-fuentes-datos", "data", "ec2")

    print(f"--- INICIO INGESTA EC2 HACIA S3 RAW (Fecha: {ingest_date}) ---")

    archivos_ec2 = ["saber11_2021.csv", "saber11_2022.csv"]
    for arch in archivos_ec2:
        path = os.path.join(ec2_data_dir, arch)
        if os.path.exists(path):
            key = f"raw/fuente=ec2/ingest_date={ingest_date}/{arch}"
            subir_archivo(s3_client, path, key)
        else:
            print(f"Aviso: Archivo {path} no encontrado.")

    print("--- INGESTA EC2 FINALIZADA CON ÉXITO ---")

if __name__ == "__main__":
    main()
