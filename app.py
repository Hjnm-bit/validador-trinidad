import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configuración de la página web de la Intendencia de Flores
st.set_page_config(page_title="Validador Urbanístico - Trinidad", page_icon="🏢", layout="centered")

st.title("🏢 Validador Urbanístico Inteligente")
st.subheader("Plan Parcial del Área Central de Trinidad (Decreto 0884)")

st.markdown("""
Esta herramienta interactiva traduce las reglas complejas del decreto a cálculos visuales e inmediatos para el ciudadano.
""")

# ---- ENTRADA DE DATOS ----
st.sidebar.header("1. Datos del Predio")
area_terreno = st.sidebar.number_input("Superficie total del terreno (m²):", min_value=10.0, value=250.0, step=10.0)
frente_terreno = st.sidebar.number_input("Frente del terreno (metros):", min_value=1.0, value=10.0, step=0.5)

st.sidebar.header("2. Datos del Proyecto Propuesto")
zona = st.sidebar.selectbox("Área de Ubicación del Proyecto:", ["Área Central de Protección Patrimonial", "Área de Amortiguación"])
area_planta_baja = st.sidebar.number_input("Área cubierta en Planta Baja (m²):", min_value=0.0, value=150.0, step=5.0)
area_total_construida = st.sidebar.number_input("Suma de áreas de TODOS los niveles (m²):", min_value=0.0, value=300.0, step=10.0)

# ---- PARSEO DE REGLAS SEGÚN EL DECRETO ----
if zona == "Área Central de Protección Patrimonial":
    fos_max = 0.75  # Art. 47
    fot_max = 3.15  # Art. 50
    retiro_post_pct = 0.25  # Art. 31
    altura_basamento = 7.0  # Art. 36
    altura_max = 15.0  # Art. 36
else:
    fos_max = 0.65  # Art. 52
    fot_max = 2.60  # Art. 52
    retiro_post_pct = 0.30  # Art. 33
    altura_basamento = 0.0  # No aplica basamento obligatorio igual
    altura_max = 12.0  # Art. 39

# ---- CÁLCULOS TÉCNICOS ----
fos_proyecto = area_planta_baja / area_terreno
fot_proyecto = area_total_construida / area_terreno

# ---- DESPLIEGUE DE RESULTADOS ----
st.header("📊 Diagnóstico de Edificabilidad")

# Validación de límites de fraccionamiento mínimos (Art. 46)
if area_terreno < 220 or frente_terreno < 8:
    st.warning("⚠️ Nota: El terreno no cumple con el fraccionamiento mínimo estándar del Art. 46 (220 m² de área y 8m de frente). Requiere consulta técnica.")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="FOS Proyecto (Ocupación del Suelo)", value=f"{fos_proyecto:.2%}", delta=f"Máx permitido: {fos_max:.2%}", delta_color="inverse")
    if fos_proyecto <= fos_max:
        st.success("✅ FOS Permitido")
    else:
        st.error("❌ Excede el FOS Máximo")

with col2:
    st.metric(label="FOT Proyecto (Volumen Total)", value=f"{fot_proyecto:.2f}", delta=f"Máx permitido: {fot_max:.2f}", delta_color="inverse")
    if fot_proyecto <= fot_max:
        st.success("✅ FOT Permitido")
    else:
        st.error("❌ Excede el FOT Máximo")

# ---- VISUALIZACIÓN GRÁFICA DEL LOTE ----
st.header("📐 Esquema Conceptual del Lote (2D)")
st.text("Representación gráfica del retiro posterior y la ocupación en planta.")

# Calcular dimensiones proporcionales para el gráfico
largo_terreno = area_terreno / frente_terreno
largo_retiro = largo_terreno * retiro_post_pct
largo_edificable_max = largo_terreno - largo_retiro
largo_ocupado_real = area_planta_baja / frente_terreno

# NUEVO: Alerta de Invasión de Retiro Posterior
if largo_ocupado_real > largo_edificable_max:
    st.error(f"🚨 **Invasión de Retiro Posterior detectada:** El proyecto requiere una profundidad de {largo_ocupado_real:.1f}m, pero el límite edificable antes del retiro es de {largo_edificable_max:.1f}m.")

fig, ax = plt.subplots(figsize=(6, 4))

# Dibujar Terreno Total
ax.add_patch(patches.Rectangle((0, 0), frente_terreno, largo_terreno, edgecolor='black', facecolor='#f0f0f0', label='Lote Completo'))

# Dibujar Zona de Retiro Posterior Obligatorio (Verde)
ax.add_patch(patches.Rectangle((0, largo_edificable_max), frente_terreno, largo_retiro, edgecolor='green', facecolor='#d4edda', hatch='//', label=f'Retiro Posterior Verde ({retiro_post_pct*100:.0f}%)'))

# Dibujar Proyección Ocupada Real del Proyecto
if largo_ocupado_real > largo_edificable_max:
    # Dibuja la parte permitida normal
    ax.add_patch(patches.Rectangle((0, 0), frente_terreno, largo_edificable_max, edgecolor='red', facecolor='#f8d7da', alpha=0.7, label='Ocupación Propuesta'))
    # Dibuja la parte que invade el retiro en un color más fuerte
    invasion = largo_ocupado_real - largo_edificable_max
    ax.add_patch(patches.Rectangle((0, largo_edificable_max), frente_terreno, invasion, edgecolor='darkred', facecolor='red', alpha=0.6, hatch='xx', label='Invasión al Retiro'))
else:
    # Dibuja la ocupación normal si no hay invasión
    ax.add_patch(patches.Rectangle((0, 0), frente_terreno, largo_ocupado_real, edgecolor='red', facecolor='#f8d7da', alpha=0.7, label='Ocupación Propuesta'))

plt.xlim(-1, frente_terreno + 2)
plt.ylim(-1, largo_terreno + 2)
plt.xlabel("Frente del lote (metros)")
plt.ylabel("Profundidad del lote (metros)")
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)

st.info("ℹ️ Alerta de Alturas (Art. 36/39): Recuerde que si edifica un volumen exento por encima del basamento de 7m, este debe retirarse 4m de la fachada frontal y 3m de las medianeras.")

# ---- GENERACIÓN DE REPORTE ----
st.markdown("---")
st.header("📄 Exportar Resultados")

# Armamos el texto del reporte usando las variables existentes
texto_reporte = f"""
=================================================
VALIDADOR URBANÍSTICO - TRINIDAD (Decreto 0884)
=================================================

1. DATOS DEL PREDIO
- Área total: {area_terreno} m²
- Frente: {frente_terreno} m
- Zona: {zona}

2. DIAGNÓSTICO DE EDIFICABILIDAD
- FOS Proyecto: {fos_proyecto:.2%} | FOS Permitido: {fos_max:.2%}
- FOT Proyecto: {fot_proyecto:.2f} | FOT Permitido: {fot_max:.2f}

3. ESTADO DEL RETIRO POSTERIOR
- Ocupación propuesta: {largo_ocupado_real:.1f} m
- Límite máximo edificable: {largo_edificable_max:.1f} m
- Infracción por invasión: {"SÍ" si largo_ocupado_real > largo_edificable_max else "NO"}

* Nota: Este reporte es de carácter informativo y no sustituye la validación técnica oficial de la Intendencia.
"""

# Creamos el botón de descarga
st.download_button(
    label="📥 Descargar Reporte (TXT)",
    data=texto_reporte,
    file_name="diagnostico_trinidad.txt",
    mime="text/plain"
)