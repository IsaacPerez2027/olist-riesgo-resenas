"""API de riesgo de mala reseña (Olist). Render: uvicorn main:app --host 0.0.0.0 --port $PORT"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

AQUI = Path(__file__).parent
CONTRATO = ["order_id", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
            "order_delivered_customer_date", "order_estimated_delivery_date", "estado_cliente", "n_items",
            "n_vendedores", "precio_total", "flete_total", "peso_total_g", "fotos_promedio", "categoria",
            "estado_vendedor", "tipo_pago", "cuotas_max"]

app = FastAPI(title="Riesgo de mala reseña · Olist", version="1.0",
              description="Dado un pedido recién entregado, devuelve la probabilidad de que reciba 1 o 2 estrellas.")
modelo = joblib.load(AQUI / "modelo_riesgo.joblib")
UMBRAL = json.loads((AQUI / "umbral.json").read_text(encoding="utf-8"))["umbral"]


class Pedido(BaseModel):
    """Las 17 columnas del contrato (todas menos `mala_resena`)."""
    order_id: str
    order_purchase_timestamp: datetime = Field(examples=["2018-03-07 22:02:23"])
    order_approved_at: Optional[datetime] = None
    order_delivered_carrier_date: Optional[datetime] = None
    order_delivered_customer_date: datetime
    order_estimated_delivery_date: datetime
    estado_cliente: str = Field(min_length=2, max_length=2)
    n_items: int = Field(ge=1)
    n_vendedores: int = Field(ge=1)
    precio_total: float = Field(ge=0)
    flete_total: float = Field(ge=0)
    peso_total_g: Optional[float] = Field(default=None, ge=0)
    fotos_promedio: Optional[float] = Field(default=None, ge=0)
    categoria: Optional[str] = None
    estado_vendedor: str = Field(min_length=2, max_length=2)
    tipo_pago: Optional[str] = None
    cuotas_max: Optional[float] = Field(default=None, ge=0)


@app.get("/")
def estado():
    return {"estado": "ok", "mensaje": "API de riesgo de mala reseña (Olist)"}


@app.post("/riesgo")
def riesgo(pedido: Pedido):
    fila = pd.DataFrame([pedido.model_dump()])[CONTRATO]
    try:
        p = float(modelo.predict_proba(fila)[0, 1])
    except Exception as error:      # el modelo no pudo calcular: se avisa sin exponer detalles internos
        raise HTTPException(status_code=500, detail=f"No se pudo calcular el riesgo: {type(error).__name__}")
    return {"probabilidad": round(p, 4), "riesgo_alto": p >= UMBRAL, "umbral": round(UMBRAL, 4)}
