import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Configuración de la página
st.set_page_config(page_title="Punto de Venta - Viva Vinto", layout="wide", page_icon="🍔")

# Definir la zona horaria de Bolivia
ZONA_HORARIA_BO = pytz.timezone("America/La_Paz")

# Inicialización de la base de datos temporal (Session State)
if "ventas" not in st.session_state:
    st.session_state["ventas"] = pd.DataFrame(columns=[
        "ID", "Fecha", "Hora", "Producto", "Categoría", "Cantidad", 
        "Precio Unit. (Bs.)", "Total (Bs.)", "Método Pago", "Atendido Por"
    ])

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
        nuevo_id = len(st.session_state["ventas"]) + 1
        
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
        st.success(f"✅ ¡Venta ID #{nuevo_id} registrada con éxito a las {hora_str} (Hora Bolivia)!")

    st.markdown("---")
    st.subheader("📋 Historial de Ventas")
    st.dataframe(st.session_state["ventas"], use_container_width=True)

    # Exportar e Eliminar
    col_acc1, col_acc2 = st.columns(2)

    with col_acc1:
        st.subheader("📥 Exportar Datos")
        if not st.session_state["ventas"].empty:
            import io
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
            id_a_eliminar = st.selectbox("Selecciona el ID de la venta a eliminar:", ids_disponibles)
            
            if st.button("❌ Eliminar Venta Seleccionada", type="secondary", use_container_width=True):
                st.session_state["ventas"] = st.session_state["ventas"][st.session_state["ventas"]["ID"] != id_a_eliminar]
                st.success(f"Venta ID #{id_a_eliminar} eliminada correctamente.")
                st.rerun()
        else:
            st.info("No hay ventas para eliminar.")

# ==================== MÓDULO 2: PANEL DE CONTROL E INFORMES ====================
elif opcion == "📊 Panel de control e informes":
    st.title("📊 Dashboard e Informes de Ventas")

    if st.session_state["ventas"].empty:
        st.warning("Aún no hay ventas registradas para generar el reporte. Registra algunas ventas primero.")
    else:
        df = st.session_state["ventas"].copy()
        
        # Convertir datos a números
        df["Total (Bs.)"] = pd.to_numeric(df["Total (Bs.)"], errors="coerce").fillna(0)
        df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)

        # Métricas principales
        m1, m2, m3 = st.columns(3)
        m1.metric("Ingresos Totales", f"{df['Total (Bs.)'].sum():.2f} BS.")
        m2.metric("Total Platos / Productos Ventas", f"{int(df['Cantidad'].sum())} unids.")
        m3.metric("Ticket Promedio", f"{df['Total (Bs.)'].mean():.2f} BS.")

        st.markdown("---")

        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Ingresos por Método de Pago (Arqueo)")
            arqueo = df.groupby("Método Pago")["Total (Bs.)"].sum()
            st.bar_chart(arqueo)

        with c2:
            st.subheader("Ventas Totales por Categoría")
            cat_ventas = df.groupby("Categoría")["Total (Bs.)"].sum()
            st.bar_chart(cat_ventas)

# ==================== MÓDULO 3: CARTA Y PRECIOS ====================
elif opcion == "📋 Carta y Precios":
    st.title("📋 Menú y Precios Oficiales")
    for cat, prods in CARTA_PRODUCTOS.items():
        st.subheader(f"📌 {cat}")
        df_cat = pd.DataFrame(list(prods.items()), columns=["Producto", "Precio (Bs.)"])
        st.table(df_cat)
