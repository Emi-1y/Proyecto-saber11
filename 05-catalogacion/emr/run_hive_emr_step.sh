#!/bin/bash
# ==============================================================================
# Script: run_hive_emr_step.sh
# Objetivo: Ejecutar el script HQL de Hive como un Step en un clúster EMR activo
#           utilizando AWS CLI y el rol de laboratorio (LabRole).
# ==============================================================================

set -e

CLUSTER_ID="${1:-j-XXXXXXXXXXXX}"
S3_BUCKET="${2:-saber11-datalake-885601272401}"
HQL_S3_PATH="s3://${S3_BUCKET}/scripts/hive/01_create_trusted_table.hql"

echo "=== Subiendo script HQL a S3 ==="
aws s3 cp 05-catalogacion/hive/01_create_trusted_table.hql "$HQL_S3_PATH"

echo "=== Agregando Step de Hive al clúster EMR: ${CLUSTER_ID} ==="
STEP_ID=$(aws emr add-steps \
    --cluster-id "$CLUSTER_ID" \
    --steps Type=HIVE,Name="Saber11_Hive_Catalog_Step",ActionOnFailure=CONTINUE,Args=[-f,"$HQL_S3_PATH"] \
    --query "StepIds[0]" \
    --output text)

echo "✓ Step de Hive enviado con ID: $STEP_ID"
echo "Monitoreando estado del Step..."

aws emr wait step-complete --cluster-id "$CLUSTER_ID" --step-id "$STEP_ID"
echo "✓ Step de Hive completado exitosamente en EMR."
