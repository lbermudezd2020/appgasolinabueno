# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="⛽ Predicción de Precios de Gasolina", layout="wide")

st.title("⛽ Predicción de Precios de Gasolina en México")
st.markdown("""
Esta aplicación estima y visualiza el precio de la gasolina según estado, año, mes y tipo de combustible.
""")

# ------------------------------
# Función para cargar datos
# ------------------------------
@st.cache_data
def cargar_datos():
    try:
        df = pd.read_excel("gasolina_mexico_completo.xlsx")
        # Verificar que las columnas existen
        expected_cols = ["estado","anio","mes","tipo_combustible","precio"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"Error: El archivo Excel debe tener las columnas: {expected_cols}")
            return pd.DataFrame()  # dataframe vacío
        return df
    except FileNotFoundError:
        st.error("Archivo Excel no encontrado. Asegúrate de subir 'gasolina_mexico_completo.xlsx'.")
        return pd.DataFrame()

# ------------------------------
# Cargar datos
# ------------------------------
df = cargar_datos()
if df.empty:
    st.stop()  # Detener la app si no hay datos

# ------------------------------
# Barra lateral de filtros
# ------------------------------
st.sidebar.header("Filtros del usuario")
estado_seleccionado = st.sidebar.selectbox("Selecciona el estado", sorted(df["estado"].unique()))
tipo_seleccionado = st.sidebar.selectbox("Tipo de combustible", sorted(df["tipo_combustible"].unique()))
anio_seleccionado = st.sidebar.slider("Año", int(df["anio"].min()), int(df["anio"].max()), int(df["anio"].max()))
mes_seleccionado = st.sidebar.slider("Mes", 1, 12, 1)

# ------------------------------
# Filtrar datos según selección
# ------------------------------
df_filtrado = df[
    (df["estado"] == estado_seleccionado) &
    (df["tipo_combustible"] == tipo_seleccionado) &
    (df["anio"] == anio_seleccionado) &
    (df["mes"] == mes_seleccionado)
]

# ------------------------------
# Mostrar precio estimado
# ------------------------------
if not df_filtrado.empty:
    precio_estimado = df_filtrado["precio"].values[0]
    st.subheader(f"Precio estimado: ${precio_estimado:.2f} MXN por litro")
else:
    st.warning("No hay datos para la combinación seleccionada.")

# ------------------------------
# Gráficos adicionales
# ------------------------------
st.markdown("---")
st.subheader("Tendencia de precios por estado y tipo de combustible")

# Crear columna fecha para gráfico
df["fecha"] = pd.to_datetime(df[["anio","mes"]].assign(day=1))

# Filtrar solo el estado y tipo seleccionados
df_plot = df[(df["estado"] == estado_seleccionado) & (df["tipo_combustible"] == tipo_seleccionado)]
df_plot = df_plot.sort_values("fecha")

# Gráfico de línea
plt.figure(figsize=(12,5))
sns.lineplot(data=df_plot, x="fecha", y="precio", marker="o")
plt.title(f"Tendencia de precios en {estado_seleccionado} ({tipo_seleccionado})")
plt.xlabel("Fecha")
plt.ylabel("Precio (MXN por litro)")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)

# ------------------------------
# Tabla resumen
# ------------------------------
st.subheader("Tabla de precios históricos")
st.dataframe(df_plot[["anio","mes","precio"]].reset_index(drop=True))



