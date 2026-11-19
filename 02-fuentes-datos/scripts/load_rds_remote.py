#!/usr/bin/env python3
import os
import csv
import pymysql

DB_HOST = "saber11-mariadb.c5rjmcacjyir.us-east-1.rds.amazonaws.com"
DB_USER = "admin_saber11"
DB_PASS = "Saber11_Password2026!"
DB_NAME = "saber11_db"

print(f"Conectando a {DB_HOST} con SSL...")
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    charset="utf8mb4",
    ssl={"check_hostname": False},
    autocommit=True
)
cur = conn.cursor()

def load(csv_path, table):
    # Obtener columnas válidas de la tabla destino
    cur.execute(f"DESCRIBE {table}")
    valid_cols = set(row[0] for row in cur.fetchall())

    with open(csv_path, "r", encoding="utf-8") as f:
        r = csv.reader(f)
        headers = next(r)
        
        # Mapear índices de columnas que sí existen en la tabla
        matching_indices = [(i, h) for i, h in enumerate(headers) if h in valid_cols]
        col_names = [h for _, h in matching_indices]
        indices = [i for i, _ in matching_indices]

        cols_str = ", ".join(col_names)
        placeholders = ", ".join(["%s"] * len(col_names))
        sql = f"INSERT IGNORE INTO {table} ({cols_str}) VALUES ({placeholders})"
        
        batch = []
        tot = 0
        for row in r:
            filtered_row = [None if row[idx] == "" else row[idx] for idx in indices]
            batch.append(filtered_row)
            if len(batch) >= 2000:
                cur.executemany(sql, batch)
                tot += len(batch)
                batch = []
        if batch:
            cur.executemany(sql, batch)
            tot += len(batch)
    print(f"Cargados {tot} registros en {table}")

data_dir = "/home/ec2-user/data/rds"
load(os.path.join(data_dir, "dim_municipios.csv"), "dim_municipios")
load(os.path.join(data_dir, "dim_colegios.csv"), "dim_colegios")
load(os.path.join(data_dir, "resultados_2019_2020.csv"), "resultados_saber11_historico_rds")

cur.execute("SELECT COUNT(*) FROM dim_municipios")
print("Total dim_municipios:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM dim_colegios")
print("Total dim_colegios:", cur.fetchone()[0])
cur.execute("SELECT COUNT(*), AVG(punt_global) FROM resultados_saber11_historico_rds")
res = cur.fetchone()
print(f"Total resultados_2019_2020: {res[0]}, Promedio Puntaje Global: {res[1]:.2f}")
conn.close()
print("Carga en RDS MariaDB finalizada con éxito!")
