import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Punto de Venta - Viva Vinto",
    page_icon="🍽️",
    layout="wide"
)

# Estilos visuales personalizados
st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #4A1521; }
    .stButton>button { background-color: #4A1521; color: white; border-radius: 8px; font-weight: bold; }
    .stButton>button:hover { background-color: #8C2D38; color: white; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Base de Datos de Productos (Menú Oficial Viva Vinto)
# -----------------------------------------------------------------------------
MENU_DATA = [
    # Phampaku
    {"Categoría": "Phampaku", "Producto": "Phampaku Pato", "Precio": 90.0},
    {"Categoría": "Phampaku", "Producto": "Phampaku Lechon", "Precio": 75.0},
    {"Categoría": "Phampaku", "Producto": "Phampaku Pollo", "Precio": 75.0},
    {"Categoría": "Phampaku", "Producto": "Phampaku Cordero", "Precio": 75.0},
    {"Categoría": "Phampaku", "Producto": "Phampaku Laping", "Precio": 75.0},
    # Phampaku Mixto
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Pato - Lechon", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Pato - Laping", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Pato - Cordero", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Pato - Pollo", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Lechon - Laping", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Lechon - Pollo", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Lechon - Cordero", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Laping - Pollo", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Laping - Cordero", "Precio": 75.0},
    {"Categoría": "Phampaku Mixto", "Producto": "Mixto Cordero - Pollo", "Precio": 75.0},
    # Picante
    {"Categoría": "Picante", "Producto": "Picante De Pollo", "Precio": 75.0},
    {"Categoría": "Picante", "Producto": "Picante De Lengua", "Precio": 75.0},
    {"Categoría": "Picante", "Producto": "Picante Mixto", "Precio": 75.0},
    # Otros Platos
    {"Categoría": "Otros Platos", "Producto": "Chanka de Pollo", "Precio": 55.0},
    {"Categoría": "Otros Platos", "Producto": "Charque", "Precio": 75.0},
    {"Categoría": "Otros Platos", "Producto": "Pique", "Precio": 90.0},
    # Para Picar
    {"Categoría": "Para Picar", "Producto": "Mote de Haba", "Precio": 20.0},
    {"Categoría": "Para Picar", "Producto": "Quesillo", "Precio": 8.0},
    {"Categoría": "Para Picar", "Producto": "K'allu", "Precio": 15.0},
    # Menú para Niños
    {"Categoría": "Menu para Niños", "Producto": "Salchipapas", "Precio": 25.0},
    {"Categoría": "Menu para Niños", "Producto": "Pollo Dorado", "Precio": 30.0},
    # Guarniciones
    {"Categoría": "Guarniciones", "Producto": "Porción de Chuño", "Precio": 5.0},
    {"Categoría": "Guarniciones", "Producto": "Porción de Arroz", "Precio": 5.0},
    {"Categoría": "Guarniciones", "Producto": "Porción de Papa", "Precio": 5.0},
    {"Categoría": "Guarniciones", "Producto": "Porción de Plátano", "Precio": 5.0},
    {"Categoría": "Guarniciones", "Producto": "Porción de Ensalada", "Precio": 5.0},
]

df_menu = pd.DataFrame(MENU_DATA)

# Memoria temporal de la sesión
if 'ventas' not in st.session_state:
    st.session_state.ventas = pd.DataFrame(columns=[
        "ID", "Fecha", "Hora", "Producto", "Categoría", "Cantidad", "Precio Unit. (Bs.)", "Total (Bs.)", "Método Pago", "Atendido Por"
    ])

# -----------------------------------------------------------------------------
# Interfaz Principal
# -----------------------------------------------------------------------------
st.markdown("<p class='main-header'>🍽️ Sistema POS & BI - Viva Vinto</p>", unsafe_allow_html=True)

menu_opcion = st.sidebar.radio("Navegación", ["📝 Registrar Venta", "📊 Dashboard & Reportes", "📋 Carta y Precios"])

# MÓDULO 1: REGISTRAR VENTA
if menu_opcion == "📝 Registrar Venta":
    st.subheader("Registrar Nueva Venta")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        categoria_sel = st.selectbox("1. Selecciona Categoría", df_menu["Categoría"].unique())
        productos_filtrados = df_menu[df_menu["Categoría"] == categoria_sel]["Producto"].tolist()
        
        producto_sel = st.selectbox("2. Selecciona Platillo / Bebida", productos_filtrados)
        precio_unit = df_menu[df_menu["Producto"] == producto_sel]["Precio"].values[0]
        
        st.info(f"💰 **Precio Unitario:** {precio_unit:.2f} Bs.")
        
    with col2:
        cantidad = st.number_input("3. Cantidad", min_value=1, value=1, step=1)
        metodo_pago = st.selectbox("4. Método de Pago", ["Efectivo", "QR / Transferencia", "Tarjeta"])
        atendido_por = st.text_input("5. Atendido por", value="Caja 1")
        
        total_calculado = cantidad * precio_unit
        st.metric(label="Total a Cobrar", value=f"{total_calculado:.2f} Bs.")

    if st.button("🔴 Registrar Venta", use_container_width=True):
        now = datetime.now()
        nueva_venta = {
            "ID": len(st.session_state.ventas) + 1,
            "Fecha": now.strftime("%Y-%m-%d"),
            "Hora": now.strftime("%H:%M:%S"),
            "Producto": producto_sel,
            "Categoría": categoria_sel,
            "Cantidad": cantidad,
            "Precio Unit. (Bs.)": precio_unit,
            "Total (Bs.)": total_calculado,
            "Método Pago": metodo_pago,
            "Atendido Por": atendido_por
        }
        st.session_state.ventas = pd.concat([st.session_state.ventas, pd.DataFrame([nueva_venta])], ignore_index=True)
        st.success(f"¡Venta registrada! Total: {total_calculado:.2f} Bs.")

    st.markdown("---")
    st.write("### 📋 Historial de Ventas")
    st.dataframe(st.session_state.ventas, use_container_width=True)

# MÓDULO 2: DASHBOARD Y ANALÍTICA DE NEGOCIO
elif menu_opcion == "📊 Dashboard & Reportes":
    st.subheader("📊 Control de Caja e Inteligencia de Negocios")
    
    df_v = st.session_state.ventas
    
    if df_v.empty:
        st.warning("Aún no hay ventas registradas. Ve a 'Registrar Venta' para añadir transacciones.")
    else:
        total_ingresos = df_v["Total (Bs.)"].sum()
        total_platos = df_v["Cantidad"].sum()
        ticket_promedio = df_v["Total (Bs.)"].mean()
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Ingresos Totales", f"{total_ingresos:.2f} Bs.")
        kpi2.metric("Platos Vendidos", f"{total_platos} unids.")
        kpi3.metric("Ticket Promedio", f"{ticket_promedio:.2f} Bs.")
        
        st.markdown("---")
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.write("#### Ingresos por Método de Pago (Arqueo)")
            st.bar_chart(df_v.groupby("Método Pago")["Total (Bs.)"].sum())
            
        with col_graf2:
            st.write("#### Ventas Totales por Categoría")
            st.bar_chart(df_v.groupby("Categoría")["Total (Bs.)"].sum())

        st.markdown("---")
        csv_data = df_v.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte Completo en Excel (CSV)",
            data=csv_data,
            file_name="reporte_ventas_viva_vinto.csv",
            mime="text/csv",
        )

# MÓDULO 3: CARTA Y PRECIOS
elif menu_opcion == "📋 Carta y Precios":
    st.subheader("Menú de Productos Registrados")
    st.dataframe(df_menu, use_container_width=True)
