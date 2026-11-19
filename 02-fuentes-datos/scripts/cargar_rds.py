#!/usr/bin/env python3
"""
cargar_rds.py
-------------
Carga las tablas maestras (dim_municipios, dim_colegios) y la tabla de resultados
históricos (resultados_saber11_historico_rds) en la base de datos MariaDB / MySQL.
Lee las variables de conexión desde el archivo .env.
"""

import os
import csv
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_HOST = os.getenv("RDS_HOST", "localhost")
DB_PORT = int(os.getenv("RDS_PORT", 3306))
DB_USER = os.getenv("RDS_USER", "admin_saber11")
DB_PASSWORD = os.getenv("RDS_PASSWORD", "")
DB_NAME = os.getenv("RDS_DATABASE", "saber11_db")

def get_connection():
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset="utf8mb4",
            ssl={"check_hostname": False},
            autocommit=False
        )
        return conn
    except Exception as e:
        print(f"Error conectando a MariaDB ({DB_HOST}:{DB_PORT}): {e}")
        return None

def cargar_csv(conn, filepath, table_name, batch_size=2000):
    if not os.path.exists(filepath):
        print(f"Archivo no encontrado: {filepath}")
        return

    print(f"Cargando {filepath} en tabla '{table_name}'...")
    cursor = conn.cursor()
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)
        placeholders = ", ".join(["%s"] * len(headers))
        columns_str = ", ".join(headers)
        sql = f"INSERT IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
        
        batch = []
        total = 0
        for row in reader:
            # Reemplazar cadenas vacías por None para que se almacenen como NULL
            cleaned_row = [None if val == "" else val for val in row]
            batch.append(cleaned_row)
            if len(batch) >= batch_size:
                cursor.executemany(sql, batch)
                conn.commit()
                total += len(batch)
                print(f"  Insertados {total} registros en {table_name}...")
                batch = []
        
        if batch:
            cursor.executemany(sql, batch)
            conn.commit()
            total += len(batch)
            
    print(f"Finalizada carga de {table_name}. Total insertados: {total}")
    cursor.close()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rds_data_dir = os.path.join(base_dir, "data", "rds")

    print(f"Conectando a MariaDB en {DB_HOST}:{DB_PORT} (DB: {DB_NAME})...")
    conn = get_connection()
    if not conn:
        print("Asegúrate de que la instancia RDS esté creada y las variables en .env estén configuradas.")
        sys.exit(1)

    try:
        # 1. Cargar Maestras primero por restricciones de llaves foráneas
        cargar_csv(conn, os.path.join(rds_data_dir, "dim_municipios.csv"), "dim_municipios")
        cargar_csv(conn, os.path.join(rds_data_dir, "dim_colegios.csv"), "dim_colegios")

        # 2. Cargar Resultados Históricos
        cargar_csv(conn, os.path.join(rds_data_dir, "resultados_2019_2020.csv"), "resultados_saber11_historico_rds")

        print("Toda la carga en RDS MariaDB se completó exitosamente.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
