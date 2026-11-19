# 03 - Ingesta Automática hacia AWS S3 Data Lake (Zona Raw)

## 1. Objetivo
Implementar y orquestar los procesos de **ingesta automática** para extraer continuamente datos desde las 3 fuentes heterogéneas (RDS MariaDB, servidor EC2 y API Socrata) y depositarlos en el Data Lake de Amazon S3 en la zona `raw/`, organizados bajo la convención de particionado por fecha de ingesta: `s3://saber11-datalake-xyz/raw/fuente=X/ingest_date=YYYY-MM-DD/`.

---

## 2. Arquitectura de Ingesta Automática

El pipeline no depende de ejecuciones manuales aisladas; opera mediante tres mecanismos automáticos programados y coordinados:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   MECANISMOS DE AUTOMATIZACIÓN                         │
└────────────────────────────────────────────────────────────────────────┘

1. EC2 Cron Job (Diario 02:00 AM)
   /home/ec2-user/data/saber11/*.csv ──(aws s3 sync cron)──► s3://.../raw/fuente=ec2/

2. Amazon EventBridge Rule (Diario 03:00 AM)
   cron(0 3 * * ? *) ──► AWS Lambda (lambda_ingesta_function.py)
                                  │
                                  ├─► Extrae Socrata API (datos.gov.co) ──► s3://.../raw/fuente=api/
                                  │
                                  └─► Dispara AWS Glue Job (saber11-raw-to-trusted)

3. AWS Glue Scheduled Trigger (Nativo AWS Glue)
   saber11-daily-scheduled-trigger (cron: 0 3 * * ? *) ──► Inicia ETL Raw -> Trusted
```

---

## 3. Componentes de Automatización

### A. AWS Lambda Automática (`03-ingesta/lambda/lambda_ingesta_function.py`)
- **Disparador:** Amazon EventBridge (Cron diario o eventos S3 PutObject).
- **Acción 1:** Consulta la API de Socrata (Dataset `kgxf-xxbe`) para el último periodo disponible y deposita el JSON en `raw/fuente=api/ingest_date=YYYY-MM-DD/`.
- **Acción 2:** Llama programáticamente a la API de AWS Glue (`glue.start_job_run(JobName='saber11-raw-to-trusted')`) para disparar el procesamiento ETL inmediatamente después de la ingesta.

### B. Ingesta Periódica EC2 vía Crontab (`03-ingesta/scripts/configurar_cron_ec2.sh`)
- Automatiza la sincronización de archivos CSV generados o recibidos en el servidor Linux EC2 (`/home/ec2-user/data/saber11/`) hacia S3 Raw mediante `aws s3 sync`.
- Se ejecuta desatendido a las 02:00 AM generando logs de auditoría en `/home/ec2-user/logs/sync_YYYY-MM-DD.log`.

### C. AWS Glue Trigger Programado (`03-ingesta/scripts/configurar_eventbridge_glue.py`)
- Disparador nativo de AWS Glue tipo `SCHEDULED` con expresión `cron(0 3 * * ? *)`.
- Garantiza la ejecución diaria del job de Spark `saber11-raw-to-trusted` activando `job-bookmarks` para procesar únicamente datos nuevos.

---

## 4. Comandos de Despliegue y Ejecución

### Paso 1: Configurar la sincronización automática en EC2
```bash
# Conectarse a la instancia EC2 y ejecutar:
bash 03-ingesta/scripts/configurar_cron_ec2.sh saber11-datalake-885601272401
```

### Paso 2: Crear el disparador programado en AWS Glue / EventBridge
```bash
python 03-ingesta/scripts/configurar_eventbridge_glue.py
```

### Paso 3: Desplegar la función Lambda de Ingesta Automática
```bash
# Empaquetar y crear función Lambda con LabRole
zip -j lambda_ingesta.zip 03-ingesta/lambda/lambda_ingesta_function.py

aws lambda create-function \
    --function-name saber11-automated-ingest \
    --runtime python3.11 \
    --role arn:aws:iam::885601272401:role/LabRole \
    --handler lambda_ingesta_function.lambda_handler \
    --zip-file fileb://lambda_ingesta.zip \
    --timeout 60 \
    --environment "Variables={S3_BUCKET_NAME=saber11-datalake-885601272401,GLUE_JOB_NAME=saber11-raw-to-trusted}"
```

### Paso 4: Ejecución puntual de prueba de los scripts de ingesta
```bash
# Ingesta desde RDS MariaDB:
python 03-ingesta/scripts/ingesta_rds.py

# Ingesta desde EC2:
python 03-ingesta/scripts/ingesta_ec2.py

# Ingesta desde API Socrata / DIVIPOLA:
python 03-ingesta/scripts/ingesta_api.py
```

---

## 5. Resultado Esperado en S3 Raw
```
s3://saber11-datalake-885601272401/raw/
├── fuente=rds/
│   └── ingest_date=2026-11-18/
│       ├── dim_colegios.csv
│       ├── dim_municipios.csv
│       └── resultados_2019_2020.csv
├── fuente=ec2/
│   └── ingest_date=2026-11-18/
│       ├── saber11_2021.csv
│       └── saber11_2022.csv
└── fuente=api/
    └── ingest_date=2026-11-18/
        ├── saber11_2023.json
        └── divipola_municipios.json
```

---

## 6. Evidencias
- `evidencias/03_s3_raw_bucket_console.png`: Objetos y prefijos particionados en S3 Raw.
- `evidencias/03_ingesta_terminal_output.png`: Salida de ejecución de los componentes de ingesta.
