# Evidencias de Ejecución del Proyecto

En este directorio se almacenan los pantallazos, extractos de terminal y logs que certifican la ejecución y el cumplimiento de cada uno de los 8 requerimientos del Data Lake en AWS.

## Convención de Nombres de Archivos
- `01_...`: Caso de estudio, validación del dataset y diccionario de datos.
- `02_...`: Configuración de fuentes (RDS MariaDB, EC2, API).
- `03_...`: Ingestión automática hacia S3 Raw.
- `04_...`: Ejecución exitosa del Glue Job / Spark ETL hacia S3 Trusted.
- `05_...`: Catalogación en AWS Glue Data Catalog y tablas Hive.
- `06_...`: Consultas analíticas ejecutadas en Athena y EMR Hive.
- `07_...`: Pipeline de analítica descriptiva avanzada en PySpark.
- `08_...`: Dashboard en Streamlit y endpoint en API Gateway.

## Índice de Evidencias

| ID | Fase | Archivo | Descripción |
| :--- | :--- | :--- | :--- |
| 01 | Caso de estudio | `01_socrata_dataset_verified.png` | Verificación del dataset `kgxf-xxbe` en datos.gov.co. |
| 02.1 | Fuentes de datos | `02_rds_mariadb_status.png` | Instancia RDS en estado `Available`. |
| 02.2 | Fuentes de datos | `02_rds_query_dbeaver.png` | Consulta SELECT a las tablas maestras en MariaDB. |
| 02.3 | Fuentes de datos | `02_ec2_files_ls.png` | Listado de archivos CSV en la instancia EC2. |
| 03.1 | Ingesta | `03_s3_raw_bucket_console.png` | Consola de S3 con la estructura particionada de `raw/`. |
| 03.2 | Ingesta | `03_ingesta_terminal_output.png` | Log de ejecución del script de ingesta. |
| 04.1 | ETL Glue | `04_glue_job_success.png` | Job Run de AWS Glue en estado `SUCCEEDED`. |
| 04.2 | ETL Glue | `04_s3_trusted_parquet_partitions.png` | Particiones Parquet creadas en `s3://.../trusted/`. |
| 05.1 | Catálogo | `05_glue_database_tables.png` | Tablas registradas en el AWS Glue Data Catalog. |
| 05.2 | Catálogo | `05_glue_crawler_success.png` | Historial del Crawler completado con particiones añadidas. |
| 06.1 | SQL | `06_athena_ranking_departamental.png` | Consulta y visualización del ranking en Athena. |
| 06.2 | SQL | `06_athena_brecha_oficial.png` | Consulta de brecha pública vs privada en Athena. |
| 07.1 | PySpark | `07_pyspark_local_run.png` | Salida en terminal del análisis univariado y correlaciones. |
| 07.2 | PySpark | `07_s3_refined_partitions.png` | Datasets refinados guardados en S3 Refined. |
| 08.1 | Visualización | `08_streamlit_dashboard_main.png` | Dashboard principal en Streamlit. |
| 08.2 | Visualización | `08_api_gateway_route_console.png` | Ruta y proxy configurados en API Gateway. |
| 08.3 | Visualización | `08_app_accessible_browser.png` | App cargada exitosamente vía API Gateway URL. |
