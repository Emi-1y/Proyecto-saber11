-- ==============================================================================
-- 06 - CONSULTAS ANALÍTICAS SQL (ATHENA / HIVE / SPARKSQL)
-- ==============================================================================

-- 1. ¿Cuál es el ranking de departamentos por puntaje global promedio?
SELECT 
    cole_depto_ubicacion AS departamento,
    COUNT(*) AS total_estudiantes,
    ROUND(AVG(punt_global), 2) AS promedio_global,
    ROUND(STDDEV(punt_global), 2) AS desv_global,
    MAX(punt_global) AS max_global,
    MIN(punt_global) AS min_global
FROM saber11_catalog.saber11_unified
GROUP BY cole_depto_ubicacion
ORDER BY promedio_global DESC;

-- 2. ¿Cuál es la brecha de puntaje entre colegios oficiales y no oficiales?
SELECT 
    periodo,
    cole_naturaleza,
    COUNT(*) AS total_estudiantes,
    ROUND(AVG(punt_global), 2) AS promedio_global,
    ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
    ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
    ROUND(AVG(punt_c_naturales), 2) AS prom_ciencias,
    ROUND(AVG(punt_sociales_ciudadanas), 2) AS prom_sociales,
    ROUND(AVG(punt_ingles), 2) AS prom_ingles
FROM saber11_catalog.saber11_unified
GROUP BY periodo, cole_naturaleza
ORDER BY periodo ASC, cole_naturaleza ASC;

-- 3. ¿Cómo influye el estrato socioeconómico en el puntaje de matemáticas y global?
SELECT 
    fami_estratovivienda AS estrato,
    COUNT(*) AS total_evaluados,
    ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
    ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
    ROUND(AVG(punt_global), 2) AS prom_global
FROM saber11_catalog.saber11_unified
GROUP BY fami_estratovivienda
ORDER BY prom_global DESC;

-- 4. ¿Cómo evolucionó el puntaje promedio por año y por área?
SELECT 
    periodo,
    COUNT(*) AS total_evaluados,
    ROUND(AVG(punt_global), 2) AS prom_global,
    ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
    ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
    ROUND(AVG(punt_c_naturales), 2) AS prom_ciencias,
    ROUND(AVG(punt_sociales_ciudadanas), 2) AS prom_sociales,
    ROUND(AVG(punt_ingles), 2) AS prom_ingles
FROM saber11_catalog.saber11_unified
GROUP BY periodo
ORDER BY periodo ASC;

-- 5. ¿Qué municipios tienen los mejores y peores resultados en inglés (y niveles B1/B+)?
SELECT 
    cole_mcpio_ubicacion AS municipio,
    cole_depto_ubicacion AS departamento,
    COUNT(*) AS total_estudiantes,
    ROUND(AVG(punt_ingles), 2) AS prom_ingles,
    ROUND(SUM(CASE WHEN desemp_ingles IN ('B1', 'B+') THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_bilingue_b1_bmas
FROM saber11_catalog.saber11_unified
GROUP BY cole_mcpio_ubicacion, cole_depto_ubicacion
HAVING COUNT(*) >= 50
ORDER BY prom_ingles DESC;

-- 6. ¿Hay diferencias significativas entre zona urbana y rural?
SELECT 
    cole_area_ubicacion AS zona,
    COUNT(*) AS total_estudiantes,
    ROUND(AVG(punt_global), 2) AS prom_global,
    ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
    ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura,
    ROUND(AVG(punt_ingles), 2) AS prom_ingles
FROM saber11_catalog.saber11_unified
GROUP BY cole_area_ubicacion;

-- 7. ¿Influye el acceso a internet o computador en el puntaje global (Brecha Digital)?
SELECT 
    fami_tieneinternet AS tiene_internet,
    fami_tienecomputador AS tiene_computador,
    COUNT(*) AS total_evaluados,
    ROUND(AVG(punt_global), 2) AS prom_global,
    ROUND(AVG(punt_matematicas), 2) AS prom_matematicas,
    ROUND(AVG(punt_lectura_critica), 2) AS prom_lectura
FROM saber11_catalog.saber11_unified
GROUP BY fami_tieneinternet, fami_tienecomputador
ORDER BY prom_global DESC;

-- 8. Calidad de Datos: Porcentaje de completitud y faltantes por columna
SELECT 
    COUNT(*) AS total_filas,
    ROUND(SUM(CASE WHEN fami_estratovivienda IS NULL OR fami_estratovivienda = 'NO_REPORTADO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_estrato,
    ROUND(SUM(CASE WHEN fami_educacionpadre IS NULL OR fami_educacionpadre = 'NO_REPORTADO' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_educ_padre,
    ROUND(SUM(CASE WHEN fami_tieneinternet IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_internet,
    ROUND(SUM(CASE WHEN cole_cod_dane_establecimiento IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_nulos_colegio
FROM saber11_catalog.saber11_unified;
