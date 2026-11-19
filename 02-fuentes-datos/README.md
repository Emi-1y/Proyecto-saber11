# 02 - Fuentes de Datos: Simulación y Preparación

## 1. Objetivo
Configurar y poblar las tres fuentes de datos heterogéneas que alimentarán el Data Lake:
1. **RDS MariaDB:** Base de datos relacional para datos maestros de colegios/municipios y resultados históricos (2019-2020).
2. **Archivos CSV en EC2:** Instancia de servidor Linux para almacenamiento de lotes legacy (2021-2022).
3. **URL / API Socrata:** Endpoint directo de la API abierta para el periodo reciente (2023+) y dataset DIVIPOLA (DANE).

---

## 2. Requisitos Previos
- AWS CLI configurado (`aws configure` con credenciales de la sesión).
- Variables de `.env` completadas.
- Python 3.11 con dependencias instaladas (`pip install -r requirements.txt`).

---

## 3. Comandos Exactos Numerados

### Paso 1: Generar o descargar la muestra inicial de datos
Ejecuta el script de preparación para extraer los datos desde la API SODA y dividirlos en las particiones de las tres fuentes:
```bash
python 02-fuentes-datos/scripts/preparar_fuentes.py --sample-size 100000
```

### Paso 2: Crear la instancia de Amazon RDS (MariaDB)
*(Pide confirmación antes de ejecutar este comando en la nube)*
```bash
aws rds create-db-instance \
    --db-instance-identifier saber11-mariadb \
    --db-instance-class db.t3.micro \
    --engine mariadb \
    --allocated-storage 20 \
    --master-username admin_saber11 \
    --master-user-password TU_PASSWORD_AQUI \
    --backup-retention-period 0 \
    --publicly-accessible \
    --region us-east-1
```

### Paso 3: Poblar el esquema y tablas en RDS MariaDB
Una vez la instancia RDS esté en estado `available`:
```bash
mysql -h saber11-mariadb.cxxxxxx.us-east-1.rds.amazonaws.com -u admin_saber11 -p saber11_db < 02-fuentes-datos/sql/init_schema.sql
python 02-fuentes-datos/scripts/cargar_rds.py
```

### Paso 4: Crear la instancia EC2 y copiar los archivos CSV
```bash
# Lanzar instancia Amazon Linux 2023 (t3.micro)
aws ec2 run-instances \
    --image-id resolve:ssm:/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
    --instance-type t3.micro \
    --key-name saber11-key \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=saber11-fileserver}]' \
    --region us-east-1

# Crear directorio en EC2 y transferir archivos
ssh -i ~/.ssh/saber11-key.pem ec2-user@IP_PUBLICA_EC2 "mkdir -p /home/ec2-user/data/saber11"
scp -i ~/.ssh/saber11-key.pem 02-fuentes-datos/data/saber11_2021.csv 02-fuentes-datos/data/saber11_2022.csv ec2-user@IP_PUBLICA_EC2:/home/ec2-user/data/saber11/
```

---

## 4. Resultado Esperado
- Instancia RDS MariaDB activa con las tablas `dim_colegio`, `dim_municipio` y `resultados_2019_2020` con datos consultables.
- Instancia EC2 con los archivos `saber11_2021.csv` y `saber11_2022.csv` en `/home/ec2-user/data/saber11/`.
- Script de extracción API funcionando para 2023 y DIVIPOLA.

---

## 5. Evidencias (Pantallazos)
<!-- Adjuntar capturas en ../evidencias/ -->
- `evidencias/02_rds_mariadb_status.png`: Consola de AWS RDS en estado Available.
- `evidencias/02_rds_query_dbeaver.png`: Consulta SELECT en DBeaver sobre MariaDB.
- `evidencias/02_ec2_files_ls.png`: Terminal SSH en EC2 ejecutando `ls -lh /home/ec2-user/data/saber11/`.
