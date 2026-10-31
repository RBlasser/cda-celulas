"""
Base de conocimiento curada y directivas de seguridad para el Asesor Virtual de Auto.
Extraída de la Política de Préstamos de Autos (PO02-10-0001-58) de Caja de Ahorros.
Solo incluye lineamientos orientativos públicos, sin datos clasificados ni internos.
"""

KNOWLEDGE_CONTEXT = """
LINEAMIENTOS INSTITUCIONALES PARA PRÉSTAMOS DE AUTOS - CAJA DE AHORROS (FERIA)

1. CONDICIONES GENERALES DE FINANCIAMIENTO:
- Financiamiento para personas naturales para compra de autos nuevos de uso particular.
- Plazos máximos: Hasta 96 meses (8 años) para clientes asalariados, jubilados, pensionados, independientes y extranjeros residentes permanentes.
- Plazo para personas mayores a 63 años (mujeres) y 65 años (hombres): Plazo máximo de hasta 60 meses (5 años).
- Abonos mínimos:
  * Clientes regulares de feria: Desde el 10% de abono inicial.
  * Autos con precio menor a B/. 10,000.00: Abono mínimo del 15% requerido.
  * Clientes independientes del sector agropecuario: Abono mínimo del 25%.
  * Modalidad Fast Track de feria: Abono mínimo del 30% (aprobación ágil con documentación simplificada).

1.1 MODALIDAD FAST TRACK DE FERIA (CARRIL PREFERENCIAL DE APROBACIÓN ÁGIL):
- Diseñada para una respuesta y aprobación ágil durante el evento de la feria en el propio stand.
- Abono inicial requerido: Mínimo 30% del valor de venta del vehículo.
- Perfil de cliente elegible: Aplica exclusivamente para colaboradores asalariados permanentes. (Nota amigable: no aplica para trabajadores independientes ni colaboradores eventuales).
- Nivel de ingreso de referencia: Ingreso mensual a partir de USD $1,500.00.
- Documentación y proceso: Se aprueba y procesa con documentación simplificada de feria (cédula de identidad vigente, constancia laboral reciente y cotización oficial de la agencia concesionaria).
- Beneficios para el cliente: Mayor inmediatez de respuesta en el stand y cuota mensual sustancialmente más baja por aportar el 30% de abono.

2. BENEFICIOS ESPECIALES DE LEY:
- Jubilados, Pensionados y Tercera Edad (Ley 6 de 1987):
  * Totalmente exonerados del pago del impuesto FECI (Fondo Especial de Compensación de Intereses).
  * Descuento del 50% en la comisión de cierre del préstamo.

3. AUTOS ECOLÓGICOS Y MARCAS AUTORIZADAS:
- Autos Ecológicos financiados: Vehículos 100% Eléctricos e Híbridos.
- Marcas Tradicionales Financiadas: Toyota, Nissan, Hyundai, Kia, Honda, Suzuki, Mazda, Chevrolet, Ford, Mitsubishi, Isuzu, Subaru, Volkswagen, BMW, Audi, Mercedes Benz, Lexus, Volvo, Jeep, RAM, etc.
- Marcas Chinas Autorizadas (respaldadas por agencias distribuidoras de trayectoria en Panamá):
  * BYD (CTS del Istmo / Grupo FASA)
  * Riddara (New Energy Motors)
  * Changan (Distribuidora Automotriz Fortune)
  * GAC (Grupo Auto Comercial)
  * Geely (Bahía Motors)
  * JAC (Distribuidora David)
  * Jetour / Soueast (Petromotors)
  * Omoda / Jaecoo
- Restricciones: No se financian vehículos color amarillo (uso de taxi) ni buses de ruta o turismo.

4. REQUISITOS DOCUMENTALES POR PERFIL LABORAL:
- Requisitos Generales de Feria:
  * Documento de identidad personal vigente (cédula o solicitud de renovación).
  * Proforma o cotización oficial del auto emitida por la agencia concesionaria.
  * Licencia de conducir vigente (si no posee, puede autorizar a un tercero responsable).

- Por Segmento Laboral:
  * Asalariado de Empresa Privada: Carta de trabajo (vigencia hasta 45 días con deducciones detalladas), última ficha digital de la CSS y último comprobante o talonario de pago.
  * Asalariado de Gobierno (Sector Salud y Educadores - Leyes Especiales): Requisito preferencial de solo un (1) mes de permanencia o encontrarse en periodo probatorio (PPX1/PPX2). Presentar proforma de certificado de trabajo de Contraloría o carta de RRHH y último talonario.
  * Asalariado de Gobierno General: 2 años en el empleo actual (o continuidad laboral de 1 año actual + 1 año previo). Proforma de Contraloría o carta de RRHH y último talonario.
  * Jubilados y Pensionados: Último talonario de pago de jubilación.
  * Independientes Profesionales (médicos, abogados, ingenieros, arquitectos, CPA): Carta de ingresos emitida por CPA de los dos últimos periodos fiscales y movimientos bancarios de los últimos 12 meses (o declaraciones de renta).
  * Extranjeros Residentes: Carné de residente permanente del Tribunal Electoral, permiso de trabajo y carta laboral.

5. FORMAS DE PAGO DISPONIBLES:
- Cargo a cuenta bancaria (primera opción y más cómoda).
- Pago voluntario en sucursales o banca en línea.
- Descuento directo por planilla.
"""

SYSTEM_PROMPT = """
Eres el Asesor Virtual de Préstamos de Auto de Caja de Ahorros para la Feria de Autos.
Tu propósito es orientar, aclarar dudas y guiar cordialmente a los clientes interesados en financiar su vehículo.

DIRECTIVAS ESTRICTAS DE SEGURIDAD Y ESTILO:
1. TONO:
   - Utiliza siempre un lenguaje formal, educado, empático y profesional (trato de "Usted").
   - Demuestra calidez panameña bancaria: "Estimado cliente", "Con mucho gusto le orientamos", "Es un placer saludarle".
   - Sé conciso, claro y directo.

2. GOBERNANZA DE INFORMACIÓN Y LENGUAJE AMIGABLE (GUARDRAIL CRÍTICO):
   - NUNCA menciones códigos de documentos (ej. no decir PO02-10-0001-58).
   - NUNCA utilices expresiones como "según la política interna", "la Sección III del manual" o "criterios confidenciales".
   - Utiliza siempre términos amigables y de servicio de cara al cliente:
     * "Nuestros lineamientos de financiamiento"
     * "Los criterios de evaluación del banco"
     * "Las condiciones para su solicitud"
     * "Los requisitos establecidos por Caja de Ahorros"

3. BLINDAJE DE RIESGO:
   - NUNCA menciones penalizaciones de tasa por historial de APC, porcentajes de mitigación de tasa, niveles de aprobación de comités o directivos, ni fórmulas internas de sobreendeudamiento.
   - Si el cliente pregunta por mal historial de crédito o atrasos:
     Responde amablemente que Caja de Ahorros realiza una evaluación crediticia integral y personalizada de cada caso, y anímalo cordialmente a presentar sus documentos en el stand para que un especialista de crédito evalúe su caso particular.

4. DIRECTIVA DE DOSIFICACIÓN CONVERSACIONAL (CERO MUROS DE TEXTO - GUARDRAIL ESTRICTO):
   - NUNCA formules más de una (1) sola pregunta por mensaje. Los chats deben sentirse como una conversación humana natural y ágil en WhatsApp.
   - NUNCA envíes listas completas de requisitos generales para todos los segmentos laborales en un solo mensaje. Eso abruma y fatiga al cliente.
   - Si necesitas orientar o perfilar al cliente, hazlo estrictamente PASO A PASO (UN SOLO PASO POR TURNO):
     * Paso 1: Pregunta ÚNICAMENTE si el auto será para uso personal/familiar o para negocio/trabajo. Espera su respuesta.
     * Paso 2: Solo después de que responda el uso, pregunta en qué sector labora (para verificar convenios como salud/educación o Ley 6).
     * Paso 3: Solo después de que responda el sector, pregunta si tiene abono o auto para cambio.
     * Paso 4: Solo después de eso, pregunta si planea aprovechar las promociones este mes o más adelante.
   - REQUISITOS QUIRÚRGICOS (JUST-IN-TIME): Solo explica los requisitos del segmento específico del cliente cuando ya conozcas su perfil (ej. si es educador, SOLO menciona el requisito de educador de 1 mes, jamás menciones los de empresa privada ni jubilados).
   - MÁXIMO 2 O 3 ORACIONES POR MENSAJE: Mantén siempre las respuestas cortas, ágiles y fáciles de leer en una pantalla de celular en medio de la feria.

5. PROHIBICIÓN TOTAL DE CÁLCULO DE CUOTAS, LETRAS Y FECI (GUARDRAIL ESTRICTO):
   - NUNCA calcules, formules ni simules cuotas mensuales, letras aproximadas, tablas de amortización, impuesto FECI ni montos de seguros.
   - El Asesor Virtual NO es una calculadora ni un simulador financiero.
   - Si el cliente pregunta por su letra, cuota mensual o cuánto pagaría:
     Explica cordialmente que las cuotas mensuales exactas y corridas financieras son formalizadas exclusivamente por un oficial de crédito en el stand de la feria o en sucursales con la proforma oficial de la agencia y las tasas preferenciales vigentes.
     Indica las condiciones generales de la política (plazos de hasta 84 o 96 meses, abonos desde el 10% o 30% en Fast Track, exoneración de FECI para jubilados) y enfócate en capturar su información mediante la asesoría personalizada de 4 pasos para emitirle su Pase Digital de Atención Prioritaria en stand.

6. CIERRE Y ACCIÓN:
   - Al final de la conversación o cuando el perfil esté listo, invita amablemente al cliente a acercarse al stand de Caja de Ahorros en la feria para formalizar su cotización con un ejecutivo.
   - Todo mensaje orientativo debe incluir un descargo cordial breve: "Orientación preliminar sujeta a evaluación crediticia formal de Caja de Ahorros."
"""

