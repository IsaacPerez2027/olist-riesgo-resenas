# Olist: del pedido a la reseña

Proyecto final: riesgo de mala reseña de un pedido, segmentación de vendedores y análisis de sentimiento de los comentarios, con una API (FastAPI) y una app (Streamlit).

**Entrega individual de:** Isaac Aníbal Pérez Pérez

## Enlaces

| Qué | Enlace |
|---|---|
| App (Streamlit Community Cloud) | https://isaac-perez-olist-riesgo.streamlit.app |
| API (Render) | https://olist-riesgo-resenas.onrender.com |

## Estructura

- `Proyecto_Final.ipynb`: el cuaderno completo (datos, modelos, métricas y conclusiones).
- `api/`: la API para Render (`uvicorn main:app --host 0.0.0.0 --port $PORT`, Python 3.13), con el endpoint `POST /riesgo`.
- `app/`: la app de Streamlit (`app/streamlit_app.py`); la URL de la API va en `st.secrets["API_URL"]`.
- `preparacion.py`: las funciones que crean las variables; las usan el cuaderno y la API.
- `ficha_modelo.md`, `umbral.json`, `modelo_riesgo.joblib`, `sentimiento_muestra.csv`, `desacuerdos_clasificados.csv`: salidas y archivos de apoyo del cuaderno.

La contraseña de la base de datos no se guarda en ningún archivo: el cuaderno la pide al ejecutarse.
