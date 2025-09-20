import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="⛽ Predicción Gasolina México", layout="wide")

st.title("⛽ Predicción de Precios de Gasolina en México")
st.write("Esta aplicación estima el precio de la gasolina según estado, mes, año y tipo de combustible.")

# ----------- Cargar datos -----------
@st.cache_data
def cargar_datos():
    # Leer Excel
    df = pd.read_excel("gasolina_mexico_completo.xlsx")

    # Normalizar nombres de columnas
    df.columns = [c.strip().lower().replace(" ", "_").replace("á", "a") for c in df.columns]

    # Eliminar filas sin datos esenciales
    df = df.dropna(subset=["estado", "anio", "mes", "tipo_combustible", "precio"])

    # Crear columna de fecha
    df["fecha"] = pd.to_datetime(
        df["anio"].astype(int).astype(str) + "-" + df["mes"].astype(int).astype(str) + "-01"
    )

    return df

df = cargar_datos()

# ----------- Menús interactivos -----------
estados = df["estado"].unique()
tipo_combustibles = df["tipo_combustible"].unique()
anios = sorted(df["anio"].unique())
meses = list(range(1, 13))

st.sidebar.header("Filtros")
estado_sel = st.sidebar.selectbox("Selecciona el estado:", estados)
tipo_sel = st.sidebar.selectbox("Selecciona tipo de combustible:", tipo_combustibles)
anio_sel = st.sidebar.selectbox("Selecciona el año:", anios)
mes_sel = st.sidebar.selectbox("Selecciona el mes:", meses)

# ----------- Filtrar datos -----------

df_filtro = df[
    (df["estado"] == estado_sel) &
    (df["tipo_combustible"] == tipo_sel) &
    (df["anio"] == anio_sel) &
    (df["mes"] == mes_sel)
]

# ----------- Modelo de regresión -----------
# Variables: estado (dummys), tipo_combustible (dummys), mes, anio
X = pd.get_dummies(df[["estado", "tipo_combustible"]], drop_first=True)
X["mes"] = df["mes"]
X["anio"] = df["anio"]
y = df["precio"]

model = LinearRegression()
model.fit(X, y)

# Crear entrada para predicción
entrada = pd.get_dummies(
    pd.DataFrame({
        "estado": [estado_sel],
        "tipo_combustible": [tipo_sel],
        "mes": [mes_sel],
        "anio": [anio_sel]
    }),
    drop_first=True
)

# Alinear columnas de entrada con las columnas de entrenamiento
for col in X.columns:
    if col not in entrada.columns:
        entrada[col] = 0
entrada = entrada[X.columns]

pred = model.predict(entrada)[0]

st.subheader(f"💰 Precio estimado: ${pred:.2f} MXN")

# ----------- Gráfica histórica del estado y tipo -----------

df_plot = df[
    (df["estado"] == estado_sel) &
    (df["tipo_combustible"] == tipo_sel)
].sort_values("fecha")

plt.figure(figsize=(12,5))
sns.lineplot(data=df_plot, x="fecha", y="precio", marker="o")
plt.title(f"Histórico de precios en {estado_sel} - {tipo_sel}")
plt.xlabel("Fecha")
plt.ylabel("Precio (MXN)")
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(plt)


