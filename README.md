# Pipeline End-to-End de Big Data en AWS: Resultados Pruebas Saber 11 (ICFES)

[![AWS Region](https://img.shields.io/badge/AWS%20Region-us--east--1-orange.svg)](https://aws.amazon.com/)
[![Storage](https://img.shields.io/badge/Storage-S3%20(Raw%2FTrusted%2FRefined)-blue.svg)](https://aws.amazon.com/s3/)
[![Processing](https://img.shields.io/badge/Engine-AWS%20Glue%20%7C%20Apache%20Spark-red.svg)](https://aws.amazon.com/glue/)
[![Catalog](https://img.shields.io/badge/Catalog-Glue%20Data%20Catalog%20%7C%20Hive-yellow.svg)](https://aws.amazon.com/glue/)
[![Analytics](https://img.shields.io/badge/Analytics-Athena%20%7C%20EMR%20%7C%20SparkSQL%20%7C%20PySpark-green.svg)](https://aws.amazon.com/athena/)
[![App](https://img.shields.io/badge/Frontend-Streamlit%20%2B%20API%20Gateway-FF4B4B.svg)](https://streamlit.io/)

Este proyecto implementa una arquitectura completa de **Data Lakehouse en Amazon Web Services (AWS)** para procesar, limpiar, catalogar, consultar con SQL y Spark, y visualizar los microdatos históricos de los **Resultados de las pruebas de Estado Saber 11 (ICFES)** en Colombia.

---

## 1. Arquitectura de la Solución

```
RDS MariaDB  ─┐
Archivos EC2 ─┼─► Ingesta automática ─► S3 raw/ ─► Glue+Spark ─► S3 trusted/ ─► S3 refined/
URL / API    ─┘  (cron / Lambda / Glue)                              │
                                                  Glue Data Catalog / Hive
                                                                      │
                                        Athena · Hive (EMR) · SparkSQL · PySpark
                                                                      │
                                          Gráficas + Streamlit (EC2) ─► API Gateway
```

### Convenciones Globales
- **Región AWS:** `us-east-1` (N. Virginia).
- **Prefijo de Recursos:** `saber11-` (ej. `saber11-datalake-885601272401`, `saber11-mariadb`).
- **Particionado en Data Lake:**
  - `raw/`: particionado por fecha de ingesta (`ingest_date=YYYY-MM-DD`).
  - `trusted/` & `refined/`: particionado por periodo académico (`periodo=YYYYN`) en formato columnar **Apache Parquet (Snappy)**.

---

## 2. Ingesta Automática y Orquestación (Punto 3)

El pipeline cuenta con procesos automáticos desatendidos para la extracción periódica:
1. **EC2 Crontab (`03-ingesta/scripts/configurar_cron_ec2.sh`):** Tarea programada en Linux que sincroniza diariamente a las 02:00 AM los archivos CSV hacia `s3://.../raw/fuente=ec2/ingest_date=YYYY-MM-DD/`.
2. **Amazon EventBridge + AWS Lambda (`03-ingesta/lambda/lambda_ingesta_function.py`):** Regla programada (`cron(0 3 * * ? *)`) que extrae automáticamente nuevos registros desde la API Socrata de `datos.gov.co` y deposita el JSON en S3 Raw.
3. **AWS Glue Scheduled Trigger (`03-ingesta/scripts/configurar_eventbridge_glue.py`):** Disparador programado nativo que enciende el Job de Spark `saber11-raw-to-trusted` activando `job-bookmarks` para procesar incrementales.

---

## 3. Motores SQL y Benchmark Comparativo (Puntos 5 y 6)

Se implementaron y ejecutaron las 8 consultas de negocio en tres motores SQL diferentes sobre el mismo dataset en S3:
- **Amazon Athena:** Consultas interactivas serverless sobre el Glue Data Catalog.
- **Apache SparkSQL:** Ejecución en memoria con optimización Catalyst (`06-consultas-sql/scripts/ejecutar_consultas_sparksql.py`).
- **Apache Hive sobre Amazon EMR:** Definición HQL y ejecución distribuida mediante Steps (`05-catalogacion/emr/run_hive_emr_step.sh`).

👉 Para la sustentación técnica, consulte el análisis detallado de latencia y costos en:  
**[06-consultas-sql/BENCHMARK_COMPARATIVO.md](06-consultas-sql/BENCHMARK_COMPARATIVO.md)**

---

## 4. Estructura del Repositorio

El repositorio se divide en módulos correspondientes a cada uno de los 8 puntos requeridos:

| Directorio | Tema | Descripción |
| :--- | :--- | :--- |
| [`01-caso-estudio/`](01-caso-estudio/) | Caso de estudio | Diccionario de datos (`kgxf-xxbe`), preguntas de negocio, dataset DIVIPOLA (`gdxc-w37w`) y aclaraciones metodológicas. |
| [`02-fuentes-datos/`](02-fuentes-datos/) | Fuentes de datos | DDL de RDS MariaDB, scripts de despliegue en EC2 y conector para la API de Socrata. |
| [`03-ingesta/`](03-ingesta/) | Ingesta hacia S3 | Ingesta automática hacia la zona `s3://.../raw/` (Lambda, EventBridge, Cron EC2). |
| [`04-procesamiento-glue-spark/`](04-procesamiento-glue-spark/) | Procesamiento ETL | Jobs de AWS Glue y Apache Spark para transformar de Raw a Trusted (Bronze a Silver). |
| [`05-catalogacion/`](05-catalogacion/) | Metadatos y Catálogo | AWS Glue Crawlers, DDL de Apache Hive en EMR y scripts de ejecución por Steps. |
| [`06-consultas-sql/`](06-consultas-sql/) | Analítica SQL | Consultas en Athena, Hive (EMR) y SparkSQL con benchmark de tiempos y costos. |
| [`07-pyspark/`](07-pyspark/) | Analítica con PySpark | Scripts de agregación, correlaciones de Pearson y exportación a S3 Refined. |
| [`08-visualizacion-api/`](08-visualizacion-api/) | Visualización & API | Dashboards interactivos en Streamlit y proxy reverso con Amazon API Gateway. |
| [`evidencias/`](evidencias/) | Evidencias y Auditoría | Logs de ejecución, resultados de Athena/SparkSQL y capturas de consola. |

---

## 5. Preguntas de Negocio Abordadas

1. **Ranking Departamental:** ¿Cuál es el ranking de departamentos por puntaje global promedio?
2. **Brecha Oficial vs. No Oficial:** ¿Cuál es la brecha de puntajes entre colegios públicos y privados?
3. **Influencia Socioeconómica:** ¿Cómo se relacionan el estrato y el nivel educativo parental con el desempeño en Matemáticas?
4. **Evolución Temporal:** ¿Cómo han variado los promedios por área disciplinar a lo largo de los años?
5. **Municipios Destacados en Inglés:** ¿Cuáles son los municipios con mejores y peores desempeños en inglés y niveles MCER (B1/B+)?
6. **Brecha Urbano vs. Rural:** ¿Qué disparidades existen en el rendimiento de acuerdo a la ubicación del colegio?
7. **Acceso a TIC (Brecha Digital):** ¿Cómo impacta la tenencia simultánea de computador e internet en el puntaje global?
8. **Métricas de Calidad de Datos:** ¿Cuál es el porcentaje de valores nulos o incompletos por variable en el Data Lake?

---

## 6. Guía Rápida de Reproducibilidad Local

### Paso 1: Clonar y configurar el entorno
```bash
git clone https://github.com/Emi-1y/Proyecto-saber11.git
cd Proyecto-saber11

# Crear entorno virtual de Python
python -m venv venv

# En Windows:
.\venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar credenciales y variables de entorno
```bash
cp .env.example .env
# Edita .env con tus identificadores y credenciales de AWS
```

---

## 7. Aclaraciones Metodológicas y Conclusiones Técnicas

1. **Uso de Datos Sintéticos Controlados:** Para garantizar la viabilidad técnica y no agotar el presupuesto de **AWS Academy Learner Lab** descargando el histórico masivo de >7.2 millones de filas (>5 GB crudo), se generó un universo controlado de **50,000 registros** distribuido en 5 cohortes (2019 a 2023). Dicho dataset respeta estrictamente el esquema oficial de 51 columnas de `datos.gov.co` (`kgxf-xxbe`) y replica distribuciones estadísticas y brechas socioeconómicas reales.
2. **Corrección de Jerarquía Geográfica:** Con base en el estándar oficial DIVIPOLA del DANE, se aclara y certifica que el código DANE **`52`** corresponde al departamento de **NARIÑO**, mientras que **PASTO** es su municipio capital (código `52001`). Cualquier referencia previa en borradores que colocaba a Pasto a nivel de departamento fue corregida en la base de datos y scripts de transformación.
3. **Desacoplamiento Almacenamiento-Cómputo:** El uso del formato Parquet particionado en S3 permitió reducir los tiempos de consulta de decenas de segundos en bases relacionales a sub-segundo en Athena y SparkSQL, demostrando la eficiencia de una arquitectura Data Lakehouse.

---

## 8. Control de Costos y Buenas Prácticas en AWS Academy
- **LabRole:** En entornos educativos de AWS Academy, todos los servicios (Glue, Lambda, EMR, EC2) se ejecutan con el rol federado `LabRole` e `LabInstanceProfile`.
- **Apagado de Recursos:** Al finalizar la jornada o sustentación, se recomienda detener la base RDS y la instancia EC2:
  ```bash
  aws rds stop-db-instance --db-instance-identifier saber11-mariadb
  aws ec2 stop-instances --instance-ids i-0a3de8469efde1296
  ```
