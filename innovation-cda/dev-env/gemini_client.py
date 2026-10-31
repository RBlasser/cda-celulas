"""
Cliente REST ligero para Google Gemini API sin dependencias externas pesadas.
Permite consultar modelos Gemini (por defecto gemini-2.0-flash o gemini-1.5-flash)
con soporte de fallback inteligente si no se dispone de conexión o clave API.
"""

import os
import requests
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from knowledge_base import SYSTEM_PROMPT, KNOWLEDGE_CONTEXT

# Cargar automáticamente variables de entorno desde .env si existe
load_dotenv()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
FALLBACK_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent"


def query_gemini_api(messages: List[Dict[str, str]], api_key: str = None) -> Tuple[bool, str]:
    """
    Envía el historial de mensajes a la API de Gemini usando requests.
    Retorna (éxito, respuesta_o_error).
    """
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key:
        return False, "No se ha configurado una clave de API (GEMINI_API_KEY)."

    # Preparar el contenido para Gemini API
    # Inyectamos el SYSTEM_PROMPT y el KNOWLEDGE_CONTEXT en la instrucción de sistema
    payload = {
        "system_instruction": {
            "parts": [
                {"text": f"{SYSTEM_PROMPT}\n\nCONTEXTO INSTITUCIONAL:\n{KNOWLEDGE_CONTEXT}"}
            ]
        },
        "contents": [],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }

    # Convertir historial de mensajes
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        payload["contents"].append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Intentar con gemini-2.0-flash y luego gemini-1.5-flash si falla
    for url in [GEMINI_API_URL, FALLBACK_API_URL]:
        try:
            resp = requests.post(
                f"{url}?key={key}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=25
            )
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return True, parts[0].get("text", "")
            elif resp.status_code == 400:
                error_data = resp.json()
                return False, f"Error en la consulta: {error_data.get('error', {}).get('message', 'Parámetros inválidos')}"
        except Exception as e:
            continue

    return False, "No fue posible conectar con el servicio de IA en este momento."


def stream_gemini_api(messages: List[Dict[str, str]], api_key: str = None):
    """
    Generador que emite fragmentos de texto en tiempo real desde la API de Gemini (SSE).
    """
    import json
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key:
        return

    stream_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:streamGenerateContent?alt=sse"

    payload = {
        "system_instruction": {
            "parts": [
                {"text": f"{SYSTEM_PROMPT}\n\nCONTEXTO INSTITUCIONAL:\n{KNOWLEDGE_CONTEXT}"}
            ]
        },
        "contents": [],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048,
            "thinkingConfig": {
                "thinkingBudget": 0
            }
        }
    }

    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        payload["contents"].append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    try:
        resp = requests.post(
            f"{stream_url}&key={key}",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=25
        )
        if resp.status_code == 200:
            for line in resp.iter_lines():
                if line:
                    decoded = line.decode("utf-8")
                    if decoded.startswith("data: "):
                        data = json.loads(decoded[6:])
                        candidates = data.get("candidates", [])
                        if candidates:
                            part = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                            if part:
                                yield part
    except Exception:
        pass



def get_smart_local_response(user_query: str) -> str:
    """
    Motor local de respuestas orientativas basado en los lineamientos de Caja de Ahorros.
    Se activa inmediatamente cuando no hay clave API configurada, asegurando
    que el prototipo sea 100% interactivo y funcional en ferias o demos.
    """
    q = user_query.lower()

    if any(k in q for k in ["letra", "cuota", "cuanto pagaria", "cuánto pagaría", "calcular", "simular", "simulacion", "simulación", "feci", "costarme"]):
        return (
            "Estimado cliente, con mucho gusto le orientamos. 🚗 ![Panamá](/public/flag_pa.svg)\n\n"
            "En **Caja de Ahorros**, las cuotas mensuales exactas y corridas financieras formales son estructuradas "
            "directamente por un **oficial de crédito** en nuestro stand de feria o en cualquiera de nuestras sucursales, "
            "utilizando la cotización formal de la agencia concesionaria y las tasas preferenciales del evento.\n\n"
            "Respecto a los lineamientos generales de nuestra política de financiamiento:\n"
            "• **Plazos máximos:** Hasta 84 meses (7 años) y hasta 96 meses en autos nuevos para colaboradores asalariados e independientes (hasta 60 meses para jubilados).\n"
            "• **Abonos iniciales:** Desde el 10% en condiciones regulares de feria, o 30% en la modalidad ágil *Fast Track*.\n"
            "• **Beneficios de Ley:** Clientes jubilados y de tercera edad (Ley 6 de 1987) cuentan con **100% de exoneración del impuesto FECI** y 50% de descuento en gastos de cierre.\n\n"
            "Le invitamos a realizar una rápida asesoría de 4 pasos para perfilar su solicitud y emitirle su Pase Digital prioritario para ser atendido en stand."
        )

    if any(k in q for k in ["educador", "maestro", "profesor", "salud", "médico", "medico", "enfermera", "leyes especiales"]):
        return (
            "Estimado cliente, es un placer saludarle.\n\n"
            "Para los servidores públicos del **Sector Salud y Educación (amparados por Leyes Especiales)**, "
            "Caja de Ahorros contempla condiciones preferenciales:\n\n"
            "• **Tiempo de servicio requerido:** Únicamente se solicita **un (1) mes de permanencia** o encontrarse en periodo probatorio (PPX1/PPX2).\n"
            "• **Documentos necesarios:**\n"
            "  - Proforma de certificado de trabajo emitida por Contraloría General o carta de Recursos Humanos.\n"
            "  - Último talonario o comprobante de pago.\n"
            "  - Cédula de identidad vigente.\n"
            "  - Proforma o cotización oficial del vehículo emitida por la agencia concesionaria.\n\n"
            "Le invitamos cordialmente a acercarse a nuestro stand de feria para que un oficial de crédito formalice su cotización.\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif any(k in q for k in ["china", "byd", "geely", "changan", "gac", "jac", "riddara", "jetour", "marca"]):
        return (
            "Estimado cliente, con mucho gusto le orientamos.\n\n"
            "En Caja de Ahorros financiamos una amplia gama de vehículos nuevos para uso particular. "
            "Respecto a **marcas de origen chino**, mantenemos convenios con aquellas que cuentan con el respaldo formal "
            "de agencias concesionarias de trayectoria reconocida en Panamá:\n\n"
            "• **BYD** (CTS del Istmo / Grupo FASA)\n"
            "• **Geely** (Bahía Motors)\n"
            "• **Changan** (Distribuidora Automotriz Fortune)\n"
            "• **GAC** (Grupo Auto Comercial)\n"
            "• **JAC** (Distribuidora David)\n"
            "• **Riddara** (New Energy Motors)\n"
            "• **Jetour y Soueast** (Petromotors)\n\n"
            "Asimismo, financiamos todas las marcas tradicionales (Toyota, Hyundai, Kia, Nissan, Suzuki, Honda, etc.) y vehículos ecológicos (100% eléctricos e híbridos).\n\n"
            "Con la cotización oficial de la agencia, con mucho gusto le esperamos en nuestro stand.\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif any(k in q for k in ["jubilado", "pensionado", "tercera edad", "ley 6", "feci"]):
        return (
            "Estimado cliente, gracias por consultar con nosotros.\n\n"
            "Para nuestros clientes **Jubilados, Pensionados y de la Tercera Edad**, amparados bajo la **Ley 6 de 1987**, "
            "ofrecemos beneficios muy atractivos:\n\n"
            "• **Exoneración total del FECI (1%):** Su financiamiento no paga el impuesto de retención FECI.\n"
            "• **50% de descuento en la comisión de cierre:** Ahorro directo en los gastos iniciales de trámite.\n"
            "• **Requisitos simplificados:** Cédula de identidad vigente, último talonario de pago de jubilación y proforma del auto.\n"
            "• **Plazo:** Hasta 96 meses (para clientes hasta 63 años mujeres / 65 años hombres) o hasta 60 meses en edades mayores.\n\n"
            "Será un honor atenderle en nuestro stand de la feria para calcular su cuota con estos beneficios aplicados.\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif "fast track" in q:
        return (
            "Estimado cliente, con mucho gusto le explicamos los abonos y el funcionamiento de la modalidad Fast Track:\n\n"
            "**1. Abonos Mínimos Generales de Feria:**\n"
            "• **Clientes regulares de feria:** Abonos desde el **10%** del valor del vehículo.\n"
            "• **Autos con precio menor a B/. 10,000.00:** Se requiere un abono mínimo del **15%**.\n"
            "• **Sector Agropecuario (independientes):** Abono mínimo del **25%**.\n\n"
            "**2. ¿Cómo funciona la Modalidad Fast Track de Feria?**\n"
            "Es un carril preferencial de atención diseñado para brindarle una respuesta y preaprobación ágil en el propio stand de Caja de Ahorros:\n"
            "• **Abono inicial:** Requiere un abono inicial mínimo del **30%** del valor de compra del auto.\n"
            "• **Perfil elegible:** Aplica exclusivamente para colaboradores **asalariados permanentes** (no aplica para colaboradores eventuales ni trabajadores independientes).\n"
            "• **Ingreso mensual de referencia:** Contar con un ingreso mensual a partir de **USD $1,500.00**.\n"
            "• **Trámite expedito:** Se procesa con **documentación simplificada de feria** (cédula vigente, constancia laboral reciente y cotización de la agencia) para darle respuesta en tiempo récord.\n\n"
            "Un abono del 30% además le garantiza una cuota mensual sustancialmente más baja. ¡Le esperamos con gusto en nuestro stand para evaluar de inmediato su solicitud!\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif any(k in q for k in ["abono", "cuanto de abono", "mínimo", "porcentaje", "down payment"]):
        return (
            "Estimado cliente, con gusto le detallamos los abonos establecidos por Caja de Ahorros:\n\n"
            "• **Clientes regulares de feria:** Abonos desde el **10%** del valor del auto.\n"
            "• **Autos con precio menor a B/. 10,000.00:** Se requiere un abono mínimo del **15%**.\n"
            "• **Sector Agropecuario (independientes):** Abono mínimo del **25%**.\n"
            "• **Modalidad Fast Track de Feria:** Con un abono inicial del **30%**, los colaboradores asalariados permanentes con ingreso desde B/. 1,500.00 acceden a un proceso de preaprobación ágil con documentación simplificada de feria.\n\n"
            "Un mayor abono le permitirá contar con una cuota mensual más baja. ¡Le esperamos en nuestro stand para evaluar las mejores opciones para su presupuesto!\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif any(k in q for k in ["plazo", "meses", "años", "tiempo"]):
        return (
            "Estimado cliente, en Caja de Ahorros disponemos de plazos muy cómodos para su financiamiento:\n\n"
            "• **Hasta 96 meses (8 años):** Disponible para clientes asalariados, independientes, jubilados y pensionados.\n"
            "• **Hasta 60 meses (5 años):** Para clientes mayores a 63 años (damas) o 65 años (caballeros).\n\n"
            "Puede financiar tanto vehículos de combustión tradicional como modelos ecológicos (híbridos y eléctricos).\n\n"
            "Con gusto podemos simular su plazo preferido en la pestaña de 'Simulador' o en nuestro stand de feria.\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif any(k in q for k in ["empresa privada", "privada", "asalariado"]):
        return (
            "Estimado cliente, para colaboradores de la **Empresa Privada**, los recaudos establecidos son:\n\n"
            "• Cédula de identidad personal vigente.\n"
            "• **Carta de trabajo original** (con vigencia no mayor a 45 días), que detalle su salario y deducciones.\n"
            "• **Última ficha digital** de la Caja de Seguro Social (CSS).\n"
            "• **Último talonario o comprobante de pago** salarial.\n"
            "• Cotización o proforma oficial emitida por la agencia concesionaria.\n\n"
            "Con estos sencillos recaudos, nuestro equipo en el stand podrá procesar su precalificación inmediata.\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif any(k in q for k in ["independiente", "profesional", "cpa", "abogado", "arquitecto"]):
        return (
            "Estimado cliente, para **Profesionales Independientes**, los lineamientos de evaluación solicitan:\n\n"
            "• Cédula de identidad personal vigente.\n"
            "• **Carta de ingresos emitida por un Contador Público Autorizado (CPA)** correspondiente a los dos últimos periodos fiscales.\n"
            "• **Movimientos bancarios de los últimos 12 meses** (o copia de sus dos últimas declaraciones de renta presentadas ante la DGI).\n"
            "• Cotización oficial de la agencia de autos.\n\n"
            "Le invitamos a presentar sus documentos en nuestro stand para brindarle una asesoría personalizada a la medida de su negocio.\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    elif any(k in q for k in ["apc", "atraso", "mancha", "historial", "crédito malo", "buro", "score"]):
        return (
            "Estimado cliente, comprendemos perfectamente su consulta.\n\n"
            "En Caja de Ahorros realizamos una **evaluación crediticia integral y personalizada** de cada cliente, "
            "tomando en cuenta su estabilidad laboral, capacidad actual de pago y el respaldo de la garantía.\n\n"
            "Le animamos cordialmente a presentar sus documentos en nuestro stand de la feria. Nuestros ejecutivos de crédito "
            "analizarán con total discreción y profesionalismo las opciones disponibles para brindarle la mejor alternativa posible.\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )

    else:
        return (
            "Estimado cliente, gracias por comunicarse con el Asesor Virtual de Caja de Ahorros para la Feria de Autos.\n\n"
            "Con mucho gusto puedo orientarle sobre:\n"
            "• **Requisitos documentales** según su perfil (Empresa Privada, Sector Salud/Educación, Jubilados o Independientes).\n"
            "• **Condiciones de financiamiento:** Abono mínimo (desde 10%, o 15% para autos menores a B/. 10,000.00), plazos de hasta 96 meses.\n"
            "• **Marcas autorizadas:** Modelos tradicionales, ecológicos (eléctricos/híbridos) y marcas chinas con respaldo local.\n"
            "• **Beneficios por Ley 6:** Exoneración de FECI y 50% de descuento en gastos de cierre para jubilados.\n\n"
            "¿En qué aspecto específico de su financiamiento le gustaría que le orientemos hoy?\n\n"
            "*Orientación preliminar sujeta a la evaluación crediticia formal del banco.*"
        )
