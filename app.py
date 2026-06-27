import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de la página web
st.set_page_config(page_title="Cotizador de Fibra", page_icon="⚡", layout="centered")

st.title("⚡ Cotizador de Planes de Internet")
st.markdown("Selecciona los filtros para generar la cotización para tu cliente.")
st.write("---")

# Cargar los datos del archivo Excel
@st.cache_data
def cargar_datos():
    # Cargamos la pestaña correspondiente
    df = pd.read_excel("OFERTA TOTAL.xlsx", sheet_name="MI FIBRA WIN")
    # Limpiamos espacios en blanco si los hubiera
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()
    return df

try:
    df_original = cargar_datos()

    # --- FILTROS DINÁMICOS ---
    # 1. Operador
    operadores = df_original["OPERADOR"].unique()
    operador_sel = st.selectbox("1. Seleccionar Operador:", operadores)

    # Filtrar por operador para el siguiente paso
    df_filtrado = df_original[df_original["OPERADOR"] == operador_sel]

    # 2. Localidad
    localidades = df_filtrado["LOCALIDAD"].unique()
    localidad_sel = st.selectbox("2. Seleccionar Localidad:", localidades)

    # Filtrar por localidad
    df_filtrado = df_filtrado[df_filtrado["LOCALIDAD"] == localidad_sel]

    # 3. Plan
    planes = df_filtrado["PLAN"].unique()
    plan_sel = st.selectbox("3. Seleccionar Plan:", planes)

    # Filtrar por plan
    df_filtrado = df_filtrado[df_filtrado["PLAN"] == plan_sel]

    # 4. Velocidad Real
    velocidades = df_filtrado["VELOCIDAD REAL"].unique()
    velocidad_sel = st.selectbox("4. Seleccionar Velocidad Real (Mbps):", velocidades)

    # Fila final seleccionada
    fila_final = df_filtrado[df_filtrado["VELOCIDAD REAL"] == velocidad_sel]

    st.write("---")

    # --- MOSTRAR RESULTADOS ---
    if not fila_final.empty:
        # Extraer los datos de la fila
        res = fila_final.iloc[0]
        
        precio_real = res["PRECIO REAL"]
        precio_promo = res["PRECIO PROMOCION"]
        meses_promo = res["MESES PROMO"]
        vel_promo = res["VELOCIDAD PROMOCION"]
        adicional = res["ADICIONAL"] if pd.notna(res["ADICIONAL"]) else "Ninguno"

        # Diseño visual de los resultados
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="💰 Precio Real", value=f"S/. {precio_real}")
            st.metric(label="🚀 Velocidad Contratada", value=f"{velocidad_sel} Mbps")
            
        with col2:
            st.metric(label="🎁 Precio Promoción", value=f"S/. {precio_promo}")
            st.markdown(f"**Duración de Promo:** {meses_promo}")
            st.markdown(f"**Beneficio de Velocidad:** {vel_promo}")

        if adicional != "Ninguno":
            st.info(f"💡 **Adicional:** {adicional}")

        # --- BOTÓN DE WHATSAPP ---
        st.write("---")
        
        # Estructurar el mensaje de texto para WhatsApp
        mensaje_texto = (
            f"🚀 *¡HOLA! AQUÍ TIENES TU COTIZACIÓN EXCLUSIVA!* 🚀\n\n"
            f"📌 *Operador:* {operador_sel}\n"
            f"📍 *Zona de cobertura:* {localidad_sel}\n"
            f"📋 *Plan:* {plan_sel}\n"
            f"⚡ *Velocidad Base:* {velocidad_sel} Mbps\n"
            f"🎁 *Velocidad Promo:* {vel_promo}\n\n"
            f"--- DETALLE DE PRECIOS ---\n"
            f"💵 *Precio Regular:* S/. {precio_real}\n"
            f"🎉 *Precio Promocional:* S/. {precio_promo}\n"
            f"⏳ *Duración del descuento:* {meses_promo}\n"
            f"➕ *Adicional:* {adicional}\n\n"
            f"¿Te gustaría que agendemos tu instalación hoy mismo? 😊"
        )
        
        # Codificar el texto para que sea compatible con un enlace web URL
        mensaje_codificado = urllib.parse.quote(mensaje_texto)
        enlace_whatsapp = f"https://wa.me/?text={mensaje_codificado}"
        
        # Botón visual llamativo
        st.markdown(
            f'<a href="{enlace_whatsapp}" target="_blank" style="text-decoration:none;">'
            f'<div style="background-color:#25D366;color:white;padding:12px 20px;text-align:center;'
            f'border-radius:8px;font-weight:bold;font-size:18px;box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">'
            f'📲 Copiar Cotización y Enviar por WhatsApp'
            f'</div></a>', 
            unsafe_allow_index=True
        )

    else:
        st.warning("No se encontró una combinación exacta para los filtros seleccionados.")

except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'OFERTA TOTAL.xlsx'. Asegúrate de ponerlo en la misma carpeta que este script.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el archivo: {e}")