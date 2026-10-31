"""
Asesor Virtual de Auto - Feria de Préstamos Caja de Ahorros
Desarrollado con Chainlit.
Proporciona atención conversacional ágil, streaming de respuestas con Gemini,
orientación por perfil laboral y simulación de crédito con generación de pase digital.
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
    DB_PATH
)

# Cargar variables de entorno (.env)
load_dotenv()


def calculate_loan_summary(
    precio: float, 
    pct_abono: float = 10.0, 
    plazo_meses: int = 84, 
    tasa_anual: float = 6.75, 
    es_jubilado: bool = False,
    es_salud_educacion: bool = False
):
    """
    Cálculo matemático puro y determinístico de la cuota de auto.
    Aplica lineamientos de Caja de Ahorros y Ley 6 de 1987.
    """
    # Política de abonos mínimos
    if precio < 10000.0 and pct_abono < 15.0:
        pct_abono = 15.0
    elif pct_abono < 10.0:
        pct_abono = 10.0
        
    monto_abono = round(precio * (pct_abono / 100.0), 2)
    monto_financiar = round(precio - monto_abono, 2)
    tasa_mensual = (tasa_anual / 100.0) / 12.0
    
    # Amortización francesa nivelada
    if tasa_mensual > 0:
        factor = (1 + tasa_mensual) ** plazo_meses
        cuota_cap_int = round(monto_financiar * (tasa_mensual * factor) / (factor - 1), 2)
    else:
        cuota_cap_int = round(monto_financiar / plazo_meses, 2)
        
    # FECI (1% anual si aplica regular, 0% si jubilado Ley 6 o financiamiento <= B/. 5,000)
    if es_jubilado or monto_financiar <= 5000.0:
        cuota_feci = 0.00
    else:
        cuota_feci = round((monto_financiar * 0.01) / 12.0, 2)
        
    seguro_estimado = 38.00
    cuota_total = round(cuota_cap_int + cuota_feci + seguro_estimado, 2)
    codigo_pase = f"CDA-AUTO-{random.randint(1000, 9999)}"
    
    return {
        "precio": precio,
        "pct_abono": pct_abono,
        "monto_abono": monto_abono,
        "monto_financiar": monto_financiar,
        "plazo_meses": plazo_meses,
        "cuota_cap_int": cuota_cap_int,
        "cuota_feci": cuota_feci,
        "seguro_estimado": seguro_estimado,
        "cuota_total": cuota_total,
        "codigo_pase": codigo_pase,
        "es_jubilado": es_jubilado,
        "es_salud_educacion": es_salud_educacion
    }


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
        leads.append(registro)
        with open(leads_file, "w", encoding="utf-8") as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error al guardar lead: {e}")


def format_loan_markdown(data: dict, client_data: dict = None) -> str:
    """Formatea la simulación y el pase digital en un mensaje markdown profesional y determinístico."""
    if data["es_jubilado"]:
        feci_str = "B/. 0.00 *(Exonerado 100% por Ley 6 de 1987)*"
        beneficio_perfil = "• **Condición Especial:** Jubilado / Pensionado *(Aplica beneficio de Ley 6: 0% FECI y 50% de descuento en gastos de cierre)*\n"
    elif data.get("es_salud_educacion", False):
        feci_str = f"B/. {data['cuota_feci']:,.2f}/mes"
        beneficio_perfil = "• **Condición Especial:** Sector Salud / Educación *(Beneficio de permanencia preferencial desde 1 mes o periodo probatorio)*\n"
    else:
        feci_str = f"B/. {data['cuota_feci']:,.2f}/mes"
        beneficio_perfil = ""
    
    # Inclusión de datos del titular registrado
    if client_data and client_data.get("nombre"):
        titular_str = (
            f"• **Titular:** {client_data['nombre']}\n"
            f"• **Cédula de Identidad:** `{client_data.get('cedula', 'N/A')}`\n"
            f"• **Contacto:** {client_data.get('celular', 'N/A')} | {client_data.get('correo', 'N/A')}\n"
        )
    else:
        titular_str = ""
    
    md = (
        f"### 🧮 Simulación Estimada de Financiamiento\n\n"
        f"• **Precio de Venta del Auto:** B/. {data['precio']:,.2f}\n"
        f"• **Abono Inicial ({data['pct_abono']:.0f}%):** B/. {data['monto_abono']:,.2f}\n"
        f"• **Monto Neto a Financiar:** B/. {data['monto_financiar']:,.2f}\n"
        f"• **Plazo:** {data['plazo_meses']} meses ({data['plazo_meses']//12} años)\n"
        f"{beneficio_perfil}\n"
        f"---\n"
        f"### 💳 **Cuota Mensual Total Aproximada:** **B/. {data['cuota_total']:,.2f}**\n\n"
        f"**Desglose mensual de la cuota:**\n"
        f"• **Capital e Intereses:** B/. {data['cuota_cap_int']:,.2f}/mes\n"
        f"• **Impuesto FECI:** {feci_str}\n"
        f"• **Seguro de Auto y Vida Estimado:** B/. {data['seguro_estimado']:,.2f}/mes\n\n"
        f"---\n"
        f"### 🎫 Pase Digital de Atención en Stand\n"
        f"**Código de Turno:** `{data['codigo_pase']}`\n"
        f"{titular_str}\n"
        f"Presente este código o menciónelo al oficial de crédito en nuestro stand de **Caja de Ahorros** en la feria para agilizar su cotización y precalificación formal.\n\n"
        f"*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
    )
    return md


def es_pregunta_solicitud_datos_letra(texto: str) -> bool:
    """Detecta determinísticamente si el usuario pregunta qué se necesita o cuál sería su letra sin dar aún cifras."""
    t = texto.lower()
    frases_clave = [
        "cual seria mi letra", "cuál sería mi letra",
        "que necesitas saber", "qué necesitas saber",
        "que ocupas saber", "qué ocupas saber",
        "que datos necesitas", "qué datos necesitas",
        "que ocupan saber de mi", "qué ocupan saber de mí",
        "que se necesita para saber mi letra", "qué se necesita para saber mi letra",
        "como se calcula la letra", "cómo se calcula la letra",
        "como calculo mi letra", "cómo calculo mi letra",
        "que piden para saber la cuota", "qué piden para saber la cuota",
        "que necesito para simular", "qué necesito para simular"
    ]
    coincide_frase = any(f in t for f in frases_clave)
    tiene_letra_y_pregunta = ("letra" in t or "cuota" in t) and any(w in t for w in ["que", "qué", "como", "cómo", "saber", "necesit", "ocup"])
    
    # Verificar si ya incluye números explícitos de precio (en cuyo caso se debe simular)
    tiene_cifras = bool(re.search(r'\d{4,6}|\d{1,3}[,\.]\d{3}', t))
    
    return (coincide_frase or tiene_letra_y_pregunta) and not tiene_cifras


def obtener_mensaje_solicitud_datos():
    """Genera la respuesta cordial solicitando los 4 datos clave con botones interactivos."""
    contenido = (
        "¡Con mucho gusto le ayudamos a calcular su letra mensual estimada! 🚗🇵🇦\n\n"
        "Para brindarle una cifra personalizada y transparente que incluya capital, intereses y los seguros correspondientes, requerimos conocer los siguientes detalles:\n\n"
        "1. **Precio del vehículo:** El valor de venta aproximado del auto que le interesa (nuevo o de marcas participantes).\n"
        "2. **Abono inicial:** Cuánto tiene previsto aportar como abono (el mínimo de feria es desde el 10% en autos regulares, o 30% si desea calificar a la modalidad ágil *Fast Track*).\n"
        "3. **Su perfil laboral:**\n"
        "   - Empresa privada o gobierno (permanente o continuidad laboral).\n"
        "   - Leyes especiales (Sector Salud o Educación).\n"
        "   - Jubilado o pensionado *(aplica exoneración total de FECI por Ley 6 de 1987)*.\n"
        "   - Profesional independiente.\n"
        "4. **Plazo deseado:** Habitualmente hasta 84 meses (7 años) para autos nuevos, o hasta 60 meses en perfiles de jubilados.\n\n"
        "---\n\n"
        "💡 *Puede respondernos indicando sus datos (ejemplo: **\"Auto de B/. 18,500 con 10% de abono a 7 años, trabajo en educación\"**) o presionar una de las siguientes opciones para ver una simulación inmediata:*"
    )
    
    acciones = [
        cl.Action(name="preset_sedan", payload={"value": "Deseo simular un auto de B/. 18,500 con 10% de abono a 84 meses para asalariado"}, label="🚗 Auto B/. 18,500 (Asalariado)"),
        cl.Action(name="preset_educador", payload={"value": "Deseo simular un auto de B/. 16,000 con 15% de abono a 84 meses para sector salud o educación"}, label="🏥 Auto B/. 16,000 (Salud/Educador)"),
        cl.Action(name="preset_jubilado", payload={"value": "Deseo simular un auto de B/. 22,000 con 15% de abono a 60 meses para jubilado Ley 6"}, label="👴 Auto B/. 22,000 (Jubilado Ley 6)")
    ]
    return contenido, acciones


def es_intencion_simulacion(texto: str) -> bool:
    """Detecta si el mensaje contiene intención de simulación de cuota o letra."""
    t = texto.lower()
    palabras = [
        "simular", "simulacion", "simulación", "simule",
        "calcular cuota", "calcular letra", "calcula",
        "cuanto pagaria", "cuánto pagaría", "cuanto seria la letra", "cuánto sería la letra",
        "cuota para", "letra para", "cuota de", "letra de"
    ]
    tiene_palabra_sim = any(k in t for k in palabras)
    tiene_cifras = bool(re.search(r'(?:b/\.|\$)?\s*(\d{1,3}(?:[,\.]\d{3})*(?:\.\d{2})?|\d{4,6})', t))
    return tiene_palabra_sim or (("letra" in t or "cuota" in t) and tiene_cifras)


def extraer_parametros_consulta(texto: str) -> dict:
    """Extrae determinísticamente los parámetros de la consulta del usuario."""
    t = texto.lower()
    
    # 1. Precio (soporta 18500, 18,500, 18.500, 18k, con o sin símbolos)
    match_k = re.search(r'\b(\d{1,2})\s*k\b', t)
    match_precio = re.search(r'\b(\d{4,6}(?:\.\d{2})?|\d{1,3}(?:[,\.]\d{3})+(?:\.\d{2})?)\b', t)
    
    precio = 18500.0
    if match_k:
        precio = float(match_k.group(1)) * 1000.0
    elif match_precio:
        val_str = match_precio.group(1).replace(",", "")
        try:
            precio = float(val_str)
        except ValueError:
            precio = 18500.0

    # 2. Perfil
    es_jubilado = any(k in t for k in ["jubilad", "pensionad", "ley 6", "tercera edad"])
    es_salud_educacion = any(k in t for k in ["educa", "maestr", "profesor", "salud", "medic", "médic", "enfermer"])
    
    # 3. Abono (%)
    if "fast track" in t:
        pct_abono = 30.0
    else:
        match_pct = re.search(r'(\d{1,2})\s*%', t)
        if match_pct:
            try:
                pct_abono = float(match_pct.group(1))
            except ValueError:
                pct_abono = 15.0 if precio < 10000.0 else 10.0
        else:
            pct_abono = 15.0 if precio < 10000.0 else 10.0

    # Garantizar abono mínimo según política de CDA
    if precio < 10000.0 and pct_abono < 15.0:
        pct_abono = 15.0
    elif pct_abono < 10.0:
        pct_abono = 10.0

    # 4. Plazo (meses)
    match_plazo = re.search(r'(\d{1,2})\s*(?:meses|mes)', t)
    match_anios = re.search(r'(\d)\s*(?:años|año|anios|anio)', t)
    
    if match_plazo:
        plazo_meses = int(match_plazo.group(1))
    elif match_anios:
        plazo_meses = int(match_anios.group(1)) * 12
    else:
        plazo_meses = 60 if es_jubilado else 84
        
    if es_jubilado and plazo_meses > 60:
        plazo_meses = 60
    elif plazo_meses > 84:
        plazo_meses = 84

    return {
        "precio": precio,
        "pct_abono": pct_abono,
        "plazo_meses": plazo_meses,
        "es_jubilado": es_jubilado,
        "es_salud_educacion": es_salud_educacion
    }


@cl.on_chat_start
async def on_chat_start():
    """Inicializa la sesión de chat y crea el registro base en SQLite."""
    session_id = cl.user_session.get("id") or str(random.randint(100000, 999999))
    cl.user_session.set("session_id", session_id)
    cl.user_session.set("messages", [])
    cl.user_session.set("client_data", None)
    
    # Inicializar sesión en la base de datos SQLite
    db_guardar_chat_json(session_id, [])
    
    await cl.Message(
        content=(
            "### 🚗 ¡Bienvenido a la Feria de Autos con **Caja de Ahorros**!\n"
            "*El Banco de la Familia Panameña 🇵🇦*\n\n"
            "👋 **Paso previo obligatorio:** Por favor complete el formulario en pantalla con su **Nombre Completo, Cédula de Identidad, Celular y Correo** para habilitar la atención del **Asesor Virtual** y asignarle su Pase Digital de feria.\n\n"
            "*Una vez enviado el formulario, el asistente activará inmediatamente todas las opciones de consulta y simulación.*"
        )
    ).send()


@cl.action_callback("salud_educadores")
@cl.action_callback("marcas_chinas")
@cl.action_callback("fast_track")
@cl.action_callback("jubilados")
@cl.action_callback("solicitar_letra")
@cl.action_callback("simular")
@cl.action_callback("preset_sedan")
@cl.action_callback("preset_educador")
@cl.action_callback("preset_jubilado")
async def handle_quick_action(action: cl.Action):
    """Maneja los clics en los botones de acción rápida."""
    query = action.payload.get("value", "")
    await process_user_query(query)


@cl.on_message
async def on_message(message: cl.Message):
    """Maneja los mensajes ingresados por el usuario."""
    await process_user_query(message.content)


async def process_user_query(user_query: str):
    """Procesa la consulta del usuario persistiendo clientes y chat JSON en SQLite."""
    session_id = cl.user_session.get("session_id") or cl.user_session.get("id") or "default-session"
    messages = cl.user_session.get("messages", [])
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
        
        # Guardar cliente en SQLite en el subfolder dedicado database/
        db_guardar_cliente(
            session_id=session_id,
            nombre=client_data["nombre"],
            cedula=client_data["cedula"],
            celular=client_data["celular"],
            correo=client_data["correo"]
        )
        guardar_lead_registro(client_data)
        
        bienvenida = (
            f"### ¡Mucho gusto y bienvenido/a, **{client_data['nombre']}**! 🚗🇵🇦\n"
            f"*Caja de Ahorros — El Banco de la Familia Panameña*\n\n"
            f"Hemos registrado exitosamente sus datos de contacto para su cotización:\n"
            f"• **Titular:** {client_data['nombre']}\n"
            f"• **Cédula de Identidad:** `{client_data['cedula']}`\n"
            f"• **Celular:** `{client_data['celular']}`\n"
            f"• **Correo:** `{client_data['correo']}`\n\n"
            f"---\n"
            f"Soy su **Asesor Virtual de Auto**. Puedo orientarle en:\n"
            f"• **Requisitos documentales** según su perfil (Salud, Educación, Empresa Privada, Jubilados o Independientes).\n"
            f"• **Abonos mínimos, plazos y marcas autorizadas** (incluyendo BYD, Geely, Changan y modelos ecológicos).\n"
            f"• **Beneficios por Ley 6** para jubilados (exoneración total de FECI).\n"
            f"• **Simulación de su letra mensual** y emisión de su **Pase Digital prioritario**.\n\n"
            f"Seleccione una de las siguientes opciones o escriba su consulta con total libertad:"
        )
        
        actions = [
            cl.Action(name="solicitar_letra", payload={"value": "Quiero saber cuál sería mi letra, qué necesitas saber de mí?"}, label="🧮 ¿Cuál sería mi letra?"),
            cl.Action(name="salud_educadores", payload={"value": "¿Cuáles son los requisitos y el tiempo de permanencia si soy educador o trabajo en el sector salud?"}, label="🏥 Salud y Educadores"),
            cl.Action(name="marcas_chinas", payload={"value": "¿Puedo financiar un vehículo de marcas de origen chino como BYD, Geely o Changan con Caja de Ahorros?"}, label="🇨🇳 Marcas Chinas (BYD, Geely)"),
            cl.Action(name="fast_track", payload={"value": "¿Cuánto es el porcentaje de abono mínimo y cómo funciona la modalidad Fast Track de feria?"}, label="⚡ Abonos y Fast Track"),
            cl.Action(name="jubilados", payload={"value": "¿Qué beneficios aplican para jubilados y tercera edad según la Ley 6 de 1987?"}, label="👴 Jubilados (Ley 6)"),
        ]
        
        messages.append({"role": "assistant", "content": bienvenida})
        cl.user_session.set("messages", messages)
        db_guardar_chat_json(session_id, messages)
        
        await cl.Message(content=bienvenida, actions=actions).send()
        return

    # 1. CASO DETERMINÍSTICO A: El usuario pregunta qué se necesita para saber su letra
    if es_pregunta_solicitud_datos_letra(user_query):
        contenido, acciones = obtener_mensaje_solicitud_datos()
        messages.append({"role": "assistant", "content": contenido})
        cl.user_session.set("messages", messages)
        db_guardar_chat_json(session_id, messages)
        
        await cl.Message(content=contenido, actions=acciones).send()
        return

    # 2. CASO DETERMINÍSTICO B: Cálculo de simulación de cuota / letra
    if es_intencion_simulacion(user_query):
        params = extraer_parametros_consulta(user_query)
        client_data = cl.user_session.get("client_data")
        sim_data = calculate_loan_summary(
            precio=params["precio"],
            pct_abono=params["pct_abono"],
            plazo_meses=params["plazo_meses"],
            tasa_anual=6.75,
            es_jubilado=params["es_jubilado"],
            es_salud_educacion=params["es_salud_educacion"]
        )
        response_text = format_loan_markdown(sim_data, client_data)
        
        messages.append({"role": "assistant", "content": response_text})
        cl.user_session.set("messages", messages)
        
        # Persistir en SQLite con datos de la cotización y pase digital
        db_guardar_chat_json(
            session_id=session_id,
            messages=messages,
            pase_digital=sim_data["codigo_pase"],
            precio=sim_data["precio"],
            cuota=sim_data["cuota_total"]
        )
        
        await cl.Message(content=response_text).send()
        return

    # 3. Consulta de orientación con Gemini Streaming o Fallback local
    api_key = os.getenv("GEMINI_API_KEY", "")
    streamed_anything = False
    
    # Crear mensaje vacío para streaming progresivo
    reply_msg = cl.Message(content="")
    
    if api_key:
        async with cl.Step(name="Orientación Inteligente Caja de Ahorros", type="tool") as step:
            step.output = "Consultando lineamientos de financiamiento de feria..."
            
        try:
            # Ejecutar el generador SSE síncrono en un hilo asíncrono
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

    # 4. Fallback determinista local en caso de no haber API o fallo de conexión
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
    
    # Persistir en SQLite
    db_guardar_chat_json(session_id, messages)
