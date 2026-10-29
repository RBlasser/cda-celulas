import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Official Caja de Ahorros Color Palette
    CDA_BLUE = RGBColor(7, 69, 148)       # #074594 Exact Logo Blue
    CDA_DARK_BLUE = RGBColor(4, 45, 98)   # #042D62 Dark Navy
    CDA_LIGHT_BG = RGBColor(245, 248, 253)# #F5F8FD Crisp light slide background
    TEXT_DARK = RGBColor(15, 34, 64)      # #0F2240 Deep Charcoal/Navy
    TEXT_MUTED = RGBColor(90, 105, 130)   # #5A6982 Secondary text
    WHITE = RGBColor(255, 255, 255)
    CARD_BG = RGBColor(255, 255, 255)
    CARD_BORDER = RGBColor(215, 226, 240)
    ACCENT_CYAN = RGBColor(0, 164, 228)   # Bright Cyan
    ACCENT_GREEN = RGBColor(22, 163, 74)  # Success Green
    ACCENT_RED = RGBColor(220, 38, 38)    # Alert Red
    ACCENT_AMBER = RGBColor(217, 119, 6)  # Warning Amber
    SOFT_GREEN_BG = RGBColor(236, 253, 245)
    SOFT_RED_BG = RGBColor(254, 242, 242)
    SOFT_BLUE_BG = RGBColor(238, 246, 255)
    SOFT_AMBER_BG = RGBColor(254, 243, 199)

    logo_path = os.path.abspath("cda-logo.png")

    def add_header(slide, title_text, category_text="CÉLULAS DE INNOVACIÓN CON IA"):
        # Top banner in CDA Blue
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        banner.fill.solid()
        banner.fill.fore_color.rgb = CDA_BLUE
        banner.line.color.rgb = CDA_BLUE

        # Category tag
        cat_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.12), Inches(9.5), Inches(0.28))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_CYAN

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.36), Inches(9.5), Inches(0.68))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(20)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

        # Logo on right of banner
        if os.path.exists(logo_path):
            slide.shapes.add_picture(logo_path, Inches(10.7), Inches(0.15), width=Inches(2.1))

        # Bottom footer bar
        footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.15), Inches(13.333), Inches(0.35))
        footer.fill.solid()
        footer.fill.fore_color.rgb = RGBColor(235, 240, 248)
        footer.line.color.rgb = RGBColor(220, 228, 240)

        f_box = slide.shapes.add_textbox(Inches(0.6), Inches(7.18), Inches(12.133), Inches(0.28))
        tf_f = f_box.text_frame
        tf_f.margin_left = tf_f.margin_right = tf_f.margin_top = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = "Caja de Ahorros de Panamá  |  Iniciativa de Innovación Tecnológica (StraTech & CDA)  |  Uso Exclusivo de Negocio"
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = TEXT_MUTED

    def set_slide_background(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    # =========================================================================
    # SLIDE 1: PORTADA INSTITUCIONAL
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, CDA_BLUE)

    dec_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.7), Inches(11.733), Inches(6.1))
    dec_card.fill.solid()
    dec_card.fill.fore_color.rgb = CDA_BLUE
    dec_card.line.color.rgb = ACCENT_CYAN
    dec_card.line.width = Pt(2.0)

    if os.path.exists(logo_path):
        s1.shapes.add_picture(logo_path, Inches(1.3), Inches(1.2), width=Inches(3.8))

    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.3), Inches(2.7), Inches(4.8), Inches(0.42))
    pill.fill.solid()
    pill.fill.fore_color.rgb = ACCENT_CYAN
    pill.line.fill.background()
    p_tf = pill.text_frame
    p_tf.margin_top = Inches(0.06)
    p_p = p_tf.paragraphs[0]
    p_p.text = "PORTAFOLIO DE INTELIGENCIA ARTIFICIAL"
    p_p.alignment = PP_ALIGN.CENTER
    p_p.font.size = Pt(11)
    p_p.font.bold = True
    p_p.font.color.rgb = CDA_DARK_BLUE

    t_box = s1.shapes.add_textbox(Inches(1.3), Inches(3.25), Inches(10.5), Inches(1.4))
    t_tf = t_box.text_frame
    t_tf.word_wrap = True
    p1 = t_tf.paragraphs[0]
    p1.text = "Células de Innovación con IA"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    p2 = t_tf.add_paragraph()
    p2.text = "Diseño de Soluciones: Asesor de Feria de Autos y Formalización de Préstamos"
    p2.font.size = Pt(20)
    p2.font.color.rgb = RGBColor(195, 230, 255)
    p2.space_before = Pt(8)

    div = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.3), Inches(4.85), Inches(10.5), Inches(0.03))
    div.fill.solid()
    div.fill.fore_color.rgb = ACCENT_CYAN
    div.line.fill.background()

    meta_box = s1.shapes.add_textbox(Inches(1.3), Inches(5.05), Inches(10.5), Inches(1.3))
    m_tf = meta_box.text_frame
    m_p1 = m_tf.paragraphs[0]
    m_p1.text = "Audiencia: Vicepresidencia de Negocio, Dirección de Operaciones, Canales y Riesgo de Crédito"
    m_p1.font.size = Pt(12)
    m_p1.font.color.rgb = WHITE

    m_p2 = m_tf.add_paragraph()
    m_p2.text = "Desarrollado por: Célula de Innovación (StraTech / Caja de Ahorros)  •  Líder Técnico: Rodolfo Blasser  •  Octubre 2026"
    m_p2.font.size = Pt(11)
    m_p2.font.color.rgb = RGBColor(180, 215, 250)
    m_p2.space_before = Pt(4)


    # =========================================================================
    # SLIDE 2: VISIÓN DEL PORTAFOLIO - DOS SOLUCIONES ESTRATÉGICAS
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, CDA_LIGHT_BG)
    add_header(s2, "Visión Estratégica: Dos Soluciones para Acelerar el Negocio", "PORTAFOLIO DE INNOVACIÓN")

    intro_box = s2.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(12.133), Inches(0.55))
    i_tf = intro_box.text_frame
    i_tf.word_wrap = True
    i_p = i_tf.paragraphs[0]
    i_p.text = "La Célula de Innovación ha diseñado dos herramientas complementarias que impactan directamente el ciclo de vida del cliente: desde la captación comercial inmediata en ferias hasta la rápida entrega del dinero en operaciones de préstamo."
    i_p.font.size = Pt(12)
    i_p.font.color.rgb = TEXT_DARK

    # Card 1: Feria de Autos
    c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.95), Inches(5.8), Inches(4.95))
    c1.fill.solid()
    c1.fill.fore_color.rgb = CARD_BG
    c1.line.color.rgb = CARD_BORDER
    c1.line.width = Pt(1.5)

    c1_hdr = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(2.1), Inches(5.4), Inches(0.65))
    c1_hdr.fill.solid()
    c1_hdr.fill.fore_color.rgb = SOFT_BLUE_BG
    c1_hdr.line.color.rgb = ACCENT_CYAN
    c1_tf = c1_hdr.text_frame
    c1_p = c1_tf.paragraphs[0]
    c1_p.text = "PRODUCTO 01: Venta y Canales"
    c1_p.font.bold = True
    c1_p.font.size = Pt(12.5)
    c1_p.font.color.rgb = CDA_BLUE
    c1_p2 = c1_tf.add_paragraph()
    c1_p2.text = "Asesor Virtual para Feria de Autos (Front-Office)"
    c1_p2.font.size = Pt(10.5)
    c1_p2.font.color.rgb = TEXT_DARK

    c1_body = s2.shapes.add_textbox(Inches(0.85), Inches(2.85), Inches(5.3), Inches(3.2))
    tf1 = c1_body.text_frame
    tf1.word_wrap = True

    items1 = [
        ("Objetivo de Negocio", "Capturar prospectos en stands abarrotados (Panamá Motor Show), reduciendo tiempos de espera de 20 min a 2 min."),
        ("Rol de la IA", "Interacción natural y amigable que califica al cliente según la política crediticia oficial de Caja de Ahorros."),
        ("Simulación en Vivo", "Calcula abono mínimo, plazo y letra quincenal/mensual con base en la marca y valor del auto."),
        ("Entregable al Negocio", "Lead calificado entregado en segundos al ejecutivo comercial en el stand para cierre inmediato.")
    ]
    for idx, (title, desc) in enumerate(items1):
        p_t = tf1.paragraphs[0] if idx == 0 else tf1.add_paragraph()
        p_t.text = f"• {title}: "
        p_t.font.bold = True
        p_t.font.size = Pt(10.5)
        p_t.font.color.rgb = CDA_BLUE
        if idx > 0: p_t.space_before = Pt(6)
        run = p_t.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(10)
        run.font.color.rgb = TEXT_DARK

    c1_metric = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.15), Inches(5.4), Inches(0.55))
    c1_metric.fill.solid()
    c1_metric.fill.fore_color.rgb = SOFT_BLUE_BG
    c1_metric.line.color.rgb = ACCENT_CYAN
    m_tf1 = c1_metric.text_frame
    mp1 = m_tf1.paragraphs[0]
    mp1.text = "Tiempo de Atención: De 20 min a 90 seg  |  +40% Captura de Prospectos"
    mp1.alignment = PP_ALIGN.CENTER
    mp1.font.bold = True
    mp1.font.size = Pt(10)
    mp1.font.color.rgb = CDA_BLUE

    # Card 2: Formalización
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.95), Inches(5.9), Inches(4.95))
    c2.fill.solid()
    c2.fill.fore_color.rgb = CARD_BG
    c2.line.color.rgb = CARD_BORDER
    c2.line.width = Pt(1.5)

    c2_hdr = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(2.1), Inches(5.5), Inches(0.65))
    c2_hdr.fill.solid()
    c2_hdr.fill.fore_color.rgb = SOFT_GREEN_BG
    c2_hdr.line.color.rgb = ACCENT_GREEN
    c2_tf = c2_hdr.text_frame
    c2_p = c2_tf.paragraphs[0]
    c2_p.text = "PRODUCTO 02: Operaciones y Eficiencia"
    c2_p.font.bold = True
    c2_p.font.size = Pt(12.5)
    c2_p.font.color.rgb = ACCENT_GREEN
    c2_p2 = c2_tf.add_paragraph()
    c2_p2.text = "Asistente Desacoplado de Formalización (Back-Office)"
    c2_p2.font.size = Pt(10.5)
    c2_p2.font.color.rgb = TEXT_DARK

    c2_body = s2.shapes.add_textbox(Inches(7.05), Inches(2.85), Inches(5.4), Inches(3.2))
    tf2 = c2_body.text_frame
    tf2.word_wrap = True

    items2 = [
        ("Objetivo de Negocio", "Acelerar la confección y firma de préstamos personales aprobados sin alterar sistemas bancarios (Cero riesgo de IT)."),
        ("Auditoría y Semáforo", "Filtra en 5 seg expedientes incompletos; detiene casos de jubilados sin certificado de CSS (evita 20 días de espera)."),
        ("Smart Clipboard", "Extracción de cartas y talonarios de Contraloría. Copiado en 1 clic hacia Ultimus (de 10 min a 40 seg, 0% error tipeo)."),
        ("Ensamblador Contractual", "Procesa cartas de saldo de otros bancos y genera pagarés y promesas de pago listas para firma del cliente en 15 seg.")
    ]
    for idx, (title, desc) in enumerate(items2):
        p_t = tf2.paragraphs[0] if idx == 0 else tf2.add_paragraph()
        p_t.text = f"• {title}: "
        p_t.font.bold = True
        p_t.font.size = Pt(10.5)
        p_t.font.color.rgb = ACCENT_GREEN
        if idx > 0: p_t.space_before = Pt(6)
        run = p_t.add_run()
        run.text = desc
        run.font.bold = False
        run.font.size = Pt(10)
        run.font.color.rgb = TEXT_DARK

    c2_metric = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(6.15), Inches(5.5), Inches(0.55))
    c2_metric.fill.solid()
    c2_metric.fill.fore_color.rgb = SOFT_GREEN_BG
    c2_metric.line.color.rgb = ACCENT_GREEN
    m_tf2 = c2_metric.text_frame
    mp2 = m_tf2.paragraphs[0]
    mp2.text = "Reducción Operativa: De 60 min a 2 min por préstamo  |  0% Error en Core IBS"
    mp2.alignment = PP_ALIGN.CENTER
    mp2.font.bold = True
    mp2.font.size = Pt(10)
    mp2.font.color.rgb = ACCENT_GREEN


    # =========================================================================
    # SLIDE 3: AGENTE AUTO - EL RETO DE NEGOCIO EN FERIAS
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, CDA_LIGHT_BG)
    add_header(s3, "Agente para Feria de Autos: El Reto en el Stand Comercial", "PRODUCTO 01 — ASESOR VIRTUAL DE AUTO")

    p_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(1.4), Inches(5.8), Inches(5.4))
    p_box.fill.solid()
    p_box.fill.fore_color.rgb = SOFT_RED_BG
    p_box.line.color.rgb = ACCENT_RED
    p_box.line.width = Pt(1.5)

    p_hdr = s3.shapes.add_textbox(Inches(0.9), Inches(1.55), Inches(5.2), Inches(0.45))
    p_tf = p_hdr.text_frame
    p_p = p_tf.paragraphs[0]
    p_p.text = "La Fricción Operativa Actual en Ferias"
    p_p.font.size = Pt(15)
    p_p.font.bold = True
    p_p.font.color.rgb = ACCENT_RED

    pain_points = [
        ("Aglomeración en Horas Pico", "Durante ferias como Panamá Motor Show, decenas de personas se acercan al stand simultáneamente; los ejecutivos no dan abasto."),
        ("Pérdida de Prospectos Calificados", "Los clientes que esperan más de 10 minutos se marchan a stands de bancos competidores sin cotizar."),
        ("Consultas Repetitivas y Básicas", "El 70% del tiempo de los ejecutivos se consume respondiendo: '¿Cuánto tengo que pagar por este auto?' o '¿Califico con mi salario?'."),
        ("Leads Incompletos en Papel", "Anotaciones en volantes que luego se extravían o tardan días en registrarse en el sistema bancario.")
    ]

    p_content = s3.shapes.add_textbox(Inches(0.9), Inches(2.1), Inches(5.2), Inches(4.4))
    p_ctf = p_content.text_frame
    p_ctf.word_wrap = True
    for idx, (t, d) in enumerate(pain_points):
        pp = p_ctf.paragraphs[0] if idx == 0 else p_ctf.add_paragraph()
        pp.text = f"• {t}: "
        pp.font.bold = True
        pp.font.size = Pt(10.5)
        pp.font.color.rgb = ACCENT_RED
        if idx > 0: pp.space_before = Pt(8)
        run = pp.add_run()
        run.text = d
        run.font.bold = False
        run.font.size = Pt(10)
        run.font.color.rgb = TEXT_DARK

    s_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.4), Inches(5.9), Inches(5.4))
    s_box.fill.solid()
    s_box.fill.fore_color.rgb = SOFT_GREEN_BG
    s_box.line.color.rgb = ACCENT_GREEN
    s_box.line.width = Pt(1.5)

    s_hdr = s3.shapes.add_textbox(Inches(7.1), Inches(1.55), Inches(5.3), Inches(0.45))
    s_tf = s_hdr.text_frame
    s_p = s_tf.paragraphs[0]
    s_p.text = "La Propuesta de Valor del Asesor Virtual"
    s_p.font.size = Pt(15)
    s_p.font.bold = True
    s_p.font.color.rgb = ACCENT_GREEN

    sol_points = [
        ("Atención Simultánea e Ilimitada", "Los clientes interactúan desde tótems táctiles, tablets en el stand o escaneando un código QR en su celular."),
        ("Calificación Inteligente en 90 Segundos", "Filtra según la política de crédito CDA (edad 21-75, ingresos mínimos, estabilidad laboral) sin fricción."),
        ("Simulación Visual y Transparente", "Presenta al instante la letra quincenal y mensual estimada, ajustando plazos y abonos al presupuesto del usuario."),
        ("Cierre Asistido para el Ejecutivo", "El lead llega formalizado al CRM o correo del ejecutivo del stand con la cotización exacta para firmar la solicitud multiproducto.")
    ]

    s_content = s3.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.3), Inches(4.4))
    s_ctf = s_content.text_frame
    s_ctf.word_wrap = True
    for idx, (t, d) in enumerate(sol_points):
        sp = s_ctf.paragraphs[0] if idx == 0 else s_ctf.add_paragraph()
        sp.text = f"• {t}: "
        sp.font.bold = True
        sp.font.size = Pt(10.5)
        sp.font.color.rgb = ACCENT_GREEN
        if idx > 0: sp.space_before = Pt(8)
        run = sp.add_run()
        run.text = d
        run.font.bold = False
        run.font.size = Pt(10)
        run.font.color.rgb = TEXT_DARK


    # =========================================================================
    # SLIDE 4: AGENTE AUTO - DIAGRAMA DE FLUJO DE LA EXPERIENCIA
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, CDA_LIGHT_BG)
    add_header(s4, "Agente para Feria de Autos: Flujo de Interacción del Cliente", "DIAGRAMA DE EXPERIENCIA DE NEGOCIO")

    f_info = s4.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(12.133), Inches(0.45))
    f_tf = f_info.text_frame
    f_p = f_tf.paragraphs[0]
    f_p.text = "Flujo paso a paso diseñado para maximizar la conversión en stand, garantizando rigor de crédito en 4 etapas fluidas:"
    f_p.font.size = Pt(12)
    f_p.font.color.rgb = TEXT_DARK

    step_width = Inches(2.8)
    step_gap = Inches(0.28)
    step_top = Inches(1.9)
    step_h = Inches(4.15)
    start_x = Inches(0.6)

    steps_data = [
        ("PASO 01", "Bienvenida y Prospección", CDA_BLUE, [
            "Cliente escanea QR o toca pantalla.",
            "IA saluda cordialmente e indaga marca y modelo de interés.",
            "Pregunta si es auto nuevo o de segunda.",
            "Tono cercano, empático y 100% institucional."
        ]),
        ("PASO 02", "Filtro de Política CDA", ACCENT_AMBER, [
            "Verifica edad del solicitante (21 a 75 años al vencer el crédito).",
            "Consulta ingreso mensual aproximado.",
            "Valida tipo de empleo (empresa privada, gobierno o independiente).",
            "Filtra viabilidad antes de ilusionar al cliente."
        ]),
        ("PASO 03", "Simulación de Cuota", ACCENT_CYAN, [
            "Aplica parámetros oficiales de tasa y plazo CDA.",
            "Calcula cuota mensual y quincenal.",
            "Permite al cliente ajustar abono (ej. 10%, 15%, 20%) para ver cómo baja su letra.",
            "Calcula capacidad de pago en segundos."
        ]),
        ("PASO 04", "Captura y Cierre", ACCENT_GREEN, [
            "Captura Nombre, Cédula, Teléfono y Correo.",
            "Genera Ficha de Lead Calificado en PDF/JSON.",
            "Notifica en tiempo real al ejecutivo comercial del stand.",
            "Cliente recibe la proforma en su WhatsApp."
        ])
    ]

    for i, (badge, title, color, points) in enumerate(steps_data):
        bx = start_x + i * (step_width + step_gap)
        sc = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, bx, step_top, step_width, step_h)
        sc.fill.solid()
        sc.fill.fore_color.rgb = CARD_BG
        sc.line.color.rgb = color
        sc.line.width = Pt(1.5)

        sb = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, bx, step_top, step_width, Inches(0.45))
        sb.fill.solid()
        sb.fill.fore_color.rgb = color
        sb.line.color.rgb = color
        sbtf = sb.text_frame
        sbp = sbtf.paragraphs[0]
        sbp.text = badge
        sbp.font.bold = True
        sbp.font.size = Pt(11)
        sbp.font.color.rgb = WHITE
        sbp.alignment = PP_ALIGN.CENTER

        st_box = s4.shapes.add_textbox(bx + Inches(0.15), step_top + Inches(0.55), step_width - Inches(0.3), Inches(0.65))
        st_tf = st_box.text_frame
        st_tf.word_wrap = True
        stp = st_tf.paragraphs[0]
        stp.text = title
        stp.font.bold = True
        stp.font.size = Pt(11.5)
        stp.font.color.rgb = color

        sb_box = s4.shapes.add_textbox(bx + Inches(0.15), step_top + Inches(1.25), step_width - Inches(0.3), Inches(2.7))
        sb_tf = sb_box.text_frame
        sb_tf.word_wrap = True
        for p_idx, pt in enumerate(points):
            pp = sb_tf.paragraphs[0] if p_idx == 0 else sb_tf.add_paragraph()
            pp.text = f"• {pt}"
            pp.font.size = Pt(10)
            pp.font.color.rgb = TEXT_DARK
            if p_idx > 0: pp.space_before = Pt(6)

        if i < 3:
            arrow = s4.shapes.add_shape(MSO_SHAPE.CHEVRON, bx + step_width + Inches(0.06), step_top + Inches(1.8), Inches(0.18), Inches(0.5))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = ACCENT_CYAN
            arrow.line.fill.background()

    sum_pill = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(6.25), Inches(12.133), Inches(0.7))
    sum_pill.fill.solid()
    sum_pill.fill.fore_color.rgb = SOFT_GREEN_BG
    sum_pill.line.color.rgb = ACCENT_GREEN
    sp_tf = sum_pill.text_frame
    sp_tf.word_wrap = True
    sp_p = sp_tf.paragraphs[0]
    sp_p.text = "Impacto Operativo para el Banco: Reduce el tiempo de cotización de 20 minutos a 90 segundos. El ejecutivo del stand recibe un prospecto 100% calificado según política, eliminando clientes fuera de perfil y cerrando ventas en el acto."
    sp_p.font.size = Pt(10.5)
    sp_p.font.color.rgb = RGBColor(16, 120, 50)
    sp_p.font.bold = True


    # =========================================================================
    # SLIDE 5: AGENTE FORMALIZACIÓN - EL DESAFÍO EN PRÉSTAMOS PERSONALES
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, CDA_LIGHT_BG)
    add_header(s5, "Formalización de Préstamos: Cuellos de Botella Reales", "PRODUCTO 02 — FORMALIZACIÓN DE PRÉSTAMOS PERSONALES")

    f_desc = s5.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(12.133), Inches(0.55))
    f_tf = f_desc.text_frame
    f_tf.word_wrap = True
    fp = f_tf.paragraphs[0]
    fp.text = "Una vez el crédito es aprobado por el comité o ejecutivo, comienza la formalización para que el cliente firme y reciba su desembolso. Las sesiones de trabajo con Crédito (Ricardo Herrera) revelaron 3 stoppers críticos:"
    fp.font.size = Pt(12)
    fp.font.color.rgb = TEXT_DARK

    c_w = Inches(3.8)
    c_gap = Inches(0.36)
    c_top = Inches(1.95)
    c_h = Inches(4.95)

    pain_cards = [
        ("Stopper 01: Certificado CSS", ACCENT_RED, [
            ("Situación en Jubilados:", "Para firmar la orden de descuento, se requiere obligatoriamente el certificado físico de jubilación."),
            ("Demora de 7 a 20 Días:", "Este documento depende de la CSS y demora semanas. Si el analista avanza en Ultimus sin él, el expediente queda bloqueado."),
            ("Dolor Declarado:", "'Aunque tenga el préstamo aprobado, no puedo mover para que el cliente firme porque necesito ese número para llenar la orden' (Ricardo Herrera).")
        ], "Demora: 7 a 20 días hábiles en CSS"),
        ("Stopper 02: Transcripción Manual", ACCENT_AMBER, [
            ("10 a 15 Campos a Mano:", "El analista debe transcribir manualmente salarios, descuentos, deducciones y razón social desde PDFs no estandarizados."),
            ("Grilla Densa de Contraloría:", "Debe buscar 'con lupa' el número de Planilla (ej. 14) y Posición (ej. 101010) en talonarios diminutos."),
            ("Riesgo de Rechazo en IBS:", "Cualquier error tipográfico provoca el rechazo automático de los Web Services hacia el Core Bancario IBS en Ultimus.")
        ], "Riesgo: Errores tipográficos rechazan en IBS"),
        ("Stopper 03: Compra de Saldo", CDA_BLUE, [
            ("Papelería Legal Artesanal:", "Una gran parte de los préstamos cancela deudas en otros bancos (Banco General, BAC, Banistmo, financieras)."),
            ("Cartas de Promesa de Pago:", "Ultimus no redacta cartas a terceros bancos. El analista abre plantillas Word, busca números de cuenta, saldos y vigencias a mano."),
            ("Consumo de Tiempo Humano:", "Redactar pagarés, órdenes de descuento y promesas de pago toma entre 20 y 35 minutos por cliente.")
        ], "Carga: 20 a 35 min redactando en Word")
    ]

    for idx, (title, color, bullets, metric_text) in enumerate(pain_cards):
        cx = Inches(0.6) + idx * (c_w + c_gap)
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, c_top, c_w, c_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        chdr = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, c_top, c_w, Inches(0.52))
        chdr.fill.solid()
        chdr.fill.fore_color.rgb = color
        chdr.line.color.rgb = color
        ctf = chdr.text_frame
        cp = ctf.paragraphs[0]
        cp.text = title
        cp.font.bold = True
        cp.font.size = Pt(11)
        cp.font.color.rgb = WHITE
        cp.alignment = PP_ALIGN.CENTER

        cbody = s5.shapes.add_textbox(cx + Inches(0.15), c_top + Inches(0.6), c_w - Inches(0.3), Inches(3.6))
        cbtf = cbody.text_frame
        cbtf.word_wrap = True
        for b_idx, (b_title, b_desc) in enumerate(bullets):
            bp = cbtf.paragraphs[0] if b_idx == 0 else cbtf.add_paragraph()
            bp.text = f"{b_title} "
            bp.font.bold = True
            bp.font.size = Pt(10)
            bp.font.color.rgb = color
            if b_idx > 0: bp.space_before = Pt(6)
            run = bp.add_run()
            run.text = b_desc
            run.font.bold = False
            run.font.size = Pt(9.5)
            run.font.color.rgb = TEXT_DARK

        cmetric = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.15), c_top + Inches(4.35), c_w - Inches(0.3), Inches(0.45))
        cmetric.fill.solid()
        cmetric.fill.fore_color.rgb = SOFT_RED_BG if color == ACCENT_RED else (SOFT_AMBER_BG if color == ACCENT_AMBER else SOFT_BLUE_BG)
        cmetric.line.color.rgb = color
        cm_tf = cmetric.text_frame
        cmp = cm_tf.paragraphs[0]
        cmp.text = metric_text
        cmp.font.bold = True
        cmp.font.size = Pt(9)
        cmp.font.color.rgb = color
        cmp.alignment = PP_ALIGN.CENTER


    # =========================================================================
    # SLIDE 6: AGENTE FORMALIZACIÓN - FILOSOFÍA DESACOPLADA (CERO RIESGO)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, CDA_LIGHT_BG)
    add_header(s6, "Arquitectura Desacoplada: Cero Riesgo Tecnológico e Inmediatez", "PRODUCTO 02 — PARADIGMA TECNOLÓGICO")

    f_desc6 = s6.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(12.133), Inches(0.55))
    f_tf6 = f_desc6.text_frame
    f_tf6.word_wrap = True
    fp6 = f_tf6.paragraphs[0]
    fp6.text = "¿Cómo implementamos IA en formalización sin esperar meses por aprobaciones de seguridad, APIs de Ultimus ni accesos al Core IBS? Mediante el paradigma Sidecar Copilot (Asistente Desacoplado):"
    fp6.font.size = Pt(12)
    fp6.font.color.rgb = TEXT_DARK

    pillars = [
        ("Cero Acceso a Ultimus BPM", "No requiere licencias de desarrollo, RPA invasivos ni APIs propietarias de Ultimus. El sistema no toca el BPM directamente."),
        ("Cero Conexión al Core IBS", "Elimina cualquier riesgo de corrupción de datos transaccionales bancarios. El analista mantiene la custodia de la transacción final."),
        ("Cero VPN ni Permisos de Red", "Opera como una herramienta web ágil para el analista. No requiere apertura de puertos de firewall internos ni dependencias de Active Directory."),
        ("Control Humano (Human-in-the-Loop)", "La IA audita, extrae y redacta en segundos; el analista humano valida en pantalla y confirma el ingreso. Máxima seguridad y gobernanza.")
    ]

    pil_w = Inches(5.8)
    pil_h = Inches(2.05)
    pil_coords = [
        (Inches(0.6), Inches(1.95)),
        (Inches(6.8), Inches(1.95)),
        (Inches(0.6), Inches(4.25)),
        (Inches(6.8), Inches(4.25))
    ]

    for idx, (p_title, p_desc) in enumerate(pillars):
        px, py = pil_coords[idx]
        p_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pil_w, pil_h)
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = CARD_BG
        p_card.line.color.rgb = CDA_BLUE
        p_card.line.width = Pt(1.5)

        pp_hdr = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, py, pil_w, Inches(0.45))
        pp_hdr.fill.solid()
        pp_hdr.fill.fore_color.rgb = SOFT_BLUE_BG
        pp_hdr.line.color.rgb = CDA_BLUE
        pp_tf = pp_hdr.text_frame
        pp_p = pp_tf.paragraphs[0]
        pp_p.text = p_title
        pp_p.font.bold = True
        pp_p.font.size = Pt(11.5)
        pp_p.font.color.rgb = CDA_BLUE

        p_body = s6.shapes.add_textbox(px + Inches(0.2), py + Inches(0.55), pil_w - Inches(0.4), Inches(1.35))
        pb_tf = p_body.text_frame
        pb_tf.word_wrap = True
        pbp = pb_tf.paragraphs[0]
        pbp.text = p_desc
        pbp.font.size = Pt(10.5)
        pbp.font.color.rgb = TEXT_DARK

    takeaway = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.6), Inches(6.45), Inches(12.133), Inches(0.55))
    takeaway.fill.solid()
    takeaway.fill.fore_color.rgb = SOFT_GREEN_BG
    takeaway.line.color.rgb = ACCENT_GREEN
    t_tf = takeaway.text_frame
    tp = t_tf.paragraphs[0]
    tp.text = "Conclusión para Negocio y Ciberseguridad: Se puede desplegar y probar en días sin riesgo operativo ni auditorías de red complejas."
    tp.font.bold = True
    tp.font.size = Pt(10.5)
    tp.font.color.rgb = RGBColor(16, 120, 50)
    tp.alignment = PP_ALIGN.CENTER


    # =========================================================================
    # SLIDE 7: AGENTE FORMALIZACIÓN - DIAGRAMA DE LOS 3 CASOS DE USO
    # (AQUÍ ESTÁN LOS ÚNICOS EMOJIS DEL DOCUMENTO: 🟢, 🟡, 🔴)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, CDA_LIGHT_BG)
    add_header(s7, "Los 3 Casos de Uso del Copiloto de Formalización", "DIAGRAMA DE ARQUITECTURA FUNCIONAL")

    intro7 = s7.shapes.add_textbox(Inches(0.6), Inches(1.25), Inches(12.133), Inches(0.45))
    i_tf7 = intro7.text_frame
    ip7 = i_tf7.paragraphs[0]
    ip7.text = "El copiloto acompaña al analista en tres fases continuas, resolviendo cada cuello de botella de manera precisa y medible:"
    ip7.font.size = Pt(11.5)
    ip7.font.color.rgb = TEXT_DARK

    cu_w = Inches(3.8)
    cu_gap = Inches(0.36)
    cu_top = Inches(1.78)
    cu_h = Inches(5.2)

    # Note: ONLY 🟢, 🟡, 🔴 are used here, as explicitly requested!
    cu_data = [
        ("CASO 1: SEMÁFORO", "Auditoría Inteligente", ACCENT_GREEN, [
            ("Insumo:", "Expediente digital del cliente (PDFs de cédula, carta y talonario)."),
            ("Qué hace la IA:", "Inspecciona identidad cruzada, vigencias (<30 días) y calendarios (no descuento en diciembre)."),
            ("Dictamen Semafórico:", "Clasifica en 3 estados normativos:"),
            ("• 🟢 Verde (Conforme):", "Expediente consistente y vigente; listo para formalizar."),
            ("• 🟡 Amarillo (Alerta):", "Vencimiento cercano (<48h); firma prioritaria."),
            ("• 🔴 Rojo (Bloqueo):", "Falta certificado CSS de jubilado o cédula inconsistente; devolución inmediata a sucursal."),
            ("Entrega:", "Ficha de Certificación de Calidad CDA.")
        ], "Semáforo: 🟢 Verde  |  🟡 Amarillo  |  🔴 Rojo"),
        ("CASO 2: SMART CLIPBOARD", "Extracción Estructurada", ACCENT_CYAN, [
            ("Insumo:", "Carta de trabajo y talonario comprobante."),
            ("Qué hace la IA:", "Lee tablas complejas y ubica con precisión espacial 'PLANILLA' y 'POSICIÓN' de Contraloría."),
            ("Reconciliación:", "Verifica matemáticamente que Salario Bruto - Descuentos = Salario Neto."),
            ("Interacción Humana:", "Panel con botón 'Copiar' (1 clic). El analista copia y pega (Ctrl+V) en Ultimus BPM en pantalla dividida."),
            ("Impacto:", "De 10 min a 40 segundos, con 0% error.")
        ], "Smart Clipboard: De 10 min a 40 seg | Cero error"),
        ("CASO 3: ENSAMBLADOR", "Confección Contractual", CDA_BLUE, [
            ("Insumo:", "Cartas de saldo externas (BG, BAC, Banistmo) y condiciones aprobadas CDA."),
            ("Qué hace la IA:", "Extrae banco acreedor, cuenta/tarjeta a pagar, saldo exacto y fecha límite de vigencia."),
            ("Templating Legal:", "Inyecta los datos sobre plantillas oficiales .docx de Caja de Ahorros."),
            ("Entrega:", "Paquete Contractual Completo (.docx y .pdf) listo para firma (Promesas de pago, pagaré notarial, órdenes de descuento).")
        ], "Contratos: De 30 min a 15 seg en .docx")
    ]

    for idx, (badge, title, color, pts, metric_lbl) in enumerate(cu_data):
        cx = Inches(0.6) + idx * (cu_w + cu_gap)
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, cu_top, cu_w, cu_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = color
        card.line.width = Pt(1.5)

        b_hdr = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cu_top, cu_w, Inches(0.55))
        b_hdr.fill.solid()
        b_hdr.fill.fore_color.rgb = color
        b_hdr.line.color.rgb = color
        btf = b_hdr.text_frame
        bp1 = btf.paragraphs[0]
        bp1.text = badge
        bp1.font.bold = True
        bp1.font.size = Pt(10.5)
        bp1.font.color.rgb = WHITE
        bp1.alignment = PP_ALIGN.CENTER
        bp2 = btf.add_paragraph()
        bp2.text = title
        bp2.font.size = Pt(9)
        bp2.font.color.rgb = WHITE
        bp2.alignment = PP_ALIGN.CENTER

        b_body = s7.shapes.add_textbox(cx + Inches(0.15), cu_top + Inches(0.62), cu_w - Inches(0.3), Inches(3.95))
        bbtf = b_body.text_frame
        bbtf.word_wrap = True
        for p_idx, (pt_t, pt_d) in enumerate(pts):
            pp = bbtf.paragraphs[0] if p_idx == 0 else bbtf.add_paragraph()
            pp.text = f"{pt_t} "
            pp.font.bold = True
            pp.font.size = Pt(9)
            pp.font.color.rgb = color if "•" not in pt_t else TEXT_DARK
            if p_idx > 0: pp.space_before = Pt(4)
            run = pp.add_run()
            run.text = pt_d
            run.font.bold = False
            run.font.size = Pt(8.5)
            run.font.color.rgb = TEXT_DARK

        bmetric = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx + Inches(0.15), cu_top + Inches(4.62), cu_w - Inches(0.3), Inches(0.45))
        bmetric.fill.solid()
        bmetric.fill.fore_color.rgb = SOFT_GREEN_BG if color == ACCENT_GREEN else SOFT_BLUE_BG
        bmetric.line.color.rgb = color
        bm_tf = bmetric.text_frame
        bmp = bm_tf.paragraphs[0]
        bmp.text = metric_lbl
        bmp.font.bold = True
        bmp.font.size = Pt(8.5)
        bmp.font.color.rgb = color
        bmp.alignment = PP_ALIGN.CENTER

        if idx < 2:
            arr = s7.shapes.add_shape(MSO_SHAPE.CHEVRON, cx + cu_w + Inches(0.08), cu_top + Inches(2.2), Inches(0.2), Inches(0.55))
            arr.fill.solid()
            arr.fill.fore_color.rgb = ACCENT_CYAN
            arr.line.fill.background()


    # =========================================================================
    # SLIDE 8: TABLA COMPARATIVA - ANTES VS DESPUÉS (MÉTRICAS DE NEGOCIO)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, CDA_LIGHT_BG)
    add_header(s8, "Impacto Cuantitativo: Proceso Tradicional vs. Asistente IA", "MÉTRICAS DE EFICIENCIA OPERATIVA")

    i_box8 = s8.shapes.add_textbox(Inches(0.6), Inches(1.25), Inches(12.133), Inches(0.4))
    i_tf8 = i_box8.text_frame
    ip8 = i_tf8.paragraphs[0]
    ip8.text = "Comparativa directa de tiempos y calidad operativa en la formalización de préstamos personales:"
    ip8.font.size = Pt(11.5)
    ip8.font.color.rgb = TEXT_DARK

    rows = 5
    cols = 4
    left = Inches(0.6)
    top = Inches(1.72)
    width = Inches(12.133)
    height = Inches(4.9)

    table_shape = s8.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table

    table.columns[0].width = Inches(2.7)
    table.columns[1].width = Inches(3.3)
    table.columns[2].width = Inches(3.3)
    table.columns[3].width = Inches(2.833)

    table_data = [
        ("Fase Operativa", "Proceso Tradicional (Manual)", "Con Asistente Inteligente (IA)", "Ganancia Neta para el Negocio"),
        ("1. Auditoría del Expediente", "20 min por cliente.\nRevisión manual de cada PDF; expedientes trabados semanas por falta de soporte de CSS.", "5 a 10 segundos.\nSemáforo automático; detección preventiva de jubilados sin soporte.", "Ahorro >95% en revisión.\nCero expedientes estancados."),
        ("2. Carga de Datos en Ultimus", "10 min tipeando a mano.\nBúsqueda con lupa de Planilla y Posición; errores tipográficos hacia Core IBS.", "30 a 50 segundos.\nSmart Clipboard con copiado en 1 clic y datos normalizados.", "Reducción del 90% en digitación.\nCero rechazos en Core IBS."),
        ("3. Confección de Compra de Saldo", "20 a 35 min redactando.\nRedacción manual de cartas a otros bancos, pagarés y órdenes de descuento.", "15 segundos.\nGeneración instantánea del paquete (.docx y .pdf) listo para firma.", "Ahorro de 30 min por cliente.\nExactitud contable y legal."),
        ("RESUMEN TOTAL POR EXPEDIENTE", "~60 minutos por crédito.\nRiesgo de error humano y demora en firma.", "Menos de 2 minutos.\nAnalista enfocado en control y servicio al cliente.", "Aceleración de 30x.\nMayor colocación de cartera.")
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, cell_value in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = cell_value
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if r_idx == 0 or c_idx == 3 else PP_ALIGN.LEFT
            
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = CDA_BLUE
                p.font.bold = True
                p.font.size = Pt(10.5)
                p.font.color.rgb = WHITE
            elif r_idx == 4:
                cell.fill.solid()
                cell.fill.fore_color.rgb = SOFT_GREEN_BG
                p.font.bold = True
                p.font.size = Pt(9.5)
                p.font.color.rgb = ACCENT_GREEN
            else:
                cell.fill.solid()
                if c_idx == 1:
                    cell.fill.fore_color.rgb = SOFT_RED_BG
                    p.font.color.rgb = RGBColor(170, 30, 30)
                elif c_idx == 2:
                    cell.fill.fore_color.rgb = SOFT_GREEN_BG
                    p.font.color.rgb = RGBColor(15, 115, 45)
                else:
                    cell.fill.fore_color.rgb = WHITE
                    p.font.color.rgb = TEXT_DARK
                p.font.size = Pt(9)


    # =========================================================================
    # SLIDE 9: CONCLUSIÓN Y PRÓXIMOS PASOS RECOMENDADOS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, CDA_LIGHT_BG)
    add_header(s9, "Conclusión y Ruta de Implementación para el Negocio", "HOJA DE RUTA ESTRATÉGICA")

    c_box9 = s9.shapes.add_textbox(Inches(0.6), Inches(1.3), Inches(12.133), Inches(0.45))
    c_tf9 = c_box9.text_frame
    cp9 = c_tf9.paragraphs[0]
    cp9.text = "Plan de acción ágil para validar y desplegar el valor de ambos agentes en Caja de Ahorros:"
    cp9.font.size = Pt(12)
    cp9.font.color.rgb = TEXT_DARK

    steps_roadmap = [
        ("Hito 1: Demostración Interactiva", [
            "Presentar el prototipo funcional del Asesor de Autos (Chainlit/Streamlit) a Ventas y Mercadeo.",
            "Validar parámetros de tasas de feria y marcas destacadas.",
            "Duración estimada: Sesión ejecutiva de 45 minutos."
        ], ACCENT_CYAN),
        ("Hito 2: Piloto de Formalización", [
            "Probar el Smart Clipboard y Semáforo con 3 analistas de formalización durante 2 semanas.",
            "Medir reducción real de tiempos de transcripción.",
            "Ajustar plantillas de cartas de compra de saldo oficiales."
        ], CDA_BLUE),
        ("Hito 3: Despliegue en Stand de Feria", [
            "Instalar el Asesor Virtual en quioscos/tablets en la siguiente feria automotriz.",
            "Capturar leads en vivo y derivar a ejecutivos del stand.",
            "Medir clientes atendidos vs. ferias anteriores."
        ], ACCENT_AMBER),
        ("Hito 4: Medición de ROI y Escalamiento", [
            "Presentar informe de resultados a la Vicepresidencia con métricas de tiempos y conversión.",
            "Definir roadmap para extender a préstamos hipotecarios.",
            "Consolidar la Célula de Innovación como motor ágil del banco."
        ], ACCENT_GREEN)
    ]

    r_w = Inches(5.8)
    r_h = Inches(2.25)
    r_coords = [
        (Inches(0.6), Inches(1.9)),
        (Inches(6.8), Inches(1.9)),
        (Inches(0.6), Inches(4.45)),
        (Inches(6.8), Inches(4.45))
    ]

    for idx, (title, bullets, color) in enumerate(steps_roadmap):
        rx, ry = r_coords[idx]
        rcard = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, rx, ry, r_w, r_h)
        rcard.fill.solid()
        rcard.fill.fore_color.rgb = CARD_BG
        rcard.line.color.rgb = color
        rcard.line.width = Pt(1.5)

        rhdr = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, rx, ry, r_w, Inches(0.45))
        rhdr.fill.solid()
        rhdr.fill.fore_color.rgb = color
        rhdr.line.color.rgb = color
        rtf = rhdr.text_frame
        rp = rtf.paragraphs[0]
        rp.text = title
        rp.font.bold = True
        rp.font.size = Pt(11.5)
        rp.font.color.rgb = WHITE

        rbody = s9.shapes.add_textbox(rx + Inches(0.2), ry + Inches(0.55), r_w - Inches(0.4), Inches(1.6))
        rbtf = rbody.text_frame
        rbtf.word_wrap = True
        for b_idx, b_text in enumerate(bullets):
            bp = rbtf.paragraphs[0] if b_idx == 0 else rbtf.add_paragraph()
            bp.text = f"• {b_text}"
            bp.font.size = Pt(9.5)
            bp.font.color.rgb = TEXT_DARK
            if b_idx > 0: bp.space_before = Pt(4)


    # =========================================================================
    # SLIDE 10: CIERRE INSTITUCIONAL
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, CDA_BLUE)

    dec_card10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.9), Inches(11.333), Inches(5.7))
    dec_card10.fill.solid()
    dec_card10.fill.fore_color.rgb = CDA_BLUE
    dec_card10.line.color.rgb = ACCENT_CYAN
    dec_card10.line.width = Pt(2.0)

    if os.path.exists(logo_path):
        s10.shapes.add_picture(logo_path, Inches(4.7), Inches(1.5), width=Inches(3.9))

    thx_box = s10.shapes.add_textbox(Inches(1.5), Inches(3.2), Inches(10.333), Inches(1.5))
    thx_tf = thx_box.text_frame
    thx_tf.word_wrap = True
    tp1 = thx_tf.paragraphs[0]
    tp1.text = "Transformando la Experiencia del Cliente y la Eficiencia Operativa con Inteligencia Artificial"
    tp1.alignment = PP_ALIGN.CENTER
    tp1.font.size = Pt(22)
    tp1.font.bold = True
    tp1.font.color.rgb = WHITE

    tp2 = thx_tf.add_paragraph()
    tp2.text = "Caja de Ahorros de Panamá  •  Célula de Innovación (StraTech / CDA)"
    tp2.alignment = PP_ALIGN.CENTER
    tp2.font.size = Pt(14)
    tp2.font.color.rgb = ACCENT_CYAN
    tp2.space_before = Pt(12)

    tp3 = thx_tf.add_paragraph()
    tp3.text = "Líder Técnico: Rodolfo Blasser  |  Contacto y Demostraciones Técnicas Disponibles"
    tp3.alignment = PP_ALIGN.CENTER
    tp3.font.size = Pt(12)
    tp3.font.color.rgb = RGBColor(190, 220, 255)
    tp3.space_before = Pt(8)

    output_filename = "Presentacion_Celulas_Innovacion_CDA.pptx"
    prs.save(output_filename)
    print(f"Presentation successfully updated and saved to: {os.path.abspath(output_filename)}")

if __name__ == "__main__":
    create_deck()
