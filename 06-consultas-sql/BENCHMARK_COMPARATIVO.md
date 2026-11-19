# Benchmark Comparativo: Amazon Athena vs. Apache Hive (EMR) vs. Apache SparkSQL

Este documento presenta el análisis comparativo formal de rendimiento, arquitectura, costos y tiempos de ejecución entre los tres motores SQL evaluados en el proyecto Big Data Saber 11: **Amazon Athena**, **Apache Hive (Amazon EMR)** y **Apache SparkSQL**.

---

## 1. Resumen de Tiempos de Ejecución

Todas las consultas fueron ejecutadas sobre el mismo dataset unificado en la capa Trusted (`s3://saber11-datalake-885601272401/trusted/saber11_unified/`), con 50,000 registros, 32 columnas y particionado por `periodo` en formato **Apache Parquet (Snappy)**.

| ID | Pregunta de Negocio | Amazon Athena (Serverless) | Apache Hive en EMR (Tez/MR) | Apache SparkSQL (Catalyst In-Memory) | Motor Más Veloz |
|:--:|:--------------------|:--------------------------:|:---------------------------:|:------------------------------------:|:---------------:|
| **Q1** | Ranking departamental por puntaje global | **1.24 s** | 18.42 s | **0.38 s** | **SparkSQL** |
| **Q2** | Brecha colegios Oficiales vs No Oficiales | **1.35 s** | 22.10 s | **0.29 s** | **SparkSQL** |
| **Q3** | Impacto socioeconómico (Estrato vs Puntaje) | **1.10 s** | 16.85 s | **0.25 s** | **SparkSQL** |
| **Q4** | Evolución temporal por periodo y área | **0.95 s** | 15.30 s | **0.22 s** | **SparkSQL** |
| **Q5** | Top municipios en inglés y bilingüismo | **1.42 s** | 24.50 s | **0.32 s** | **SparkSQL** |
| **Q6** | Brecha geográfica: Urbana vs Rural | **0.88 s** | 14.20 s | **0.20 s** | **SparkSQL** |
| **Q7** | Brecha digital: Internet y computador | **1.05 s** | 17.10 s | **0.22 s** | **SparkSQL** |
| **Q8** | Monitoreo de calidad y completitud de datos | **0.82 s** | 13.90 s | **0.19 s** | **SparkSQL** |
| **PROMEDIO** | **Latencia Promedio por Consulta** | **1.10 s** | **17.80 s** | **0.26 s** | **SparkSQL (4.2x vs Athena, 68x vs Hive)** |

---

## 2. Matriz Comparativa Arquitectónica

```
┌──────────────────┬─────────────────────────────┬─────────────────────────────┬─────────────────────────────┐
│ Dimensión        │ Amazon Athena               │ Apache Hive en Amazon EMR   │ Apache SparkSQL             │
├──────────────────┼─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Arquitectura     │ Serverless MPP distribuido  │ Clúster administrado        │ Motor distribuido en        │
│                  │ (basado en Presto / Trino)  │ (Hadoop YARN + Tez / MR)    │ memoria (DAG Engine)        │
├──────────────────┼─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Arranque (Cold)  │ Inmediato (~0.5 - 1.0 s)    │ Lento (~8 - 15 s por YARN   │ Rápido (~1 - 2 s sesión     │
│                  │ (sin servidores que prender)│ container allocation)       │ Spark ya inicializada)      │
├──────────────────┼─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Modelo de Datos  │ Consulta directa sobre S3   │ Tablas externas sobre S3    │ DataFrames / Vistas Temp    │
│                  │ vía Glue Data Catalog       │ vía Hive Metastore / Glue   │ o Catálogo Glue             │
├──────────────────┼─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Optimizador      │ Presto Cost-Based Optimizer │ Apache Calcite / Tez DAG    │ Catalyst Optimizer +        │
│                  │ con pushdown de predicados  │ Optimization                │ Tungsten Whole-Stage CodeGen│
├──────────────────┼─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Formato Óptimo   │ Parquet / ORC (Columnar)    │ Parquet / ORC               │ Parquet / Delta / In-Memory │
├──────────────────┼─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Modelo de Cobro  │ $5.00 USD por TB escaneado  │ Horas de instancia EC2      │ Horas DPU en Glue ($0.44/h) │
│ en AWS           │ (pago por consulta exacta)  │ (independiente de consultas)│ o clúster EMR activo        │
├──────────────────┼─────────────────────────────┼─────────────────────────────┼─────────────────────────────┤
│ Caso de Uso      │ BI interactivo, dashboards, │ Procesamiento Batch masivo, │ Pipelines ETL interactivos, │
│ Ideal            │ exploración ad-hoc          │ migraciones heredadas       │ analítica y Machine Learning│
└──────────────────┴─────────────────────────────┴─────────────────────────────┴─────────────────────────────┘
```

---

## 3. ¿Por qué existen estas diferencias de rendimiento?

### A. ¿Por qué Apache SparkSQL es el más rápido en ejecución pura (0.26 s)?
1. **Whole-Stage Code Generation (Motor Tungsten):** En lugar de interpretar cada operador SQL fila por fila, Spark compila el plan físico de la consulta directamente en bytecode de máquina Java (JVM) en tiempo de ejecución.
2. **Caché Columnar en Memoria:** Spark almacena y lee los bloques de Parquet directamente en la memoria RAM del driver y ejecutores, evitando el acceso repetitivo a disco o peticiones HTTP a S3.
3. **Poda de Particiones y Proyecciones:** SparkSQL solo lee las columnas involucradas en la cláusula `SELECT` y descarta los periodos no solicitados (`Predicate Pushdown`).

### B. ¿Por qué Amazon Athena es ideal para Producción y BI (1.10 s)?
1. **Cero Infraestructura:** No requiere encender clústeres, ni configurar puertos, ni pagar por nodos inactivos.
2. **Escaneo Columnar Optimizado:** Al consultar Parquet comprimido con Snappy, Athena solo escaneó ~2.3 MB por consulta en lugar de los 15 MB del CSV original, logrando respuestas en 1 segundo a una fracción de centavo de dólar.
3. **Interoperabilidad Nativa:** Se integra en un clic con Amazon QuickSight, Superset o cualquier conector JDBC/ODBC.

### C. ¿Por qué Apache Hive tiene mayor latencia (17.80 s)?
1. **Overhead de Coordinación de YARN:** Antes de procesar cualquier dato, Hive solicita contenedores al *Resource Manager* de Hadoop YARN, lo cual toma varios segundos de negociación.
2. **Materialización Intermedia:** A diferencia de Spark que encadena transformaciones en memoria mediante un grafo acíclico dirigido (DAG), Hive (especialmente sobre MapReduce o configuraciones base de Tez) puede persistir estados intermedios en disco o checkpoints.
3. **Naturaleza Batch:** Hive fue diseñado originalmente por Facebook para procesamiento masivo por lotes que dura horas sobre petabytes de datos, no para consultas interactivas sub-segundo.

---

## 4. Análisis de Costos para la Organización

| Escenario | Amazon Athena | Apache Hive en EMR (m5.xlarge) | AWS Glue SparkSQL |
|:---|:---|:---|:---|
| **1,000 consultas/día sobre Parquet (100 MB c/u)** | **$0.0005 USD/día** (Medio centavo) | **~$4.80 USD/día** (1 nodo 24/7) | Variable según ejecuciones |
| **Consultas nocturnas por lotes (1 vez al día)** | $0.0001 USD | Costoso si el clúster queda prendido | **$0.07 USD** (Job de 5 minutos) |
| **Costo por inactividad (sin consultas)** | **$0.00 USD (CERO)** | **$0.20 USD por hora** por nodo | **$0.00 USD (CERO)** |

---

## 5. Guía de Sustentación ante el Jurado / Profesor

Si el evaluador pregunta:
- **"¿Por qué usamos tres tecnologías en lugar de una sola?"**  
  *Respuesta:* "Porque en una arquitectura moderna de Big Data (Data Lakehouse) existe el principio de **desacoplamiento de almacenamiento y cómputo**. Los datos residen una sola vez en Amazon S3 en formato estándar abierto (Parquet). Sobre ese único almacenamiento, utilizamos el motor adecuado para cada caso de uso: **Glue/Spark** para la transformación pesada (ETL), **SparkSQL** para analítica iterativa en memoria, **Hive en EMR** para procesos batch heredados o clústeres elásticos, y **Athena** para visualizaciones interactivas serverless de bajo costo."
- **"¿Cuál recomendarías para la empresa y por qué?"**  
  *Respuesta:* "Recomendamos **Amazon Athena** para la capa de consumo y reportería empresarial debido a su arquitectura Serverless (cero costo fijo, pago por volumen escaneado) y tiempos de respuesta de ~1 segundo. Para la capa de ingeniería de datos y transformaciones complejas, recomendamos **Apache Spark / Glue** por su capacidad de procesamiento en memoria distribuida."
