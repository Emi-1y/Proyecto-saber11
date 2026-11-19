# 07 - Analítica Descriptiva Avanzada con PySpark

## 1. Objetivo
Desarrollar análisis descriptivos avanzados, distribuciones estadísticas, matrices de correlación y agregaciones complejas sobre el Data Lake en S3 utilizando **Apache Spark (PySpark)**, tanto en entorno local (muestra) como en cluster EMR / Glue Interactive Sessions.

---

## 2. Requisitos Previos
- Java 17 instalado en el sistema (`java -version`).
- Librería `pyspark` instalada en el entorno virtual.
- Acceso a los archivos Parquet en S3 Trusted o réplica local para depuración.

---

## 3. Comandos Exactos Numerados

### Paso 1: Ejecutar el script analítico principal en PySpark
```bash
python 07-pyspark/scripts/analisis_descriptivo_spark.py \
    --input-path s3://saber11-datalake-TUNOMBRE/trusted/saber11_unified/ \
    --output-path s3://saber11-datalake-TUNOMBRE/refined/analisis_resumen/
```

### Paso 2: Análisis ejecutados en el pipeline de PySpark
El script realiza automáticamente:
1. **Estadísticas univariadas:** Media, mediana, desviación estándar, percentiles 25, 50 y 75 por componente evaluado.
2. **Matriz de correlación de Pearson:** Cruce entre puntajes de las 5 áreas y puntaje global.
3. **Análisis de brecha por cuartiles socioeconómicos:** Agrupación por nivel educativo de los padres vs puntajes por área.
4. **Ranking y dispersión por municipios:** Cálculo de varianza intraterritorial.

### Paso 3: Exportar dataset refinado (Gold/Refined)
Los DataFrames refinados agregados se guardan en `s3://.../refined/` en formato Parquet para consumo ultrarrápido desde la aplicación web Streamlit y dashboards.

---

## 4. Resultado Esperado
- Tablas consolidadas generadas en la capa `refined/`:
  - `refined/resumen_departamental/`
  - `refined/correlaciones_areas/`
  - `refined/brecha_digital_resumen/`
- Reporte estadístico impreso en la terminal y guardado en log.

---

## 5. Evidencias (Pantallazos)
<!-- Adjuntar capturas en ../evidencias/ -->
- `evidencias/07_pyspark_local_run.png`: Salida en terminal de la ejecución de PySpark mostrando la matriz de correlación.
- `evidencias/07_s3_refined_partitions.png`: Particiones de la zona Refined generadas en S3.
