# app.py
import streamlit as st
import pandas as pd
import os

# --- Configuración de la Página ---
# Esto debe ser lo primero en tu script. Le da a la página un título y un ícono.
st.set_page_config(
    page_title="Calculadora de IAF",
    page_icon="🌿",
    layout="centered"
)

# --- Título Principal y Descripción ---
st.title('🌿 Calculadora de Índice de Área Foliar (IAF)')
st.write(
    "Una herramienta para estimar el IAF de tu cultivo de tomate a partir de mediciones simples."
)

# --- Función para Cargar Datos y Calcular 'k' ---
# Usamos @st.cache_data para que el archivo se lea solo una vez y la app sea rápida.
@st.cache_data
def cargar_modelo(ruta_archivo):
    """
    Lee los datos limpios de las hojas y calcula el factor de corrección 'k' promedio.
    """
    if not os.path.exists(ruta_archivo):
        # Si no encuentra el archivo, muestra un error en la página.
        st.error(f"Error: No se encontró el archivo de datos '{ruta_archivo}'.")
        st.warning("Asegúrate de que este archivo esté en la misma carpeta que 'app.py'.")
        return None
    
    # Lee el archivo CSV con el formato correcto
    df = pd.read_csv(ruta_archivo, sep=',', decimal='.')
    
    # Calcula el 'k' promedio
    df['k'] = df['area_cm2'] / (df['largo_cm'] * df['ancho_cm'])
    k_promedio = df['k'].mean()
    
    return k_promedio

# --- Cargar el Modelo (el factor 'k') ---
nombre_archivo_datos = 'datos_limpios_sin_atipicos.csv'
k = cargar_modelo(nombre_archivo_datos)

# Si el archivo se cargó correctamente, mostramos la calculadora.
if k is not None:
    # --- Entradas del Usuario en la Barra Lateral ---
    # Colocar los controles en la barra lateral mantiene la página principal limpia.
    with st.sidebar:
        st.header('Parámetros del Cultivo')
        
        # Usamos valores predeterminados y límites para una mejor experiencia de usuario.
        largo = st.number_input('Largo promedio de la hoja (cm):', min_value=1.0, value=39.0, step=0.5)
        ancho = st.number_input('Ancho promedio de la hoja (cm):', min_value=1.0, value=38.0, step=0.5)
        hojas = st.number_input('Número de hojas por planta:', min_value=1, value=14)
        plantas = st.number_input('Plantas por metro cuadrado:', min_value=0.1, value=3.3, step=0.1)

    # --- Botón de Cálculo y Visualización del Resultado ---
    st.divider() # Dibuja una línea separadora para un look más limpio.
    
    # Centramos el botón para un mejor diseño
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button('Calcular IAF', use_container_width=True):
            # Fórmula para el área y el IAF
            area_cm2 = k * largo * ancho
            area_m2 = area_cm2 / 10000
            iaf_calculado = area_m2 * hojas * plantas
            
            # st.metric es una forma elegante de mostrar un número clave
            st.metric(label="Índice de Área Foliar (IAF) Estimado", value=f"{iaf_calculado:.2f}")

            # Un "expander" oculta los detalles, pero permite al usuario verlos si lo desea
            with st.expander("Ver detalles del cálculo"):
                st.write(f"Área estimada por hoja: **{area_cm2:.2f} cm²**")
                st.write(f"Área foliar total por planta: **{area_m2 * hojas:.4f} m²**")
                st.info(f"Cálculo basado en un factor 'k' de **{k:.4f}**")