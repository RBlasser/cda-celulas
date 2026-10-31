# Prototipo PoC Standalone HTTP - Asistente de Formalización de Préstamos Personales 🇵🇦

Prototipo funcional en **Python (FastAPI)** que sirve como prueba de concepto (PoC) para validar la interacción, flujos de negocio y experiencia del analista antes de la compilación final en **Rust** (`axum` + `rust-embed`).

---

## 🌟 Características del Prototipo

1. **Interfaz Única (Single-Pane Workspace):**
   * **Panel Superior / Carga:** Arrastre de documentos escaneados (cédula, talonario de pago, carta laboral, proforma/APC).
   * **Panel Auditoría:** Despliegue del Semáforo Normativo (`VERDE`, `AMARILLO`, `ROJO`) y lista detallada de inconsistencias normativas.
   * **Panel Smart Clipboard:** Despliegue de tarjetas de datos estructurados con botones de copiado en 1 clic para traslado a Ultimus BPM en pantalla dividida (`Win + Flechas`).
   * **Panel Ensamblador Legal:** Generación inmediata y descarga de la Carta de Promesa de Pago en formato `.docx` para casos de compra de saldo.

2. **Capa Multi-Proveedor de IA:**
   * Dropdown en cabecera para alternar dinámicamente entre:
     * `Google Gemini (Gemini 1.5 Flash)`
     * `Anthropic (Claude 3.5 Sonnet)`
     * `OpenAI (GPT-4o)`
   * Entrada segura de API Key por el analista en tiempo de ejecución.

3. **Principios de Ingeniería (Fail-Fast y Cero Mockdata):**
   * **Cero sobreingeniería:** Flujo directo sin dependencias superfluas.
   * **Cero fallback silencioso:** Si la API Key es errónea o la llamada a la IA falla, la interfaz despliega el error real devuelto por el proveedor.
   * **Cero datos simulados:** Toda respuesta proviene del procesamiento real de los documentos subidos.

---

## 🚀 Instrucciones de Ejecución

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Iniciar el servidor local:**
   ```bash
   python -m uvicorn app:app --host 127.0.0.1 --port 8080 --reload
   ```
   O simplemente ejecutando:
   ```cmd
   run.bat
   ```

3. **Abrir en el navegador:**
   Navega a [http://127.0.0.1:8080](http://127.0.0.1:8080).
