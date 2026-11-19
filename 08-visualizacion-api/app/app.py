import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import boto3
import io

# 1. Configuración de la página
st.set_page_config(
    page_title="Saber 11 Analytics | Data Lakehouse AWS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS modernos y sobrios (Sin emojis, tipografía elegante, cards estilo SaaS)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Ocultar barra superior por defecto de streamlit si aplica */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .header-badge {
        display: inline-block;
        padding: 4px 12px;
        background: #EFF6FF;
        color: #1D4ED8;
        border: 1px solid #BFDBFE;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }

    .header-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin: 0;
    }

    .header-description {
        font-size: 0.95rem;
        color: #64748B;
        margin-top: 0.35rem;
        margin-bottom: 1.8rem;
    }

    /* KPI Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        margin-bottom: 1.8rem;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }

    .kpi-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07);
    }

    .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.65rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.1;
    }

    .kpi-sub {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 4px;
    }

    /* Contenedores de Gráficos */
    .chart-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
    }

    /* Ajustes de filtros laterales */
    .sidebar-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #0F172A;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Carga y normalización de datos
@st.cache_data(ttl=3600)
def cargar_datos():
    bucket = os.getenv("S3_BUCKET_NAME", "saber11-datalake-885601272401")
    region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    
    # 1. Intentar cargar desde S3 Trusted (Parquet)
    try:
        s3 = boto3.client("s3", region_name=region)
        response = s3.list_objects_v2(Bucket=bucket, Prefix="trusted/saber11_unified/", MaxKeys=50)
        parquet_keys = [obj["Key"] for obj in response.get("Contents", []) if obj["Key"].endswith(".parquet")]
        if parquet_keys:
            dfs = []
            for key in parquet_keys[:10]:
                obj = s3.get_object(Bucket=bucket, Key=key)
                dfs.append(pd.read_parquet(io.BytesIO(obj["Body"].read())))
            if dfs:
                df = pd.concat(dfs, ignore_index=True)
                return normalizar_dataset(df)
    except Exception:
        pass

    # 2. Fallback local: Parquet
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    local_trusted = os.path.join(base_dir, "04-procesamiento-glue-spark", "data", "trusted", "saber11_unified")
    if os.path.exists(local_trusted):
        return normalizar_dataset(pd.read_parquet(local_trusted))
    
    # 3. Fallback local: CSV de muestra
    csv_sample = os.path.join(base_dir, "02-fuentes-datos", "data", "rds", "resultados_2019_2020.csv")
    if os.path.exists(csv_sample):
        return normalizar_dataset(pd.read_csv(csv_sample))

    return pd.DataFrame()

def normalizar_dataset(df):
    if df.empty:
        return df

    # Reemplazar terminología oficial/no oficial por Público / Privado
    if "cole_naturaleza" in df.columns:
        df["cole_naturaleza"] = df["cole_naturaleza"].astype(str).str.upper()
        df["tipo_colegio"] = df["cole_naturaleza"].replace({
            "OFICIAL": "Público",
            "NO OFICIAL": "Privado",
            "NO_OFICIAL": "Privado"
        })
    else:
        df["tipo_colegio"] = "No Especificado"

    # Corrección de geografía
    if "cole_depto_ubicacion" in df.columns:
        df["cole_depto_ubicacion"] = df["cole_depto_ubicacion"].replace({
            "PASTO": "NARIÑO",
            "pasto": "NARIÑO"
        })

    # Normalizar zonas
    if "cole_area_ubicacion" in df.columns:
        df["cole_area_ubicacion"] = df["cole_area_ubicacion"].astype(str).str.capitalize()

    return df

df = cargar_datos()

# 4. Header de la aplicación
st.markdown('<span class="header-badge">Arquitectura Data Lakehouse AWS</span>', unsafe_allow_html=True)
st.markdown('<h1 class="header-title">Analítica de Resultados Saber 11 (ICFES)</h1>', unsafe_allow_html=True)
st.markdown('<p class="header-description">Evaluación de rendimiento académico, factores socioeconómicos y brechas estructurales en Colombia.</p>', unsafe_allow_html=True)

if df.empty:
    st.error("No se encontraron datos disponibles. Verifique la conexión con S3 o el archivo local.")
    st.stop()

# 5. Barra lateral con filtros sobrios y claros
st.sidebar.markdown('<div class="sidebar-title">Filtros de Análisis</div>', unsafe_allow_html=True)

# Filtro Periodo
periodos_disponibles = sorted(list(df["periodo"].dropna().unique())) if "periodo" in df.columns else []
selected_periodos = st.sidebar.multiselect(
    "Periodo Académico:",
    options=periodos_disponibles,
    default=periodos_disponibles
)

# Filtro Departamento
deptos_disponibles = sorted(list(df["cole_depto_ubicacion"].dropna().unique())) if "cole_depto_ubicacion" in df.columns else []
selected_deptos = st.sidebar.multiselect(
    "Departamento:",
    options=deptos_disponibles,
    default=deptos_disponibles[:8] if len(deptos_disponibles) > 8 else deptos_disponibles
)

# Filtro Tipo de Colegio (Público vs Privado)
tipos_disponibles = sorted(list(df["tipo_colegio"].dropna().unique()))
selected_tipos = st.sidebar.multiselect(
    "Tipo de Colegio:",
    options=tipos_disponibles,
    default=tipos_disponibles
)

# Aplicar filtros
df_view = df.copy()
if selected_periodos and "periodo" in df_view.columns:
    df_view = df_view[df_view["periodo"].isin(selected_periodos)]
if selected_deptos and "cole_depto_ubicacion" in df_view.columns:
    df_view = df_view[df_view["cole_depto_ubicacion"].isin(selected_deptos)]
if selected_tipos and "tipo_colegio" in df_view.columns:
    df_view = df_view[df_view["tipo_colegio"].isin(selected_tipos)]

# 6. Tarjetas de Métricas Principales (KPIs Ejecutivos)
total_est = len(df_view)
prom_global = df_view["punt_global"].mean() if "punt_global" in df_view.columns and total_est > 0 else 0
prom_mat = df_view["punt_matematicas"].mean() if "punt_matematicas" in df_view.columns and total_est > 0 else 0
prom_lec = df_view["punt_lectura_critica"].mean() if "punt_lectura_critica" in df_view.columns and total_est > 0 else 0
prom_ing = df_view["punt_ingles"].mean() if "punt_ingles" in df_view.columns and total_est > 0 else 0

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-label">Estudiantes Evaluados</div>
        <div class="kpi-value">{total_est:,}</div>
        <div class="kpi-sub">Muestra filtrada</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Puntaje Global Promedio</div>
        <div class="kpi-value">{prom_global:.1f}</div>
        <div class="kpi-sub">Escala sobre 500</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Promedio Matemáticas</div>
        <div class="kpi-value">{prom_mat:.1f}</div>
        <div class="kpi-sub">Escala sobre 100</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Lectura Crítica</div>
        <div class="kpi-value">{prom_lec:.1f}</div>
        <div class="kpi-sub">Escala sobre 100</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Inglés</div>
        <div class="kpi-value">{prom_ing:.1f}</div>
        <div class="kpi-sub">Escala sobre 100</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 7. Navegación por Módulos Temáticos (Tabs limpios sin emojis)
tab_ranking, tab_brecha, tab_socio, tab_evolucion, tab_datos = st.tabs([
    "Ranking Departamental",
    "Colegios Públicos vs. Privados",
    "Factores Socioeconómicos y TIC",
    "Evolución Histórica",
    "Explorador de Datos"
])

# Paleta de colores sobria
COLOR_PUBLICO = "#2563EB"   # Azul clásico
COLOR_PRIVADO = "#059669"   # Verde esmeralda sobrio
PALETA_CATEGORICA = [COLOR_PUBLICO, COLOR_PRIVADO, "#7C3AED", "#D97706", "#DC2626"]

# --- TAB 1: RANKING DEPARTAMENTAL ---
with tab_ranking:
    st.markdown("#### Desempeño Promedio por Departamento")
    st.caption("Puntaje global consolidado por departamento de ubicación de la institución educativa.")
    
    if "cole_depto_ubicacion" in df_view.columns and "punt_global" in df_view.columns and total_est > 0:
        agg_depto = df_view.groupby("cole_depto_ubicacion")["punt_global"].agg(["mean", "count"]).reset_index()
        agg_depto.columns = ["Departamento", "Promedio", "Total"]
        agg_depto = agg_depto.sort_values(by="Promedio", ascending=True)

        fig_rank = px.bar(
            agg_depto,
            x="Promedio",
            y="Departamento",
            orientation="h",
            color="Promedio",
            color_continuous_scale="Blues",
            text=agg_depto["Promedio"].apply(lambda x: f"{x:.1f}"),
            labels={"Promedio": "Puntaje Global Promedio", "Departamento": ""}
        )
        fig_rank.update_layout(
            template="plotly_white",
            height=460,
            margin=dict(l=0, r=20, t=10, b=30),
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9")
        )
        fig_rank.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig_rank, use_container_width=True)

# --- TAB 2: BRECHA PÚBLICO VS PRIVADO ---
with tab_brecha:
    st.markdown("#### Comparativa: Instituciones Públicas vs. Privadas")
    st.caption("Diferencial de desempeño por área de conocimiento y zona geográfica.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        areas = ["punt_matematicas", "punt_lectura_critica", "punt_c_naturales", "punt_sociales_ciudadanas", "punt_ingles"]
        areas_disp = [a for a in areas if a in df_view.columns]
        if areas_disp and "tipo_colegio" in df_view.columns and total_est > 0:
            agg_areas = df_view.groupby("tipo_colegio")[areas_disp].mean().reset_index()
            agg_melt = agg_areas.melt(id_vars="tipo_colegio", var_name="Area", value_name="Puntaje")
            
            nombres_areas = {
                "punt_matematicas": "Matemáticas",
                "punt_lectura_critica": "Lectura Crítica",
                "punt_c_naturales": "Ciencias Naturales",
                "punt_sociales_ciudadanas": "Sociales y Ciudadanas",
                "punt_ingles": "Inglés"
            }
            agg_melt["Area"] = agg_melt["Area"].map(nombres_areas)

            fig_areas = px.bar(
                agg_melt,
                x="Area",
                y="Puntaje",
                color="tipo_colegio",
                barmode="group",
                title="Puntaje Promedio por Área del Conocimiento",
                color_discrete_map={"Público": COLOR_PUBLICO, "Privado": COLOR_PRIVADO},
                labels={"tipo_colegio": "Sector", "Puntaje": "Puntaje (0 - 100)", "Area": ""}
            )
            fig_areas.update_layout(
                template="plotly_white",
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(range=[0, 100], gridcolor="#F1F5F9")
            )
            st.plotly_chart(fig_areas, use_container_width=True)

    with col2:
        if "cole_area_ubicacion" in df_view.columns and "punt_global" in df_view.columns and total_est > 0:
            fig_box = px.box(
                df_view,
                x="tipo_colegio",
                y="punt_global",
                color="cole_area_ubicacion",
                title="Distribución del Puntaje Global (Urbano vs. Rural)",
                color_discrete_map={"Urbano": "#3B82F6", "Rural": "#F59E0B"},
                labels={"tipo_colegio": "Sector", "punt_global": "Puntaje Global", "cole_area_ubicacion": "Zona"}
            )
            fig_box.update_layout(
                template="plotly_white",
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(gridcolor="#F1F5F9")
            )
            st.plotly_chart(fig_box, use_container_width=True)

# --- TAB 3: FACTORES SOCIOECONÓMICOS Y TIC ---
with tab_socio:
    st.markdown("#### Impacto del Nivel Socioeconómico y Brecha Digital")
    st.caption("Relación entre estrato de vivienda, tenencia de herramientas tecnológicas y rendimiento global.")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if "fami_estratovivienda" in df_view.columns and "punt_global" in df_view.columns and total_est > 0:
            df_estrato = df_view[~df_view["fami_estratovivienda"].isin(["NO_REPORTADO", "No reportado", ""])]
            agg_estrato = df_estrato.groupby("fami_estratovivienda")["punt_global"].agg(["mean", "count"]).reset_index()
            agg_estrato.columns = ["Estrato", "Promedio", "Total"]
            agg_estrato = agg_estrato.sort_values(by="Promedio", ascending=True)

            fig_est = px.bar(
                agg_estrato,
                x="Estrato",
                y="Promedio",
                color="Promedio",
                color_continuous_scale="Blues",
                text=agg_estrato["Promedio"].apply(lambda x: f"{x:.1f}"),
                title="Puntaje Global Promedio según Estrato Socioeconómico",
                labels={"Promedio": "Puntaje Global", "Estrato": ""}
            )
            fig_est.update_layout(
                template="plotly_white",
                height=380,
                coloraxis_showscale=False,
                yaxis=dict(gridcolor="#F1F5F9")
            )
            fig_est.update_traces(textposition="outside")
            st.plotly_chart(fig_est, use_container_width=True)

    with col4:
        if "fami_tieneinternet" in df_view.columns and "fami_tienecomputador" in df_view.columns and "punt_global" in df_view.columns and total_est > 0:
            df_tic = df_view.copy()
            df_tic["Acceso_TIC"] = "Sin Internet ni PC"
            df_tic.loc[(df_tic["fami_tieneinternet"] == "Si") & (df_tic["fami_tienecomputador"] == "No"), "Acceso_TIC"] = "Solo Internet"
            df_tic.loc[(df_tic["fami_tieneinternet"] == "No") & (df_tic["fami_tienecomputador"] == "Si"), "Acceso_TIC"] = "Solo Computador"
            df_tic.loc[(df_tic["fami_tieneinternet"] == "Si") & (df_tic["fami_tienecomputador"] == "Si"), "Acceso_TIC"] = "Internet + Computador"

            agg_tic = df_tic.groupby("Acceso_TIC")["punt_global"].agg(["mean", "count"]).reset_index()
            agg_tic.columns = ["Condicion_TIC", "Promedio", "Total"]
            agg_tic = agg_tic.sort_values(by="Promedio", ascending=False)

            fig_tic = px.bar(
                agg_tic,
                x="Condicion_TIC",
                y="Promedio",
                color="Promedio",
                color_continuous_scale="Teal",
                text=agg_tic["Promedio"].apply(lambda x: f"{x:.1f}"),
                title="Brecha Digital: Acceso a Internet y Computador",
                labels={"Promedio": "Puntaje Global", "Condicion_TIC": ""}
            )
            fig_tic.update_layout(
                template="plotly_white",
                height=380,
                coloraxis_showscale=False,
                yaxis=dict(gridcolor="#F1F5F9")
            )
            fig_tic.update_traces(textposition="outside")
            st.plotly_chart(fig_tic, use_container_width=True)

# --- TAB 4: EVOLUCIÓN HISTÓRICA ---
with tab_evolucion:
    st.markdown("#### Tendencia Temporal por Periodo Académico")
    st.caption("Seguimiento del puntaje global y competencias disciplinares a través de las cohortes evaluadas.")
    
    if "periodo" in df_view.columns and "punt_global" in df_view.columns and total_est > 0:
        agg_periodo = df_view.groupby("periodo")[["punt_global", "punt_matematicas", "punt_lectura_critica", "punt_ingles"]].mean().reset_index()
        agg_periodo.rename(columns={
            "punt_global": "Puntaje Global",
            "punt_matematicas": "Matemáticas",
            "punt_lectura_critica": "Lectura Crítica",
            "punt_ingles": "Inglés"
        }, inplace=True)

        fig_evol = px.line(
            agg_periodo,
            x="periodo",
            y=["Puntaje Global", "Matemáticas", "Lectura Crítica", "Inglés"],
            markers=True,
            title="Evolución de Promedios por Cohorte",
            labels={"value": "Puntaje Promedio", "periodo": "Periodo", "variable": "Componente"},
            color_discrete_sequence=["#0F172A", "#2563EB", "#059669", "#7C3AED"]
        )
        fig_evol.update_layout(
            template="plotly_white",
            height=400,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig_evol, use_container_width=True)

# --- TAB 5: EXPLORADOR DE DATOS ---
with tab_datos:
    st.markdown("#### Explorador de Microdatos Filtrados")
    st.caption("Visualice y descargue la muestra filtrada de registros para auditoría o análisis externo.")
    
    cols_mostrar = [c for c in [
        "periodo", "cole_depto_ubicacion", "cole_mcpio_ubicacion", "tipo_colegio",
        "cole_area_ubicacion", "fami_estratovivienda", "punt_global", "punt_matematicas",
        "punt_lectura_critica", "punt_ingles", "desemp_ingles"
    ] if c in df_view.columns]

    st.dataframe(
        df_view[cols_mostrar].head(100),
        use_container_width=True,
        hide_index=True
    )

    csv_data = df_view[cols_mostrar].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar datos filtrados (CSV)",
        data=csv_data,
        file_name="saber11_muestra_filtrada.csv",
        mime="text/csv"
    )

# 8. Pie de página sobrio
st.markdown("---")
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; color: #94A3B8; font-size: 0.8rem;">
    <div>Data Lakehouse Saber 11 | ICFES Colombia</div>
    <div>AWS Architecture: S3 · Glue · Athena · PySpark · Streamlit</div>
</div>
""", unsafe_allow_html=True)
