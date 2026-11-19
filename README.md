# Pipeline End-to-End de Big Data en AWS: Resultados Pruebas Saber 11 (ICFES)

Este proyecto implementa una arquitectura completa de **Data Lakehouse en Amazon Web Services (AWS)** para procesar, limpiar, catalogar, consultar y visualizar los microdatos históricos de los **Resultados de las pruebas de Estado Saber 11 (ICFES)** en Colombia.

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
- **Prefijo de Recursos:** `saber11-` (ej. `saber11-datalake-xyz`, `saber11-mariadb`).
- **Particionado en Data Lake:**
  - `raw/`: particionado por fecha de ingesta (`ingest_date=YYYY-MM-DD`).
  - `trusted/` & `refined/`: particionado por periodo académico (`periodo=YYYYN`) en formato columnar **Apache Parquet (Snappy)**.

---

## 2. Estructura del Repositorio

El repositorio se divide en módulos correspondientes a cada uno de los 8 requerimientos del proyecto:

| Directorio | Tema | Descripción |
| :--- | :--- | :--- |
| [`01-caso-estudio/`](01-caso-estudio/) | Caso de estudio | Diccionario de datos (`kgxf-xxbe`), preguntas de negocio refinadas y dataset DIVIPOLA (`gdxc-w37w`). |
| [`02-fuentes-datos/`](02-fuentes-datos/) | Fuentes de datos | DDL de RDS MariaDB, scripts de despliegue en EC2 y conector para la API de Socrata. |
| [`03-ingesta/`](03-ingesta/) | Ingesta hacia S3 | Pipelines de extracción automática hacia la zona `s3://.../raw/`. |
| [`04-procesamiento-glue-spark/`](04-procesamiento-glue-spark/) | Procesamiento ETL | Jobs de AWS Glue y Apache Spark para transformar de Raw a Trusted (Bronze a Silver). |
| [`05-catalogacion/`](05-catalogacion/) | Metadatos y Catálogo | AWS Glue Crawlers y DDL de Apache Hive en EMR. |
| [`06-consultas-sql/`](06-consultas-sql/) | Analítica SQL | Consultas analíticas en Amazon Athena, Hive en EMR y SparkSQL. |
| [`07-pyspark/`](07-pyspark/) | Analítica con PySpark | Scripts de agregación, correlaciones y modelos descriptivos con PySpark. |
| [`08-visualizacion-api/`](08-visualizacion-api/) | Visualización & API | Dashboards en Streamlit y publicación del servicio vía Amazon API Gateway. |
| [`evidencias/`](evidencias/) | Evidencias y Auditoría | Capturas de pantalla, logs de ejecución y verificación de cada fase. |

---

## 3. Preguntas de Negocio Abordadas

1. **Ranking Departamental:** ¿Cuál es el ranking de departamentos por puntaje global promedio?
2. **Brecha Oficial vs. No Oficial:** ¿Cuál es la brecha de puntajes entre colegios públicos y privados?
3. **Influencia Socioeconómica:** ¿Cómo se relacionan el estrato y el nivel educativo parental con el desempeño en Matemáticas?
4. **Evolución Temporal:** ¿Cómo han variado los promedios por área disciplinar a lo largo de los años?
5. **Municipios Destacados en Inglés:** ¿Cuáles son los municipios con mejores y peores desempeños en inglés y niveles MCER (B1/B+)?
6. **Brecha Urbano vs. Rural:** ¿Qué disparidades existen en el rendimiento de acuerdo a la ubicación del colegio?
7. **Acceso a TIC (Brecha Digital):** ¿Cómo impacta la tenencia simultánea de computador e internet en el puntaje global?
8. **Métricas de Calidad de Datos:** ¿Cuál es el porcentaje de valores nulos o incompletos por variable en el Data Lake?

---

## 4. Guía Rápida de Reproducibilidad Local

### Paso 1: Clonar y configurar el entorno
```bash
git clone https://github.com/Emi-1y/Proyecto-saber11.git
cd proyecto3-saber11-aws

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

## 5. Control de Costos y Buenas Prácticas en AWS
- **AWS Academy / LabRole:** En entornos académicos con roles prefijados, todas las políticas de Glue, EMR y Lambda deben ejecutarse asociadas al rol `LabRole`.
- **Apagado de Recursos:** Los clusters de Amazon EMR y las instancias EC2 deben detenerse o terminarse una vez finalizada la sesión de trabajo para evitar el consumo de créditos.
- **Desarrollo Iterativo:** Todos los scripts se prueban inicialmente en local con una **muestra representativa (10k a 100k filas)** antes de disparar jobs sobre el histórico completo (> 7M registros).
