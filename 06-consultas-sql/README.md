# 06 - Consultas Analíticas con SQL (Athena, EMR/Hive y SparkSQL)

## 1. Objetivo
Ejecutar consultas analíticas estructuradas para responder a las preguntas de negocio definidas en la Fase 1, comparando la ejecución entre tres motores SQL sobre el Data Lake:
1. **Amazon Athena** (Serverless Presto/Trino sobre Glue Data Catalog).
2. **Apache Hive en Amazon EMR** (MapReduce / Tez sobre metastore).
3. **SparkSQL** (Motor distribuido en memoria).

---

## 2. Requisitos Previos
- Tabla `saber11_trusted` catalogada en Glue / Hive.
- Bucket de resultados de Athena configurado: `s3://saber11-datalake-TUNOMBRE/athena-query-results/`.
- Cluster EMR (opcional, cuando se ejecuten las pruebas en Hive).

---

## 3. Comandos Exactos Numerados

### Paso 1: Configurar ubicación de resultados en Athena
```bash
aws athena update-work-group \
    --work-group primary \
    --configuration-updates "ResultConfigurationUpdates={OutputLocation=s3://saber11-datalake-TUNOMBRE/athena-query-results/}" \
    --region us-east-1
```

### Paso 2: Ejecutar las consultas en Athena mediante script o AWS CLI
```bash
python 06-consultas-sql/scripts/ejecutar_consultas_athena.py
```

### Paso 3: Consultas de Negocio Principales (SQL)

#### Consulta 1: Ranking Departamental por Puntaje Global Promedio
```sql
SELECT 
    cole_depto_ubicacion AS departamento,
    COUNT(*) AS total_evaluados,
    ROUND(AVG(punt_global), 2) AS promedio_global,
    ROUND(STDDEV(punt_global), 2) AS desv_global,
    MAX(punt_global) AS max_global,
    MIN(punt_global) AS min_global
FROM saber11_catalog.saber11_trusted
GROUP BY cole_depto_ubicacion
ORDER BY promedio_global DESC;
```

#### Consulta 2: Brecha entre Colegios Oficiales y No Oficiales
```sql
SELECT 
    periodo,
    cole_naturaleza,
    COUNT(*) AS total_estudiantes,
    ROUND(AVG(punt_global), 2) AS promedio_global,
    ROUND(AVG(punt_matematicas), 2) AS promedio_matematicas,
    ROUND(AVG(punt_lectura_critica), 2) AS promedio_lectura,
    ROUND(AVG(punt_ingles), 2) AS promedio_ingles
FROM saber11_catalog.saber11_trusted
GROUP BY periodo, cole_naturaleza
ORDER BY periodo, cole_naturaleza;
```

#### Consulta 3: Impacto Socioeconómico (Estrato vs. Matemáticas)
```sql
SELECT 
    fami_estratovivienda AS estrato,
    COUNT(*) AS total_estudiantes,
    ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
    ROUND(AVG(punt_global), 2) AS prom_global
FROM saber11_catalog.saber11_trusted
WHERE fami_estratovivienda IS NOT NULL AND fami_estratovivienda != 'NO_REPORTADO'
GROUP BY fami_estratovivienda
ORDER BY prom_global DESC;
```

#### Consulta 4: Brecha Digital (Computador e Internet)
```sql
SELECT 
    fami_tieneinternet AS tiene_internet,
    fami_tienecomputador AS tiene_computador,
    COUNT(*) AS total,
    ROUND(AVG(punt_global), 2) AS prom_global,
    ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura
FROM saber11_catalog.saber11_trusted
GROUP BY fami_tieneinternet, fami_tienecomputador
ORDER BY prom_global DESC;
```

---

## 4. Resultado Esperado
- Tablas de resultados en formato tabular exportables a CSV/JSON.
- Verificación del tiempo de respuesta y bytes escaneados en Amazon Athena.

---

## 5. Evidencias (Pantallazos)
<!-- Adjuntar capturas en ../evidencias/ -->
- `evidencias/06_athena_ranking_departamental.png`: Editor de Athena mostrando el resultado del ranking departamental.
- `evidencias/06_athena_brecha_oficial.png`: Resultado SQL de la brecha público vs privado.
- `evidencias/06_hive_emr_query.png`: Consola de Hive en EMR ejecutando la consulta descriptiva.
