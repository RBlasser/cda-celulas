"""
Asesor Virtual de Auto - Feria de Préstamos Caja de Ahorros
Desarrollado con Chainlit.
Proporciona atención conversacional ágil, streaming de respuestas con Gemini,
orientación por perfil laboral, indagación progresiva no invasiva y simulación con pase digital.
"""

import os
import re
import sys
import asyncio
import random
import datetime
from dotenv import load_dotenv
import chainlit as cl
import nest_asyncio
nest_asyncio.apply = lambda *args, **kwargs: None

# Fix de compatibilidad para Python 3.14 y AnyIO / Starlette / Nest-AsyncIO
import sniffio
sniffio.current_async_library = lambda: "asyncio"

if sys.version_info >= (3, 14) and hasattr(asyncio.tasks, '_CTask'):
    asyncio.Task = asyncio.tasks.Task = asyncio.tasks._CTask
    asyncio.Future = asyncio.futures.Future = asyncio.futures._CFuture

from knowledge_base import SYSTEM_PROMPT, KNOWLEDGE_CONTEXT
from gemini_client import stream_gemini_api, get_smart_local_response
from database import (
    guardar_cliente as db_guardar_cliente,
    guardar_chat_json as db_guardar_chat_json,
    actualizar_perfil_cliente as db_actualizar_perfil_cliente,
    DB_PATH
)

# Cargar variables de entorno (.env)
load_dotenv()


def guardar_lead_registro(client_data: dict):
    """Almacena el lead registrado en un archivo JSON local para seguimiento comercial."""
    import json
    leads_file = "leads_feria_autos.json"
    registro = {
        **client_data,
        "fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        leads = []
        if os.path.exists(leads_file):
            with open(leads_file, "r", encoding="utf-8") as f:
                leads = json.load(f)
        ced = registro.get("cedula")
        updated = False
        for i, lead in enumerate(leads):
            if ced and lead.get("cedula") == ced:
                leads[i].update(registro)
                updated = True
                break
        if not updated:
            leads.append(registro)
        with open(leads_file, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar lead: {e}")


def obtener_mensaje_condiciones_politica(params: dict = None):
    """
    Genera la respuesta con información general de la política pública (zona no confidencial)
    sin realizar cálculos de cuotas, letras, FECI ni seguros, invitando a la perfilación.
    """
    marca_str = f" para su vehículo **{params['marca']}**" if params and params.get("marca") else ""
    abono_ref = f" (con su **{params['pct_abono']:.0f}% de abono** previsto)" if params and params.get("pct_abono") else ""
    
    contenido = (
        f"### 📋 Condiciones Generales de Financiamiento (Política Pública) 🚗 🇵🇦\n\n"
        f"En **Caja de Ahorros**, las cuotas mensuales exactas y corridas financieras formales son estructuradas "
        f"directamente por un **oficial de crédito** en el stand de la feria o en cualquiera de nuestras sucursales, "
        f"utilizando la cotización formal emitida por la agencia concesionaria{marca_str}.\n\n"
        f"**Lineamientos generales de financiamiento:**\n"
        f"• **Plazos máximos:** Hasta **84 meses (7 años)** y hasta **96 meses (8 años)** para autos nuevos en colaboradores asalariados e independientes (hasta **60 meses** en jubilados o mayores a 63/65 años).\n"
        f"• **Abono inicial requerido:** Desde el **10%** en condiciones regulares de feria{abono_ref}, o **30%** bajo la modalidad ágil *Fast Track*.\n"
        f"• **Beneficios por Ley 6 de 1987:** Clientes jubilados y de tercera edad cuentan con **100% de exoneración del impuesto FECI** y 50% de descuento en gastos de cierre.\n"
        f"• **Convenios de Leyes Especiales:** Servidores públicos de Salud y Educación aplican con solo **1 mes de permanencia** laboral o periodo probatorio.\n\n"
        f"---\n\n"
        f"🎯 **Para orientarle con el mejor plan y asignarle un código de turno prioritario en stand:**\n"
        f"¿Desea realizar la **Asesoría Personalizada en 4 pasos rápidos** para perfilar su solicitud?"
    )
    
    acciones = [
        cl.Action(name="iniciar_perfilacion", payload={"value": "Deseo realizar la asesoría personalizada paso a paso"}, label="🎯 Iniciar Perfilación (4 Pasos)"),
        cl.Action(name="salud_educadores", payload={"value": "¿Cuáles son los requisitos y el tiempo de permanencia si soy educador o trabajo en el sector salud?"}, label="🏥 Salud y Educadores"),
        cl.Action(name="fast_track", payload={"value": "¿Cuánto es el porcentaje de abono mínimo y cómo funciona la modalidad Fast Track de feria?"}, label="⚡ Modalidad Fast Track (30%)"),
        cl.Action(name="jubilados", payload={"value": "¿Qué beneficios aplican para jubilados y tercera edad según la Ley 6 de 1987?"}, label="👴 Jubilados (Ley 6)")
    ]
    return contenido, acciones


def es_consulta_letra_o_cuota(texto: str) -> bool:
    """Detecta si el usuario pregunta por letras, cuotas, montos mensuales o simulación."""
    t = texto.lower()
    frases = [
        "letra", "cuota", "cuanto pagaria", "cuánto pagaría", "cuanto seria", "cuánto sería",
        "cuanto podria costarme", "cuánto podría costarme", "costaria", "costaría",
        "calcular", "simular", "simulacion", "simulación", "feci", "amortizacion", "amortización",
        "tabla de pago", "desglose", "intereses", "mensualidad", "pago mensual", "precio"
    ]
    return any(f in t for f in frases)


def es_intencion_perfilacion(texto: str) -> bool:
    """Detecta si el usuario desea asesoría personalizada o perfilación para saber su mejor opción."""
    t = texto.lower()
    frases = [
        "asesoria personalizada", "asesoría personalizada",
        "perfilarme", "perfilacion", "perfilación",
        "recomiendame", "recomiéndame", "mejor tasa",
        "que me conviene", "qué me conviene",
        "orientame segun mi perfil", "oriéntame según mi perfil",
        "quiero asesorarme", "asesorame", "asesórame"
    ]
    return any(f in t for f in frases)


def extraer_parametros_consulta(texto: str, historial: list = None) -> dict:
    """Extrae datos de contexto como marca, abono o sector para personalizar respuestas sin calcular letras."""
    t = texto.lower()
    
    marca_detectada = None
    pct_abono_hist = None
    sector_hist = None
    
    marcas_conocidas = [
        "nissan", "toyota", "hyundai", "kia", "byd", "geely", "changan",
        "suzuki", "honda", "mazda", "ford", "chevrolet", "gac", "mg", "chery"
    ]
    for m in marcas_conocidas:
        if m in t:
            marca_detectada = m.title()
            break

    match_pct = re.search(r'(\d{1,2})\s*%', t)
    if match_pct:
        try:
            pct_abono_hist = float(match_pct.group(1))
        except ValueError:
            pass

    if historial:
        for msg in reversed(historial):
            c = msg.get("content", "").lower()
            if not marca_detectada:
                for m in marcas_conocidas:
                    if m in c:
                        marca_detectada = m.title()
                        break
            if not pct_abono_hist:
                mpct = re.search(r'(\d{1,2})\s*%', c)
                if mpct:
                    try:
                        pct_abono_hist = float(mpct.group(1))
                    except ValueError:
                        pass
            if not sector_hist:
                if any(k in c for k in ["consultor", "independiente", "servicios profesionales"]):
                    sector_hist = "Profesional Independiente"
                elif any(k in c for k in ["educa", "maestr", "profesor", "salud", "medic", "médic", "enfermer"]):
                    sector_hist = "Salud / Educación"
                elif any(k in c for k in ["jubilad", "pensionad", "ley 6", "tercera edad"]):
                    sector_hist = "Jubilado"
                elif any(k in c for k in ["privad", "empresa"]):
                    sector_hist = "Empresa Privada"
                elif any(k in c for k in ["public", "públic", "gobiern"]):
                    sector_hist = "Sector Público"

    return {
        "pct_abono": pct_abono_hist or 10.0,
        "marca": marca_detectada,
        "sector": sector_hist
    }


# =========================================================================
# FLUJO DE INDAGACIÓN PROGRESIVA NO INVASIVA (4 PASOS "GIVE TO GET")
# =========================================================================

async def iniciar_paso_1_uso():
    """Paso 1: Uso del vehículo para orientar producto y plazo sin pedir dinero."""
    cl.user_session.set("perfil_comercial", {})
    msg = (
        "### 🎯 Asesoría Personalizada — Paso 1 de 4\n\n"
        "Para orientarle con el mejor plan y plazo de financiamiento de Caja de Ahorros:\n\n"
        "¿Este vehículo sería principalmente para su **uso personal / familiar** o para **trabajo / plataforma / negocio**?"
    )
    actions = [
        cl.Action(name="perfil_uso", payload={"value": "Personal / Familiar"}, label="👨‍👩‍👧 Familiar / Personal"),
        cl.Action(name="perfil_uso", payload={"value": "Trabajo / Negocio / Plataforma"}, label="💼 Trabajo / Negocio")
    ]
    await cl.Message(content=msg, actions=actions).send()


@cl.action_callback("iniciar_perfilacion")
async def callback_iniciar_perfilacion(action: cl.Action):
    await iniciar_paso_1_uso()


@cl.action_callback("perfil_uso")
async def callback_perfil_uso(action: cl.Action):
    uso = action.payload.get("value", "Personal / Familiar")
    perfil = cl.user_session.get("perfil_comercial", {})
    perfil["uso_vehiculo"] = uso
    cl.user_session.set("perfil_comercial", perfil)

    msg = (
        f"✓ **Uso registrado:** {uso}\n\n"
        "### 🏛️ Paso 2 de 4: Sector Laboral (Convenios Institucionales)\n\n"
        "En Caja de Ahorros contamos con condiciones preferenciales según su sector (por ejemplo, aprobación rápida con **solo 1 mes de permanencia** para Salud y Educación, o **0% FECI** para jubilados).\n\n"
        "¿En qué sector labora actualmente?"
    )
    actions = [
        cl.Action(name="perfil_sector", payload={"value": "Salud o Educación (Leyes Especiales)"}, label="🏥 Salud / Educación"),
        cl.Action(name="perfil_sector", payload={"value": "Sector Público / Gobierno"}, label="🏛️ Sector Público"),
        cl.Action(name="perfil_sector", payload={"value": "Empresa Privada"}, label="🏢 Empresa Privada"),
        cl.Action(name="perfil_sector", payload={"value": "Profesional Independiente"}, label="👔 Independiente"),
        cl.Action(name="perfil_sector", payload={"value": "Jubilado / Pensionado (Ley 6)"}, label="👴 Jubilado (Ley 6)")
    ]
    await cl.Message(content=msg, actions=actions).send()


@cl.action_callback("perfil_sector")
async def callback_perfil_sector(action: cl.Action):
    sector = action.payload.get("value", "Empresa Privada")
    perfil = cl.user_session.get("perfil_comercial", {})
    perfil["sector_laboral"] = sector
    cl.user_session.set("perfil_comercial", perfil)

    msg = (
        f"✓ **Sector registrado:** {sector}\n\n"
        "### 💵 Paso 3 de 4: Modalidad de Abono Inicial\n\n"
        "Respecto al enganche inicial de su auto: ¿Tiene contemplado entregar un abono en efectivo o dar un auto usado como parte de pago (*Trade-in*)?"
    )
    actions = [
        cl.Action(name="perfil_abono", payload={"value": "Abono en efectivo"}, label="💵 Abono en efectivo"),
        cl.Action(name="perfil_abono", payload={"value": "Auto usado para cambio (Trade-in)"}, label="🚗 Auto a cambio (Trade-in)"),
        cl.Action(name="perfil_abono", payload={"value": "Busco financiamiento con mínimo (10%)"}, label="⚡ Mínimo de feria (10%)")
    ]
    await cl.Message(content=msg, actions=actions).send()


@cl.action_callback("perfil_abono")
async def callback_perfil_abono(action: cl.Action):
    abono = action.payload.get("value", "Mínimo de feria (10%)")
    perfil = cl.user_session.get("perfil_comercial", {})
    perfil["tipo_abono"] = abono
    cl.user_session.set("perfil_comercial", perfil)

    msg = (
        f"✓ **Modalidad de abono:** {abono}\n\n"
        "### ⏱️ Paso 4 de 4: Momento de Decisión\n\n"
        "Para que nuestro equipo en el stand le reserve la tasa promocional de feria:\n\n"
        "¿Su plan es aprovechar las condiciones del evento para reservar **este mes**, o está evaluando opciones con calma para más adelante?"
    )
    actions = [
        cl.Action(name="perfil_tiempo", payload={"value": "Aprovechar la feria (Este mes)", "temp": "🔥 ALTA (Cierre en Feria)"}, label="🔥 Aprovechar la feria (Este mes)"),
        cl.Action(name="perfil_tiempo", payload={"value": "Próximos 2 a 3 meses", "temp": "⚡ MEDIA (Prospecto Calificado)"}, label="🗓️ Próximos 2 a 3 meses"),
        cl.Action(name="perfil_tiempo", payload={"value": "Solo explorando opciones", "temp": "🔍 INFORMATIVO"}, label="🔍 Solo explorando opciones")
    ]
    await cl.Message(content=msg, actions=actions).send()


@cl.action_callback("perfil_tiempo")
async def callback_perfil_tiempo(action: cl.Action):
    momento = action.payload.get("value", "Este mes")
    temp = action.payload.get("temp", "ALTA")
    session_id = cl.user_session.get("session_id") or cl.user_session.get("id") or "default-session"
    
    perfil = cl.user_session.get("perfil_comercial", {})
    perfil["momento_compra"] = momento
    perfil["temperatura_lead"] = temp
    cl.user_session.set("perfil_comercial", perfil)
    
    # Persistir perfil comercial en base de datos SQLite
    db_actualizar_perfil_cliente(session_id, perfil)
    
    # Actualizar archivo tabular/JSON de leads
    client_data = cl.user_session.get("client_data") or {}
    full_lead = {**client_data, **perfil}
    guardar_lead_registro(full_lead)
    
    codigo_pase = cl.user_session.get("codigo_pase") or f"CDA-FERIA-{random.randint(1000, 9999)}"
    
    # Identificar beneficio comercial directo para mostrar valor
    sector = perfil.get("sector_laboral", "")
    if "Salud" in sector or "Educación" in sector:
        beneficio_desc = (
            "• **Beneficio Exclusivo CDA:** Aplica trámite ágil con **solo 1 mes de permanencia** o periodo probatorio (Leyes especiales) y opción de descuento directo."
        )
    elif "Jubilado" in sector:
        beneficio_desc = (
            "• **Beneficio de Ley 6 de 1987:** Exoneración del **100% del impuesto FECI** y **50% de descuento** en gastos de cierre del préstamo."
        )
    elif "Público" in sector:
        beneficio_desc = (
            "• **Beneficio para Sector Público:** Financiamiento de hasta 84 meses por descuento directo con cuota preferencial."
        )
    else:
        beneficio_desc = (
            "• **Condiciones de Feria:** Financiamiento de hasta 84 meses (7 años) y abonos desde el 10% en marcas tradicionales y chinas autorizadas (BYD, Geely, Changan)."
        )

    resumen_msg = (
        f"### 🎉 ¡Perfil Configurado con Éxito!\n\n"
        f"Estimado/a **{client_data.get('nombre', 'Cliente')}**, hemos estructurado su ficha comercial para la feria:\n\n"
        f"• **Uso Previsto:** {perfil.get('uso_vehiculo')}\n"
        f"• **Sector Laboral:** {perfil.get('sector_laboral')}\n"
        f"• **Modalidad de Abono:** {perfil.get('tipo_abono')}\n"
        f"• **Interés de Compra:** {perfil.get('temperatura_lead')}\n"
        f"{beneficio_desc}\n\n"
        f"---\n\n"
        f"### 🎫 Su Pase Digital Prioritario de Atención\n"
        f"**Código de Turno:** `{codigo_pase}`\n\n"
        f"Mencione este código a nuestro oficial de crédito en el stand de **Caja de Ahorros** en la feria para recibir atención preferencial y tramitar su cotización formal.\n\n"
        f"*¿Desea consultar los requisitos de su perfil o las marcas autorizadas?*"
    )
    
    post_actions = [
        cl.Action(name="requisitos_laborales", payload={"value": "¿Cuáles son los requisitos de documentación para mi perfil?"}, label="📋 Requisitos Documentales"),
        cl.Action(name="marcas_chinas", payload={"value": "¿Qué marcas chinas financia Caja de Ahorros?"}, label="🇨🇳 Marcas Chinas (BYD, Geely)"),
        cl.Action(name="fast_track", payload={"value": "¿Cómo funciona la modalidad Fast Track de 30% de abono?"}, label="⚡ Modalidad Fast Track")
    ]
    
    messages = cl.user_session.get("messages", [])
    messages.append({"role": "assistant", "content": resumen_msg})
    cl.user_session.set("messages", messages)
    db_guardar_chat_json(session_id, messages, pase_digital=codigo_pase)
    
    await cl.Message(content=resumen_msg, actions=post_actions).send()


# =========================================================================
# CICLO DE VIDA DE CHAINLIT
# =========================================================================

@cl.on_chat_start
async def on_chat_start():
    """Inicializa la sesión de chat y crea el registro base en SQLite."""
    session_id = cl.user_session.get("id") or str(random.randint(100000, 999999))
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("messages", [])
    cl.user_session.set("client_data", None)
    cl.user_session.set("perfil_comercial", {})
    
    # Inicializar sesión en la base de datos SQLite
    db_guardar_chat_json(session_id, [])
    
    await cl.Message(
        content=(
            "### 🚗 ¡Bienvenido a la Feria de Autos con **Caja de Ahorros**!\n"
            "*El Banco de la Familia Panameña* 🇵🇦\n\n"
            "👋 **Paso previo:** Complete el formulario en pantalla con su **Nombre, Cédula, Celular y Correo** para activar al **Asesor Virtual** y asignarle su Pase Digital de feria.\n\n"
            "*Una vez enviado, el asistente activará inmediatamente todas las opciones de asesoría personalizada y simulación.*"
        )
    ).send()


@cl.action_callback("salud_educadores")
@cl.action_callback("marcas_chinas")
@cl.action_callback("fast_track")
@cl.action_callback("jubilados")
@cl.action_callback("politica_condiciones")
@cl.action_callback("requisitos_laborales")
async def handle_quick_action(action: cl.Action):
    """Maneja los clics en los botones de acción rápida."""
    query = action.payload.get("value", "")
    await process_user_query(query)


@cl.on_message
async def on_message(message: cl.Message):
    """Maneja los mensajes ingresados por el usuario."""
    is_reg = "Registro de Precalificación:" in message.content or "[REGISTRO_CLIENTE]" in message.content
    # No llamar a message.remove() aquí: en Chainlit 2.x eliminar el mensaje del turno suprime
    # los mensajes de respuesta asociados. custom.js ya lo oculta visualmente del DOM con CSS.
    await process_user_query(message.content, is_registration=is_reg)


async def process_user_query(user_query: str, is_registration: bool = False):
    """Procesa la consulta del usuario persistiendo clientes y chat JSON en SQLite."""
    session_id = cl.user_session.get("session_id") or cl.user_session.get("id") or "default-session"
    messages = cl.user_session.get("messages", [])
    if not is_registration:
        messages.append({"role": "user", "content": user_query})
        # Persistir turno de usuario en SQLite
        db_guardar_chat_json(session_id, messages)
    
    # 0. CASO DETERMINÍSTICO PREVIO: Registro de Formulario del Cliente
    if "Registro de Precalificación:" in user_query or "[REGISTRO_CLIENTE]" in user_query:
        nombre_m = re.search(r'Nombre:\s*([^|]+)', user_query)
        cedula_m = re.search(r'C[eé]dula:\s*([^|]+)', user_query)
        celular_m = re.search(r'Celular:\s*([^|]+)', user_query)
        correo_m = re.search(r'Correo:\s*([^\s|]+)', user_query)
        
        client_data = {
            "nombre": nombre_m.group(1).strip() if nombre_m else "Cliente Estimado",
            "cedula": cedula_m.group(1).strip() if cedula_m else "N/A",
            "celular": celular_m.group(1).strip() if celular_m else "N/A",
            "correo": correo_m.group(1).strip() if correo_m else "N/A"
        }
        
        cl.user_session.set("client_data", client_data)
        
        db_guardar_cliente(
            session_id=session_id,
            nombre=client_data["nombre"],
            cedula=client_data["cedula"],
            celular=client_data["celular"],
            correo=client_data["correo"]
        )
        codigo_pase = cl.user_session.get("codigo_pase") or f"CDA-FERIA-{random.randint(1000, 9999)}"
        cl.user_session.set("codigo_pase", codigo_pase)
        
        guardar_lead_registro({**client_data, "codigo_pase": codigo_pase})
        
        bienvenida = (
            f"### ¡Mucho gusto y bienvenido/a, **{client_data['nombre']}**! 🚗 🇵🇦\n"
            f"*Caja de Ahorros — El Banco de la Familia Panameña*\n\n"
            f"Hemos registrado exitosamente sus datos de contacto para su cotización:\n"
            f"• **Titular:** {client_data['nombre']}\n"
            f"• **Cédula de Identidad:** `{client_data['cedula']}`\n"
            f"• **Celular:** `{client_data['celular']}`\n"
            f"• **Correo:** `{client_data['correo']}`\n\n"
            f"---\n\n"
            f"### 🎟️ ¡Pase Digital de Atención Prioritaria!\n"
            f"**Código de Turno:** `{codigo_pase}`\n\n"
            f"He preparado su perfil para atenderle sin esperas en la feria. Le invitamos a acercarse a nuestro stand de **Caja de Ahorros** presentando este mensaje para que un oficial de crédito le realice su corrida financiera formal y cotización formalizada al instante.\n\n"
            f"*¿Le gustaría confirmarme si tiene pensado visitar nuestro stand durante estos días de feria?*\n\n"
            f"---\n"
            f"Soy su **Asesor Virtual de Auto**. Para orientarle con la tasa y beneficios más convenientes, puede realizar una **Asesoría Personalizada en 4 pasos rápidos** o consultar cualquiera de nuestras opciones:"
        )
        
        actions = [
            cl.Action(name="iniciar_perfilacion", payload={"value": "Deseo realizar la asesoría personalizada paso a paso"}, label="🎯 Asesoría Personalizada (Mejor Plan)"),
            cl.Action(name="politica_condiciones", payload={"value": "¿Cuáles son las condiciones de plazos y abonos mínimos de feria según las políticas del banco?"}, label="📋 Plazos y Abonos de Feria"),
            cl.Action(name="salud_educadores", payload={"value": "¿Cuáles son los requisitos y el tiempo de permanencia si soy educador o trabajo en el sector salud?"}, label="🏥 Salud y Educadores"),
            cl.Action(name="marcas_chinas", payload={"value": "¿Puedo financiar un vehículo de marcas de origen chino como BYD, Geely o Changan con Caja de Ahorros?"}, label="🇨🇳 Marcas Chinas (BYD, Geely)"),
            cl.Action(name="fast_track", payload={"value": "¿Cuánto es el porcentaje de abono mínimo y cómo funciona la modalidad Fast Track de feria?"}, label="⚡ Abonos y Fast Track"),
            cl.Action(name="jubilados", payload={"value": "¿Qué beneficios aplican para jubilados y tercera edad según la Ley 6 de 1987?"}, label="👴 Jubilados (Ley 6)"),
        ]
        
        messages.append({"role": "assistant", "content": bienvenida})
        cl.user_session.set("messages", messages)
        db_guardar_chat_json(session_id, messages, pase_digital=codigo_pase)
        
        await cl.Message(content=bienvenida, actions=actions).send()
        return

    # 1. CASO DETERMINÍSTICO A: El usuario pide asesoría o perfilación personalizada
    if es_intencion_perfilacion(user_query):
        await iniciar_paso_1_uso()
        return

    # 2. CASO DETERMINÍSTICO B: El usuario pregunta por cuotas, letras, cálculos o condiciones de financiamiento
    if es_consulta_letra_o_cuota(user_query):
        params = extraer_parametros_consulta(user_query, messages)
        contenido, acciones = obtener_mensaje_condiciones_politica(params)
        messages.append({"role": "assistant", "content": contenido})
        cl.user_session.set("messages", messages)
        db_guardar_chat_json(session_id, messages)
        
        await cl.Message(content=contenido, actions=acciones).send()
        return

    # 4. Consulta de orientación con Gemini Streaming o Fallback local
    api_key = os.getenv("GEMINI_API_KEY", "")
    streamed_anything = False
    
    reply_msg = cl.Message(content="")
    
    if api_key:
        async with cl.Step(name="Orientación Inteligente Caja de Ahorros", type="tool") as step:
            step.output = "Consultando lineamientos de financiamiento de feria..."
            
        try:
            loop = asyncio.get_event_loop()
            
            def get_chunks():
                return list(stream_gemini_api(messages, api_key=api_key))
                
            chunks = await loop.run_in_executor(None, get_chunks)
            
            if chunks:
                streamed_anything = True
                for chunk in chunks:
                    await reply_msg.stream_token(chunk)
                    await asyncio.sleep(0.01)
                await reply_msg.send()
        except Exception:
            streamed_anything = False

    if not streamed_anything:
        fallback_text = get_smart_local_response(user_query)
        words = fallback_text.split(" ")
        for i, word in enumerate(words):
            token = word + (" " if i < len(words) - 1 else "")
            await reply_msg.stream_token(token)
            await asyncio.sleep(0.02)
        await reply_msg.send()
        reply_content = fallback_text
    else:
        reply_content = reply_msg.content

    messages.append({"role": "assistant", "content": reply_content})
    cl.user_session.set("messages", messages)
    db_guardar_chat_json(session_id, messages)
