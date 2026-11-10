"""Variables del modelo de riesgo. Entrada: las 17 columnas del contrato (sin `mala_resena`).

El pipeline guardado importa `crear_variables` desde este archivo, por eso viaja junto al .joblib.
No usa nada de la reseña: solo lo que se conoce en el momento de la entrega.
"""
import numpy as np
import pandas as pd

FECHAS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
CATEGORICAS = ["estado_cliente", "estado_vendedor", "categoria", "tipo_pago"]
NUMERICAS = [
    "dias_retraso", "entrego_tarde", "dias_prometidos", "dias_aprobacion", "dias_despacho",
    "dias_transporte", "mes_compra", "dia_semana_compra", "hora_compra", "fin_de_semana",
    "n_items", "n_vendedores", "precio_total", "flete_total", "peso_total_g", "fotos_promedio",
    "cuotas_max", "flete_sobre_precio", "precio_por_item", "peso_por_item", "mismo_estado",
]


def _dias(fin, inicio):
    return (fin - inicio).dt.total_seconds() / 86400


def crear_variables(pedidos: pd.DataFrame) -> pd.DataFrame:
    """Convierte las columnas del contrato en las variables del modelo."""
    d = pedidos.copy()
    for col in FECHAS:
        d[col] = pd.to_datetime(d[col], errors="coerce")
    for col in ["n_items", "n_vendedores", "precio_total", "flete_total", "peso_total_g",
                "fotos_promedio", "cuotas_max"]:
        d[col] = pd.to_numeric(d[col], errors="coerce")

    v = pd.DataFrame(index=d.index)
    entrega, prometida = d["order_delivered_customer_date"], d["order_estimated_delivery_date"]
    compra = d["order_purchase_timestamp"]

    v["dias_retraso"] = _dias(entrega, prometida)                 # >0: llegó después de lo prometido
    v["entrego_tarde"] = (v["dias_retraso"] > 0).astype(float)
    v["dias_prometidos"] = _dias(prometida, compra)
    v["dias_aprobacion"] = _dias(d["order_approved_at"], compra)
    v["dias_despacho"] = _dias(d["order_delivered_carrier_date"], compra)
    v["dias_transporte"] = _dias(entrega, d["order_delivered_carrier_date"])
    v["mes_compra"] = compra.dt.month
    v["dia_semana_compra"] = compra.dt.dayofweek
    v["hora_compra"] = compra.dt.hour
    v["fin_de_semana"] = (compra.dt.dayofweek >= 5).astype(float)

    for col in ["n_items", "n_vendedores", "precio_total", "flete_total", "peso_total_g",
                "fotos_promedio", "cuotas_max"]:
        v[col] = d[col]
    v["flete_sobre_precio"] = d["flete_total"] / d["precio_total"].replace(0, np.nan)
    v["precio_por_item"] = d["precio_total"] / d["n_items"].replace(0, np.nan)
    v["peso_por_item"] = d["peso_total_g"] / d["n_items"].replace(0, np.nan)
    v["mismo_estado"] = (d["estado_cliente"] == d["estado_vendedor"]).astype(float)

    for col in CATEGORICAS:
        v[col] = d[col].astype(object).where(d[col].notna(), "desconocido").astype(str)
    return v[NUMERICAS + CATEGORICAS]
