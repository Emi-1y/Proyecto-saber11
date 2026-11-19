-- ==============================================================================
-- DDL DE INICIALIZACIÓN: ESQUEMA SABER11 EN RDS MARIADB
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS saber11_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE saber11_db;

-- 1. Tabla Maestra: Municipios y Departamentos (Normalizada)
CREATE TABLE IF NOT EXISTS dim_municipios (
    cod_municipio VARCHAR(10) PRIMARY KEY,
    nom_municipio VARCHAR(100) NOT NULL,
    cod_depto VARCHAR(5) NOT NULL,
    nom_depto VARCHAR(100) NOT NULL,
    INDEX idx_depto (cod_depto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Tabla Maestra: Colegios e Instituciones Educativas
CREATE TABLE IF NOT EXISTS dim_colegios (
    cole_cod_dane_establecimiento BIGINT PRIMARY KEY,
    cole_codigo_icfes BIGINT,
    cole_nombre_establecimiento VARCHAR(200) NOT NULL,
    cole_genero VARCHAR(20),
    cole_naturaleza VARCHAR(20) NOT NULL, -- OFICIAL / NO OFICIAL
    cole_calendario VARCHAR(10),           -- A / B / OTRO
    cole_bilingue VARCHAR(5),
    cole_caracter VARCHAR(50),
    cole_area_ubicacion VARCHAR(20),       -- URBANO / RURAL
    cole_jornada VARCHAR(50),
    cole_cod_mcpio_ubicacion VARCHAR(10),
    INDEX idx_naturaleza (cole_naturaleza),
    INDEX idx_mcpio (cole_cod_mcpio_ubicacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Tabla Transaccional de Resultados Históricos (Años 2019 y 2020)
CREATE TABLE IF NOT EXISTS resultados_saber11_historico_rds (
    estu_consecutivo VARCHAR(50) PRIMARY KEY,
    periodo INT NOT NULL,                  -- ej. 20194, 20204
    estu_tipodocumento VARCHAR(10),
    estu_genero VARCHAR(5),
    estu_fechanacimiento DATE,
    estu_cod_reside_mcpio VARCHAR(10),
    fami_estratovivienda VARCHAR(30),
    fami_educacionpadre VARCHAR(100),
    fami_educacionmadre VARCHAR(100),
    fami_tieneinternet VARCHAR(10),
    fami_tienecomputador VARCHAR(10),
    cole_cod_dane_establecimiento BIGINT,
    punt_lectura_critica INT,
    punt_matematicas INT,
    punt_c_naturales INT,
    punt_sociales_ciudadanas INT,
    punt_ingles INT,
    desemp_ingles VARCHAR(10),
    punt_global INT,
    percentil_global INT,
    INDEX idx_periodo (periodo),
    INDEX idx_cole (cole_cod_dane_establecimiento),
    CONSTRAINT fk_resultados_colegio 
        FOREIGN KEY (cole_cod_dane_establecimiento) 
        REFERENCES dim_colegios (cole_cod_dane_establecimiento)
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
