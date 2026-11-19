#!/bin/bash
# ==============================================================================
# Script: configurar_cron_ec2.sh
# Objetivo: Configurar la ingesta automática periódica (Cron) en la instancia EC2
#           para sincronizar archivos locales hacia S3 Raw sin intervención manual.
# ==============================================================================

set -e

BUCKET_NAME="${1:-saber11-datalake-885601272401}"
DATA_DIR="/home/ec2-user/data/saber11"
SCRIPT_PATH="/home/ec2-user/scripts/sync_s3_raw.sh"

echo "=== Configurando Ingesta Automática por Cron en EC2 ==="

# 1. Crear directorio de scripts
mkdir -p /home/ec2-user/scripts

# 2. Crear script ejecutable de sincronización
cat << 'EOF' > "$SCRIPT_PATH"
#!/bin/bash
FECHA_HOY=$(date +%Y-%m-%d)
LOG_FILE="/home/ec2-user/logs/sync_${FECHA_HOY}.log"
mkdir -p /home/ec2-user/logs

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Iniciando sincronización hacia S3..." >> "$LOG_FILE"

# Sincronizar hacia prefijo particionado en S3 Raw
aws s3 sync /home/ec2-user/data/saber11/ "s3://saber11-datalake-885601272401/raw/fuente=ec2/ingest_date=${FECHA_HOY}/" \
    --exclude "*" \
    --include "*.csv" \
    --only-show-errors >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sincronización completada exitosamente." >> "$LOG_FILE"
EOF

chmod +x "$SCRIPT_PATH"
echo "✓ Script de sincronización creado en: $SCRIPT_PATH"

# 3. Registrar tarea en crontab (se ejecuta todos los días a las 02:00 AM)
CRON_JOB="0 2 * * * $SCRIPT_PATH"

(crontab -l 2>/dev/null | grep -Fv "$SCRIPT_PATH" ; echo "$CRON_JOB") | crontab -

echo "✓ Tarea cron registrada exitosamente en crontab:"
crontab -l | grep "$SCRIPT_PATH"
echo "=== Ingesta Automática EC2 lista y programada ==="
