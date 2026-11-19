-- ==============================================================================
-- DDL DE HIVE / ATHENA: TABLA EXTERNA EN S3 TRUSTED
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS saber11_catalog
  COMMENT 'Catalogo de datos pruebas Saber 11 ICFES'
  LOCATION 's3://saber11-datalake-885601272401/trusted/';

USE saber11_catalog;

CREATE EXTERNAL TABLE IF NOT EXISTS saber11_catalog.saber11_unified (
    estu_consecutivo STRING COMMENT 'Identificador anonimizado del evaluado',
    estu_tipodocumento STRING COMMENT 'Tipo de documento',
    estu_genero STRING COMMENT 'Genero del estudiante',
    estu_fechanacimiento STRING COMMENT 'Fecha nacimiento DD/MM/YYYY',
    fami_estratovivienda STRING COMMENT 'Estrato socioeconomico reportado',
    fami_educacionpadre STRING COMMENT 'Nivel educativo padre',
    fami_educacionmadre STRING COMMENT 'Nivel educativo madre',
    fami_tieneinternet STRING COMMENT 'Acceso a internet Si/No',
    fami_tienecomputador STRING COMMENT 'Acceso a computador Si/No',
    cole_cod_dane_establecimiento BIGINT COMMENT 'Codigo DANE colegio (12 digitos)',
    cole_codigo_icfes BIGINT COMMENT 'Codigo ICFES colegio',
    cole_nombre_establecimiento STRING COMMENT 'Nombre oficial institucion',
    cole_genero STRING COMMENT 'Genero colegio MIXTO/FEMENINO/MASCULINO',
    cole_naturaleza STRING COMMENT 'Naturaleza OFICIAL/NO OFICIAL',
    cole_calendario STRING COMMENT 'Calendario A/B/OTRO',
    cole_bilingue STRING COMMENT 'Bilingue S/N',
    cole_caracter STRING COMMENT 'Caracter academico/tecnico',
    cole_area_ubicacion STRING COMMENT 'Zona URBANO/RURAL',
    cole_jornada STRING COMMENT 'Jornada escolar',
    cole_cod_mcpio_ubicacion STRING COMMENT 'Codigo DANE municipio colegio',
    cole_mcpio_ubicacion STRING COMMENT 'Municipio colegio',
    cole_cod_depto_ubicacion STRING COMMENT 'Codigo DANE depto colegio',
    cole_depto_ubicacion STRING COMMENT 'Departamento colegio',
    punt_lectura_critica INT COMMENT 'Puntaje Lectura Critica (0-100)',
    punt_matematicas INT COMMENT 'Puntaje Matematicas (0-100)',
    punt_c_naturales INT COMMENT 'Puntaje Ciencias Naturales (0-100)',
    punt_sociales_ciudadanas INT COMMENT 'Puntaje Sociales y Ciudadanas (0-100)',
    punt_ingles INT COMMENT 'Puntaje Ingles (0-100)',
    desemp_ingles STRING COMMENT 'Nivel ingles A-, A1, A2, B1, B+',
    punt_global INT COMMENT 'Puntaje Global ICFES (0-500)',
    percentil_global INT COMMENT 'Percentil nacional global'
)
COMMENT 'Tabla unificada y limpia de resultados Saber 11'
PARTITIONED BY (periodo INT)
STORED AS PARQUET
LOCATION 's3://saber11-datalake-885601272401/trusted/saber11_unified/'
TBLPROPERTIES (
    'parquet.compression' = 'SNAPPY'
);

-- Reparar metadatos para descubrir particiones existentes en S3
MSCK REPAIR TABLE saber11_catalog.saber11_unified;
