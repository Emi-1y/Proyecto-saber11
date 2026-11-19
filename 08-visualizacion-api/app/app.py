import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import boto3
import io

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Saber 11 - ICFES | Data Lake AWS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #4B5563;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def cargar_datos():
    bucket = os.getenv("S3_BUCKET_NAME", "saber11-datalake-885601272401")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    # 1. Intentar cargar desde S3
    try:
        s3 = boto3.client("s3", region_name=region)
        # Buscar el archivo parquet en trusted
        response = s3.list_objects_v2(Bucket=bucket, Prefix="trusted/saber11_unified/", MaxKeys=50)
        parquet_keys = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".parquet")]
        if parquet_keys:
            dfs = []
            for key in parquet_keys[:10]: # Muestra representativa para interactividad rápida
                obj = s3.get_object(Bucket=bucket, Key=key)
                dfs.append(pd.read_parquet(io.BytesIO(obj["Body"].read())))
            if dfs:
                return pd.concat(dfs, ignore_index=True)
    except Exception as e:
        pass

    # 2. Fallback a datos locales
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local_trusted = os.path.join(base_dir, "04-procesamiento-glue-spark", "data", "trusted", "saber11_unified")
    if os.path.exists(local_trusted):
        return pd.read_parquet(local_trusted)
    
    # 3. Fallback a muestra de EC2 / RDS
    csv_sample = os.path.join(base_dir, "02-fuentes-datos", "data", "rds", "resultados_2019_2020.csv")
    if os.path.exists(csv_sample):
        return pd.read_csv(csv_sample)

    return pd.DataFrame()

df = cargar_datos()

# Encabezado
st.markdown('<div class="main-title">🎓 Data Lake Saber 11 (ICFES) — Analítica Educativa</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Arquitectura Data Lakehouse en AWS | Fuentes federadas: RDS MariaDB + EC2 CSVs + Socrata API | Motor: Glue + Athena + PySpark</div>', unsafe_allow_html=True)

if df.empty:
    st.warning("No se encontraron datos disponibles. Asegúrate de ejecutar el pipeline de ingestión y Glue ETL.")
    st.stop()

# Barra lateral de filtros
st.sidebar.header("🔍 Filtros de Consulta")

periodos = sorted(list(df["periodo"].dropna().unique())) if "periodo" in df.columns else []
selected_periodos = st.sidebar.multiselect("Periodo Académico:", periodos, default=periodos)

deptos = sorted(list(df["cole_depto_ubicacion"].dropna().unique())) if "cole_depto_ubicacion" in df.columns else []
selected_deptos = st.sidebar.multiselect("Departamento:", deptos, default=deptos[:8] if len(deptos) > 8 else deptos)

naturalezas = list(df["cole_naturaleza"].dropna().unique()) if "cole_naturaleza" in df.columns else []
selected_nat = st.sidebar.multiselect("Naturaleza del Colegio:", naturalezas, default=naturalezas)

# Filtrar DataFrame
df_filtered = df.copy()
if selected_periodos and "periodo" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["periodo"].isin(selected_periodos)]
if selected_deptos and "cole_depto_ubicacion" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["cole_depto_ubicacion"].isin(selected_deptos)]
if selected_nat and "cole_naturaleza" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["cole_naturaleza"].isin(selected_nat)]

# Tarjetas KPI Principales
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_est = len(df_filtered)
prom_global = df_filtered["punt_global"].mean() if "punt_global" in df_filtered.columns else 0
prom_mat = df_filtered["punt_matematicas"].mean() if "punt_matematicas" in df_filtered.columns else 0
prom_lec = df_filtered["punt_lectura_critica"].mean() if "punt_lectura_critica" in df_filtered.columns else 0
prom_ing = df_filtered["punt_ingles"].mean() if "punt_ingles" in df_filtered.columns else 0

with kpi1:
    st.metric("Total Evaluados", f"{total_est:,}")
with kpi2:
    st.metric("Puntaje Global", f"{prom_global:.1f} / 500")
with kpi3:
    st.metric("Matemáticas", f"{prom_mat:.1f} / 100")
with kpi4:
    st.metric("Lectura Crítica", f"{prom_lec:.1f} / 100")
with kpi5:
    st.metric("Inglés", f"{prom_ing:.1f} / 100")

st.markdown("---")

# Pestañas de análisis temático
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Ranking Departamental",
    "⚖️ Brecha Oficial vs No Oficial",
    "🌐 Brecha Digital & Estrato",
    "📈 Tendencia Temporal"
])

with tab1:
    st.subheader("Ranking de Departamentos por Desempeño Global")
    if "cole_depto_ubicacion" in df_filtered.columns and "punt_global" in df_filtered.columns:
        depto_agg = df_filtered.groupby("cole_depto_ubicacion")["punt_global"].agg(["mean", "count", "std"]).reset_index()
        depto_agg = depto_agg.sort_values(by="mean", ascending=True)
        depto_agg.columns = ["Departamento", "Puntaje_Promedio", "Total_Estudiantes", "Desv_Estandar"]
        
        fig_rank = px.bar(
            depto_agg,
            x="Puntaje_Promedio",
            y="Departamento",
            orientation="h",
            color="Puntaje_Promedio",
            color_continuous_scale="Blues",
            text=depto_agg["Puntaje_Promedio"].apply(lambda x: f"{x:.1f}"),
            title="Puntaje Global Promedio por Departamento"
        )
        fig_rank.update_layout(height=500, xaxis_title="Puntaje Global Promedio (0-500)", yaxis_title="")
        st.plotly_chart(fig_rank, use_container_width=True)

with tab2:
    st.subheader("Comparativa: Colegios Oficiales vs. No Oficiales")
    col_a, col_b = st.columns(2)
    
    if "cole_naturaleza" in df_filtered.columns:
        with col_a:
            areas = ["punt_lectura_critica", "punt_matematicas", "punt_c_naturales", "punt_sociales_ciudadanas", "punt_ingles"]
            areas_disponibles = [a for a in areas if a in df_filtered.columns]
            if areas_disponibles:
                agg_nat = df_filtered.groupby("cole_naturaleza")[areas_disponibles].mean().reset_index()
                agg_melt = agg_nat.melt(id_vars="cole_naturaleza", var_name="Area", value_name="Puntaje")
                agg_melt["Area"] = agg_melt["Area"].str.replace("punt_", "").str.replace("_", " ").str.title()
                
                fig_nat = px.bar(
                    agg_melt,
                    x="Area",
                    y="Puntaje",
                    color="cole_naturaleza",
                    barmode="group",
                    title="Promedio por Componente Disciplinar",
                    color_discrete_map={"OFICIAL": "#2563EB", "NO OFICIAL": "#10B981"}
                )
                fig_nat.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_nat, use_container_width=True)

        with col_b:
            if "cole_area_ubicacion" in df_filtered.columns and "punt_global" in df_filtered.columns:
                fig_box = px.box(
                    df_filtered,
                    x="cole_naturaleza",
                    y="punt_global",
                    color="cole_area_ubicacion",
                    title="Distribución del Puntaje Global (Urbano vs. Rural)",
                    color_discrete_map={"URBANO": "#3B82F6", "RURAL": "#F59E0B"}
                )
                st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    st.subheader("Impacto del Acceso a Internet, Computador y Estrato")
    col_c, col_d = st.columns(2)
    
    with col_c:
        if "fami_tieneinternet" in df_filtered.columns and "fami_tienecomputador" in df_filtered.columns and "punt_global" in df_filtered.columns:
            df_filtered["Acceso_TIC"] = "Sin TIC"
            df_filtered.loc[(df_filtered["fami_tieneinternet"] == "Si") & (df_filtered["fami_tienecomputador"] == "No"), "Acceso_TIC"] = "Solo Internet"
            df_filtered.loc[(df_filtered["fami_tieneinternet"] == "No") & (df_filtered["fami_tienecomputador"] == "Si"), "Acceso_TIC"] = "Solo PC"
            df_filtered.loc[(df_filtered["fami_tieneinternet"] == "Si") & (df_filtered["fami_tienecomputador"] == "Si"), "Acceso_TIC"] = "Internet + PC"

            tic_agg = df_filtered.groupby("Acceso_TIC")["punt_global"].agg(["mean", "count"]).reset_index()
            tic_agg.columns = ["Condicion_TIC", "Promedio_Global", "Total"]
            tic_agg = tic_agg.sort_values(by="Promedio_Global", ascending=False)
            
            fig_tic = px.bar(
                tic_agg,
                x="Condicion_TIC",
                y="Promedio_Global",
                color="Promedio_Global",
                color_continuous_scale="Purples",
                text=tic_agg["Promedio_Global"].apply(lambda x: f"{x:.1f}"),
                title="Puntaje Global según Disponibilidad de Herramientas TIC"
            )
            st.plotly_chart(fig_tic, use_container_width=True)

    with col_d:
        if "fami_estratovivienda" in df_filtered.columns and "punt_global" in df_filtered.columns:
            estrato_agg = df_filtered[df_filtered["fami_estratovivienda"] != "NO_REPORTADO"].groupby("fami_estratovivienda")["punt_global"].mean().reset_index()
            estrato_agg = estrato_agg.sort_values(by="punt_global", ascending=True)
            
            fig_estrato = px.line(
                estrato_agg,
                x="fami_estratovivienda",
                y="punt_global",
                markers=True,
                title="Gradiente Socioeconómico: Puntaje vs Estrato Residencial",
                labels={"fami_estratovivienda": "Estrato", "punt_global": "Promedio Puntaje Global"}
            )
            fig_estrato.update_traces(line_color="#8B5CF6", line_width=3)
            st.plotly_chart(fig_estrato, use_container_width=True)

with tab4:
    st.subheader("Evolución de Puntajes a lo Largo de los Periodos")
    if "periodo" in df_filtered.columns and "punt_global" in df_filtered.columns:
        periodo_agg = df_filtered.groupby("periodo")[["punt_global", "punt_matematicas", "punt_lectura_critica", "punt_ingles"]].mean().reset_index()
        fig_evol = px.line(
            periodo_agg,
            x="periodo",
            y=["punt_global", "punt_matematicas", "punt_lectura_critica", "punt_ingles"],
            markers=True,
            title="Trayectoria Histórica por Periodo Evaluado",
            labels={"value": "Puntaje Promedio", "periodo": "Periodo", "variable": "Componente"}
        )
        st.plotly_chart(fig_evol, use_container_width=True)

st.markdown("---")
st.caption("Proyecto de Big Data en AWS: Resultados Pruebas Saber 11 ICFES | Pipeline end-to-end reproducible.")
