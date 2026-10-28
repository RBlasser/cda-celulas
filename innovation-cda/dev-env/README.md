# Prototipo Asesor Virtual de Auto - Feria de Préstamos Caja de Ahorros 🚗🇵🇦

Prototipo conversacional refactorizado con **Chainlit** para la atención digital a clientes en el contexto de la **Feria de Préstamos de Auto** de **Caja de Ahorros (CDA)**.

El sistema ofrece streaming en tiempo real a 60 fps con **Google Gemini 3.5 Flash** (usando Server-Sent Events nativos), cálculo de cuotas de financiamiento, generación de pases digitales para el stand y fallback inteligente local para operar sin conexión ni costo de API.

---

## 🌟 Características de la Versión Chainlit

1. **💬 Interfaz Conversacional Nativa (Chat-First)**:
   - Diseño limpio con avatar coral para el usuario y robot dorado para el Asesor.
   - Streaming en vivo palabra por palabra (reduce la latencia percibida a 0).
   - Acciones interactivas al iniciar sesión (*Starters*):
     - 🏥 Requisitos para Salud y Educadores (1 mes de permanencia).
     - 🇨🇳 Marcas Chinas respaldadas (BYD, Geely, Changan, GAC, JAC, etc.).
     - ⚡ Abonos mínimos y Modalidad Fast Track (30% de abono).
     - 👴 Beneficios para Jubilados (Ley 6 de 1987).
     - 🧮 Simulación de cuotas de auto.

2. **🧮 Simulador y Pase Digital Integrado en el Chat**:
   - Cálculos automáticos de amortización francesa, seguro referencial y exoneración de FECI.
   - Emisión de comprobante digital con código de turno único (`CDA-AUTO-XXXX`) para el stand.

3. **🛡️ Guardrails Institucionales**:
   - Cero fuga de secciones de manuales o códigos confidenciales.
   - Vocabulario amigable y cercano (*"nuestros lineamientos de financiamiento"*).

---

## 🚀 Instrucciones de Ejecución

### 1. Iniciar con Chainlit (Versión Actual)
En la terminal dentro de `dev-env`:
```powershell
python -m chainlit run app.py -w
```
O simplemente ejecutando el archivo por lotes:
```powershell
.\run.bat
```
La aplicación abrirá automáticamente en su navegador en `http://localhost:8000`.

### 2. Iniciar la versión anterior de Streamlit (Respaldada)
Si desea volver a consultar el dashboard multipestaña con sliders:
```powershell
python -m streamlit run app_streamlit.py
```

---

## 📁 Estructura de Archivos

```
dev-env/
├── app.py                # Aplicación conversacional principal con Chainlit y streaming
├── app_streamlit.py      # Respaldo de la versión anterior con pestañas y sliders en Streamlit
├── gemini_client.py      # Cliente con stream_gemini_api (SSE) y motor local de respaldo
├── knowledge_base.py     # Base de conocimiento curada y directivas institucionales
├── chainlit.md           # Pantalla de bienvenida institucional personalizada
├── run.bat               # Script directo de ejecución para Windows
├── .chainlit/config.toml # Configuración de Chainlit (idioma español, marca CDA)
└── .env                  # Clave GEMINI_API_KEY configurada localmente
```
