# Diagramas de Flujo de Negocio con Sustento Técnico
## Casos de Uso del Asistente Inteligente de Formalización Desacoplado (Sin Ultimus ni Core Bancario)

**Proyecto:** Célula de Innovación Caja de Ahorros — Producto 02 (Formalización de Préstamos Personales)  
**Audiencia:** Operaciones de Crédito, Riesgo Operativo, Auditoría Interna, Tecnología y Canales  
**Elaborado por:** Célula de Innovación (StraTech / Caja de Ahorros) — Líder Técnico: Rodolfo Blasser  
**Fecha:** 28 de octubre de 2026  
**Versión:** 1.0 (Documento Exclusivo de Diagramación de Procesos y Flujos de Datos)  

---

## 1. Mapa General: Los Tres Casos de Uso en el Ciclo de Formalización

```mermaid
flowchart TD
    subgraph EXPEDIENTE["1. Entrada de Documentos del Préstamo Aprobado"]
        IN_DOCS["Expediente Digital del Cliente (PDFs)<br>• Cédula de Identidad Personal<br>• Carta de Trabajo (Privada o Pública)<br>• Talonario de Pago / Comprobante<br>• Ficha Digital de la CSS<br>• Cartas de Saldo Externas (Compra de Saldo)"]
    end

    subgraph CASO1["2. Caso de Uso 1: Auditoría Inteligente y Semáforo"]
        CU1["Auditoría Documental Cruzada<br>• Validación de identidad (nombre y cédula)<br>• Control estricto de vigencias temporales<br>• Detección de certificado para jubilados<br>• Verificación de calendarios de descuento"]
        SEM_RED["🔴 Rechazo Preventivo<br>Devolución inmediata a sucursal"]
        SEM_GREEN["🟢 Expediente Certificado<br>Apto para formalización"]
        CU1 -->|"Inconsistencias / Faltantes"| SEM_RED
        CU1 -->|"100% Conforme"| SEM_GREEN
    end

    subgraph CASO2["3. Caso de Uso 2: Copiloto de Extracción y Smart Clipboard"]
        CU2["Extracción Estructurada Multimodal<br>• Normalización de razón social<br>• Reconciliación de salarios y descuentos<br>• Lectura espacial de Planilla y Posición (Contraloría)"]
        CLIPBOARD["Smart Clipboard (1-Click Copy)<br>Pegado rápido en Ultimus BPM (30-50 seg)"]
        SEM_GREEN --> CU2
        CU2 --> CLIPBOARD
    end

    subgraph CASO3["4. Caso de Uso 3: Pre-Diligenciador de Documentación Legal"]
        CU3["Ensamblaje Contractual Automatizado<br>• Lectura de cartas de saldo de otros bancos<br>• Extracción de montos exactos y vigencias<br>• Diligenciamiento sobre plantillas oficiales (.docx)"]
        DOCS_OUT["Paquete Legal Listo para Firma<br>• Cartas de Promesa Irrevocable de Pago<br>• Pagaré Notarial y Minuta de Préstamo<br>• Órdenes de Descuento Institucionales"]
        CLIPBOARD --> CU3
        CU3 --> DOCS_OUT
    end

    IN_DOCS --> CU1
```

---

## 2. Caso de Uso 1: Auditoría Inteligente y Semáforo de Pre-Formalización
### *(Checklist Normativo y Consistencia Documental Cruzada)*

### Perspectiva de Negocio:
Evita que el analista invierta tiempo abriendo y leyendo manualmente entre 4 y 6 documentos PDF para descubrir errores al final del trámite. Detecta expedientes viciados antes de iniciar la digitación en el BPM, protegiendo al banco de sanciones normativas y eliminando reprocesos con sucursales.

### Sustento Técnico:
Ingesta en memoria volátil sin persistencia externa. Inferencia multimodal vía Gemini API con extracción tipada de metadatos de identidad, fechas y entidades institucionales. Motor determinístico de reglas booleanas para cotejo cruzado de cédulas, cálculo de días hábiles de vigencia y validación contra matrices de corte de planillas y calendarios de descuento.

```mermaid
flowchart TD
    subgraph INGESTA["1. Ingesta y Clasificación Documental"]
        FILES["Carga de Archivos del Préstamo (PDF / Imágenes)"] --> CLASSIFY["Clasificación Multimodal de Documentos<br>(Gemini Vision API)"]
        CLASSIFY --> D_CED["Cédula de Identidad"]
        CLASSIFY --> D_CART["Carta de Trabajo"]
        CLASSIFY --> D_TAL["Talonario de Pago"]
        CLASSIFY --> D_FICH["Ficha Digital CSS"]
        CLASSIFY --> D_JUB["Certificado Jubilado (CSS / Contraloría)"]
    end

    subgraph EXTRACCION["2. Extracción de Metadatos Críticos (JSON Estructurado)"]
        D_CED --> E_CED["Metadatos Cédula:<br>• Nombre completo<br>• Número de cédula<br>• Fecha de expiración"]
        D_CART --> E_CART["Metadatos Carta:<br>• Razón social empleadora<br>• Nombre y cédula colaborador<br>• Salario base y deducciones<br>• Fecha emisión de la carta"]
        D_TAL --> E_TAL["Metadatos Talonario:<br>• Nombre y cédula<br>• Salario neto y deducciones<br>• Institución / Código patronal"]
        D_FICH --> E_FICH["Metadatos Ficha:<br>• Número patronal<br>• Cuotas acumuladas"]
        D_JUB --> E_JUB["Metadatos Jubilación:<br>• Número de Certificado CSS<br>• Tipo de pensión"]
    end

    subgraph REGLAS["3. Motor Determinístico de Reglas de Negocio"]
        R1{"Regla 1: Identidad Cruzada<br>¿Nombre y cédula idénticos<br>en Cédula, Carta, Talonario y Ficha?"}
        R2{"Regla 2: Vigencia de Carta<br>¿Emisión no mayor a 30 días (privada)<br>o 45 días (pública)?"}
        R3{"Regla 3: Vigencia de Cédula<br>¿Fecha expiración > Fecha actual?"}
        R4{"Regla 4: Perfil Jubilado<br>¿Si es jubilado, existe el<br>Certificado emitido por la CSS?"}
        R5{"Regla 5: Calendario Institucional<br>¿Corte de planilla vigente y<br>aplica política de no descuento en diciembre?"}

        E_CED & E_CART & E_TAL & E_FICH --> R1
        E_CART --> R2
        E_CED --> R3
        E_JUB --> R4
        E_TAL --> R5
    end

    subgraph DICTAMEN["4. Generación del Dictamen de Pre-Formalización"]
        R1 & R2 & R3 & R4 & R5 --> EVAL["Matriz de Evaluación de Calidad"]
        
        EVAL -->|"Falla Crítica (Identidad, Caducidad o Falta Certificado)"| RED["🔴 Semáforo Rojo: EXPEDIENTE NO CONFORME<br>• Detalle exacto de inconsistencias<br>• Registro en bitácora local<br>• Devolución inmediata a agencia de origen"]
        
        EVAL -->|"Alerta Preventiva (Vigencia próxima a vencer en < 5 días)"| YELLOW["🟡 Semáforo Amarillo: EXPEDIENTE CON ADVERTENCIA<br>• Requiere validación de fechas límites por analista"]
        
        EVAL -->|"100% Cumplimiento de Reglas"| GREEN["🟢 Semáforo Verde: EXPEDIENTE CERTIFICADO<br>• Habilitación automática del Caso 2 (Smart Clipboard)<br>• Cero riesgo de rechazo normativo"]
    end
```

---

## 3. Caso de Uso 2: Copiloto de Extracción Estructurada y Smart Clipboard
### *(Smart Clipboard & Normalización de Datos para Carga en Ultimus)*

### Perspectiva de Negocio:
Elimina el desgaste cognitivo y los errores de dedo al transcribir manualmente 10 a 12 campos desde documentos impresos o escaneados hacia Ultimus BPM. Protege al banco de rechazos en los Web Services de IBS causados por números de planilla o posición erróneos en empleados públicos, y reduce el tiempo de tipeo de 10 minutos a 30-50 segundos mediante pantalla dividida.

### Sustento Técnico:
Uso de modelos de visión multimodal con invariancia de diseño (*Zero-Shot Layout Invariance*) para interpretar cartas privadas no homogéneas y razonamiento espacial sobre tablas (*Visual Table Reasoning*) para extraer celdas en cuadrículas densas de Contraloría. Reconciliación matemática estricta antes de la entrega. Empleo de la API nativa del navegador (`navigator.clipboard.writeText`) para copiado seguro en un clic con retroalimentación visual, respetando las políticas de ciberseguridad sin requerir extensiones ni scripts invasivos.

```mermaid
flowchart TD
    subgraph ENTRADA_DOCS["1. Documentos Base Aprobados (Semáforo Verde)"]
        DOC_PRIV["Carta de Trabajo (Empresa Privada)<br>• Formato heterogéneo / Redacción libre"]
        DOC_PUB["Talonario Oficial de Contraloría<br>• Cuadrícula densa / Micro-tipografía"]
    end

    subgraph PROCESAMIENTO_COGNITIVO["2. Procesamiento Cognitivo Multimodal (Gemini API)"]
        DOC_PRIV --> P_PRIV["Comprensión Semántica Invariante al Diseño<br>• Extracción de salario base pactado<br>• Identificación de deducciones fijas<br>• Normalización de Razón Social a catálogo"]
        
        DOC_PUB --> P_PUB["Razonamiento Espacial de Grilla (Visual Table Reasoning)<br>• Ubicación visual de celda 'PLANILLA'<br>• Ubicación visual de celda 'POSICIÓN'<br>• Extracción de valores numéricos limpios (ej. 14 / 101010)"]
    end

    subgraph RECONCILIACION["3. Motor de Normalización y Reconciliación Aritmética"]
        P_PRIV & P_PUB --> NORM_FECHA["Normalización de Fechas<br>Conversión de texto libre al estándar YYYY-MM-DD"]
        NORM_FECHA --> RECON_MATH{"Reconciliación Aritmética<br>¿Salario Bruto - Deducciones == Salario Neto?"}
        
        RECON_MATH -->|"Diferencia > $0.01"| WARN_MATH["Advertencia de Descuadre Aritmético<br>(Posibles descuentos voluntarios no reflejados)"]
        RECON_MATH -->|"Cuadre Exacto"| DATA_READY["Estructura de Datos Normalizada Lista"]
    end

    subgraph INTERFAZ_USUARIO["4. Interfaz Smart Clipboard (Ergonomía de Puesto)"]
        DATA_READY --> CARD["Tarjeta Digital en Secuencia de Ultimus BPM"]
        
        CARD --> F1["1. Razón Social Empresa ➔ [ Botón Copiar ]"]
        CARD --> F2["2. Salario Bruto ➔ [ Botón Copiar ]"]
        CARD --> F3["3. Total Deducciones ➔ [ Botón Copiar ]"]
        CARD --> F4["4. Salario Neto ➔ [ Botón Copiar ]"]
        CARD --> F5["5. Fecha de Ingreso ➔ [ Botón Copiar ]"]
        CARD --> F6["6. No. Planilla (Contraloría) ➔ [ Botón Copiar ]"]
        CARD --> F7["7. No. Posición (Contraloría) ➔ [ Botón Copiar ]"]
        
        CARD -.-> EXPORT_JSON["[ Descargar Ficha JSON / Excel ]<br>(Respaldo de auditoría)"]
    end

    subgraph OPERACION_ULTIMUS["5. Pegado Asistido en Ultimus BPM (Pantalla Dividida)"]
        F1 & F2 & F3 & F4 & F5 & F6 & F7 -->|"Clic en Copiar<br>(API: navigator.clipboard.writeText)"| CLIP["Portapapeles del Sistema<br>(Feedback: '✓ ¡Copiado!' en verde)"]
        
        CLIP -->|"Analista presiona Ctrl + V<br>(Ventana paralela: Win + Flecha Derecha)"| ULTIMUS_FIELDS["Campos del Formulario en Ultimus BPM<br>• Cero errores de transcripción tipográfica<br>• Tiempo de llenado: 30 a 50 segundos"]
    end
```

---

## 4. Caso de Uso 3: Pre-Diligenciador y Ensamblador de Documentación Contractual
### *(Cartas de Promesa de Pago, Pagarés y Órdenes de Descuento para Compra de Saldo)*

### Perspectiva de Negocio:
En préstamos para consolidación de pasivos externos, el analista pierde entre 20 y 35 minutos buscando saldos y cuentas en cartas de bancos competidores para tipear minutas y promesas en Word. El módulo automatiza la extracción de deudas externas y diligencia en segundos el paquete contractual oficial de Caja de Ahorros, garantizando exactitud matemática y jurídica para la firma del cliente.

### Sustento Técnico:
Extracción semántica multimodal de cartas de saldo de cualquier banco de la plaza panameña (Banco General, Banistmo, BAC, Global Bank, etc.). Validación cruzada de fechas de vigencia de la promesa contra la fecha de desembolso proyectada. Motor local de ensamblaje documental (*Document Templating Engine*) que inyecta variables en plantillas `.docx` oficiales de Caja de Ahorros respetando formatos notariales, firmas y cláusulas condicionales.

```mermaid
flowchart TD
    subgraph INSUMOS_PASIVOS["1. Insumos de la Compra de Saldo"]
        LETTERS["Cartas de Saldo Externas (PDFs escaneados)<br>• Banco General, Banistmo, BAC, Financieras, etc."]
        PROFORMA["Proforma Aprobada Caja de Ahorros<br>• Monto total del préstamo aprobado<br>• Tasa, plazo, letra mensual y seguro"]
    end

    subgraph EXTRACCION_LEGAL["2. Extracción Cognitiva de Pasivos a Cancelar (Gemini API)"]
        LETTERS --> EXTRACT_BANKS["Extracción por Institución Acreedora:<br>• Razón Social del Banco Acreedor<br>• Número de Préstamo o Tarjeta a Cancelar<br>• Saldo Total al Corte (Cifras exactas al centavo)<br>• Fecha Límite de Vigencia de la Carta de Saldo"]
        
        PROFORMA --> EXTRACT_COND["Extracción de Condiciones CDA:<br>• Nombre y Cédula del Deudor<br>• Domicilio y Generales<br>• Cuota Quincenal/Mensual Pactada<br>• Tasa de Interés y Plazo en Meses"]
    end

    subgraph VALIDACION_FINANCIERA["3. Validación de Capacidad y Vigencia Contractual"]
        EXTRACT_BANKS & EXTRACT_COND --> SUM_CHECK{"Consistencia Financiera<br>¿Suma de saldos externos <= Monto aprobado CDA?"}
        
        SUM_CHECK -->|"Excede Monto Aprobado"| STOP_DIFF["🔴 Alerta de Descuadre de Saldo<br>• Fondos insuficientes para cancelación<br>• Pausa de generación contractual"]
        
        SUM_CHECK -->|"Suma Conforme"| DATE_CHECK{"Control de Vencimiento de Cartas<br>¿Vigencia de carta > Fecha proyectada de pago?"}
        
        DATE_CHECK -->|"Carta Expirada o Próxima a Expirar"| WARN_DATE["🟡 Alerta: Carta de Saldo por Vencer<br>• Requiere actualización antes de emitir promesa"]
        DATE_CHECK -->|"Fechas Hábiles Válidas"| TEMPLATE_ENGINE["Motor Local de Ensamblaje Documental (.docx)"]
    end

    subgraph PLANTILLAS_CDA["4. Repositorio de Plantillas Oficiales de Caja de Ahorros"]
        T_PROM["Plantilla Oficial: Promesa Irrevocable de Pago (.docx)"]
        T_PAG["Plantilla Oficial: Pagaré Notarial y Contrato (.docx)"]
        T_ORD["Plantilla Oficial: Orden de Descuento por Planilla (.docx)"]
        
        T_PROM & T_PAG & T_ORD --> TEMPLATE_ENGINE
    end

    subgraph GENERACION_FINAL["5. Paquete Documental Listo para Firma"]
        TEMPLATE_ENGINE --> GEN_FILES["Fusión de Variables y Generación en Memoria"]
        
        GEN_FILES --> OUT_PROM["📄 Cartas de Promesa de Pago a Terceros<br>• Personalizada por cada banco acreedor<br>• Número de cuenta y saldo exacto liquidado"]
        
        GEN_FILES --> OUT_PAG["📄 Pagaré Notarial y Contrato de Préstamo<br>• Desglose legal de cuota, plazo y seguro<br>• Cláusulas de compra de saldo incorporadas"]
        
        GEN_FILES --> OUT_ORD["📄 Orden de Descuento Institucional<br>• Formateada para Contraloría, CSS o Privada<br>• Calendario de descuento ajustado"]
        
        OUT_PROM & OUT_PAG & OUT_ORD --> BUNDLE["📦 Paquete Contractual Completo (.docx / .pdf)<br>Descarga instantánea para revisión y firma del cliente"]
    end
```

---

## 5. Resumen Comparativo de Arquitectura Técnica y Valor de Negocio

| Dimensión | Caso de Uso 1: Auditoría Inteligente | Caso de Uso 2: Smart Clipboard | Caso de Uso 3: Ensamblador Contractual |
| :--- | :--- | :--- | :--- |
| **Objetivo de Negocio** | Filtrar expedientes viciados o incompletos antes de ingresar al sistema. | Acelerar el tipeo de datos en Ultimus BPM sin cometer errores tipográficos. | Automatizar la emisión legal de cartas de pago a otros bancos y pagarés. |
| **Sustento Técnico Clave** | Inferencia multimodal estructurada + motor determinístico de reglas booleanas. | *Visual Table Reasoning* (grillas densas) + Web Clipboard API nativa. | Extracción de pasivos + motor de templating `.docx` en memoria volátil. |
| **Interacción con Ultimus** | **Cero contacto** (Actúa como filtro previo en escritorio del analista). | **Pegado asistido manual** (`Ctrl + V`) en pantalla dividida sin plugins. | **Cero contacto** (Genera archivos Word/PDF listos para firma y archivo). |
| **Ahorro de Tiempo Medido** | De 20 minutos a **10 segundos** de revisión. | De 10 minutos a **30–50 segundos** de digitación. | De 35 minutos a **15 segundos** de redacción. |
| **Impacto en Riesgo Operativo** | Cero multas por expedientes sin vigencia o sin certificado de jubilados. | Cero rechazos de Web Services en IBS por Planilla/Posición erróneas. | Cero errores en cifras o números de cuentas de bancos competidores. |
