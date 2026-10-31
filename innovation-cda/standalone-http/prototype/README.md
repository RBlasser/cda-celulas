# Prototipo PoC Standalone HTTP - Asesor Virtual de Préstamo de Auto 🚗🇵🇦

Prototipo conversacional refactorizado en **Python (Chainlit)** para la atención digital a clientes en el contexto de la **Feria de Préstamos de Auto** de **Caja de Ahorros (CDA)**.

Este componente funciona como la prueba de concepto (PoC) para validar la interacción comercial y captura de datos antes de la compilación final en **Rust** (`axum` + `rusqlite` + `rust-embed`).

---

## 🌟 Características de la Versión PoC

1. **💬 Interfaz Conversacional de Cara al Cliente (Modo Kiosco / QR):**
   * Perfilación comercial ágil en 3 a 5 turnos.
   * Captura estructurada de datos (Cédula, Nombre, Celular, Correo, Auto de interés, Rango salarial).
   * Generación de comprobante digital de turno para el stand.

2. **💾 Persistencia de Conversaciones y Leads:**
   * Registro atómico local de prospectos en archivo de base de datos / JSON para garantizar trazabilidad comercial de todos los visitantes del stand.
   * Capacidad de consulta y exportación para el seguimiento post-feria por los oficiales de crédito.

3. **🛡️ Principios de Ingeniería (Fail-Fast y Cero Mockdata):**
   * **Cero sobreingeniería:** Interfaz enfocada en la conversación y captura del lead.
   * **Cero fallbacks silenciosos:** Si la API externa no responde o las credenciales no son válidas, la aplicación reporta el error visiblemente.
   * **Cero datos simulados:** Respuestas calculadas a partir del diálogo real con el visitante.

---

## 🚀 Instrucciones de Ejecución

1. **Iniciar con Chainlit:**
   ```powershell
   python -m chainlit run app.py -w
   ```
   O ejecutando directamente el script por lotes:
   ```cmd
   run.bat
   ```

2. **Abrir en el navegador:**
   La aplicación levantará automáticamente en [http://localhost:8000](http://localhost:8000).
