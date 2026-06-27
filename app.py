import streamlit as st
import os

# --- INSTALACIÓN FORZADA ---
try:
    import openpyxl
except ImportError:
    os.system("pip install openpyxl pandas")
    st.rerun()

import pandas as pd
import urllib.parse

# Configuración de la página web
st.set_page_config(page_title="Cotizador de Fibra", page_icon="⚡", layout="centered")

# Cargar los datos del archivo Excel
@st.cache_data
def cargar_datos():
    df = pd.read_excel("OFERTA TOTAL.xlsx", sheet_name="MI FIBRA WIN")
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].str.strip()
    return df

# --- FUNCIÓN PARA LIMPIAR TODO ---
def limpiar_filtros():
    for key in ["operador", "localidad", "plan", "velocidad"]:
        if key in st.session_state:
            del st.session_state[key]

try:
    df_original = cargar_datos()

    # --- FILTROS DINÁMICOS CON ESTADO ---
    
    # 1. Operador
    operadores = [" Seleccionar..."] + list(df_original["OPERADOR"].unique())
    if "operador" not in st.session_state:
        st.session_state["operador"] = operadores[0]
        
    operador_sel = st.selectbox("1. Seleccionar Operador:", operadores, key="operador")

    # --- CAMBIO DINÁMICO DE COLOR DE FONDO ---
    # Colores suaves/pasteles para mantener una excelente legibilidad del texto negro
    if "WIN" in operador_sel.upper():
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #FFE6CC; /* Anaranjado Pastel */
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    elif "MI FIBRA" in operador_sel.upper():
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #FCE4EC; /* Fucsia / Rosado Suave */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Título y descripción (se colocan aquí para que el fondo aplique correctamente desde el inicio)
    st.title("⚡ Cotizador de Planes de Internet")
    st.markdown("Selecciona los filtros para generar la cotización para tu cliente.")
    st.write("---")

    if operador_sel != " Seleccionar...":
        df_filtrado = df_original[df_original["OPERADOR"] == operador_sel]

        # 2. Localidad
        localidades = [" Seleccionar..."] + list(df_filtrado["LOCALIDAD"].unique())
        if "localidad" not in st.session_state:
            st.session_state["localidad"] = localidades[0]
            
        localidad_sel = st.selectbox("2. Seleccionar Localidad:", localidades, key="localidad")

        if localidad_sel != " Seleccionar...":
            df_filtrado = df_filtrado[df_filtrado["LOCALIDAD"] == localidad_sel]

            # 3. Plan
            planes = [" Seleccionar..."] + list(df_filtrado["PLAN"].unique())
            if "plan" not in st.session_state:
                st.session_state["plan"] = planes[0]
                
            plan_sel = st.selectbox("3. Seleccionar Plan:", planes, key="plan")

            if plan_sel != " Seleccionar...":
                df_filtrado = df_filtrado[df_filtrado["PLAN"] == plan_sel]

                # 4. Velocidad Real
                velocidades = [" Seleccionar..."] + list(df_filtrado["VELOCIDAD REAL"].unique())
                if "velocidad" not in st.session_state:
                    st.session_state["velocidad"] = velocidades[0]
                    
                velocidad_sel = st.selectbox("4. Seleccionar Velocidad Real (Mbps):", velocidades, key="velocidad")

                st.write("---")

                # --- MOSTRAR RESULTADOS SI SE SELECCIONÓ TODO ---
                if velocidad_sel != " Seleccionar...":
                    fila_final = df_filtrado[df_filtrado["VELOCIDAD REAL"] == velocidad_sel]

                    if not fila_final.empty:
                        res = fila_final.iloc[0]
                        
                        precio_real = res["PRECIO REAL"]
                        precio_promo = res["PRECIO PROMOCION"]
                        meses_promo = res["MESES PROMO"]
                        vel_promo = res["VELOCIDAD PROMOCION"]
                        adicional = res["ADICIONAL"] if pd.notna(res["ADICIONAL"]) else "Ninguno"

                        # Componentes visuales de resultados
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

                        # --- GENERACIÓN DEL MENSAJE Y BOTÓN DE WHATSAPP ---
                        st.write("---")
                        
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
                        
                        mensaje_codificado = urllib.parse.quote(mensaje_texto)
                        enlace_whatsapp = f"https://wa.me/?text={mensaje_codificado}"
                        
                        st.link_button("📲 Enviar Cotización por WhatsApp", enlace_whatsapp, type="primary", use_container_width=True)
                    else:
                        st.warning("No se encontró una combinación exacta para los filtros seleccionados.")
    
    # --- BOTÓN DE LIMPIAR ---
    st.write(" ")
    st.button("🔄 Limpiar Todo / Nueva Cotización", on_click=limpiar_filtros, use_container_width=True)

except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'OFERTA TOTAL.xlsx'. Asegúrate de ponerlo en la misma carpeta que este script.")
except Exception as e:
    st.error(f"Ocurrió un error al procesar el archivo: {e}")
