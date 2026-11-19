#!/bin/bash
# ==============================================================================
# Script: crear_cluster_emr_transient.sh
# Objetivo: Lanzar un clúster Amazon EMR transitorio (auto-terminable) con Apache Hive,
#           ejecutar el script HQL de catalogación y apagarse automáticamente para
#           optimizar costos en AWS Academy Learner Lab.
# ==============================================================================

set -e

S3_BUCKET="${1:-saber11-datalake-885601272401}"
HQL_S3_PATH="s3://${S3_BUCKET}/scripts/hive/01_create_trusted_table.hql"
LOG_URI="s3://${S3_BUCKET}/emr-logs/"

echo "=== 1. Subiendo HQL a S3 ==="
aws s3 cp 05-catalogacion/hive/01_create_trusted_table.hql "$HQL_S3_PATH"

echo "=== 2. Lanzando Clúster EMR Transitorio con Hive ==="
CLUSTER_ID=$(aws emr create-cluster \
    --name "saber11-hive-catalog-cluster" \
    --release-label emr-6.10.0 \
    --applications Name=Hive Name=Hadoop \
    --service-role LabRole \
    --ec2-attributes InstanceProfile=LabInstanceProfile,SubnetId=subnet-04ea4f9011933df57 \
    --instance-type m5.xlarge \
    --instance-count 1 \
    --auto-terminate \
    --log-uri "$LOG_URI" \
    --steps Type=HIVE,Name="Hive_DDL_Execution",ActionOnFailure=TERMINATE_CLUSTER,Args=[-f,"$HQL_S3_PATH"] \
    --query "ClusterId" \
    --output text)

echo "✓ Clúster EMR lanzado con ID: $CLUSTER_ID"
echo "El clúster ejecutará el script Hive HQL y se apagará automáticamente al terminar."
