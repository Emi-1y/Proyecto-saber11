# 05 - Catalogación: AWS Glue Data Catalog & Apache Hive

## 1. Objetivo
Registrar los metadatos y esquemas de los datos almacenados en S3 (zona `raw/` y zona `trusted/`) en el **AWS Glue Data Catalog**, así como definir las tablas externas en el metastore de **Apache Hive en Amazon EMR**, permitiendo la interoperabilidad SQL sin mover físicamente los archivos.

---

## 2. Requisitos Previos
- Datos transformados en `s3://.../trusted/` en formato Parquet.
- Rol IAM `LabRole` para Glue Crawler.
- Acceso a Glue Data Catalog y/o cluster EMR en ejecución.

---

## 3. Comandos Exactos Numerados

### Paso 1: Crear la base de datos en AWS Glue Data Catalog
```bash
aws glue create-database \
    --database-input '{"Name": "saber11_catalog", "Description": "Catálogo de datos pruebas Saber 11 ICFES"}' \
    --region us-east-1
```

### Paso 2: Crear y ejecutar el Glue Crawler para la zona Trusted
```bash
aws glue create-crawler \
    --name saber11-trusted-crawler \
    --role LabRole \
    --database-name saber11_catalog \
    --targets '{"S3Targets": [{"Path": "s3://saber11-datalake-TUNOMBRE/trusted/saber11_unified/"}]}' \
    --region us-east-1

# Iniciar el Crawler
aws glue start-crawler --name saber11-trusted-crawler --region us-east-1
```

### Paso 3: Monitorear el Crawler hasta que finalice
```bash
aws glue get-crawler --name saber11-trusted-crawler --query 'Crawler.State' --output text --region us-east-1
```

### Paso 4: DDL manual alternativo en Hive / Athena
En caso de requerir registro DDL explícito mediante HiveQL o Athena:
```sql
-- Ejecutar en Hive CLI (EMR) o Athena
CREATE EXTERNAL TABLE IF NOT EXISTS saber11_catalog.saber11_trusted (
    estu_consecutivo STRING,
    estu_genero STRING,
    estu_fechanacimiento DATE,
    estu_depto_reside STRING,
    estu_mcpio_reside STRING,
    fami_estratovivienda STRING,
    fami_educacionpadre STRING,
    fami_educacionmadre STRING,
    fami_tieneinternet STRING,
    fami_tienecomputador STRING,
    cole_cod_dane_establecimiento BIGINT,
    cole_nombre_establecimiento STRING,
    cole_naturaleza STRING,
    cole_calendario STRING,
    cole_area_ubicacion STRING,
    cole_jornada STRING,
    cole_depto_ubicacion STRING,
    cole_mcpio_ubicacion STRING,
    punt_lectura_critica INT,
    punt_matematicas INT,
    punt_c_naturales INT,
    punt_sociales_ciudadanas INT,
    punt_ingles INT,
    desemp_ingles STRING,
    punt_global INT,
    percentil_global INT
)
PARTITIONED BY (periodo INT)
STORED AS PARQUET
LOCATION 's3://saber11-datalake-TUNOMBRE/trusted/saber11_unified/';

MSCK REPAIR TABLE saber11_catalog.saber11_trusted;
```

---

## 4. Resultado Esperado
- Base de datos `saber11_catalog` visible en AWS Glue Console.
- Tabla `saber11_unified` o `saber11_trusted` reconocida con todas sus columnas tipificadas y las particiones (`periodo=...`) descubiertas automáticamente.

---

## 5. Evidencias (Pantallazos)
<!-- Adjuntar capturas en ../evidencias/ -->
- `evidencias/05_glue_database_tables.png`: Consola de AWS Glue Data Catalog mostrando las tablas creadas.
- `evidencias/05_glue_crawler_success.png`: Historial del Crawler completado con las tablas y particiones añadidas.
