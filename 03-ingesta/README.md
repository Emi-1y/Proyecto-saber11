# 03 - Ingesta Automática hacia AWS S3 Data Lake (Zona Raw)

## 1. Objetivo
Implementar los procesos de ingestión automática para extraer los datos desde las 3 fuentes heterogéneas y depositarlos en el Data Lake de Amazon S3 en la zona `raw/`, organizados bajo la convención de particionado por fecha de ingesta: `s3://saber11-datalake-xyz/raw/fuente=X/ingest_date=YYYY-MM-DD/`.

---

## 2. Requisitos Previos
- Bucket de S3 creado y accesible.
- Conectividad activa hacia RDS MariaDB, EC2 (SSH/SCP) y la API SODA (`datos.gov.co`).
- Entorno local o Lambda con permisos sobre S3 (`s3:PutObject`).

---

## 3. Comandos Exactos Numerados

### Paso 1: Crear el Bucket de S3 del Data Lake
```bash
aws s3api create-bucket \
    --bucket saber11-datalake-TUNOMBRE \
    --region us-east-1
```

### Paso 2: Ejecutar la ingesta desde RDS MariaDB a S3 Raw
Extrae las tablas maestras y los resultados de 2019-2020 exportándolos a JSON/CSV en S3:
```bash
python 03-ingesta/scripts/ingesta_rds.py
```

### Paso 3: Ejecutar la ingesta desde el Servidor de Archivos EC2 a S3 Raw
Sincroniza los archivos CSV acumulados en la instancia EC2 directamente hacia S3:
```bash
python 03-ingesta/scripts/ingesta_ec2.py
# O directamente desde la instancia EC2 vía AWS CLI:
# aws s3 sync /home/ec2-user/data/saber11/ s3://saber11-datalake-TUNOMBRE/raw/fuente=ec2/ingest_date=$(date +%F)/
```

### Paso 4: Ejecutar la ingesta desde la API Socrata y DIVIPOLA
Descarga paginada del año 2023+ y del dataset de municipios:
```bash
python 03-ingesta/scripts/ingesta_api.py
```

### Paso 5: Verificar el contenido depositado en S3 Raw
```bash
aws s3 ls s3://saber11-datalake-TUNOMBRE/raw/ --recursive --human-readable
```

---

## 4. Resultado Esperado
Estructura organizada en Amazon S3:
```
s3://saber11-datalake-TUNOMBRE/raw/
├── fuente=rds/
│   └── ingest_date=YYYY-MM-DD/
│       ├── dim_colegios.csv
│       ├── dim_municipios.csv
│       └── resultados_2019_2020.csv
├── fuente=ec2/
│   └── ingest_date=YYYY-MM-DD/
│       ├── saber11_2021.csv
│       └── saber11_2022.csv
└── fuente=api/
    └── ingest_date=YYYY-MM-DD/
        ├── saber11_2023.json
        └── divipola_municipios.json
```

---

## 5. Evidencias (Pantallazos)
<!-- Adjuntar capturas en ../evidencias/ -->
- `evidencias/03_s3_raw_bucket_console.png`: Consola de Amazon S3 mostrando los prefijos de `raw/`.
- `evidencias/03_ingesta_terminal_output.png`: Salida exitosa de los scripts de ingesta en la terminal.
