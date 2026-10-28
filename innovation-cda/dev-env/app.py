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

# Cargar variables de entorno (.env)
load_dotenv()


def calculate_loan_summary(precio: float, pct_abono: float = 15.0, plazo_meses: int = 84, tasa_anual: float = 6.75, es_jubilado: bool = False):
    """Calcula cuota referencial, desglose y pase digital."""
    monto_abono = precio * (pct_abono / 100.0)
    monto_financiar = precio - monto_abono
    tasa_mensual = (tasa_anual / 100.0) / 12.0
    
    # Amortización francesa
    if tasa_mensual > 0:
        cuota_cap_int = monto_financiar * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)
    else:
        cuota_cap_int = monto_financiar / plazo_meses
        
    # FECI (1% anual si aplica regular, 0% si jubilado Ley 6)
    if es_jubilado or monto_financiar <= 5000.0:
        cuota_feci = 0.0
    else:
        cuota_feci = (monto_financiar * 0.01) / 12.0
        
    seguro_estimado = 38.00
    cuota_total = cuota_cap_int + cuota_feci + seguro_estimado
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
        "es_jubilado": es_jubilado
    }


def format_loan_markdown(data: dict) -> str:
    """Formatea la simulación y el pase digital en un mensaje markdown profesional."""
    feci_str = "B/. 0.00 *(Exonerado por Ley 6 de 1987)*" if data["es_jubilado"] else f"B/. {data['cuota_feci']:,.2f}/mes"
    
    md = (
        f"### 🧮 Simulación Estimada de Financiamiento\n\n"
        f"• **Precio de Venta del Auto:** B/. {data['precio']:,.2f}\n"
        f"• **Abono Inicial ({data['pct_abono']:.0f}%):** B/. {data['monto_abono']:,.2f}\n"
        f"• **Monto a Financiar:** B/. {data['monto_financiar']:,.2f}\n"
        f"• **Plazo:** {data['plazo_meses']} meses ({data['plazo_meses']//12} años)\n\n"
        f"---\n"
        f"### 💳 **Cuota Mensual Total Aproximada:** **B/. {data['cuota_total']:,.2f}**\n\n"
        f"**Desglose mensual de la cuota:**\n"
        f"• Capital e Intereses: B/. {data['cuota_cap_int']:,.2f}/mes\n"
        f"• Impuesto FECI: {feci_str}\n"
        f"• Seguro de Auto Estimado: B/. {data['seguro_estimado']:,.2f}/mes\n\n"
        f"---\n"
        f"### 🎫 Pase Digital de Atención en Stand\n"
        f"**Código de Turno:** `{data['codigo_pase']}`\n\n"
        f"Presente este código o menciónelo al oficial de crédito en nuestro stand de **Caja de Ahorros** en la feria para agilizar su cotización y precalificación formal.\n\n"
        f"*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
    )
    return md


@cl.on_chat_start
async def on_chat_start():
    """Inicializa la sesión de chat y envía el mensaje de bienvenida con atajos interactivos."""
    cl.user_session.set("messages", [])
    
    actions = [
        cl.Action(name="salud_educadores", payload={"value": "¿Cuáles son los requisitos y el tiempo de permanencia si soy educador o trabajo en el sector salud?"}, label="🏥 Salud y Educadores"),
        cl.Action(name="marcas_chinas", payload={"value": "¿Puedo financiar un vehículo de marcas de origen chino como BYD, Geely o Changan con Caja de Ahorros?"}, label="🇨🇳 Marcas Chinas (BYD, Geely)"),
        cl.Action(name="fast_track", payload={"value": "¿Cuánto es el porcentaje de abono mínimo y cómo funciona la modalidad Fast Track de feria?"}, label="⚡ Abonos y Fast Track"),
        cl.Action(name="jubilados", payload={"value": "¿Qué beneficios aplican para jubilados y tercera edad según la Ley 6 de 1987?"}, label="👴 Jubilados (Ley 6)"),
        cl.Action(name="simular", payload={"value": "Deseo simular la cuota mensual para un auto de B/. 18,500"}, label="🧮 Simular Cuota de Auto"),
    ]
    
    await cl.Message(
        content=(
            "¡Bienvenido a la Feria de Autos con **Caja de Ahorros**! 🚗🇵🇦\n\n"
            "Soy su **Asesor Virtual de Auto**. Es un placer saludarle y orientarle en la elección de su próximo financiamiento.\n\n"
            "Puedo brindarle información sobre:\n"
            "• **Requisitos documentales** según su perfil laboral (Salud, Educación, Empresa Privada, Jubilados o Independientes).\n"
            "• **Abonos mínimos, plazos y marcas autorizadas** (incluyendo modelos ecológicos y marcas chinas con respaldo).\n"
            "• **Beneficios por Ley 6** para jubilados y pensionados.\n"
            "• **Simulaciones de cuotas** mensuales para su presupuesto.\n\n"
            "Seleccione una de las siguientes opciones frecuentes o escriba su consulta con total libertad:"
        ),
        actions=actions
    ).send()


@cl.action_callback("salud_educadores")
@cl.action_callback("marcas_chinas")
@cl.action_callback("fast_track")
@cl.action_callback("jubilados")
@cl.action_callback("simular")
async def handle_quick_action(action: cl.Action):
    """Maneja los clics en los botones de acción rápida."""
    query = action.payload.get("value", "")
    await process_user_query(query)


@cl.on_message
async def on_message(message: cl.Message):
    """Maneja los mensajes ingresados por el usuario."""
    await process_user_query(message.content)


async def process_user_query(user_query: str):
    """Procesa la consulta del usuario, manejando simulación o consulta a Gemini en streaming."""
    messages = cl.user_session.get("messages", [])
    messages.append({"role": "user", "content": user_query})
    
    # 1. Detección de consulta de simulación numérica
    q_lower = user_query.lower()
    match_precio = re.search(r'(?:precio|auto|cuesta|valor|de|por)\s*(?:b/\.|\$)?\s*(\d{1,3}(?:[,\.]\d{3})*(?:\.\d{2})?|\d{4,6})', q_lower)
    es_simulacion = any(k in q_lower for k in ["simular", "calcular cuota", "cuanto pagaria", "cuánto pagaría", "cuota para", "simulacion", "simulación"])
    
    if es_simulacion or ("simular" in q_lower and "auto" in q_lower):
        precio = 18500.0
        if match_precio:
            val_str = match_precio.group(1).replace(",", "")
            try:
                precio = float(val_str)
            except ValueError:
                precio = 18500.0
                
        pct_abono = 30.0 if "fast track" in q_lower else (15.0 if precio < 10000.0 else 10.0)
        es_jubilado = any(k in q_lower for k in ["jubilado", "pensionado", "ley 6", "tercera edad"])
        plazo = 60 if es_jubilado else 84
        
        sim_data = calculate_loan_summary(precio, pct_abono, plazo, tasa_anual=6.75, es_jubilado=es_jubilado)
        response_text = format_loan_markdown(sim_data)
        
        messages.append({"role": "assistant", "content": response_text})
        cl.user_session.set("messages", messages)
        
        await cl.Message(content=response_text).send()
        return

    # 2. Consulta de orientación con Gemini Streaming o Fallback
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

    # 3. Fallback determinista local en caso de no haber API o fallo de conexión
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
