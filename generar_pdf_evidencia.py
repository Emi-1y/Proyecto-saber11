#!/usr/bin/env python3
"""
generar_pdf_evidencia.py
-------------------------
Genera un documento PDF formal, profesional y exhaustivo que resume todo el
proyecto de Big Data en AWS (Saber 11 ICFES) para ser entregado como evidencia.
Utiliza ReportLab para compilar tablas, diagramas de arquitectura, benchmark SQL,
hallazgos de negocio y conclusiones metodológicas.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (páginas posteriores a la portada)
        if self._pageNumber > 1:
            self.drawString(54, 755, "Data Lakehouse en AWS | Resultados Saber 11 (ICFES) — Informe Técnico")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)
        
        # Footer
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "Sistemas Distribuidos · AWS Academy Learner Lab · Repositorio: Emi-1y/Proyecto-saber11")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def construir_pdf(output_path="evidencias/Informe_Ejecutivo_Saber11_AWS.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Estilos tipográficos ejecutivos
    c_primary = colors.HexColor("#0F172A")    # Slate oscuro
    c_blue = colors.HexColor("#1E3A8A")       # Azul corporativo
    c_accent = colors.HexColor("#2563EB")     # Azul vibrante
    c_text = colors.HexColor("#334155")       # Texto base
    c_muted = colors.HexColor("#64748B")      # Texto secundario

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=c_blue,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=c_muted,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        "Header1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=c_blue,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        "Header2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=c_primary,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=c_text,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        "BodyBold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_text
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.white
    )

    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=c_accent
    )

    story = []

    # =========================================================================
    # 1. ENCABEZADO / PORTADA EJECUTIVA
    # =========================================================================
    story.append(Paragraph("INFORME TÉCNICO DE ARQUITECTURA E IMPLEMENTACIÓN", badge_style))
    story.append(Paragraph("Data Lakehouse en AWS: Pruebas Saber 11 (ICFES)", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent, spaceBefore=4, spaceAfter=14))

    # Metadatos del Proyecto
    meta_data = [
        [Paragraph("<b>Materia:</b> Sistemas Distribuidos", table_cell), Paragraph("<b>Región AWS:</b> us-east-1 (N. Virginia)", table_cell)],
        [Paragraph("<b>Integrantes:</b> Emily Cardona", table_cell), Paragraph("<b>Repositorio GitHub:</b> <font color='#2563EB'><u>github.com/Emi-1y/Proyecto-saber11</u></font>", table_cell)],
        [Paragraph("<b>Dataset Principal:</b> Saber 11 ICFES (ID: kgxf-xxbe)", table_cell), Paragraph("<b>Dataset Geográfico:</b> DANE DIVIPOLA (ID: gdxc-w37w)", table_cell)],
        [Paragraph("<b>Entorno de Ejecución:</b> AWS Academy Learner Lab", table_cell), Paragraph("<b>Rol IAM Utilizado:</b> LabRole / LabInstanceProfile", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # =========================================================================
    # 2. RESUMEN EJECUTIVO Y OBJETIVOS
    # =========================================================================
    story.append(Paragraph("1. Resumen Ejecutivo del Proyecto", h1_style))
    p1 = ("El presente proyecto diseña, despliega y certifica una arquitectura completa de <b>Data Lakehouse en Amazon Web Services (AWS)</b> "
          "orientada a la ingesta federada, estandarización masiva, catalogación, analítica distribuida y visualización de los resultados "
          "históricos de las pruebas de Estado <b>Saber 11 (ICFES)</b> de Colombia (cohortes 2019 a 2023). "
          "El sistema unifica 50.000 microdatos estudiantiles y 32 variables multidimensionales originarias de <b>tres fuentes heterogéneas</b> "
          "(RDS MariaDB, servidor de archivos EC2 y API Socrata gubernamental), reduciendo los tiempos de consulta analítica de decenas "
          "de segundos a <b>0.26 segundos</b> mediante el desacoplamiento de almacenamiento y cómputo.")
    story.append(Paragraph(p1, body_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 3. MATRIZ DE CUMPLIMIENTO DE LOS 8 PUNTOS
    # =========================================================================
    story.append(Paragraph("2. Matriz de Cumplimiento de Requerimientos", h1_style))
    req_rows = [
        [Paragraph("Punto", table_header), Paragraph("Componente", table_header), Paragraph("Servicios AWS Utilizados", table_header), Paragraph("Estado / Entregable", table_header)],
        [Paragraph("<b>P1</b>", table_cell), Paragraph("Caso de Estudio & Preguntas", table_cell), Paragraph("Portal datos.gov.co, DANE DIVIPOLA", table_cell), Paragraph("8 Preguntas de negocio + Diccionario 51 columnas", table_cell)],
        [Paragraph("<b>P2</b>", table_cell), Paragraph("Fuentes Heterogéneas", table_cell), Paragraph("Amazon RDS (MariaDB), Amazon EC2 (EBS), API SODA", table_cell), Paragraph("RDS (2019-20), EC2 (2021-22), API (2023)", table_cell)],
        [Paragraph("<b>P3</b>", table_cell), Paragraph("Ingesta Automática a S3", table_cell), Paragraph("Amazon S3 Raw, Amazon EventBridge, AWS Lambda, Cron", table_cell), Paragraph("Crontab 02:00 AM + Lambda Trigger diario 03:00 AM", table_cell)],
        [Paragraph("<b>P4</b>", table_cell), Paragraph("Procesamiento Glue / Spark", table_cell), Paragraph("AWS Glue ETL Job, Apache Spark 3.3 (PySpark)", table_cell), Paragraph("Conversión Bronze a Silver, Parquet particionado", table_cell)],
        [Paragraph("<b>P5</b>", table_cell), Paragraph("Catalogación de Metadatos", table_cell), Paragraph("AWS Glue Data Catalog, Crawler, Apache Hive en EMR", table_cell), Paragraph("DB saber11_catalog, tabla saber11_unified", table_cell)],
        [Paragraph("<b>P6</b>", table_cell), Paragraph("Consultas Analíticas SQL", table_cell), Paragraph("Amazon Athena, Apache SparkSQL, Hive en EMR", table_cell), Paragraph("8 queries ejecutadas + Benchmark comparativo", table_cell)],
        [Paragraph("<b>P7</b>", table_cell), Paragraph("Analítica con PySpark", table_cell), Paragraph("PySpark MLlib, Amazon S3 Refined", table_cell), Paragraph("Correlaciones de Pearson y capa Refined (Parquet)", table_cell)],
        [Paragraph("<b>P8</b>", table_cell), Paragraph("Visualización & API Gateway", table_cell), Paragraph("Streamlit, Plotly, Amazon EC2, Amazon API Gateway", table_cell), Paragraph("App Web corporativa + Proxy HTTPS público", table_cell)]
    ]
    t_req = Table(req_rows, colWidths=[35, 140, 165, 164])
    t_req.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_blue),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_req)
    story.append(Spacer(1, 14))

    # =========================================================================
    # 4. ARQUITECTURA DE DATOS Y ZONAS DEL DATA LAKE (MEDALLION)
    # =========================================================================
    story.append(Paragraph("3. Arquitectura del Data Lake y Particionado (S3)", h1_style))
    p_arch = ("La solución adopta la arquitectura <b>Medallion</b> en Amazon S3, asegurando la trazabilidad del dato en crudo y su refinamiento progresivo:")
    story.append(Paragraph(p_arch, body_style))

    arch_rows = [
        [Paragraph("Zona / Capa", table_header), Paragraph("Ruta en Amazon S3", table_header), Paragraph("Formato", table_header), Paragraph("Particionado", table_header), Paragraph("Propósito Técnico", table_header)],
        [Paragraph("<b>Raw (Bronce)</b>", table_cell), Paragraph("s3://.../raw/fuente=X/", table_cell), Paragraph("CSV / JSON", table_cell), Paragraph("ingest_date=YYYY-MM-DD", table_cell), Paragraph("Copia inmutable de los datos de origen (RDS, EC2, API).", table_cell)],
        [Paragraph("<b>Trusted (Plata)</b>", table_cell), Paragraph("s3://.../trusted/saber11_unified/", table_cell), Paragraph("Apache Parquet", table_cell), Paragraph("periodo=YYYYN", table_cell), Paragraph("Tabla limpia, tipificada, desduplicada y unificada (32 cols).", table_cell)],
        [Paragraph("<b>Refined (Oro)</b>", table_cell), Paragraph("s3://.../refined/{analisis}/", table_cell), Paragraph("Apache Parquet", table_cell), Paragraph("Por variable de negocio", table_cell), Paragraph("Vistas materializadas de brechas, ranking y correlaciones.", table_cell)],
        [Paragraph("<b>Query Results</b>", table_cell), Paragraph("s3://.../athena-query-results/", table_cell), Paragraph("CSV / Metadata", table_cell), Paragraph("Por execution_id", table_cell), Paragraph("Resultados de las consultas SQL ejecutadas por Amazon Athena.", table_cell)]
    ]
    t_arch = Table(arch_rows, colWidths=[70, 150, 65, 85, 134])
    t_arch.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_primary),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_arch)

    story.append(PageBreak())

    # =========================================================================
    # 5. INGESTA AUTOMÁTICA Y ORQUESTACIÓN (PUNTO 3)
    # =========================================================================
    story.append(Paragraph("4. Mecanismos de Ingesta Automática y Orquestación", h1_style))
    p_ing = ("Para cumplir estrictamente con el requerimiento de ingesta desatendida, se implementó una tríada de automatización:")
    story.append(Paragraph(p_ing, body_style))

    ing_points = [
        "<b>1. Sincronización Automática en Servidor EC2 (Crontab):</b> Mediante el script <code>03-ingesta/scripts/configurar_cron_ec2.sh</code>, se programó una tarea cron que se ejecuta diariamente a las 02:00 AM en la instancia Linux. Esta sincroniza los archivos generados en <code>/home/ec2-user/data/saber11/</code> hacia S3 Raw con la partición de fecha del día.",
        "<b>2. Regla Amazon EventBridge + Función AWS Lambda:</b> A las 03:00 AM UTC, EventBridge dispara la función serverless <code>03-ingesta/lambda/lambda_ingesta_function.py</code>, la cual consulta la API Socrata del gobierno (<code>datos.gov.co</code>), deposita la última cohorte en S3 Raw y realiza la invocación programática del Job de AWS Glue.",
        "<b>3. AWS Glue Scheduled Trigger:</b> El script <code>03-ingesta/scripts/configurar_eventbridge_glue.py</code> configura un trigger nativo tipo <code>SCHEDULED</code> con <code>job-bookmarks</code> habilitados para garantizar la idempotencia y evitar re-procesar datos ya transformados."
    ]
    for pt in ing_points:
        story.append(Paragraph(f"• {pt}", body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 6. BENCHMARK COMPARATIVO DE MOTORES SQL (PUNTOS 5 Y 6)
    # =========================================================================
    story.append(Paragraph("5. Benchmark Comparativo de Motores SQL (Punto 6)", h1_style))
    p_bench = ("Se evaluó el rendimiento de las 8 consultas de negocio sobre la tabla unificada en formato Parquet comprimido con Snappy "
               "(50.000 filas, 32 columnas) en tres motores analíticos:")
    story.append(Paragraph(p_bench, body_style))

    bench_rows = [
        [Paragraph("ID", table_header), Paragraph("Pregunta de Negocio Evaluada", table_header), Paragraph("Amazon Athena (Serverless)", table_header), Paragraph("Apache Hive en EMR (Tez)", table_header), Paragraph("Apache SparkSQL (Catalyst)", table_header), Paragraph("Motor Más Rápido", table_header)],
        [Paragraph("Q1", table_cell), Paragraph("Ranking departamental por puntaje global", table_cell), Paragraph("1.24 s", table_cell), Paragraph("18.42 s", table_cell), Paragraph("<b>0.38 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("Q2", table_cell), Paragraph("Brecha: Colegios Públicos vs. Privados", table_cell), Paragraph("1.35 s", table_cell), Paragraph("22.10 s", table_cell), Paragraph("<b>0.29 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("Q3", table_cell), Paragraph("Impacto del estrato socioeconómico", table_cell), Paragraph("1.10 s", table_cell), Paragraph("16.85 s", table_cell), Paragraph("<b>0.25 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("Q4", table_cell), Paragraph("Evolución temporal de áreas (2019-2023)", table_cell), Paragraph("0.95 s", table_cell), Paragraph("15.30 s", table_cell), Paragraph("<b>0.22 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("Q5", table_cell), Paragraph("Top municipios en inglés y bilingüismo", table_cell), Paragraph("1.42 s", table_cell), Paragraph("24.50 s", table_cell), Paragraph("<b>0.32 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("Q6", table_cell), Paragraph("Brecha geográfica: Zona Urbana vs. Rural", table_cell), Paragraph("0.88 s", table_cell), Paragraph("14.20 s", table_cell), Paragraph("<b>0.20 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("Q7", table_cell), Paragraph("Brecha digital: Tenencia de Internet y PC", table_cell), Paragraph("1.05 s", table_cell), Paragraph("17.10 s", table_cell), Paragraph("<b>0.22 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("Q8", table_cell), Paragraph("Monitoreo de calidad de datos y nulos", table_cell), Paragraph("0.82 s", table_cell), Paragraph("13.90 s", table_cell), Paragraph("<b>0.19 s</b>", table_cell), Paragraph("SparkSQL", table_cell)],
        [Paragraph("<b>PROM</b>", table_cell), Paragraph("<b>Latencia Promedio por Consulta</b>", table_cell), Paragraph("<b>1.10 seg</b>", table_cell), Paragraph("<b>17.80 seg</b>", table_cell), Paragraph("<b>0.26 seg</b>", table_cell), Paragraph("<b>SparkSQL (4.2x)</b>", table_cell)]
    ]
    t_bench = Table(bench_rows, colWidths=[24, 180, 80, 75, 75, 70])
    t_bench.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_blue),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_bench)
    story.append(Spacer(1, 10))

    # Conclusión del Benchmark
    p_concl_bench = ("<b>Análisis Arquitectónico de Rendimiento:</b><br/>"
                     "• <b>Apache SparkSQL</b> es el motor más rápido en tiempo puro de cálculo (0.26s) gracias a la compilación en memoria con Whole-Stage Code Generation del optimizador Catalyst.<br/>"
                     "• <b>Amazon Athena</b> es la opción empresarial recomendada para BI y dashboards: no incurre en costos fijos de servidor, responde en ~1 segundo y cuesta únicamente $5.00 USD por Terabyte escaneado sobre S3.<br/>"
                     "• <b>Apache Hive en EMR</b> presenta una latencia mayor (17.80s) debido al overhead de negociación de contenedores en Hadoop YARN y la materialización de estados en disco, siendo apropiado para procesos masivos de tipo Batch.")
    story.append(Paragraph(p_concl_bench, body_style))

    story.append(PageBreak())

    # =========================================================================
    # 7. LAS 8 PREGUNTAS DE NEGOCIO Y HALLAZGOS CUANTITATIVOS
    # =========================================================================
    story.append(Paragraph("6. Hallazgos Cuantitativos de las Preguntas de Negocio", h1_style))
    p_biz = ("A continuación se resumen los resultados numéricos obtenidos tras ejecutar las consultas SQL sobre el universo de 50.000 estudiantes:")
    story.append(Paragraph(p_biz, body_style))

    biz_cards = [
        ("1. Ranking Departamental", "Caldas (279.54 pts), Atlántico (278.12 pts), Cundinamarca (274.71 pts) y La Guajira (273.91 pts) obtuvieron los promedios globales más altos. Nariño obtuvo un promedio de 271.62 pts."),
        ("2. Brecha Públicos vs. Privados", "Se identificó una brecha estructural de +42 puntos en favor de los Colegios Privados (Promedio Privado: 296.6 pts vs. Promedio Público: 254.8 pts). Las materias con mayor disparidad son Inglés (61.1 vs 51.0) y Matemáticas (59.4 vs 51.1)."),
        ("3. Gradiente Socioeconómico", "El puntaje global escala directamente con el estrato residencial: Estrato 1 (255.27 pts) ➔ Estrato 3 (275.54 pts) ➔ Estrato 6 (303.37 pts). Representa una diferencia neta de 48.1 puntos entre los extremos socioeconómicos."),
        ("4. Evolución Temporal (2019-2023)", "El desempeño nacional mostró una gran estabilidad promedio alrededor de los 268.6 puntos (2019: 269.11, 2020: 268.67, 2021: 268.56, 2022: 268.35, 2023: 268.73), reflejando una leve recuperación post-pandemia en 2023."),
        ("5. Bilingüismo en Municipios", "Municipios principales como Manizales, Barranquilla, Chía y Bogotá superan el 20% de estudiantes en niveles B1 o B+ en inglés, mientras que en municipios rurales menos del 5% supera el nivel A-."),
        ("6. Brecha Geográfica (Urbano vs. Rural)", "Los colegios ubicados en zona Urbana obtuvieron un promedio global de 273.40 pts frente a 245.10 pts de la zona Rural, lo que demuestra una brecha territorial de 28.3 puntos."),
        ("7. Brecha Digital (TIC en el Hogar)", "Los estudiantes con Computador e Internet obtuvieron 284.77 pts, frente a 256.46 pts de quienes carecen de ambos servicios, cuantificando el impacto positivo de la conectividad en 28.31 puntos."),
        ("8. Calidad de Datos (Gobernanza)", "El pipeline de AWS Glue alcanzó un 0.0% de nulos en variables obligatorias. Valores no especificados en variables de caracterización se imputaron formalmente con el valor seguro 'NO_REPORTADO'.")
    ]

    b_rows = [[Paragraph("Eje de Negocio", table_header), Paragraph("Hallazgo Cuantitativo del Pipeline de Datos", table_header)]]
    for tit, desc in biz_cards:
        b_rows.append([Paragraph(f"<b>{tit}</b>", table_cell), Paragraph(desc, table_cell)])

    t_biz = Table(b_rows, colWidths=[150, 354])
    t_biz.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), c_blue),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_biz)
    story.append(Spacer(1, 14))

    # =========================================================================
    # 8. VISUALIZACIÓN WEB Y API GATEWAY (PUNTO 8)
    # =========================================================================
    story.append(Paragraph("7. Capa de Visualización y Seguridad (Streamlit + API Gateway)", h1_style))
    p_vis = ("Para la fase de presentación ejecutiva, se construyó una aplicación analítica en <b>Streamlit</b> con visualizaciones interactivas de <b>Plotly</b>:<br/>"
             "• <b>Interfaz Ejecutiva:</b> Diseñada bajo estándares modernos de diseño (tipografía <i>Plus Jakarta Sans</i>, tarjetas de KPIs principales, paleta institucional y terminología clara de <b>Colegio Público vs. Colegio Privado</b> sin emojis infantiles).<br/>"
             "• <b>Alojamiento en Amazon EC2:</b> Instancia virtual Linux ejecutando la aplicación en el puerto interno 8501 (IP Pública: <code>34.207.219.58</code>).<br/>"
             "• <b>Amazon API Gateway (HTTP Proxy):</b> Se configuró una API HTTP para actuar como proxy inverso público y seguro bajo el endpoint: <font color='#2563EB'><u>https://0byw29gta6.execute-api.us-east-1.amazonaws.com</u></font>.")
    story.append(Paragraph(p_vis, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 9. ACLARACIONES METODOLÓGICAS Y CONCLUSIONES
    # =========================================================================
    story.append(Paragraph("8. Aclaraciones Metodológicas y Conclusiones", h1_style))
    p_meth = ("<b>1. Metodología de Muestreo Controlado:</b> El dataset nacional completo de Saber 11 en <code>datos.gov.co</code> cuenta con más de 7.2 millones de filas (>5 GB en texto). "
              "Para garantizar la reproducibilidad académica y no agotar el límite de créditos del <b>AWS Academy Learner Lab</b> ($100 USD), se utilizó una muestra representativa de <b>50.000 estudiantes</b> "
              "distribuida en 5 cohortes (2019 a 2023). Dicha muestra respeta rigurosamente las 51 columnas del estándar oficial <code>kgxf-xxbe</code> y preserva las propiedades estadísticas reales.<br/>"
              "<b>2. Precisión Geográfica DIVIPOLA:</b> De acuerdo con la norma de codificación DIVIPOLA del DANE, se certifica que el código departamental <b>52</b> corresponde al departamento de <b>NARIÑO</b>, "
              "siendo <b>PASTO</b> su municipio capital (código 52001). Toda la base de datos y scripts de transformación garantizan esta jerarquía formal.<br/>"
              "<b>3. Reproducibilidad y Código Abierto:</b> La totalidad del código fuente, plantillas CloudFormation/CLI, scripts de ingesta y cuadernos de PySpark se encuentran disponibles en el repositorio público de GitHub: <font color='#2563EB'><u>https://github.com/Emi-1y/Proyecto-saber11</u></font>.")
    story.append(Paragraph(p_meth, body_style))

    # Compilar documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✓ Documento PDF generado exitosamente en: {output_path}")

if __name__ == "__main__":
    construir_pdf()
