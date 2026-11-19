# 01 - Caso de Estudio: Resultados Pruebas Saber 11 (ICFES)

## 1. Objetivo
Definir el alcance analítico del proyecto, el catálogo de preguntas de negocio, el diccionario de datos estandarizado y la estrategia de partición federada de fuentes (RDS MariaDB, EC2 CSVs y URL/API) para el Data Lake en AWS.

---

## 2. Preguntas de Negocio Refinadas

Para responder a las necesidades de la analítica educativa en Colombia y cumplir con los requerimientos académicos del proyecto, se plantean y refinan las siguientes preguntas orientadas a consultas SQL (Athena/Hive) y PySpark:

1. **Ranking Departamental:** ¿Cuál es el ranking de departamentos por puntaje global promedio y cómo varían sus percentiles?
2. **Brecha Oficial vs. No Oficial:** ¿Cuál es la brecha estadísticamente significativa en el puntaje global y por área entre instituciones educativas públicas (Oficiales) y privadas (No Oficiales)?
3. **Impacto Socioeconómico (Estrato y Educación de los Padres):** ¿Cómo se correlaciona el estrato socioeconómico familiar y el nivel educativo de la madre/padre con el desempeño en Matemáticas y Lectura Crítica?
4. **Evolución Temporal del Rendimiento:** ¿Cómo ha evolucionado el puntaje promedio por área del conocimiento a través de los periodos evaluados (incluyendo impacto post-pandemia)?
5. **Top y Bottom de Municipios en Inglés:** ¿Cuáles son los 10 municipios con mejor y peor desempeño promedio en el componente de Inglés y qué porcentaje alcanza niveles B1/B+?
6. **Brecha Urbano - Rural:** ¿Qué disparidad existe en el puntaje global entre colegios ubicados en zona urbana versus zona rural a nivel nacional y departamental?
7. **Acceso a TIC (Brecha Digital):** ¿Cuál es el impacto diferencial en los puntajes globales entre los estudiantes que cuentan con acceso simultáneo a Internet y Computador frente a los que no cuentan con ninguno de ellos?
8. **Métricas de Calidad de Datos:** ¿Cuál es el volumen de registros y el porcentaje de completitud (valores nulos o inconsistentes) por columna a lo largo del pipeline de ingestión?

---

## 3. Estrategia de Distribución en Tres Fuentes Heterogéneas

Para simular un entorno corporativo real donde coexisten sistemas transaccionales, sistemas de archivos legados y APIs externas, el universo de datos se distribuye estratégicamente de la siguiente forma:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FUENTES HETEROGÉNEAS (ORIGEN)                        │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       ▼                           ▼                           ▼
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│  RDS MariaDB │           │ Archivos EC2 │           │  URL / API   │
│  (Relacional)│           │    (CSV)     │           │   (Socrata)  │
└──────┬───────┘           └──────┬───────┘           └──────┬───────┘
       │                          │                          │
       │ Periodos 2019-2020       │ Periodos 2021-2022       │ Periodo 2023+
       │ + Tablas Maestras        │ en /data/saber11/*.csv   │ + DIVIPOLA DANE
       │ (dim_colegios, etc.)     │                          │ (gdxc-w37w)
       │                          │                          │
       └──────────────────────────┼──────────────────────────┘
                                  ▼
                     AWS S3 (Data Lake: raw/)
```

### 3.1. Fuente 1: Base de Datos Relacional (RDS MariaDB)
- **Contenido:**
  - **Resultados Históricos (Periodos 2019 y 2020):** Evaluaciones correspondientes a los calendarios A y B de estos dos años.
  - **Tablas Maestras (Dimensiones):**
    - `dim_colegio`: Catálogo de colegios con su código DANE, nombre, naturaleza (oficial/no oficial), calendario, jornada y sede principal.
    - `dim_municipio`: Tabla normalizada de municipios y departamentos.
- **Razón técnica:** Simula el sistema transaccional central donde residen los datos maestros y el histórico consolidado más antiguo.

### 3.2. Fuente 2: Archivos Planos en Servidor (Instancia EC2)
- **Contenido:**
  - **Resultados Intermedios (Periodos 2021 y 2022):** Archivos CSV estructurados particionados por año y periodo (`saber11_2021.csv`, `saber11_2022.csv`) almacenados en el disco EBS de la instancia EC2 (`/data/saber11/`).
- **Razón técnica:** Simula un sistema heredado (legacy batch file transfer / SFTP) muy común en secretarías de educación y entidades públicas que descargan o intercambian volcados periódicos en CSV.

### 3.3. Fuente 3: Consumo Vía Web / API (Portal Socrata y DANE)
- **Contenido:**
  - **Resultados Recientes (Periodo 2023 o última cohorte disponible):** Extracción directa desde la API SODA de `datos.gov.co` con el dataset `kgxf-xxbe`.
  - **Dataset Complementario DIVIPOLA (`gdxc-w37w`):** Extracción vía API REST para obtener coordenadas de municipios, permitiendo enriquecer los dashboards y geolocalización.
- **Razón técnica:** Simula la integración moderna orientada a servicios y APIs públicas en tiempo real o programada.

---

## 4. Guía de Consumo de la API Socrata (SODA & SoQL)

- **Endpoint base:** `https://www.datos.gov.co/resource/kgxf-xxbe.json`
- **Paginación estándar:**
  La API Socrata entrega por defecto 1,000 registros por solicitud y tiene un límite superior de `$limit=50000`. Para consumir volúmenes mayores se utiliza paginación mediante `$limit` y `$offset`:
  ```
  Página 1: ?$limit=50000&$offset=0
  Página 2: ?$limit=50000&$offset=50000
  Página 3: ?$limit=50000&$offset=100000
  ```
- **Filtrado mediante SoQL ($where):**
  Para extraer únicamente el periodo deseado:
  ```http
  GET /resource/kgxf-xxbe.json?$where=periodo >= '20231'&$limit=50000 HTTP/1.1
  Host: www.datos.gov.co
  ```
- **App Token y Cuotas:**
  - Sin token: limitado a ráfagas bajas con riesgo de recibir código HTTP `429 Too Many Requests`.
  - Con App Token: hasta miles de llamadas por hora agregando la cabecera `X-App-Token: <TU_APP_TOKEN>` o el parámetro en la URL `?$$app_token=<TU_APP_TOKEN>`.
