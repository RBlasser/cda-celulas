"""
Prototipo Asesor Virtual de Auto - Feria de Préstamos Caja de Ahorros
Desarrollado con Streamlit.
"""

import os
import random
import datetime
from dotenv import load_dotenv
import streamlit as st

# Cargar automáticamente variables de entorno desde .env si existe
load_dotenv()
from knowledge_base import KNOWLEDGE_CONTEXT, SYSTEM_PROMPT
from gemini_client import query_gemini_api, get_smart_local_response

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Asesor Virtual de Auto | Caja de Ahorros",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. ESTILOS CORPORATIVOS CAJA DE AHORROS
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    /* Tipografía y paleta corporativa */
    :root {
        --cda-navy: #002855;
        --cda-blue-accent: #004b93;
        --cda-teal: #00A896;
        --cda-gold: #C5A059;
        --cda-gray-bg: #F4F6F9;
        --cda-card-bg: #FFFFFF;
    }
    
    /* Header principal */
    .cda-header {
        background: linear-gradient(135deg, #002855 0%, #004b93 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 40, 85, 0.15);
    }
    .cda-header h1 {
        color: #FFFFFF !important;
        font-size: 1.9rem;
        font-weight: 700;
        margin: 0;
        padding: 0;
    }
    .cda-header p {
        color: #D8E6F5;
        font-size: 1.05rem;
        margin: 0.3rem 0 0 0;
    }

    /* Tarjetas personalizadas */
    .cda-card {
        background: var(--cda-card-bg);
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .cda-card-header {
        font-weight: 700;
        color: #002855;
        font-size: 1.15rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #F0F4F8;
        padding-bottom: 0.4rem;
    }

    /* Badges de beneficios */
    .cda-badge {
        display: inline-block;
        background-color: #E6F7F5;
        color: #007A6C;
        font-weight: 600;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .cda-badge-gold {
        background-color: #FDF8ED;
        color: #9C782F;
        font-weight: 600;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        margin-right: 0.4rem;
    }

    /* Pase Digital */
    .cda-pass {
        background: linear-gradient(135deg, #F8FAFC 0%, #EDF2F7 100%);
        border: 2px dashed #002855;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    /* Botones de sugerencias rápidas */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }

    /* =========================================================================
       CHAT LAYOUT MINIMALISTA (ESTILO EXACTO SOLICITADO)
       ========================================================================= */
    
    /* Contenedor principal de mensajes */
    div[data-testid="stChatMessage"] {
        align-items: flex-start !important;
        gap: 16px !important;
        width: 100% !important;
        margin-bottom: 18px !important;
        font-family: inherit !important;
    }

    /* Mensaje del Usuario: Tarjeta gris redondeada suave */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background-color: #F4F6F8 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Mensaje del Asistente: Fondo transparente, sin caja */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
        background-color: transparent !important;
        border-radius: 0 !important;
        padding: 10px 20px !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Avatar Usuario: Cuadro redondeado coral con carita sonriente blanca */
    div[data-testid="stChatMessageAvatarUser"] {
        background-color: #FF6565 !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><path d="M16 6 C9 6 6 11 6 17 C6 20 7 23 9 25 C11 27 13.5 28 16 28 C18.5 28 21 27 23 25 C25 23 26 20 26 17 C26 11 23 6 16 6 Z" fill="none" stroke="%23FFFFFF" stroke-width="2" stroke-linecap="round"/><circle cx="5" cy="17" r="1.5" fill="%23FFFFFF"/><circle cx="27" cy="17" r="1.5" fill="%23FFFFFF"/><path d="M9.5 13 C12 8.5 15 11 16 11 C17 11 20 8.5 22.5 13" fill="none" stroke="%23FFFFFF" stroke-width="1.8" stroke-linecap="round"/><circle cx="12" cy="16.5" r="1.4" fill="%23FFFFFF"/><circle cx="20" cy="16.5" r="1.4" fill="%23FFFFFF"/><path d="M12.5 20.5 Q16 24 19.5 20.5" fill="none" stroke="%23FFFFFF" stroke-width="1.8" stroke-linecap="round"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 24px 24px !important;
        border-radius: 10px !important;
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        box-shadow: 0 1px 3px rgba(255, 101, 101, 0.25) !important;
    }
    div[data-testid="stChatMessageAvatarUser"] * {
        display: none !important;
    }

    /* Avatar Asistente: Cuadro redondeado ámbar con robot blanco */
    div[data-testid="stChatMessageAvatarAssistant"] {
        background-color: #F5A623 !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><line x1="16" y1="5" x2="16" y2="8" stroke="%23FFFFFF" stroke-width="2" stroke-linecap="round"/><circle cx="16" cy="4" r="1.5" fill="%23FFFFFF"/><rect x="8" y="8" width="16" height="15" rx="3.5" fill="none" stroke="%23FFFFFF" stroke-width="2"/><rect x="5.5" y="13" width="2.5" height="5" rx="1" fill="%23FFFFFF"/><rect x="24" y="13" width="2.5" height="5" rx="1" fill="%23FFFFFF"/><circle cx="12.5" cy="14" r="1.5" fill="%23FFFFFF"/><circle cx="19.5" cy="14" r="1.5" fill="%23FFFFFF"/><line x1="12" y1="18.5" x2="20" y2="18.5" stroke="%23FFFFFF" stroke-width="1.8" stroke-linecap="round"/></svg>') !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 24px 24px !important;
        border-radius: 10px !important;
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        max-width: 38px !important;
        box-shadow: 0 1px 3px rgba(245, 166, 35, 0.25) !important;
    }
    div[data-testid="stChatMessageAvatarAssistant"] * {
        display: none !important;
    }

    /* Tipografía y alineación de contenido */
    div[data-testid="stChatMessageContent"] {
        color: #1E293B !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding-top: 4px !important;
    }

    /* Input del Chat (Barra inferior con borde redondeado y flecha) */
    div[data-testid="stChatInput"] {
        border-radius: 14px !important;
        border: 1.5px solid #FCA5A5 !important;
        background-color: #F8F9FA !important;
        padding: 4px 8px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #EF4444 !important;
        box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.15) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #1E293B !important;
        font-size: 0.98rem !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #94A3B8 !important;
    }
    div[data-testid="stChatInput"] button {
        border-radius: 8px !important;
        color: #94A3B8 !important;
    }
    div[data-testid="stChatInput"] button:hover {
        color: #EF4444 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. SIDEBAR DE CONFIGURACIÓN Y ORIENTACIÓN
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏦 Caja de Ahorros")
    st.markdown("**Feria de Préstamos de Auto**")
    st.markdown("---")
    
    st.markdown("#### ⚙️ Motor de Inteligencia")
    api_key_input = st.text_input(
        "Clave Google Gemini API (Opcional):",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Si no cuenta con una clave API, la herramienta opera con su motor experto de reglas y lineamientos de Caja de Ahorros."
    )
    
    if api_key_input:
        st.success("🟢 Modo IA: Gemini Conectado")
    else:
        st.info("🔵 Modo Experto: Reglas de Feria Activo")
        
    st.markdown("---")
    st.markdown("#### 📍 Punto de Atención")
    st.markdown("""
    • **Stand Principal:** Centro de Convenciones Amador\n
    • **Horario:** 10:00 a.m. a 8:00 p.m.\n
    • **Línea de Atención:** 800-2252\n
    • **Banca en Línea:** [cajadeahorros.com.pa](https://www.cajadeahorros.com.pa)
    """)
    
    st.markdown("---")
    st.caption("Prototipo de Innovación CDA • Todos los derechos reservados.")

# -----------------------------------------------------------------------------
# 4. BANNER PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="cda-header">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1>🚗 Asesor Virtual de Auto</h1>
            <p>Orientación ágil de financiamiento y requisitos para la Feria de Autos • Caja de Ahorros</p>
        </div>
        <div style="text-align: right; font-size: 0.9rem; opacity: 0.9;">
            <span>El Banco de la Familia Panameña 🇵🇦</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. PESTAÑAS PRINCIPALES DE LA APLICACIÓN
# -----------------------------------------------------------------------------
tab_chat, tab_perfiles, tab_simulador = st.tabs([
    "💬 Asesor Virtual (Chat IA)",
    "📋 Orientador de Requisitos por Perfil",
    "🧮 Simulador de Préstamo de Auto"
])

# =============================================================================
# PESTAÑA 1: CHATBOT ASESOR IA
# =============================================================================
with tab_chat:
    col_chat_main, col_chat_side = st.columns([7, 3])
    
    with col_chat_side:
        st.markdown("""
        <div class="cda-card">
            <div class="cda-card-header">💡 Consultas Frecuentes</div>
            <p style="font-size:0.85rem; color:#64748B;">Haga clic en cualquiera de estas opciones para consultar de inmediato:</p>
        </div>
        """, unsafe_allow_html=True)
        
        pregunta_seleccionada = None
        if st.button("🏥 Requisitos para Salud / Educadores", use_container_width=True):
            pregunta_seleccionada = "¿Cuáles son los requisitos y el tiempo de permanencia si soy educador o trabajo en el sector salud?"
        if st.button("🇨🇳 ¿Financian marcas como BYD o Geely?", use_container_width=True):
            pregunta_seleccionada = "¿Puedo financiar un vehículo de marcas de origen chino como BYD, Geely o Changan con Caja de Ahorros?"
        if st.button("👴 Beneficios para Jubilados (Ley 6)", use_container_width=True):
            pregunta_seleccionada = "¿Qué beneficios y exoneraciones aplican para jubilados y pensionados bajo la Ley 6 de 1987?"
        if st.button("💰 ¿Cuánto es el abono mínimo y Fast Track?", use_container_width=True):
            pregunta_seleccionada = "¿Cuánto es el porcentaje de abono mínimo y cómo funciona la modalidad Fast Track de feria?"
        if st.button("📅 Plazos máximos de financiamiento", use_container_width=True):
            pregunta_seleccionada = "¿Hasta cuántos meses de plazo puedo financiar un auto nuevo?"
            
        st.markdown("""
        <div style="background-color: #FEF9C3; border-left: 4px solid #CA8A04; padding: 0.8rem; border-radius: 6px; font-size: 0.85rem; color: #713F12; margin-top: 1rem;">
            <strong>Nota de Confianza:</strong><br>
            Nuestras respuestas están diseñadas para orientarle cordialmente. Ninguna consulta compromete su historial de crédito.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Reiniciar conversación", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    with col_chat_main:
        # Inicializar historial de chat
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {
                    "role": "assistant",
                    "content": (
                        "¡Bienvenido a la Feria de Autos con Caja de Ahorros! 🚗🇵🇦\n\n"
                        "Soy su **Asesor Virtual de Auto**. Es un placer saludarle y orientarle en la elección de su próximo financiamiento.\n\n"
                        "Puedo brindarle información sobre:\n"
                        "• **Requisitos y documentos** según su perfil laboral.\n"
                        "• **Abonos mínimos, plazos y marcas autorizadas** (incluyendo autos ecológicos y marcas chinas con respaldo).\n"
                        "• **Beneficios por Ley 6** para jubilados y pensionados.\n\n"
                        "¿En qué podemos servirle el día de hoy?"
                    )
                }
            ]

        # Si el usuario hizo clic en una consulta frecuente
        if pregunta_seleccionada:
            st.session_state.chat_history.append({"role": "user", "content": pregunta_seleccionada})
            
            # Generar respuesta
            if api_key_input:
                success, reply = query_gemini_api(st.session_state.chat_history, api_key=api_key_input)
                if not success:
                    reply = get_smart_local_response(pregunta_seleccionada)
            else:
                reply = get_smart_local_response(pregunta_seleccionada)
                
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

        # Mostrar conversación
        for msg in st.session_state.chat_history:
            avatar = "assistant" if msg["role"] == "assistant" else "user"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

        # Input de chat
        user_input = st.chat_input("Escriba su consulta aquí (ej: ¿Qué abono se requiere si el auto cuesta menos de $10,000?)...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user", avatar="user"):
                st.markdown(user_input)

            # Generar respuesta
            with st.chat_message("assistant", avatar="assistant"):
                with st.spinner("Consultando lineamientos de Caja de Ahorros..."):
                    if api_key_input:
                        success, reply = query_gemini_api(st.session_state.chat_history, api_key=api_key_input)
                        if not success:
                            reply = get_smart_local_response(user_input)
                    else:
                        reply = get_smart_local_response(user_input)
                        
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})


# =============================================================================
# PESTAÑA 2: ORIENTADOR DE REQUISITOS POR PERFIL
# =============================================================================
with tab_perfiles:
    st.markdown("""
    ### 📋 Orientador Rápido de Documentos por Perfil Laboral
    Seleccione su perfil de trabajo para conocer los requisitos exactos establecidos por Caja de Ahorros para la feria.
    """)
    
    col_perfil_sel, col_perfil_det = st.columns([4, 6])
    
    with col_perfil_sel:
        perfil = st.radio(
            "Seleccione su segmento laboral:",
            [
                "🏢 Colaborador de Empresa Privada",
                "🏥 Sector Salud y Educadores (Leyes Especiales)",
                "🏛️ Servidor Público (Gobierno General)",
                "👴 Jubilado o Pensionado (Ley 6 de 1987)",
                "💼 Profesional Independiente",
                "🌐 Extranjero Residente Permanente",
                "⚡ Modalidad de Feria Fast Track (30% abono)"
            ],
            index=0
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="background-color: #F1F5F9; border-radius: 8px; padding: 1rem;">
            <strong style="color: #002855;">📌 Documentos Generales para Todos los Casos:</strong>
            <ul style="font-size: 0.9rem; margin-top: 0.5rem; padding-left: 1.2rem;">
                <li>Cédula de identidad personal vigente.</li>
                <li>Cotización o proforma oficial emitida por la agencia concesionaria.</li>
                <li>Licencia de conducir vigente (o carta de autorización a un conductor tercero responsable).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_perfil_det:
        if "Empresa Privada" in perfil:
            st.markdown("""
            <div class="cda-card">
                <div class="cda-card-header">🏢 Requisitos para Colaboradores de Empresa Privada</div>
                <div style="margin-bottom: 0.8rem;">
                    <span class="cda-badge">Plazo hasta 96 meses</span>
                    <span class="cda-badge">Abono desde 10%</span>
                </div>
                <strong>Documentación específica a presentar:</strong>
                <ul style="margin-top: 0.5rem;">
                    <li><strong>Carta de trabajo original:</strong> Con vigencia no mayor a 45 días, detallando cargo, salario y desglose de deducciones.</li>
                    <li><strong>Última Ficha Digital:</strong> Emitida por la Caja de Seguro Social (CSS).</li>
                    <li><strong>Último talonario o comprobante de pago:</strong> Correspondiente al pago más reciente.</li>
                    <li><strong>Tiempo de permanencia:</strong> Mínimo 1 año de continuidad laboral comprobada.</li>
                </ul>
                <div style="background-color: #EBF5FF; border-left: 4px solid #004B93; padding: 0.8rem; border-radius: 4px; margin-top: 1rem; font-size: 0.9rem;">
                    <strong>💡 Recomendación del Asesor:</strong> Si cuenta con cuenta de ahorros o corriente en Caja de Ahorros, puede solicitar que sus cuotas se debiten automáticamente con cargo a cuenta.
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif "Salud" in perfil or "Educadores" in perfil:
            st.markdown("""
            <div class="cda-card">
                <div class="cda-card-header">🏥 Sector Salud y Educadores (Leyes Especiales)</div>
                <div style="margin-bottom: 0.8rem;">
                    <span class="cda-badge" style="background-color:#DCFCE7; color:#15803D;">⭐ Beneficio Preferencial: 1 Mes de Permanencia</span>
                    <span class="cda-badge">Plazo hasta 96 meses</span>
                </div>
                <strong>Condiciones preferenciales de financiamiento:</strong>
                <ul style="margin-top: 0.5rem;">
                    <li><strong>Tiempo de servicio mínimo:</strong> Únicamente se solicita <strong>un (1) mes de permanencia</strong> o encontrarse en periodo probatorio (PPX1/PPX2).</li>
                    <li><strong>Documentos de ingresos:</strong>
                        <ul>
                            <li>Proforma de certificado de trabajo expedida por la Contraloría General de la República o carta de Recursos Humanos.</li>
                            <li>Último talonario de pago emitido por la entidad.</li>
                        </ul>
                    </li>
                    <li><strong>Descuento directo:</strong> Aplica cómodamente vía deducción por planilla institucional.</li>
                </ul>
                <div style="background-color: #DCFCE7; border-left: 4px solid #16A34A; padding: 0.8rem; border-radius: 4px; margin-top: 1rem; font-size: 0.9rem; color: #166534;">
                    <strong>🌟 Atención Especial en Stand:</strong> Los educadores y profesionales de salud cuentan con fila de atención prioritaria en nuestro stand de la feria.
                </div>
            </div>
            """, unsafe_allow_html=True)

        elif "Gobierno General" in perfil:
            st.markdown("""
            <div class="cda-card">
                <div class="cda-card-header">🏛️ Servidores Públicos (Gobierno General)</div>
                <div style="margin-bottom: 0.8rem;">
                    <span class="cda-badge">Plazo hasta 96 meses</span>
                    <span class="cda-badge">Descuento Directo por Planilla</span>
                </div>
                <strong>Documentación específica a presentar:</strong>
                <ul style="margin-top: 0.5rem;">
                    <li><strong>Tiempo de servicio requerido:</strong> 2 años en la posición actual (o continuidad laboral de 1 año en la institución actual y 1 año previo).</li>
                    <li><strong>Certificación laboral:</strong> Proforma de certificado de trabajo de Contraloría General de la República o carta de Recursos Humanos de la entidad autónoma.</li>
                    <li><strong>Comprobante:</strong> Último talonario oficial de pago.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        elif "Jubilado" in perfil or "Ley 6" in perfil:
            st.markdown("""
            <div class="cda-card">
                <div class="cda-card-header">👴 Jubilados, Pensionados y Tercera Edad (Ley 6 de 1987)</div>
                <div style="margin-bottom: 0.8rem;">
                    <span class="cda-badge-gold">⭐ 100% Exonerado de FECI (1%)</span>
                    <span class="cda-badge-gold">⭐ 50% de Descuento en Comisión de Cierre</span>
                </div>
                <strong>Beneficios de ley aplicados automáticamente:</strong>
                <ul style="margin-top: 0.5rem;">
                    <li><strong>Cero FECI:</strong> Ahorro mensual directo por no pagar el 1% del Fondo Especial de Compensación de Intereses.</li>
                    <li><strong>Gastos de cierre reducidos:</strong> 50% de descuento en la comisión administrativa de apertura.</li>
                    <li><strong>Requisitos súper simplificados:</strong>
                        <ul>
                            <li>Cédula de identidad vigente.</li>
                            <li>Último talonario o comprobante de pago de jubilación / pensión.</li>
                            <li>Cotización del vehículo emitida por la agencia concesionaria.</li>
                        </ul>
                    </li>
                    <li><strong>Plazos:</strong> Hasta 96 meses para clientes de hasta 63 años (mujeres) y 65 años (hombres); hasta 60 meses para edades mayores.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        elif "Profesional Independiente" in perfil:
            st.markdown("""
            <div class="cda-card">
                <div class="cda-card-header">💼 Profesionales Independientes</div>
                <div style="margin-bottom: 0.8rem;">
                    <span class="cda-badge">Médicos, Abogados, Ingenieros, CPA</span>
                    <span class="cda-badge">Plazo hasta 96 meses</span>
                </div>
                <strong>Documentación requerida para evaluación de ingresos:</strong>
                <ul style="margin-top: 0.5rem;">
                    <li><strong>Certificación de ingresos:</strong> Carta expedida por un Contador Público Autorizado (CPA) correspondiente a los dos últimos periodos fiscales.</li>
                    <li><strong>Sustento bancario o fiscal:</strong> Estados de cuenta bancarios de los últimos 12 meses o copia de las dos últimas declaraciones de renta presentadas ante la DGI.</li>
                    <li><strong>Copia de idoneidad profesional:</strong> Emitida por el ente regulador respectivo en Panamá.</li>
                    <li><strong>Abono mínimo:</strong> Desde 10% regular (25% para independientes del sector agropecuario).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        elif "Extranjero" in perfil:
            st.markdown("""
            <div class="cda-card">
                <div class="cda-card-header">🌐 Extranjeros Residentes Permanentes</div>
                <div style="margin-bottom: 0.8rem;">
                    <span class="cda-badge">Residencia Permanente Comprobada</span>
                    <span class="cda-badge">Plazo hasta 96 meses</span>
                </div>
                <strong>Documentación requerida:</strong>
                <ul style="margin-top: 0.5rem;">
                    <li><strong>Identificación:</strong> Carné de residente permanente emitido por el Tribunal Electoral (cédula E) y pasaporte vigente.</li>
                    <li><strong>Permiso laboral:</strong> Permiso de trabajo por tiempo indefinido debidamente refrendado por MITRADEL.</li>
                    <li><strong>Sustento laboral:</strong> Carta de trabajo original (45 días de vigencia) y última ficha de la CSS.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        elif "Fast Track" in perfil:
            st.markdown("""
            <div class="cda-card">
                <div class="cda-card-header">⚡ Modalidad de Feria Fast Track (Aprobación Ágil de Stand)</div>
                <div style="margin-bottom: 0.8rem;">
                    <span class="cda-badge" style="background-color:#FEF3C7; color:#B45309;">⚡ Aprobación Ágil en Stand</span>
                    <span class="cda-badge">Abono Inicial Mínimo del 30%</span>
                    <span class="cda-badge">Ingreso desde B/. 1,500.00</span>
                </div>
                <strong>Condiciones y funcionamiento en la feria:</strong>
                <p>Al aportar un abono inicial igual o superior al <strong>30% del valor de venta del vehículo</strong>, su solicitud ingresa en el carril ágil de feria:</p>
                <ul style="margin-top: 0.5rem;">
                    <li><strong>Perfil de cliente elegible:</strong> Diseñado exclusivamente para colaboradores <strong>asalariados permanentes</strong> con ingresos mensuales desde <strong>B/. 1,500.00</strong>.</li>
                    <li><strong>Documentación simplificada de feria:</strong> Presente su cédula de identidad vigente, constancia laboral reciente y la cotización oficial de la agencia de autos.</li>
                    <li><strong>Atención expedita:</strong> Preaprobación y cálculo ágil directamente en nuestro stand para reservar su auto de inmediato.</li>
                    <li><strong>Menor endeudamiento:</strong> Al abonar el 30%, su cuota mensual se reduce sustancialmente frente a los planes convencionales.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# PESTAÑA 3: SIMULADOR DE PRÉSTAMO DE AUTO
# =============================================================================
with tab_simulador:
    st.markdown("""
    ### 🧮 Simulador Orientativo de Financiamiento de Auto
    Calcule su cuota mensual aproximada y genere su **Pase Digital de Atención** para presentar directamente en el stand de Caja de Ahorros.
    """)
    
    col_sim_in, col_sim_out = st.columns([5, 5])
    
    with col_sim_in:
        st.markdown("#### 1. Parámetros del Vehículo")
        
        precio_auto = st.number_input(
            "Precio de venta del auto (B/.):",
            min_value=5000.0,
            max_value=120000.0,
            value=18500.0,
            step=500.0,
            format="%.2f"
        )
        
        # Validar abono mínimo orientativo según precio
        abono_min_pct = 15.0 if precio_auto < 10000.0 else 10.0
        
        col_ab_pct, col_ab_balboa = st.columns(2)
        with col_ab_pct:
            pct_abono = st.slider(
                "Porcentaje de Abono (%):",
                min_value=10.0,
                max_value=60.0,
                value=max(15.0, abono_min_pct),
                step=1.0
            )
            
        monto_abono = precio_auto * (pct_abono / 100.0)
        with col_ab_balboa:
            st.metric("Monto del Abono:", f"B/. {monto_abono:,.2f}")

        # Mensajes orientativos de abono
        if precio_auto < 10000.0 and pct_abono < 15.0:
            st.warning("⚠️ Para vehículos con precio menor a B/. 10,000.00, los lineamientos de Caja de Ahorros solicitan un abono mínimo del 15%.")
        elif pct_abono >= 30.0:
            st.success("🎉 ¡Excelente! Con un 30% o más de abono, su trámite califica para la modalidad ágil **Fast Track** de feria.")

        st.markdown("#### 2. Condiciones del Financiamiento")
        plazo_meses = st.select_slider(
            "Plazo del préstamo (meses):",
            options=[12, 24, 36, 48, 60, 72, 84, 96],
            value=84
        )
        
        tasa_interes_anual = st.number_input(
            "Tasa de interés anual referencial (%):",
            min_value=4.0,
            max_value=12.0,
            value=6.75,
            step=0.25,
            format="%.2f",
            help="Tasa anual de referencia para la feria. La tasa final es confirmada por el ejecutivo de crédito en el stand."
        )
        
        aplica_ley6 = st.checkbox(
            "Aplica beneficio de Jubilado / Pensionado / Tercera Edad (Ley 6 de 1987)",
            value=False,
            help="Exonera el 1% de FECI y concede 50% de descuento en la comisión de cierre."
        )
        
        if aplica_ley6 and plazo_meses > 60:
            st.info("ℹ️ Para clientes mayores a 63 años (mujeres) o 65 años (hombres), los lineamientos contemplan un plazo máximo de hasta 60 meses.")

    with col_sim_out:
        st.markdown("#### 3. Resultado de la Simulación")
        
        # Cálculos financieros
        monto_financiar = precio_auto - monto_abono
        tasa_mensual = (tasa_interes_anual / 100.0) / 12.0
        
        # Cuota mensual de capital e interés (Amortización francesa)
        if tasa_mensual > 0:
            cuota_capital_interes = monto_financiar * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)
        else:
            cuota_capital_interes = monto_financiar / plazo_meses

        # FECI (1% anual sobre saldo, obligatorio en Panamá para préstamos personales/autos > B/. 5,000 salvo que aplique Ley 6)
        if aplica_ley6 or monto_financiar <= 5000.0:
            tasa_feci_anual = 0.0
            cuota_feci = 0.0
        else:
            tasa_feci_anual = 1.0
            cuota_feci = (monto_financiar * 0.01) / 12.0

        # Seguro aproximado de auto (estimación referencial feria ~ B/. 38 mensual)
        seguro_auto_estimado = 38.00
        
        cuota_total_estimada = cuota_capital_interes + cuota_feci + seguro_auto_estimado
        
        # Gastos de cierre referenciales
        comision_cierre_base = max(150.0, monto_financiar * 0.01)
        if aplica_ley6:
            comision_cierre_estimada = comision_cierre_base * 0.50
        else:
            comision_cierre_estimada = comision_cierre_base

        # Renderizar métricas destacadas
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #002855 0%, #004B93 100%); color: white; border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1rem;">
            <div style="font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; opacity: 0.9;">Cuota Mensual Total Estimada</div>
            <div style="font-size: 2.5rem; font-weight: 800; color: #FFFFFF; margin: 0.2rem 0;">B/. {cuota_total_estimada:,.2f}</div>
            <div style="font-size: 0.85rem; opacity: 0.85;">Incluye Capital + Intereses + FECI + Seguro Estimado</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Desglose en tarjetas
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("Monto a Financiar", f"B/. {monto_financiar:,.2f}")
            st.metric("Capital e Intereses", f"B/. {cuota_capital_interes:,.2f}/mes")
        with col_m2:
            st.metric("Plazo Seleccionado", f"{plazo_meses} meses ({plazo_meses//12} años)")
            if aplica_ley6:
                st.metric("Impuesto FECI", "B/. 0.00 (Exonerado)")
            else:
                st.metric("Impuesto FECI", f"B/. {cuota_feci:,.2f}/mes")
                
        # Detalle de beneficios aplicados
        st.markdown("---")
        st.markdown("**Beneficios y Gastos Iniciales Estimados:**")
        st.markdown(f"• **Comisión de Cierre Estimada:** B/. {comision_cierre_estimada:,.2f}" + (" *(50% de descuento Ley 6 aplicado)*" if aplica_ley6 else ""))
        if aplica_ley6:
            st.markdown("• **Exoneración de FECI:** Ahorro directo de ~ B/. {:,.2f} al año".format(cuota_feci * 12 if cuota_feci > 0 else (monto_financiar * 0.01)))
        st.markdown("• **Seguro de Auto:** Estimado en B/. 38.00/mes (ajustable según póliza seleccionada en feria).")

        # Generador de Pase Digital de Atención
        st.markdown("---")
        if st.button("🎫 Generar Pase Digital de Atención para el Stand", use_container_width=True):
            codigo_pase = f"CDA-AUTO-{random.randint(1000, 9999)}"
            fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
            
            st.markdown(f"""
            <div class="cda-pass">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #CBD5E1; padding-bottom:0.5rem; margin-bottom:0.8rem;">
                    <strong style="color:#002855; font-size:1.1rem;">PASE DIGITAL DE ATENCIÓN • FERIA DE AUTOS</strong>
                    <span style="background-color:#002855; color:white; font-weight:700; padding:0.2rem 0.6rem; border-radius:4px;">{codigo_pase}</span>
                </div>
                <div style="font-size:0.9rem; color:#334155; line-height:1.6;">
                    <strong>Fecha:</strong> {fecha_hoy}<br>
                    <strong>Valor del Auto:</strong> B/. {precio_auto:,.2f} | <strong>Abono:</strong> B/. {monto_abono:,.2f} ({pct_abono:.0f}%)<br>
                    <strong>Monto Solicitado:</strong> B/. {monto_financiar:,.2f} | <strong>Plazo:</strong> {plazo_meses} meses<br>
                    <strong>Cuota Referencial:</strong> B/. {cuota_total_estimada:,.2f}/mes<br>
                    <strong>Beneficio Tercera Edad / Ley 6:</strong> {"SÍ (Exonerado FECI)" if aplica_ley6 else "No aplica"}<br>
                </div>
                <div style="margin-top:0.8rem; font-size:0.8rem; color:#64748B; border-top:1px solid #E2E8F0; padding-top:0.5rem;">
                    Presente este comprobante o mencione el código <strong>{codigo_pase}</strong> al oficial de crédito en nuestro stand de Caja de Ahorros para agilizar su atención.<br>
                    <em>*Cálculo referencial y orientativo sujeto a la evaluación crediticia formal del banco.*</em>
                </div>
            </div>
            """, unsafe_allow_html=True)
