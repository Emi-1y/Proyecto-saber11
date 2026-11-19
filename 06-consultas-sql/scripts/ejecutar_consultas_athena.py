#!/usr/bin/env python3
"""
ejecutar_consultas_athena.py
----------------------------
Ejecuta las consultas analíticas sobre Amazon Athena utilizando boto3.
Guarda los resultados en S3 Athena Query Results y los despliega en consola.
"""

import os
import sys
import time
import boto3
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DATABASE = os.getenv("GLUE_DATABASE", "saber11_catalog")
BUCKET = os.getenv("S3_BUCKET_NAME", "saber11-datalake-885601272401")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
OUTPUT_LOCATION = f"s3://{BUCKET}/athena-query-results/"

athena_client = boto3.client("athena", region_name=REGION)

CONSULTAS = [
    (
        "1. Ranking Departamental por Puntaje Global Promedio",
        """
        SELECT 
            cole_depto_ubicacion AS departamento,
            COUNT(*) AS total_estudiantes,
            ROUND(AVG(punt_global), 2) AS promedio_global,
            ROUND(STDDEV(punt_global), 2) AS desv_global,
            MAX(punt_global) AS max_global,
            MIN(punt_global) AS min_global
        FROM saber11_catalog.saber11_unified
        GROUP BY cole_depto_ubicacion
        ORDER BY promedio_global DESC
        LIMIT 10;
        """
    ),
    (
        "2. Brecha entre Colegios Oficiales y No Oficiales",
        """
        SELECT 
            periodo,
            cole_naturaleza,
            COUNT(*) AS total_estudiantes,
            ROUND(AVG(punt_global), 2) AS promedio_global,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
            ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
            ROUND(AVG(punt_ingles), 2) AS prom_ingles
        FROM saber11_catalog.saber11_unified
        GROUP BY periodo, cole_naturaleza
        ORDER BY periodo ASC, cole_naturaleza ASC;
        """
    ),
    (
        "3. Impacto Socioeconómico (Estrato vs Matemáticas y Global)",
        """
        SELECT 
            fami_estratovivienda AS estrato,
            COUNT(*) AS total_evaluados,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
            ROUND(AVG(punt_global), 2) AS prom_global
        FROM saber11_catalog.saber11_unified
        GROUP BY fami_estratovivienda
        ORDER BY prom_global DESC;
        """
    ),
    (
        "4. Brecha Digital: Computador e Internet",
        """
        SELECT 
            fami_tieneinternet AS tiene_internet,
            fami_tienecomputador AS tiene_computador,
            COUNT(*) AS total_evaluados,
            ROUND(AVG(punt_global), 2) AS prom_global,
            ROUND(AVG(punt_matematicas), 2) AS prom_matematicas
        FROM saber11_catalog.saber11_unified
        GROUP BY fami_tieneinternet, fami_tienecomputador
        ORDER BY prom_global DESC;
        """
    ),
    (
        "5. Calidad de Datos: Monitoreo de Nulos por Variable",
        """
        SELECT 
            COUNT(*) AS total_filas,
            ROUND(SUM(CASE WHEN fami_estratovivienda IS NULL OR fami_estratovivienda = 'NO_REPORTADO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_estrato,
            ROUND(SUM(CASE WHEN fami_educacionpadre IS NULL OR fami_educacionpadre = 'NO_REPORTADO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_educ_padre,
            ROUND(SUM(CASE WHEN fami_tieneinternet IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_internet
        FROM saber11_catalog.saber11_unified;
        """
    )
]

def ejecutar_consulta(query_sql):
    response = athena_client.start_query_execution(
        QueryString=query_sql,
        QueryExecutionContext={"Database": DATABASE},
        ResultConfiguration={"OutputLocation": OUTPUT_LOCATION}
    )
    query_id = response["QueryExecutionId"]
    
    # Esperar hasta que la consulta termine
    while True:
        status_res = athena_client.get_query_execution(QueryExecutionId=query_id)
        state = status_res["QueryExecution"]["Status"]["State"]
        if state in ["SUCCEEDED", "FAILED", "CANCELLED"]:
            if state != "SUCCEEDED":
                error_msg = status_res["QueryExecution"]["Status"].get("StateChangeReason", "Error desconocido")
                raise Exception(f"Consulta Athena falló ({state}): {error_msg}")
            break
        time.sleep(1)

    # Obtener resultados
    results = athena_client.get_query_results(QueryExecutionId=query_id)
    return results

def formatear_resultados(results):
    rows = results["ResultSet"]["Rows"]
    if not rows:
        return "Sin resultados."
    
    header = [col.get("VarCharValue", "") for col in rows[0]["Data"]]
    lines = [" | ".join(header), "-" * (len(" | ".join(header)) + 5)]
    
    for row in rows[1:]:
        row_vals = [col.get("VarCharValue", "NULL") for col in row["Data"]]
        lines.append(" | ".join(row_vals))
        
    return "\n".join(lines)

def main():
    print(f"=== EJECUTANDO CONSULTAS EN AMAZON ATHENA (DB: {DATABASE}) ===")
    print(f"Resultados guardados en: {OUTPUT_LOCATION}\n")

    for titulo, sql in CONSULTAS:
        print(f"\n>>> {titulo}")
        try:
            res = ejecutar_consulta(sql)
            print(formatear_resultados(res))
        except Exception as e:
            print(f"Error: {e}")

    print("\n=== TODAS LAS CONSULTAS DE ATHENA EJECUTADAS EXITOSAMENTE ===")

if __name__ == "__main__":
    main()
