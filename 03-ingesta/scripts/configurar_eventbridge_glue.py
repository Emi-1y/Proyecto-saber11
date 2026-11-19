#!/usr/bin/env python3
"""
Script: configurar_eventbridge_glue.py
Objetivo: Configurar el disparador automático programado (Scheduled Trigger)
          en AWS Glue y regla en Amazon EventBridge para ejecutar periódicamente
          el pipeline de ingesta y procesamiento de Saber 11.
"""

import boto3
import sys

GLUE_JOB_NAME = "saber11-raw-to-trusted"
TRIGGER_NAME = "saber11-daily-scheduled-trigger"
CRON_SCHEDULE = "cron(0 3 * * ? *)"  # Todos los días a las 03:00 UTC

glue_client = boto3.client("glue", region_name="us-east-1")
events_client = boto3.client("events", region_name="us-east-1")

def crear_glue_scheduled_trigger():
    print(f"=== Configurando AWS Glue Scheduled Trigger: {TRIGGER_NAME} ===")
    try:
        # Verificar si el trigger ya existe
        try:
            glue_client.get_trigger(Name=TRIGGER_NAME)
            print(f"El trigger {TRIGGER_NAME} ya existe. Actualizando...")
            glue_client.delete_trigger(Name=TRIGGER_NAME)
        except glue_client.exceptions.EntityNotFoundException:
            pass

        # Crear el trigger tipo SCHEDULED
        resp = glue_client.create_trigger(
            Name=TRIGGER_NAME,
            Type="SCHEDULED",
            Schedule=CRON_SCHEDULE,
            Actions=[
                {
                    "JobName": GLUE_JOB_NAME,
                    "Arguments": {
                        "--enable-metrics": "true",
                        "--job-bookmark-option": "job-bookmark-enable"
                    }
                }
            ],
            Description="Disparador diario automático para el job de procesamiento Saber 11 Raw to Trusted",
            StartOnCreation=True
        )
        print(f"✓ Trigger de Glue creado y activado exitosamente: {resp['Name']}")
        print(f"  Horario Cron: {CRON_SCHEDULE} (Diario a las 03:00 AM UTC)")
    except Exception as e:
        print(f"Nota/Advertencia en Glue Trigger: {e}")

def documentar_eventbridge_rule():
    print("\n=== Configurando Regla en Amazon EventBridge (Cron para Ingesta) ===")
    RULE_NAME = "saber11-daily-ingest-rule"
    try:
        resp = events_client.put_rule(
            Name=RULE_NAME,
            ScheduleExpression=CRON_SCHEDULE,
            State="ENABLED",
            Description="Regla diaria que activa la Lambda de ingesta de API y sincronización a S3 Raw"
        )
        print(f"✓ Regla EventBridge registrada: {resp.get('RuleArn', RULE_NAME)}")
        print(f"  Frecuencia: {CRON_SCHEDULE}")
    except Exception as e:
        print(f"Nota/Advertencia en EventBridge: {e}")

if __name__ == "__main__":
    crear_glue_scheduled_trigger()
    documentar_eventbridge_rule()
