# 08 - Visualización y Web App Streamlit con API Gateway

## 1. Objetivo
Construir una aplicación interactiva en **Streamlit** respaldada por visualizaciones analíticas (Plotly / Matplotlib) y desplegarla en una instancia EC2, exponiendo los endpoints o el servicio mediante **Amazon API Gateway** (HTTP API / Reverse Proxy) para acceso seguro y escalable.

---

## 2. Requisitos Previos
- Datos en capa `refined/` y/o conexión a Athena con `awswrangler` o `boto3`.
- Librerías `streamlit` y `plotly` instaladas.
- Instancia EC2 con Security Group permitiendo tráfico en el puerto configurado (ej. 8501).

---

## 3. Comandos Exactos Numerados

### Paso 1: Probar la aplicación Streamlit en local
```bash
streamlit run 08-visualizacion-api/app/app.py
```
Abre en el navegador: `http://localhost:8501`.

### Paso 2: Desplegar la aplicación en la instancia EC2
```bash
# Conectar a la instancia EC2
ssh -i ~/.ssh/saber11-key.pem ec2-user@IP_PUBLICA_EC2

# Clonar o actualizar el repositorio en EC2
git clone https://github.com/TU_USUARIO/proyecto3-saber11-aws.git
cd proyecto3-saber11-aws
pip3 install -r requirements.txt

# Iniciar Streamlit como servicio o con nohup / tmux
nohup streamlit run 08-visualizacion-api/app/app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

### Paso 3: Configurar Amazon API Gateway (HTTP API)
Crear una API HTTP en API Gateway con integración tipo **HTTP Proxy** apuntando a `http://IP_PUBLICA_EC2:8501`:
```bash
aws apigatewayv2 create-api \
    --name saber11-dashboard-api \
    --protocol-type HTTP \
    --target "http://IP_PUBLICA_EC2:8501" \
    --region us-east-1
```

---

## 4. Resultado Esperado
- Dashboard interactivo con:
  - Selector de periodo académico y departamento.
  - Mapas de calor y coropléticos de Colombia por puntaje promedio.
  - Gráficos de barras interactivos comparando naturaleza oficial vs no oficial.
  - Boxplots de dispersión socioeconómica.
- URL pública generada por API Gateway accesible desde cualquier navegador.

---

## 5. Evidencias (Pantallazos)
<!-- Adjuntar capturas en ../evidencias/ -->
- `evidencias/08_streamlit_dashboard_main.png`: Vista general del dashboard en Streamlit con mapas y métricas.
- `evidencias/08_api_gateway_route_console.png`: Configuración del endpoint en Amazon API Gateway.
- `evidencias/08_app_accessible_browser.png`: Acceso al dashboard a través de la URL de API Gateway.
