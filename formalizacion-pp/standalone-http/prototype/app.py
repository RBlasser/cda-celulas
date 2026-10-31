"""
Prototipo PoC Standalone HTTP - Asistente de Formalización de Préstamos Personales
Caja de Ahorros de Panamá

Implementación en FastAPI que modela el comportamiento del binario final en Rust:
- Cero sobreingeniería.
- Cero funciones fallback silenciosas (fail-fast directo).
- Cero mockdata (procesamiento contra APIs reales de IA).
- Tres casos de uso: Auditoría (Semáforo), Smart Clipboard y Ensamblador Legal (.docx).
"""

import os
import io
import json
import uuid
import shutil
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import requests
from docx import Document

app = FastAPI(title="CDA - Asistente Formalizacion PP (PoC Standalone)")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMP_DIR = BASE_DIR / "temp_storage"
TEMP_DIR.mkdir(exist_ok=True)

# Estado de sesión en memoria volátil (emula sesión de un solo analista en localhost)
current_session = {
    "provider": "google",
    "api_key": os.getenv("GEMINI_API_KEY", ""),
    "extracted_data": {},
    "audit_result": {},
    "session_id": str(uuid.uuid4())
}

SYSTEM_AUDIT_PROMPT = """Eres el Copiloto Asistencial de Formalización de Préstamos Personales de Caja de Ahorros de Panamá.
Analiza los documentos suministrados del expediente de crédito y devuelve EXCLUSIVAMENTE un objeto JSON válido (sin markdown adicional, sin ```json) con la siguiente estructura exacta:

{
  "semaforo": "VERDE" | "AMARILLO" | "ROJO",
  "hallazgos": [
    "Descripción concisa de hallazgos normativos, faltantes o alertas"
  ],
  "datos_extraidos": {
    "nombre_cliente": "Nombre completo identificado",
    "cedula": "Cédula de identidad (ej: 8-888-888)",
    "patrono": "Institución pública o empresa privada",
    "posicion_planilla": "Número de posición de Contraloría/planilla (si aplica)",
    "salario_bruto": "Monto en B/. o USD",
    "salario_neto": "Monto neto en B/. o USD",
    "monto_prestamo": "Monto aprobado",
    "plazo_meses": "Plazo en meses",
    "banco_acreedor": "Nombre del banco a comprar saldo (si aplica)",
    "saldo_compra": "Monto del saldo a cancelar a tercero (si aplica)",
    "cuenta_acreedor": "Número de préstamo/cuenta externa (si aplica)"
  }
}

Reglas normativas estrictas:
- SEMÁFORO ROJO si faltan documentos obligatorios o si hay discrepancia de identidad. Si el cliente es jubilado y no está el certificado físico de la CSS, es ROJO inmediato.
- SEMÁFORO AMARILLO si algún talonario o carta laboral tiene más de 60 días de emisión pero es subsanable.
- SEMÁFORO VERDE si el expediente está completo, vigente y consistente.
"""


def call_llm(provider: str, api_key: str, file_contents: List[dict]) -> dict:
    """
    Llama directamente al proveedor seleccionado.
    FAIL-FAST: Si la API Key está vacía, no es válida o la llamada falla,
    lanza excepción HTTP inmediata. Cero fallbacks, cero mockdata.
    """
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail=f"API Key para el proveedor '{provider}' no ha sido configurada."
        )

    provider = provider.lower()

    if provider == "google" or provider == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        parts = [{"text": SYSTEM_AUDIT_PROMPT}]
        for f in file_contents:
            parts.append({
                "inline_data": {
                    "mime_type": f["mime_type"],
                    "data": f["base64"]
                }
            })
        parts.append({"text": "Procesa y audita los documentos adjuntos. Devuelve estrictamente el JSON."})
        
        resp = requests.post(url, json={"contents": [{"parts": parts}]}, timeout=45)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Error en Google Gemini API ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        try:
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            return json.loads(raw_text.strip())
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error parseando respuesta JSON de Gemini: {str(e)}. Respuesta cruda: {raw_text}"
            )

    elif provider == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        content_blocks = []
        for f in file_contents:
            if f["mime_type"] == "application/pdf":
                content_blocks.append({
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": f["base64"]
                    }
                })
        content_blocks.append({"type": "text", "text": "Audita y extrae los datos de estos documentos. Devuelve solo el JSON."})
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2500,
            "system": SYSTEM_AUDIT_PROMPT,
            "messages": [{"role": "user", "content": content_blocks}]
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Error en Anthropic API ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        raw_text = data["content"][0]["text"].strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())

    elif provider == "openai":
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Para OpenAI se procesa texto o imágenes
        messages = [
            {"role": "system", "content": SYSTEM_AUDIT_PROMPT},
            {"role": "user", "content": "Audita el expediente adjunto. Devuelve estrictamente el JSON requerido."}
        ]
        payload = {
            "model": "gpt-4o",
            "messages": messages,
            "response_format": {"type": "json_object"}
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Error en OpenAI API ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        return json.loads(data["choices"][0]["message"]["content"])

    else:
        raise HTTPException(status_code=400, detail=f"Proveedor desconocido: '{provider}'.")


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Interfaz no encontrada.")
    return index_file.read_text(encoding="utf-8")


@app.post("/api/config")
async def update_config(provider: str = Form(...), api_key: str = Form(...)):
    """Guarda credenciales en memoria para la sesión activa."""
    current_session["provider"] = provider.strip()
    current_session["api_key"] = api_key.strip()
    return {"status": "success", "provider": current_session["provider"]}


@app.post("/api/process")
async def process_expediente(files: List[UploadFile] = File(...)):
    """
    Recibe los PDFs, guarda temporalmente en disco y ejecuta la auditoría
    y extracción con el LLM seleccionado.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Debe adjuntar al menos un documento PDF.")

    session_folder = TEMP_DIR / current_session["session_id"]
    session_folder.mkdir(exist_ok=True)

    file_payloads = []
    import base64

    for file in files:
        if not file.filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")):
            continue
        dest_path = session_folder / file.filename
        content = await file.read()
        dest_path.write_bytes(content)

        mime = "application/pdf" if file.filename.lower().endswith(".pdf") else "image/jpeg"
        b64 = base64.b64encode(content).decode("utf-8")
        file_payloads.append({
            "name": file.filename,
            "mime_type": mime,
            "base64": b64
        })

    if not file_payloads:
        raise HTTPException(status_code=400, detail="No se encontraron archivos válidos (PDF/Imágenes).")

    # Llamada al LLM
    result = call_llm(
        provider=current_session["provider"],
        api_key=current_session["api_key"],
        file_contents=file_payloads
    )

    current_session["audit_result"] = result
    current_session["extracted_data"] = result.get("datos_extraidos", {})

    return result


@app.post("/api/assemble")
async def assemble_contract():
    """
    Caso de Uso 3: Inyecta los datos extraídos en una plantilla Word (.docx)
    para cartas de promesa / compra de saldo y entrega la descarga directa.
    """
    data = current_session.get("extracted_data")
    if not data:
        raise HTTPException(
            status_code=400,
            detail="No hay datos extraídos en la sesión para ensamblar el contrato."
        )

    doc = Document()
    doc.add_heading("CAJA DE AHORROS DE PANAMÁ", level=1)
    doc.add_heading("CARTA DE PROMESA DE PAGO Y COMPRA DE SALDO", level=2)

    doc.add_paragraph(f"Fecha de emisión: {Path.cwd()}")
    doc.add_paragraph(f"Cliente: {data.get('nombre_cliente', 'N/D')}")
    doc.add_paragraph(f"Cédula de Identidad: {data.get('cedula', 'N/D')}")
    doc.add_paragraph(f"Institución / Patrono: {data.get('patrono', 'N/D')}")
    doc.add_paragraph(f"Posición / Planilla: {data.get('posicion_planilla', 'N/D')}")

    doc.add_heading("Detalle de la Obligación a Cancelar", level=3)
    p_detalle = doc.add_paragraph()
    p_detalle.add_run(f"Entidad Acreedora: {data.get('banco_acreedor', 'N/D')}\n")
    p_detalle.add_run(f"Número de Cuenta / Préstamo: {data.get('cuenta_acreedor', 'N/D')}\n")
    p_detalle.add_run(f"Saldo a Cancelar: B/. {data.get('saldo_compra', 'N/D')}\n")
    p_detalle.add_run(f"Monto Nuevo Préstamo CDA: B/. {data.get('monto_prestamo', 'N/D')}\n")
    p_detalle.add_run(f"Plazo Aprobado: {data.get('plazo_meses', 'N/D')} meses\n")

    doc.add_paragraph(
        "Por medio de la presente, Caja de Ahorros se compromete a emitir cheque de gerencia "
        "a favor de la entidad acreedora una vez perfeccionado el descuento por planilla correspondiente."
    )

    doc.add_paragraph("\n_______________________________\nFirma Autorizada - Operaciones CDA")

    out_file = TEMP_DIR / f"promesa_pago_{data.get('cedula', 'cliente')}.docx"
    doc.save(str(out_file))

    return FileResponse(
        path=out_file,
        filename=f"promesa_pago_{data.get('cedula', 'cliente')}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.post("/api/reset")
async def reset_session():
    """Limpia los datos en memoria y elimina archivos temporales de disco."""
    session_id = current_session["session_id"]
    folder = TEMP_DIR / session_id
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)

    current_session["session_id"] = str(uuid.uuid4())
    current_session["extracted_data"] = {}
    current_session["audit_result"] = {}
    return {"status": "cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
