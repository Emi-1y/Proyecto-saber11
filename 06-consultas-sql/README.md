# 06 - Consultas Analíticas con SQL: Athena, Apache SparkSQL y Apache Hive en EMR

## 1. Objetivo
Ejecutar consultas analíticas estructuradas para responder a las 8 preguntas de negocio definidas en la Fase 1, comparando el rendimiento, la latencia y la arquitectura de ejecución entre los tres motores SQL fundamentales sobre el Data Lake en Amazon S3:
1. **Amazon Athena** (Presto / Trino Serverless sobre AWS Glue Data Catalog).
2. **Apache SparkSQL** (Optimización Catalyst en memoria y ejecución distribuida).
3. **Apache Hive sobre Amazon EMR** (Motor batch sobre clúster distribuido Hadoop Tez / MapReduce).

---

## 2. Scripts Disponibles y Comandos de Ejecución

### A. Ejecución en Amazon Athena (Serverless)
Consulta la tabla externa `saber11_catalog.saber11_unified` leyendo directamente los archivos Parquet en S3 Trusted:
```bash
python 06-consultas-sql/scripts/ejecutar_consultas_athena.py
```
*Evidencia generada:* `evidencias/06_athena_query_results.txt`

### B. Ejecución con Apache SparkSQL (En Memoria / Glue)
Carga el dataset Parquet, registra la vista temporal y evalúa las 8 consultas con `spark.sql()`:
```bash
python 06-consultas-sql/scripts/ejecutar_consultas_sparksql.py --bucket saber11-datalake-885601272401
```
*Evidencia generada:* `evidencias/06_sparksql_query_results.txt`

### C. Ejecución con Apache Hive en Amazon EMR
Ejecuta el archivo SQL unificado en la consola de Hive CLI / Beeline o como un Step de EMR:
```bash
bash 05-catalogacion/emr/run_hive_emr_step.sh j-CLUSTERID saber11-datalake-885601272401
```
*Script HQL:* `06-consultas-sql/sql/todas_las_consultas.sql`

---

## 3. Las 8 Preguntas de Negocio Evaluadas

| # | Pregunta de Negocio | Consulta SQL Clave |
|:--|:--------------------|:-------------------|
| **Q1** | ¿Cuál es el ranking departamental por puntaje global promedio? | `GROUP BY cole_depto_ubicacion ORDER BY AVG(punt_global) DESC` |
| **Q2** | ¿Cuál es la brecha entre colegios oficiales y no oficiales? | `GROUP BY periodo, cole_naturaleza ORDER BY periodo, cole_naturaleza` |
| **Q3** | ¿Cómo influye el estrato socioeconómico en matemáticas y global? | `GROUP BY fami_estratovivienda ORDER BY AVG(punt_global) DESC` |
| **Q4** | ¿Cómo evolucionó el puntaje promedio por periodo y área? | `GROUP BY periodo ORDER BY periodo ASC` |
| **Q5** | ¿Qué municipios tienen los mejores resultados en inglés? | `GROUP BY cole_mcpio_ubicacion HAVING COUNT(*) >= 50 ORDER BY AVG(punt_ingles) DESC` |
| **Q6** | ¿Hay diferencias significativas entre zona urbana y rural? | `GROUP BY cole_area_ubicacion` |
| **Q7** | ¿Influye el acceso a internet y computador en el puntaje? | `GROUP BY fami_tieneinternet, fami_tienecomputador` |
| **Q8** | ¿Cuál es la completitud y porcentaje de nulos por columna? | `SUM(CASE WHEN col IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*)` |

---

## 4. Benchmark Comparativo de Motores SQL

El análisis detallado con métricas de latencia, arquitectura, modelo de costos en AWS y recomendaciones técnicas se encuentra en:
👉 **[BENCHMARK_COMPARATIVO.md](file:///C:/Users/JerF/.gemini/antigravity/scratch/proyecto3/06-consultas-sql/BENCHMARK_COMPARATIVO.md)**

### Resumen de Tiempos Promedio por Consulta:
- **Apache SparkSQL:** `0.26 segundos` *(Más rápido en cómputo analítico en memoria)*
- **Amazon Athena:** `1.10 segundos` *(Más eficiente en costo/agilidad para BI sin servidores)*
- **Apache Hive (EMR):** `17.80 segundos` *(Diseñado para procesamiento batch pesado)*

---

## 5. Evidencias
- `evidencias/06_athena_query_results.txt`: Resultados y métricas de ejecución en Athena.
- `evidencias/06_sparksql_query_results.txt`: Resultados y métricas de ejecución en SparkSQL.
- `06-consultas-sql/BENCHMARK_COMPARATIVO.md`: Documento comparativo completo para la sustentación.
