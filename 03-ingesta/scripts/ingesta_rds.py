#!/usr/bin/env python3
"""
ingesta_rds.py
--------------
Extrae datos desde RDS MariaDB (tablas maestras y resultados 2019-2020) y los deposita en S3 Raw.
Si no hay conectividad directa a RDS (entorno offline o en preparación), usa como fallback
los datos del directorio local 02-fuentes-datos/data/rds/.
Guarda los datos en:
s3://<S3_BUCKET_NAME>/raw/fuente=rds/ingest_date=YYYY-MM-DD/
"""

import os
import sys
import csv
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
DB_HOST = os.getenv("RDS_HOST")
DB_PORT = int(os.getenv("RDS_PORT", 3306))
DB_USER = os.getenv("RDS_USER", "admin_saber11")
DB_PASSWORD = os.getenv("RDS_PASSWORD", "")
DB_NAME = os.getenv("RDS_DATABASE", "saber11_db")

def get_s3_client():
    return boto3.client("s3", region_name=AWS_REGION)

def extraer_de_rds(table_name, output_csv):
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4"
        )
        cursor = conn.cursor()
        print(f"Extrayendo tabla '{table_name}' desde RDS MariaDB...")
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        
        with open(output_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
            
        print(f"  Extraídas {len(rows)} filas de {table_name}.")
        conn.close()
        return True
    except Exception as e:
        print(f"Aviso conectando a RDS ({e}). Intentando fallback local...")
        return False

def subir_archivo(s3_client, local_path, s3_key):
    print(f"Subiendo {local_path} -> s3://{S3_BUCKET}/{s3_key}...")
    s3_client.upload_file(local_path, S3_BUCKET, s3_key)
    print("  Subida completada exitosamente.")

def main():
    if not S3_BUCKET:
        print("ERROR: S3_BUCKET_NAME no está definido en .env")
        sys.exit(1)

    ingest_date = datetime.now().strftime("%Y-%m-%d")
    s3_client = get_s3_client()

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    rds_data_dir = os.path.join(base_dir, "02-fuentes-datos", "data", "rds")

    print(f"--- INICIO INGESTA RDS HACIA S3 RAW (Fecha: {ingest_date}) ---")

    tablas = [
        ("dim_municipios", "dim_municipios.csv"),
        ("dim_colegios", "dim_colegios.csv"),
        ("resultados_saber11_historico_rds", "resultados_2019_2020.csv")
    ]

    for table, filename in tablas:
        local_path = os.path.join(rds_data_dir, filename)
        # Intentar extraer directamente de RDS si está configurado
        if DB_HOST and DB_HOST != "localhost":
            exito = extraer_de_rds(table, local_path)
        
        if os.path.exists(local_path):
            key = f"raw/fuente=rds/ingest_date={ingest_date}/{filename}"
            subir_archivo(s3_client, local_path, key)
        else:
            print(f"Error: no se encontró archivo para {table} en {local_path}")

    print("--- INGESTA RDS FINALIZADA CON ÉXITO ---")

if __name__ == "__main__":
    main()
