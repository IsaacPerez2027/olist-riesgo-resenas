# Ficha del modelo · Riesgo de mala reseña (Olist)

## 1. Para qué sirve y para qué no
**Sirve para** decidir a qué clientes llamar justo después de que se les entrega un pedido, cuando el equipo de atención solo puede llamar a **1 de cada 10 pedidos**. El modelo ordena los pedidos del más al menos probable de terminar en una reseña de 1 o 2 estrellas.

**No sirve para** juzgar o sancionar a vendedores, decidir reembolsos automáticos, ni predecir cosas distintas a la reseña. Tampoco sirve con pedidos que no estén entregados.

## 2. Datos
- Origen: datos públicos de Olist (licencia MIT), cargados en la base del curso, esquema `final`.
- Periodo: pedidos comprados entre el 15 de septiembre de 2016 y el 31 de mayo de 2018.
- **77.304 pedidos**: solo los entregados, con fecha de entrega conocida y con reseña.
- Se excluyeron los pedidos cancelados, en camino o sin reseña, porque no se sabe (todavía) si habrá mala reseña.
- Siempre se usa la reseña más reciente de cada pedido. Los textos de los comentarios **no** entran al modelo: aparecen después de la reseña y serían trampa.

## 3. Qué tan bien funciona
Validación **por fecha**: se entrenó con pedidos hasta febrero de 2018 y se probó con marzo a mayo de 2018 (20.422 pedidos).

| De cada 10 clientes que llamamos… | Mala reseña |
|---|---|
| Eligiendo al azar | 1 o 2 (≈ 15 de cada 100) |
| Con la regla «llamar a los más atrasados» | ≈ 6 de cada 10 |
| **Con el modelo** | **≈ 7 de cada 10** (precisión en el 10 % de mayor riesgo: 0,67) |

Pero el resultado cambia mucho según el mes. En **marzo de 2018** hubo muchos retrasos (21 % de las entregas llegó tarde) y el modelo acertó ≈ 8 de cada 10. En **abril y mayo**, con pocos retrasos (5 % y 8 %), acertó **entre 4 y 5 de cada 10**; la regla del retraso solo 3 de cada 10. El modelo gana en los dos casos, pero lo que se puede esperar en un mes tranquilo es más cercano al segundo.

## 4. Límites conocidos
- **Depende mucho de los retrasos.** La variable que más pesa es si el pedido llegó tarde. Cuando casi nadie llega tarde, el modelo tiene menos en qué apoyarse y su acierto baja.
- Solo conoce lo que está en el contrato (fechas, precios, peso, lugares, pago). No sabe nada del producto real, del vendedor en concreto ni de lo que el cliente esperaba.
- Se entrenó con 2016 a mayo de 2018: si Olist cambia su logística o sus clientes, el modelo envejece.
- Algunas categorías y estados tienen pocos pedidos y sus resultados son menos confiables.

## 5. A quién afecta un error
- **Falso positivo** (se llama a alguien que iba a quedar contento): se gasta una llamada, y a veces molesta al cliente. Costo bajo.
- **Falso negativo** (no se llama a quien iba a dejar mala reseña): el problema sigue y la reputación del vendedor y de la plataforma se daña. Es el error más caro, pero con 1 llamada de cada 10 siempre habrá muchos.
- **Riesgo de mal uso:** usar el puntaje para castigar vendedores. Muchos retrasos dependen del transportista y no del vendedor; castigarlos por eso sería injusto.

## 6. Recomendación
- Usarlo **como ayuda**, nunca como decisión automática: una persona de atención al cliente decide a quién llamar con el puntaje a la vista.
- Revisar cada mes el porcentaje real de malas reseñas entre los pedidos llamados y los no llamados.
- Volver a entrenarlo cada 3 meses, o antes si cambia la tasa de entregas tardías.
- Guardar los casos en que el modelo falló para entender por qué.
