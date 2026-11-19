# 05 - Catalogación: AWS Glue Data Catalog & Apache Hive en Amazon EMR

## 1. Objetivo
Registrar los esquemas, metadatos y particiones de los datos depositados en S3 (zona `trusted/`) tanto en el **AWS Glue Data Catalog** como en el metastore de **Apache Hive sobre Amazon EMR**. Esto permite consultar los datos mediante SQL desacoplado (Athena, Hive en EMR, SparkSQL) sin mover ni duplicar físicamente los archivos Parquet en el Data Lake.

---

## 2. Arquitectura de Catalogación

```
                     ┌──────────────────────────────────────────────┐
                     │   S3 Trusted Data Lake (Formato Parquet)    │
                     │  s3://.../trusted/saber11_unified/periodo=*/ │
                     └──────────────────────┬───────────────────────┘
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     │                                             │
                     ▼                                             ▼
       ┌───────────────────────────┐                 ┌───────────────────────────┐
       │   AWS Glue Data Catalog   │                 │   Apache Hive Metastore   │
       │    (Servicio Serverless)  │                 │    (Amazon EMR Clúster)   │
       ├───────────────────────────┤                 ├───────────────────────────┤
       │ - Crawler automático      │                 │ - Hive DDL (HQL)          │
       │ - Inferencia de esquema   │                 │ - MSCK REPAIR TABLE       │
       │ - Consulta vía Athena     │                 │ - Ejecución Tez / MapRed  │
       └───────────────────────────┘                 └───────────────────────────┘
```

---

## 3. Implementación 1: AWS Glue Data Catalog (Serverless Crawler)

### Paso 1: Crear la Base de Datos en el Catálogo
```bash
aws glue create-database \
    --database-input '{"Name": "saber11_catalog", "Description": "Catalogo unificado Saber 11 ICFES"}' \
    --region us-east-1
```

### Paso 2: Crear y Ejecutar el Crawler de la Zona Trusted
```bash
aws glue create-crawler \
    --name saber11-trusted-crawler \
    --role LabRole \
    --database-name saber11_catalog \
    --targets '{"S3Targets": [{"Path": "s3://saber11-datalake-885601272401/trusted/saber11_unified/"}]}' \
    --region us-east-1

aws glue start-crawler --name saber11-trusted-crawler --region us-east-1
```

---

## 4. Implementación 2: Apache Hive sobre Amazon EMR

En el entorno de Big Data corporativo y académico, **Apache Hive** permite definir tablas externas basadas en HDFS o S3.

### Paso 1: El Script HQL (`05-catalogacion/hive/01_create_trusted_table.hql`)
Define la tabla externa Parquet con partición `periodo` y repara particiones con `MSCK REPAIR TABLE`:
```sql
CREATE DATABASE IF NOT EXISTS saber11_catalog
  LOCATION 's3://saber11-datalake-885601272401/trusted/';

USE saber11_catalog;

CREATE EXTERNAL TABLE IF NOT EXISTS saber11_catalog.saber11_unified (
    estu_consecutivo STRING,
    estu_genero STRING,
    estu_fechanacimiento STRING,
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
    cole_cod_mcpio_ubicacion STRING,
    cole_mcpio_ubicacion STRING,
    cole_cod_depto_ubicacion STRING,
    cole_depto_ubicacion STRING,
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
LOCATION 's3://saber11-datalake-885601272401/trusted/saber11_unified/'
TBLPROPERTIES ('parquet.compression' = 'SNAPPY');

MSCK REPAIR TABLE saber11_catalog.saber11_unified;
```

### Paso 2: Ejecución del Step de Hive en Amazon EMR (`05-catalogacion/emr/run_hive_emr_step.sh`)
Para clústeres EMR existentes o transitorios, se envía como un **Step** desatendido utilizando `LabRole`:
```bash
bash 05-catalogacion/emr/run_hive_emr_step.sh j-CLUSTERID saber11-datalake-885601272401
```

### Paso 3: Clúster EMR Transitorio Auto-terminable (`05-catalogacion/emr/crear_cluster_emr_transient.sh`)
Para optimizar el presupuesto en AWS Academy Learner Lab, el script lanza un nodo transitorio que aplica el DDL en Hive, repara los metadatos y se autodestruye al terminar:
```bash
bash 05-catalogacion/emr/crear_cluster_emr_transient.sh saber11-datalake-885601272401
```

---

## 5. Resultado Esperado y Verificación
- **Glue Console:** Base de datos `saber11_catalog` con tabla `saber11_unified` y 5 particiones activas (`periodo=20194, 20204, 20214, 20224, 20234`).
- **Hive / EMR:** Tabla externa `saber11_unified` disponible para consultas en Hive CLI o Beeline apuntando directamente al storage S3.
- Compatibilidad directa con Athena y SparkSQL a través del metastore compartido.

---

## 6. Evidencias
- `evidencias/05_glue_database_tables.png`: Base de datos y metadatos de tabla en la consola de AWS Glue.
- `evidencias/05_glue_crawler_success.png`: Historial del Crawler con estado `SUCCEEDED` y particiones añadidas.
- `05-catalogacion/hive/01_create_trusted_table.hql`: Script DDL HQL completo.
- `05-catalogacion/emr/run_hive_emr_step.sh`: Automatización del Step de Hive en EMR.
