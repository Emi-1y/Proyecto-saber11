# Diccionario de Datos: Saber 11 (ICFES) & DIVIPOLA (DANE)

## 1. Identificación de Fuentes de Datos

### Fuente Principal: Saber 11 (ICFES)
- **Nombre oficial:** Resultados únicos Saber 11
- **Entidad:** Instituto Colombiano para la Evaluación de la Educación (ICFES)
- **Portal:** Portal de Datos Abiertos de Colombia (`datos.gov.co`)
- **ID del Dataset (Socrata 4x4):** `kgxf-xxbe` *(Nota: el ID preliminar `kgxf-xxif` fue verificado y corregido al oficial `kgxf-xxbe`)*
- **URL Web:** [https://www.datos.gov.co/Educaci-n/Resultados-nicos-Saber-11/kgxf-xxbe](https://www.datos.gov.co/Educaci-n/Resultados-nicos-Saber-11/kgxf-xxbe)
- **Endpoint API SODA (JSON):** `https://www.datos.gov.co/resource/kgxf-xxbe.json`
- **Endpoint API SODA (CSV):** `https://www.datos.gov.co/resource/kgxf-xxbe.csv`
- **Volumen total:** > 7,200,000 registros históricos (2010 a 2023+), 51 columnas, ~3.5 GB sin comprimir.

### Fuente Complementaria: DIVIPOLA (DANE)
- **Nombre oficial:** DIVIPOLA - Códigos Municipios
- **Entidad:** Departamento Administrativo Nacional de Estadística (DANE)
- **Portal:** `datos.gov.co`
- **ID del Dataset:** `gdxc-w37w`
- **Endpoint API (JSON):** `https://www.datos.gov.co/resource/gdxc-w37w.json`
- **Volumen:** ~1,122 registros (1 por municipio/área no municipalizada).
- **Utilidad:** Enriquecimiento geográfico (coordenadas lat/long, validación y estandarización de códigos depto/mcpio oficiales DANE).

---

## 2. Diccionario de Datos: Dataset Principal Saber 11 (`kgxf-xxbe`)

A continuación se detalla la estructura estandarizada de las 51 columnas del dataset `kgxf-xxbe`, organizadas por dominio analítico:

### A. Información de la Prueba y del Estudiante
| Columna | Tipo Socrata | Tipo PySpark/SQL | Descripción | Ejemplo | % Nulos Estimado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `periodo` | Number | `INT` | Periodo y ciclo de presentación (Año + ciclo: ej. 20211, 20214) | `20214` | 0% |
| `estu_consecutivo` | Text | `STRING` | Identificador único anonimizado del evaluado | `SB11202140001234` | 0% |
| `estu_tipodocumento` | Text | `STRING` | Tipo de documento de identidad | `TI`, `CC`, `CR`, `PEP` | < 0.1% |
| `estu_estudiante` | Text | `STRING` | Condición del evaluado | `ESTUDIANTE`, `INDIVIDUAL` | 0% |
| `estu_genero` | Text | `STRING` | Género reportado por el estudiante | `F`, `M` | < 0.2% |
| `estu_fechanacimiento` | Text | `DATE` | Fecha de nacimiento reportada (formato DD/MM/YYYY) | `15/03/2004` | < 0.5% |
| `estu_pais_reside` | Text | `STRING` | País de residencia | `COLOMBIA` | < 0.1% |
| `estu_depto_reside` | Text | `STRING` | Departamento donde reside el estudiante | `BOGOTÁ`, `ANTIOQUIA` | < 0.2% |
| `estu_cod_reside_depto` | Number | `INT` | Código DANE del departamento de residencia (2 dígitos) | `11`, `05` | < 0.2% |
| `estu_mcpio_reside` | Text | `STRING` | Municipio donde reside el estudiante | `BOGOTÁ D.C.`, `MEDELLÍN` | < 0.2% |
| `estu_cod_reside_mcpio` | Number | `INT` | Código DANE del municipio de residencia (5 dígitos) | `11001`, `05001` | < 0.2% |

### B. Contexto Socioeconómico del Hogar
| Columna | Tipo Socrata | Tipo PySpark/SQL | Descripción | Ejemplo | % Nulos Estimado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fami_estratovivienda` | Text | `STRING` | Estrato socioeconómico de la vivienda de servicios públicos | `Estrato 1`, `Estrato 2`, `Sin Estrato` | ~2% - 5% |
| `fami_educacionpadre` | Text | `STRING` | Máximo nivel educativo alcanzado por el padre | `Secundaria (Bachillerato) completa`, `Profesional` | ~5% - 8% |
| `fami_educacionmadre` | Text | `STRING` | Máximo nivel educativo alcanzado por la madre | `Primaria incompleta`, `Técnica o tecnológica` | ~4% - 6% |
| `fami_tieneinternet` | Text | `STRING` | Dispone de conexión a Internet en su vivienda | `Si`, `No` | ~2% - 4% |
| `fami_tienecomputador` | Text | `STRING` | Dispone de computador en su hogar | `Si`, `No` | ~2% - 4% |
| `fami_tieneautomovil` | Text | `STRING` | Dispone de vehículo automóvil en el hogar | `Si`, `No` | ~3% - 5% |
| `fami_tienelavadora` | Text | `STRING` | Dispone de lavadora en el hogar | `Si`, `No` | ~3% - 5% |
| `fami_numlibros` | Text | `STRING` | Rango de libros disponibles en casa | `0 A 10 LIBROS`, `11 A 25 LIBROS` | ~5% - 8% |
| `fami_situacioneconomica` | Text | `STRING` | Percepción del estado económico del hogar respecto al año anterior | `Igual`, `Mejor`, `Peor` | ~4% - 7% |

### C. Características de la Institución Educativa (Colegio)
| Columna | Tipo Socrata | Tipo PySpark/SQL | Descripción | Ejemplo | % Nulos Estimado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `cole_codigo_icfes` | Number | `BIGINT` | Código de registro asignado por ICFES al colegio | `123456` | 0% |
| `cole_cod_dane_establecimiento` | Number | `BIGINT` | Código DANE institucional de 12 dígitos | `111001012345` | < 0.5% |
| `cole_nombre_establecimiento` | Text | `STRING` | Nombre oficial de la institución educativa | `COLEGIO SAN JOSÉ` | 0% |
| `cole_genero` | Text | `STRING` | Composición por género de la institución | `MIXTO`, `FEMENINO`, `MASCULINO` | 0% |
| `cole_naturaleza` | Text | `STRING` | Carácter administrativo: Oficial (público) o No Oficial (privado) | `OFICIAL`, `NO OFICIAL` | 0% |
| `cole_calendario` | Text | `STRING` | Calendario escolar en que opera la institución | `A`, `B`, `OTRO` | 0% |
| `cole_bilingue` | Text | `STRING` | Clasificación bilingüe del colegio | `S`, `N` | ~8% - 12% |
| `cole_caracter` | Text | `STRING` | Énfasis del plan de estudios | `ACADÉMICO`, `TÉCNICO`, `TÉCNICO/ACADÉMICO` | ~1% - 3% |
| `cole_cod_dane_sede` | Number | `BIGINT` | Código DANE de 12 dígitos de la sede específica | `111001012346` | < 0.5% |
| `cole_nombre_sede` | Text | `STRING` | Nombre oficial de la sede educativa | `SEDE PRINCIPAL` | 0% |
| `cole_sede_principal` | Text | `STRING` | Indica si la sede es la principal (`S`/`N`) | `S`, `N` | 0% |
| `cole_area_ubicacion` | Text | `STRING` | Zona geográfica del colegio | `URBANO`, `RURAL` | 0% |
| `cole_jornada` | Text | `STRING` | Modalidad de horario de clases | `MAÑANA`, `TARDE`, `COMPLETA`, `ÚNICA` | 0% |
| `cole_cod_mcpio_ubicacion` | Number | `INT` | Código DANE del municipio del colegio | `11001`, `05001` | 0% |
| `cole_mcpio_ubicacion` | Text | `STRING` | Municipio donde está ubicado el colegio | `BOGOTÁ D.C.`, `MEDELLÍN` | 0% |
| `cole_cod_depto_ubicacion` | Number | `INT` | Código DANE del departamento del colegio | `11`, `05` | 0% |
| `cole_depto_ubicacion` | Text | `STRING` | Departamento donde está ubicado el colegio | `BOGOTÁ`, `ANTIOQUIA` | 0% |

### D. Puntajes de las 5 Áreas Evaluadas y Puntaje Global
| Columna | Tipo Socrata | Tipo PySpark/SQL | Descripción | Escala / Rango | % Nulos Estimado |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `punt_lectura_critica` | Number | `INT` | Puntaje obtenido en Lectura Crítica | 0 - 100 | < 0.1% (pos-2014) |
| `percentil_lectura_critica`| Number | `INT` | Percentil nacional en Lectura Crítica | 1 - 100 | < 0.1% |
| `desemp_lectura_critica` | Number | `INT` | Nivel de desempeño en Lectura Crítica | 1 - 4 | < 0.1% |
| `punt_matematicas` | Number | `INT` | Puntaje obtenido en Matemáticas | 0 - 100 | < 0.1% (pos-2014) |
| `percentil_matematicas` | Number | `INT` | Percentil nacional en Matemáticas | 1 - 100 | < 0.1% |
| `desemp_matematicas` | Number | `INT` | Nivel de desempeño en Matemáticas | 1 - 4 | < 0.1% |
| `punt_c_naturales` | Number | `INT` | Puntaje obtenido en Ciencias Naturales | 0 - 100 | < 0.1% (pos-2014) |
| `percentil_c_naturales` | Number | `INT` | Percentil nacional en Ciencias Naturales | 1 - 100 | < 0.1% |
| `desemp_c_naturales` | Number | `INT` | Nivel de desempeño en Ciencias Naturales | 1 - 4 | < 0.1% |
| `punt_sociales_ciudadanas`| Number | `INT` | Puntaje en Sociales y Ciudadanas | 0 - 100 | < 0.1% (pos-2014) |
| `percentil_sociales_ciudadanas`| Number | `INT`| Percentil en Sociales y Ciudadanas | 1 - 100 | < 0.1% |
| `desemp_sociales_ciudadanas`| Number | `INT` | Nivel de desempeño en Sociales y Ciudadanas | 1 - 4 | < 0.1% |
| `punt_ingles` | Number | `INT` | Puntaje obtenido en Inglés | 0 - 100 | < 0.1% (pos-2014) |
| `percentil_ingles` | Number | `INT` | Percentil nacional en Inglés | 1 - 100 | < 0.1% |
| `desemp_ingles` | Text | `STRING` | Nivel MCER de desempeño en Inglés | `A-`, `A1`, `A2`, `B1`, `B+` | < 0.1% |
| `punt_global` | Number | `INT` | Puntaje global ponderado de la prueba | 0 - 500 | < 0.1% (pos-2014) |
| `percentil_global` | Number | `INT` | Percentil global en el examen a nivel país | 1 - 100 | < 0.1% |

---

## 3. Diccionario de Datos: Dataset Complementario DIVIPOLA (`gdxc-w37w`)

| Columna | Tipo Socrata | Tipo PySpark/SQL | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- | :--- |
| `cod_depto` | Text | `STRING` | Código DANE de 2 dígitos del departamento | `"11"` |
| `nom_depto` | Text | `STRING` | Nombre del departamento en mayúsculas | `"BOGOTA D.C."` |
| `cod_municipio` | Text | `STRING` | Código DANE de 5 dígitos del municipio | `"11001"` |
| `nom_municipio` | Text | `STRING` | Nombre del municipio en mayúsculas | `"BOGOTA D.C."` |
| `tipo` | Text | `STRING` | Clasificación territorial (Municipio / Isla / Área no municipalizada) | `"MUNICIPIO"` |
| `latitud` | Number | `DOUBLE` | Latitud geográfica del centroide | `4.60971` |
| `longitud` | Number | `DOUBLE` | Longitud geográfica del centroide | `-74.08175` |

---

## 4. Hallazgos Críticos de Calidad y Evolución del Esquema

1. **Ruptura Metodológica de 2014-2:**  
   Antes del segundo semestre de 2014, el examen Saber 11 evaluaba 8 áreas disciplinarias independientes (Lenguaje, Matemáticas, Ciencias Sociales, Filosofía, Biología, Química, Física, Inglés). A partir de **2014-2**, el ICFES unificó el esquema en **5 componentes transversales** y estableció el **Puntaje Global en escala de 0 a 500**. Por tanto, para asegurar consistencia analítica e integridad de esquemas en Spark y Glue, el proyecto se enfocará en periodos **>= 2015 o 2019 a 2023**, garantizando que el 100% de los registros posean las mismas columnas de puntaje sin dispersión de nulos estructurales.

2. **Estandarización de Nombres de Columnas:**  
   En las descargas manuales de periodos individuales el ICFES suele usar nombres en mayúsculas o con caracteres especiales (tildes, espacios). En la API Socrata `kgxf-xxbe`, todos los nombres ya están normalizados en **minúsculas snake_case** (`cole_cod_dane_establecimiento`, `punt_lectura_critica`), lo cual es una gran ventaja para la creación de esquemas SQL en MariaDB, Glue Data Catalog y Athena.

3. **Nulos en Variables Socioeconómicas:**  
   Las variables `fami_estratovivienda`, `fami_educacionpadre` y `fami_educacionmadre` tienen entre 2% y 8% de valores nulos o clasificaciones especiales ("No sabe / No aplica", "Sin Estrato"). Durante la fase de transformación en Glue/Spark (Silver/Trusted), se aplicará limpieza y asignación de valor por defecto (`'NO_REPORTADO'`).
