import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import plotly.express as px
import io
import os

# Configuración de la página
st.set_page_config(page_title="Punto de Venta - Viva Vinto", layout="wide", page_icon="🍔")

# Definir la zona horaria de Bolivia
ZONA_HORARIA_BO = pytz.timezone("America/La_Paz")

# ARCHIVO LOCAL DE PERSISTENCIA ( Evita que se borren los datos al salir )
ARCHIVO_CSV = "ventas_viva_vinto.csv"

# Función para cargar datos guardados automáticamente
def cargar_ventas():
    if os.path.exists(ARCHIVO_CSV):
        try:
            return pd.read_csv(ARCHIVO_CSV)
        except Exception:
            pass
    return pd.DataFrame(columns=[
        "ID", "Fecha", "Hora", "Producto", "Categoría", "Cantidad", 
        "Precio Unit. (Bs.)", "Total (Bs.)", "Método Pago", "Atendido Por"
    ])

# Función para guardar en disco cada vez que hay un cambio
def guardar_ventas():
    st.session_state["ventas"].to_csv(ARCHIVO_CSV, index=False)

# Inicialización de la base de datos persistente
if "ventas" not in st.session_state:
    st.session_state["ventas"] = cargar_ventas()

# Carta de Productos y Precios del Restaurante Viva Vinto
CARTA_PRODUCTOS = {
    "Phampaku": {
        "Phampaku Pato": 90,
        "Phampaku Pollo": 75,
        "Phampaku Lechon": 85,
        "Phampaku Mixto": 100
    },
    "Bebidas": {
        "Cerveza Paceña 620ml": 18,
        "Gaseosa 2L": 15,
        "Jarra de Chicha": 20,
        "Agua Mineral": 8
    },
    "Guarniciones": {
        "Porción de Arroz": 5,
        "Porción de Papa": 5,
        "Porción de Ensalada": 5
    }
}

# Barra Lateral de Navegación
st.sidebar.title("Navegación")
opcion = st.sidebar.radio("Ir a:", ["📝 Registrar Venta", "📊 Panel de control e informes", "📋 Carta y Precios"])

# ==================== MÓDULO 1: REGISTRAR VENTA ====================
if opcion == "📝 Registrar Venta":
    st.title("📝 Registro de Ventas - Restaurante Viva Vinto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        categoria = st.selectbox("Seleccionar Categoría:", list(CARTA_PRODUCTOS.keys()))
        producto = st.selectbox("Seleccionar Producto:", list(CARTA_PRODUCTOS[categoria].keys()))
        precio_unitario = float(CARTA_PRODUCTOS[categoria][producto])
        st.info(f"**Precio Unitario:** {precio_unitario:.2f} Bs.")

    with col2:
        cantidad = st.number_input("Cantidad:", min_value=1, value=1, step=1)
        metodo_pago = st.selectbox("Método de Pago:", ["Efectivo", "QR / Transferencia", "Tarjeta"])
        atendido_por = st.selectbox("Atendido por:", ["Caja 1", "Caja 2", "Garzón 1", "Garzón 2"])

    total = float(cantidad * precio_unitario)
    st.markdown(f"### **Total a cobrar:** `{total:.2f} Bs.`")

    if st.button("🔴 Registrar Venta", use_container_width=True):
        nuevo_id = 1 if st.session_state["ventas"].empty else int(st.session_state["ventas"]["ID"].max()) + 1
        
        # Capturar fecha y hora exacta de Bolivia
        ahora_bo = datetime.now(ZONA_HORARIA_BO)
        fecha_str = ahora_bo.strftime("%Y-%m-%d")
        hora_str = ahora_bo.strftime("%H:%M:%S")

        nueva_fila = pd.DataFrame([{
            "ID": int(nuevo_id),
            "Fecha": fecha_str,
            "Hora": hora_str,
            "Producto": producto,
            "Categoría": categoria,
            "Cantidad": int(cantidad),
            "Precio Unit. (Bs.)": float(precio_unitario),
            "Total (Bs.)": float(total),
            "Método Pago": metodo_pago,
            "Atendido Por": atendido_por
        }])

        st.session_state["ventas"] = pd.concat([st.session_state["ventas"], nueva_fila], ignore_index=True)
        guardar_ventas() # Guardado permanente automático
        st.success(f"✅ ¡Venta ID #{nuevo_id} registrada con éxito y GUARDADA a las {hora_str}!")

    st.markdown("---")
    st.subheader("📋 Historial de Ventas")
    st.dataframe(st.session_state["ventas"], use_container_width=True)

    # Exportar, Eliminar y Reiniciar Día
    col_acc1, col_acc2, col_acc3 = st.columns(3)

    with col_acc1:
        st.subheader("📥 Exportar Datos")
        if not st.session_state["ventas"].empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                st.session_state["ventas"].to_excel(writer, index=False, sheet_name='Ventas')
            
            ahora_bo = datetime.now(ZONA_HORARIA_BO)
            st.download_button(
                label="📊 Descargar Historial en Excel (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"Ventas_Viva_Vinto_{ahora_bo.strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("Registra al menos una venta para poder exportar a Excel.")

    with col_acc2:
        st.subheader("🗑️ Eliminar Venta")
        if not st.session_state["ventas"].empty:
            ids_disponibles = st.session_state["ventas"]["ID"].tolist()
            id_a_eliminar = st.selectbox("Selecciona el ID a eliminar:", ids_disponibles)
            
            if st.button("❌ Eliminar Venta Seleccionada", type="secondary", use_container_width=True):
                st.session_state["ventas"] = st.session_state["ventas"][st.session_state["ventas"]["ID"] != id_a_eliminar]
                guardar_ventas() # Actualizar guardado
                st.success(f"Venta ID #{id_a_eliminar} eliminada correctamente.")
                st.rerun()
        else:
            st.info("No hay ventas para eliminar.")

    with col_acc3:
        st.subheader("🚨 Control de Caja")
        if not st.session_state["ventas"].empty:
            if st.button("🔴 Reiniciar / Vaciar Base de Datos", type="primary", use_container_width=True):
                st.session_state["ventas"] = pd.DataFrame(columns=[
                    "ID", "Fecha", "Hora", "Producto", "Categoría", "Cantidad", 
                    "Precio Unit. (Bs.)", "Total (Bs.)", "Método Pago", "Atendido Por"
                ])
                guardar_ventas() # Guardar estado vacío
                st.success("La base de datos se ha limpiado por completo.")
                st.rerun()

# ==================== MÓDULO 2: PANEL DE CONTROL E INFORMES ====================
elif opcion == "📊 Panel de control e informes":
    st.title("📊 Dashboard e Informes de Ventas")

    if st.session_state["ventas"].empty:
        st.warning("Aún no hay ventas registradas. Registra una nueva venta para generar el reporte.")
    else:
        df = st.session_state["ventas"].copy()
        
        df["Total (Bs.)"] = pd.to_numeric(df["Total (Bs.)"], errors="coerce").fillna(0)
        df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)

        # EXPORTAR REPORTES DEL DASHBOARD EN EXCEL
        st.subheader("📥 Exportar Reporte Ejecutivo del Dashboard")
        buffer_dash = io.BytesIO()
        with pd.ExcelWriter(buffer_dash, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Historial Ventas')
            
            arqueo_summary = df.groupby("Método Pago", as_index=False)["Total (Bs.)"].sum()
            arqueo_summary.to_excel(writer, index=False, sheet_name='Resumen Pago')
            
            cat_summary = df.groupby("Categoría", as_index=False).agg({"Cantidad": "sum", "Total (Bs.)": "sum"})
            cat_summary.to_excel(writer, index=False, sheet_name='Resumen Categoría')
            
            prod_summary = df.groupby("Producto", as_index=False).agg({"Cantidad": "sum", "Total (Bs.)": "sum"})
            prod_summary.to_excel(writer, index=False, sheet_name='Ventas por Producto')

        ahora_bo = datetime.now(ZONA_HORARIA_BO)
        st.download_button(
            label="📈 Descargar Reporte de Dashboard Completo en Excel (.xlsx)",
            data=buffer_dash.getvalue(),
            file_name=f"Reporte_Dashboard_Viva_Vinto_{ahora_bo.strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.markdown("---")

        # Métricas principales
        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos Totales", f"{df['Total (Bs.)'].sum():.2f} BS.")
        m2.metric("Total Platos / Productos Ventas", f"{int(df['Cantidad'].sum())} unids.")
        m3.metric("Ticket Promedio", f"{df['Total (Bs.)'].mean():.2f} BS.")

        st.markdown("---")

        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Ingresos por Método de Pago (Arqueo)")
            arqueo = df.groupby("Método Pago", as_index=False)["Total (Bs.)"].sum()
            fig_arqueo = px.bar(
                arqueo, 
                x="Método Pago", 
                y="Total (Bs.)", 
                text_auto=".2f",
                color="Método Pago",
                title="Total Recaudado por Método de Pago"
            )
            fig_arqueo.update_layout(showlegend=False, yaxis_title="Total (Bs.)", xaxis_title="")
            fig_arqueo.update_yaxes(tickformat=",.0f") # Bloquea los decimales
            st.plotly_chart(fig_arqueo, use_container_width=True)

        with c2:
            st.subheader("Ventas Totales por Categoría")
            cat_ventas = df.groupby("Categoría", as_index=False)["Total (Bs.)"].sum()
            fig_cat = px.bar(
                cat_ventas, 
                x="Categoría", 
                y="Total (Bs.)", 
                text_auto=".2f",
                color="Categoría",
                title="Ventas Acumuladas por Categoría"
            )
            fig_cat.update_layout(showlegend=False, yaxis_title="Total (Bs.)", xaxis_title="")
            fig_cat.update_yaxes(tickformat=",.0f") # Bloquea los decimales
            st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("---")

        # SECCIÓN: GRÁFICO INDIVIDUAL POR PLATO
        st.subheader("🔍 Análisis Detallado por Plato / Producto")
        
        platos_vendidos = df["Producto"].unique()
        plato_seleccionado = st.selectbox("Elige un plato para ver sus ventas individuales:", platos_vendidos)
        
        df_plato = df[df["Producto"] == plato_seleccionado]
        
        fig_plato = px.bar(
            df_plato,
            x="Hora",
            y="Cantidad",
            color="Atendido Por",
            title=f"Unidades Vendidas de '{plato_seleccionado}' por Hora",
            text_auto=True
        )
        fig_plato.update_layout(yaxis_title="Cantidad de Platos", xaxis_title="Hora de Venta")
        fig_plato.update_yaxes(tickformat=",.0f") # Bloquea los decimales
        
        col_p1, col_p2 = st.columns(2)
        col_p1.metric(f"Total {plato_seleccionado} Vendidos", f"{int(df_plato['Cantidad'].sum())} unids.")
        col_p2.metric(f"Dinero Generado por {plato_seleccionado}", f"{df_plato['Total (Bs.)'].sum():.2f} Bs.")
        
        st.plotly_chart(fig_plato, use_container_width=True)

# ==================== MÓDULO 3: CARTA Y PRECIOS ====================
elif opcion == "📋 Carta y Precios":
    st.title("📋 Menú y Precios Oficiales")
    for cat, prods in CARTA_PRODUCTOS.items():
        st.subheader(f"📌 {cat}")
        df_cat = pd.DataFrame(list(prods.items()), columns=["Producto", "Precio (Bs.)"])
        st.table(df_cat)
