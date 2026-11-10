"""App de Streamlit · Olist: riesgo de mala reseña. Consulta la API (la URL va en st.secrets["API_URL"])."""
import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

DATOS = Path(__file__).parent / "datos"
CAMPOS_FECHA = ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
                "order_delivered_customer_date", "order_estimated_delivery_date"]

st.set_page_config(page_title="Olist · Riesgo de mala reseña", page_icon="📦", layout="wide")


@st.cache_data
def leerCsv(nombre):
    return pd.read_csv(DATOS / nombre)


def urlApi():
    try:
        return st.secrets["API_URL"].rstrip("/")
    except Exception:
        return None


def pedirRiesgo(pedido):
    """Llama a POST /riesgo. Devuelve (resultado, mensaje_de_error)."""
    url = urlApi()
    if not url:
        return None, "Falta configurar la dirección de la API (API_URL en los secretos de la app)."
    try:
        r = requests.post(f"{url}/riesgo", json=pedido, timeout=90)
    except requests.exceptions.Timeout:
        return None, "La API tardó demasiado en responder. Si estaba dormida (plan gratuito), prueba de nuevo en un minuto."
    except requests.exceptions.RequestException:
        return None, "No se pudo conectar con la API. Puede estar dormida o apagada: espera un minuto y vuelve a intentar."
    if r.status_code == 422:
        return None, "La API rechazó los datos del pedido (algún valor no es válido). Revisa los campos."
    if r.status_code != 200:
        return None, f"La API respondió con un error ({r.status_code}). Intenta de nuevo más tarde."
    return r.json(), None


def paginaRiesgo():
    st.title("📦 Riesgo de mala reseña de un pedido")
    st.write("Elige un pedido recién entregado, ajusta lo que quieras y la app le pregunta a la API qué tan probable "
             "es que el cliente deje 1 o 2 estrellas.")
    pedidos = leerCsv("pedidos_muestra.csv")
    col1, col2 = st.columns([1, 2])
    with col1:
        idx = st.selectbox("Pedido de ejemplo", range(len(pedidos)),
                           format_func=lambda i: f"{i + 1} · {pedidos.loc[i, 'order_id'][:8]}… ({pedidos.loc[i, 'estado_cliente']})")
        fila = pedidos.loc[idx]
        st.caption("Estrellas reales que dejó este cliente: " + ("⭐ 1 o 2 (mala reseña)" if fila["mala_resena"] == 1 else "3 o más"))
    with col2:
        editado = st.data_editor(fila.drop("mala_resena").astype(str).to_frame("valor"), width="stretch",
                                 disabled=["_index"], height=640, key=f"ed{idx}")
    if st.button("Calcular riesgo", type="primary"):
        pedido = {}
        for campo, valor in editado["valor"].items():
            pedido[campo] = None if valor in ("nan", "None", "") else valor
        for campo in ["n_items", "n_vendedores"]:
            pedido[campo] = int(float(pedido[campo]))
        for campo in ["precio_total", "flete_total", "peso_total_g", "fotos_promedio", "cuotas_max"]:
            pedido[campo] = None if pedido[campo] is None else float(pedido[campo])
        with st.spinner("Consultando la API… (si estaba dormida puede tardar hasta un minuto)"):
            res, error = pedirRiesgo(pedido)
        if error:
            st.warning(error)
        else:
            a, b, c = st.columns(3)
            a.metric("Probabilidad de mala reseña", f"{res['probabilidad']:.0%}")
            b.metric("¿Riesgo alto?", "Sí, llamar" if res["riesgo_alto"] else "No")
            c.metric("Umbral (10 % de mayor riesgo)", f"{res['umbral']:.0%}")
            st.progress(min(res["probabilidad"], 1.0))


def paginaComentarios():
    st.title("💬 ¿Coincide lo que escriben con las estrellas?")
    muestra = leerCsv("sentimiento_muestra.csv")
    cruce = leerCsv("cruce_estrellas.csv").set_index("estrellas")
    st.write(f"Muestra de **{len(muestra):,}** comentarios en portugués, clasificados con un modelo preentrenado "
             "(*cardiffnlp/twitter-xlm-roberta-base-sentiment*). Las estrellas se agrupan igual que el modelo: "
             "1–2 negativo, 3 neutro, 4–5 positivo.")
    st.metric("Porcentaje de coincidencia", f"{muestra['coincide'].mean():.1%}")
    st.subheader("Estrellas contra sentimiento")
    st.dataframe(cruce.style.background_gradient(cmap="Blues", axis=None), width="stretch")
    st.subheader("Desacuerdos clasificados")
    st.dataframe(leerCsv("desacuerdos_clasificados.csv"), width="stretch", hide_index=True)
    st.subheader("Explora los desacuerdos")
    c1, c2 = st.columns(2)
    estrellas = c1.multiselect("Estrellas", [1, 2, 3, 4, 5], default=[5, 1])
    sentimiento = c2.multiselect("Sentimiento del modelo", ["negative", "neutral", "positive"],
                                 default=["negative", "positive"])
    filtro = muestra[(~muestra["coincide"]) & muestra["estrellas"].isin(estrellas) & muestra["sentimiento"].isin(sentimiento)]
    st.caption(f"{len(filtro)} comentarios")
    st.dataframe(filtro[["estrellas", "sentimiento", "confianza", "comentario"]].head(200), width="stretch", hide_index=True)


def paginaVendedores():
    st.title("🏪 ¿Qué tipos de vendedores hay?")
    perfiles = leerCsv("perfiles_segmentos.csv")
    vendedores = leerCsv("segmentos_vendedores.csv")
    st.write(f"Se segmentaron **{len(vendedores):,}** vendedores con al menos 10 pedidos entregados usando K-Means "
             "(k = 4; ver la justificación en el cuaderno).")
    st.subheader("Perfil y acción por segmento")
    for _, s in perfiles.iterrows():
        with st.expander(f"{s['nombre_segmento']} · {int(s['vendedores'])} vendedores"):
            st.write(f"**Acción:** {s['accion']}")
            st.dataframe(s.drop(["nombre_segmento", "accion", "vendedores"]).to_frame("mediana"), width="stretch")
    st.subheader("Los grupos en dos dimensiones")
    st.image(str(DATOS / "segmentos_pca.png"))
    st.subheader("Vendedores")
    estados = sorted(vendedores["estado_vendedor"].unique())
    filtro = st.multiselect("Estado del vendedor", estados, default=[])
    tabla = vendedores if not filtro else vendedores[vendedores["estado_vendedor"].isin(filtro)]
    st.dataframe(tabla.drop(columns=["segmento"]), width="stretch", hide_index=True)


def paginaFicha():
    st.markdown((DATOS / "ficha_modelo.md").read_text(encoding="utf-8"))
    metricas = json.loads((DATOS / "metricas.json").read_text(encoding="utf-8"))
    with st.expander("Cifras de la validación por fecha"):
        st.json({k: metricas[k] for k in ["azar", "regla_retraso", "regresion_logistica", "xgboost", "por_mes"]})


pagina = st.navigation([
    st.Page(paginaRiesgo, title="Riesgo de un pedido", icon="📦", default=True),
    st.Page(paginaComentarios, title="Comentarios", icon="💬"),
    st.Page(paginaVendedores, title="Pregunta abierta: vendedores", icon="🏪"),
    st.Page(paginaFicha, title="Ficha del modelo", icon="📄"),
])
pagina.run()
