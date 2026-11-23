"""
06_build_presentation.py
------------------------
Genera la presentacion final de 8 minutos (11 diapositivas widescreen 16:9)
en PowerPoint (.pptx) y la exporta a PDF mediante PowerPoint COM para
verificacion visual.
"""

from __future__ import annotations

from pathlib import Path
import win32com.client
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

BASE_DIR = Path(__file__).resolve().parent.parent
PRES_DIR = BASE_DIR / "presentacion"
FIG_DIR = PRES_DIR / "figures"
PPTX_PATH = PRES_DIR / "Presentacion_Final_Grupo2_Aysen_MP25.pptx"
PDF_PATH = PRES_DIR / "Presentacion_Final_Grupo2_Aysen_MP25.pdf"

# Paleta sobria academica
NAVY = RGBColor(15, 41, 66)
BLUE = RGBColor(15, 76, 129)
TEAL = RGBColor(42, 157, 143)
CRIMSON = RGBColor(193, 18, 31)
AMBER = RGBColor(217, 119, 6)
SLATE = RGBColor(51, 65, 85)
MUTED = RGBColor(100, 116, 139)
BG = RGBColor(248, 250, 252)
WHITE = RGBColor(255, 255, 255)
BORDER = RGBColor(226, 232, 240)
SOFT_BLUE = RGBColor(239, 246, 255)
SOFT_AMBER = RGBColor(254, 243, 199)
SOFT_RED = RGBColor(254, 242, 242)
SOFT_TEAL = RGBColor(240, 253, 250)


def set_slide_bg(slide, color: RGBColor) -> None:
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_header(slide, section_tag: str, title: str, slide_num: int, total_slides: int = 11) -> None:
    set_slide_bg(slide, BG)
    # Franja superior fina
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.10))
    bar.fill.solid()
    bar.fill.fore_color.rgb = BLUE
    bar.line.fill.background()

    # Etiqueta de seccion
    tb_tag = slide.shapes.add_textbox(Inches(0.55), Inches(0.22), Inches(6.0), Inches(0.28))
    p = tb_tag.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = section_tag.upper()
    r.font.name = "Segoe UI"
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = TEAL

    # Titulo principal
    tb_title = slide.shapes.add_textbox(Inches(0.55), Inches(0.46), Inches(12.2), Inches(0.55))
    p2 = tb_title.text_frame.paragraphs[0]
    r2 = p2.add_run()
    r2.text = title
    r2.font.name = "Segoe UI"
    r2.font.size = Pt(24)
    r2.font.bold = True
    r2.font.color.rgb = NAVY

    # Linea divisoria
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(1.06), Inches(12.23), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER
    line.line.fill.background()

    # Pie de pagina
    tb_ft = slide.shapes.add_textbox(Inches(0.55), Inches(7.12), Inches(9.5), Inches(0.28))
    pf = tb_ft.text_frame.paragraphs[0]
    rf = pf.add_run()
    rf.text = "Grupo N° 2 | MP2,5 y Clima en la Región de Aysén (SINCA 2013–2026) | EIN092B Visualización — USM"
    rf.font.name = "Segoe UI"
    rf.font.size = Pt(9.5)
    rf.font.color.rgb = MUTED

    tb_num = slide.shapes.add_textbox(Inches(11.6), Inches(7.12), Inches(1.18), Inches(0.28))
    pn = tb_num.text_frame.paragraphs[0]
    pn.alignment = PP_ALIGN.RIGHT
    rn = pn.add_run()
    rn.text = f"{slide_num} / {total_slides}"
    rn.font.name = "Segoe UI"
    rn.font.size = Pt(9.5)
    rn.font.bold = True
    rn.font.color.rgb = BLUE


def add_card(slide, left: float, top: float, width: float, height: float, fill_color: RGBColor = WHITE, accent: RGBColor | None = None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.adjustments[0] = 0.04
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.color.rgb = BORDER
    shape.line.width = Pt(1.0)
    if accent is not None:
        acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top + 0.08), Inches(0.08), Inches(height - 0.16))
        acc.fill.solid()
        acc.fill.fore_color.rgb = accent
        acc.line.fill.background()
    return shape


def add_bullets(slide, left: float, top: float, width: float, height: float, items: list[tuple[str, str]], font_size: float = 13.5, space_after: float = 8.0) -> None:
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for idx, (lead, body) in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.15
        r_bul = p.add_run()
        r_bul.text = "▪ "
        r_bul.font.name = "Segoe UI"
        r_bul.font.size = Pt(font_size)
        r_bul.font.bold = True
        r_bul.font.color.rgb = BLUE
        if lead:
            r1 = p.add_run()
            r1.text = lead + " "
            r1.font.name = "Segoe UI"
            r1.font.size = Pt(font_size)
            r1.font.bold = True
            r1.font.color.rgb = NAVY
        r2 = p.add_run()
        r2.text = body
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(font_size)
        r2.font.color.rgb = SLATE


def add_kpi_box(slide, left: float, top: float, width: float, height: float, label: str, val: str, sub: str, accent: RGBColor) -> None:
    add_card(slide, left, top, width, height, WHITE, accent)
    tb = slide.shapes.add_textbox(Inches(left + 0.18), Inches(top + 0.10), Inches(width - 0.28), Inches(height - 0.18))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    r1 = p1.add_run()
    r1.text = label.upper()
    r1.font.name = "Segoe UI"
    r1.font.size = Pt(9.5)
    r1.font.bold = True
    r1.font.color.rgb = MUTED

    p2 = tf.add_paragraph()
    p2.space_before = Pt(2)
    r2 = p2.add_run()
    r2.text = val
    r2.font.name = "Segoe UI"
    r2.font.size = Pt(22)
    r2.font.bold = True
    r2.font.color.rgb = accent

    p3 = tf.add_paragraph()
    p3.space_before = Pt(2)
    r3 = p3.add_run()
    r3.text = sub
    r3.font.name = "Segoe UI"
    r3.font.size = Pt(10.5)
    r3.font.color.rgb = SLATE


def add_notes(slide, text: str) -> None:
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = text


def build_presentation() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ---------------- SLIDE 1: PORTADA ----------------
    s1 = prs.slides.add_slide(blank)
    set_slide_bg(s1, NAVY)
    # Banda lateral decorativa
    band = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.32), Inches(7.5))
    band.fill.solid()
    band.fill.fore_color.rgb = TEAL
    band.line.fill.background()

    accent_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.95), Inches(1.45), Inches(1.8), Inches(0.08))
    accent_line.fill.solid()
    accent_line.fill.fore_color.rgb = AMBER
    accent_line.line.fill.background()

    tb = s1.shapes.add_textbox(Inches(0.95), Inches(1.75), Inches(11.4), Inches(2.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = "Caracterización visual y temporal de episodios de MP2,5 y clima en la Región de Aysén"
    r.font.name = "Segoe UI"
    r.font.size = Pt(36)
    r.font.bold = True
    r.font.color.rgb = WHITE

    p_sub = tf.add_paragraph()
    p_sub.space_before = Pt(14)
    rs = p_sub.add_run()
    rs.text = "Series de tiempo, regímenes meteorológicos (PCA/K-Means) y arquitectura Python → Power BI (SINCA 2013–2026)"
    rs.font.name = "Segoe UI"
    rs.font.size = Pt(18)
    rs.font.color.rgb = RGBColor(186, 230, 253)

    tb_meta = s1.shapes.add_textbox(Inches(0.95), Inches(4.75), Inches(11.4), Inches(2.1))
    tfm = tb_meta.text_frame
    tfm.word_wrap = True
    for idx, (k, v) in enumerate([
        ("Integrantes (Grupo N° 2):", "Maximiliano del Río Lincoñir (mdelrio@usm.cl)  |  Patricio Aylwin Retamal (paylwin@usm.cl)"),
        ("Asignatura y Profesor:", "EIN092B Visualización — Ingeniería en Informática, UTFSM  |  Prof. Jorge Portilla"),
        ("Fecha y Repositorio:", "28 de noviembre de 2026  |  github.com/MaksiiDR/aysen-mp25-visualizacion"),
    ]):
        pm = tfm.paragraphs[0] if idx == 0 else tfm.add_paragraph()
        pm.space_after = Pt(8)
        rk = pm.add_run()
        rk.text = k + " "
        rk.font.name = "Segoe UI"
        rk.font.size = Pt(13.5)
        rk.font.bold = True
        rk.font.color.rgb = RGBColor(148, 163, 184)
        rv = pm.add_run()
        rv.text = v
        rv.font.name = "Segoe UI"
        rv.font.size = Pt(13.5)
        rv.font.color.rgb = WHITE
    add_notes(s1, "[0:00–0:25 | 25s] Presentar título, integrantes (Grupo 2) y el alcance del proyecto: 13 años de datos SINCA en la Región de Aysén.")

    # ---------------- SLIDE 2: PROBLEMA Y OBJETIVOS ----------------
    s2 = prs.slides.add_slide(blank)
    add_header(s2, "1. Contexto y Problemática", "MP2,5 en Aysén: problema de salud pública y brecha analítica", 2)

    add_card(s2, 0.55, 1.28, 5.95, 5.55, WHITE, CRIMSON)
    tb2a = s2.shapes.add_textbox(Inches(0.82), Inches(1.42), Inches(5.45), Inches(0.4))
    p = tb2a.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Problemática y brecha de visualización"
    r.font.name = "Segoe UI"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = CRIMSON
    add_bullets(s2, 0.82, 1.92, 5.45, 4.7, [
        ("Zona saturada:", "Coyhaique supera reiteradamente la norma DS 12 (50 µg/m³ en 24 h) por calefacción residencial a leña entre abril y septiembre [1]–[4]."),
        ("Escala multivariada:", "Más de 115.000 registros horarios por variable en Coyhaique II, imposibles de diagnosticar en tablas estáticas."),
        ("Brecha en SINCA:", "El portal descarga series aisladas sin comparar estaciones, separar tendencias STL ni vincular episodios con la meteorología."),
        ("Pregunta de investigación:", "¿Cómo han evolucionado los episodios de MP2,5 en Aysén (2013–2026) y qué condiciones climáticas se asocian a ellos?"),
    ], font_size=13.5, space_after=12)

    add_card(s2, 6.80, 1.28, 5.98, 5.55, WHITE, BLUE)
    tb2b = s2.shapes.add_textbox(Inches(7.08), Inches(1.42), Inches(5.45), Inches(0.4))
    p = tb2b.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Objetivo general y objetivos específicos"
    r.font.name = "Segoe UI"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = BLUE

    add_card(s2, 7.05, 1.92, 5.45, 1.35, SOFT_BLUE)
    tb_og = s2.shapes.add_textbox(Inches(7.22), Inches(2.02), Inches(5.12), Inches(1.18))
    tf_og = tb_og.text_frame
    tf_og.word_wrap = True
    pog = tf_og.paragraphs[0]
    r1 = pog.add_run()
    r1.text = "Objetivo general: "
    r1.font.name = "Segoe UI"
    r1.font.size = Pt(13)
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r2 = pog.add_run()
    r2.text = "Diseñar y evaluar visualizaciones y modelos de series de tiempo que caractericen la evolución y regímenes climáticos del MP2,5 en Coyhaique, Puerto Aysén y Cochrane (2013–2026)."
    r2.font.name = "Segoe UI"
    r2.font.size = Pt(12.8)
    r2.font.color.rgb = SLATE

    add_bullets(s2, 7.08, 3.48, 5.45, 3.15, [
        ("OE1 — Patrones:", "Describir ciclos diarios, estacionales y sincronía entre las cuatro estaciones regionales."),
        ("OE2 — Tendencias:", "Cuantificar tendencias interanuales y días sobre norma controlando vacíos y el cierre parcial de 2026."),
        ("OE3 — Clima y regímenes:", "Relacionar episodios con temperatura, viento, humedad y presión mediante CCF, PCA y clustering."),
    ], font_size=13.5, space_after=12)
    add_notes(s2, "[0:25–1:05 | 40s] Contextualizar el problema sanitario en Aysén, la brecha de SINCA, la pregunta y los tres objetivos específicos.")

    # ---------------- SLIDE 3: RETROALIMENTACION PRESENTACION 1 ----------------
    s3 = prs.slides.add_slide(blank)
    add_header(s3, "2. Ajustes de Presentación 1", "Cómo incorporamos las tres observaciones de la retroalimentación", 3)

    cards = [
        (
            "Obs. 1: Enfoque en series de tiempo + Power BI",
            "\"El estudio se basa en identificar patrones más que en predicción: explorar series de tiempo y migrar visualización final a Power BI.\"",
            [
                ("Series de tiempo:", "Descomposición STL robusta, Mann–Kendall + Sen, ACF/PACF y correlación cruzada (CCF)."),
                ("Flujo Python → Power BI:", "Análisis, modelos y prototipo interactivo en Python; exportación de esquema estrella (8 tablas) + medidas DAX para Power BI."),
                ("Clasificación solo explicativa:", "Validación temporal (TimeSeriesSplit) para cuantificar cuánto explica el clima, sin forzar pronóstico operativo."),
            ],
            BLUE,
            SOFT_BLUE,
        ),
        (
            "Obs. 2: Manejo de faltantes y año incompleto 2026",
            "\"Falta manejo en cuanto a datos faltantes o incompletos (año presente).\"",
            [
                ("Auditoría de 25 CSV:", "Trazabilidad de registros validados, preliminares y no validados; exclusión de NO, NOx y NO₂ (>70% vacíos)."),
                ("Regla DS 12 estricta:", "Promedio 24 h solo con ≥18 h válidas (75%); sin imputación ciega de huecos largos."),
                ("Año 2026 (corte 23 oct):", "Marcado como incompleto; se comparan años completos (2014–2025), ventana YTD (ene–23 oct) e invierno completo (100% en 2026)."),
            ],
            AMBER,
            SOFT_AMBER,
        ),
        (
            "Obs. 3: Verificación de rosa de vientos",
            "\"La rosa de los vientos necesita dirección de corrientes; asegurarse de que el dataset posea esos datos.\"",
            [
                ("Hallazgo de auditoría:", "SINCA NO entrega dirección horaria del viento en ninguna estación; solo provee tablas históricas agregadas de 24 sectores de 15° (suma 100%)."),
                ("Cobertura verificada:", "Disponible en Coyhaique II, Coyhaique y Vialidad; ausente en Cochrane."),
                ("Decisión visual:", "Rosa acotada al régimen climatológico histórico; análisis de episodios basado en velocidad horaria/diaria del viento."),
            ],
            TEAL,
            SOFT_TEAL,
        ),
    ]
    for i, (head, quote, pts, acc, qbg) in enumerate(cards):
        left = 0.55 + i * 4.18
        add_card(s3, left, 1.28, 3.92, 5.55, WHITE, acc)
        tb_h = s3.shapes.add_textbox(Inches(left + 0.18), Inches(1.42), Inches(3.58), Inches(0.62))
        tfh = tb_h.text_frame
        tfh.word_wrap = True
        ph = tfh.paragraphs[0]
        rh = ph.add_run()
        rh.text = head
        rh.font.name = "Segoe UI"
        rh.font.size = Pt(14)
        rh.font.bold = True
        rh.font.color.rgb = acc

        add_card(s3, left + 0.16, 2.08, 3.60, 1.12, qbg)
        tb_q = s3.shapes.add_textbox(Inches(left + 0.24), Inches(2.14), Inches(3.44), Inches(1.02))
        tfq = tb_q.text_frame
        tfq.word_wrap = True
        pq = tfq.paragraphs[0]
        rq = pq.add_run()
        rq.text = quote
        rq.font.name = "Segoe UI"
        rq.font.size = Pt(10.5)
        rq.font.italic = True
        rq.font.color.rgb = SLATE

        add_bullets(s3, left + 0.16, 3.35, 3.60, 3.35, pts, font_size=11.5, space_after=8)
    add_notes(s3, "[1:05–1:50 | 45s] Recalcar explícitamente que atendimos las tres observaciones de la Presentación 1: series de tiempo + Power BI, control de 2026 incompleto y verificación real de la rosa de vientos.")

    # ---------------- SLIDE 4: AUDITORIA DE DATOS ----------------
    s4 = prs.slides.add_slide(blank)
    add_header(s4, "3. Auditoría de Datos SINCA", "Cobertura histórica, vacíos y control del corte parcial 2026", 4)

    add_kpi_box(s4, 0.55, 1.25, 2.90, 1.22, "Series analizadas", "25 CSV", "22 horarias + 3 rosas (4 estaciones)", BLUE)
    add_kpi_box(s4, 3.65, 1.25, 2.90, 1.22, "Coyhaique II (MP2,5)", "98,9%", "115.200 horas | 4.761 días válidos", TEAL)
    add_kpi_box(s4, 6.75, 1.25, 2.90, 1.22, "Corte año 2026", "23 oct", "80,8% año | 100% invierno Abr–Sep", AMBER)
    add_kpi_box(s4, 9.85, 1.25, 2.93, 1.22, "Alerta Cochrane", "78,6%", "2021–23 no validado | 2024–25 completo", CRIMSON)

    add_card(s4, 0.55, 2.66, 8.35, 4.22, WHITE)
    s4.shapes.add_picture(str(FIG_DIR / "slide_completeness_audit.png"), Inches(0.68), Inches(2.78), width=Inches(8.10))

    add_card(s4, 9.10, 2.66, 3.68, 4.22, WHITE, BLUE)
    tb4 = s4.shapes.add_textbox(Inches(9.32), Inches(2.80), Inches(3.28), Inches(0.4))
    p = tb4.text_frame.paragraphs[0]
    r = p.add_run()
    r.text = "Decisiones de calidad"
    r.font.name = "Segoe UI"
    r.font.size = Pt(14.5)
    r.font.bold = True
    r.font.color.rgb = NAVY
    add_bullets(s4, 9.32, 3.28, 3.30, 3.45, [
        ("Exclusión justificada:", "NO (9,2%), NOx (10,0%) y NO₂ (30,0%) descartados del análisis multivariado."),
        ("Ventana YTD (ene–23 oct):", "Contiene el 99,7% de los episodios históricos de Coyhaique II, habilitando comparar 2026 sin sesgo."),
        ("Transparencia SINCA:", "16,6% de días 2026 en Coyhaique II y 31,9% en Cochrane incluyen registros preliminares."),
    ], font_size=11.8, space_after=10)
    add_notes(s4, "[1:50–2:30 | 40s] Mostrar el mapa de completitud anual. Destacar por qué 2026 tiene 100% de cobertura invernal y por qué Cochrane 2021-2023 se marca como incompleto/no validado.")

    # ---------------- SLIDE 5: METODOLOGIA Y EVALUACION OBJETIVA ----------------
    s5 = prs.slides.add_slide(blank)
    add_header(s5, "4. Metodología y Selección Objetiva", "Pipeline analítico y matriz cuantitativa de selección visual", 5)

    # Flujo horizontal 4 cajas
    steps = [
        ("1. Ingesta y Auditoría", "25 CSV SINCA, regla DS 12 (≥18 h), filtros físicos, YTD 2026", BLUE),
        ("2. Series de Tiempo", "STL robusto, Mann–Kendall + Sen, ACF/PACF, CCF climático", TEAL),
        ("3. PCA y Clustering", "6 variables, K-Means vs GMM vs Ward + TimeSeriesSplit", AMBER),
        ("4. Dash → Power BI", "Prototipo interactivo Python + esquema estrella y DAX", NAVY),
    ]
    for i, (st_t, st_d, col) in enumerate(steps):
        left = 0.55 + i * 3.12
        add_card(s5, left, 1.28, 2.92, 1.38, WHITE, col)
        tb = s5.shapes.add_textbox(Inches(left + 0.16), Inches(1.38), Inches(2.64), Inches(1.18))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        r1 = p1.add_run()
        r1.text = st_t
        r1.font.name = "Segoe UI"
        r1.font.size = Pt(13)
        r1.font.bold = True
        r1.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.space_before = Pt(4)
        r2 = p2.add_run()
        r2.text = st_d
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(11)
        r2.font.color.rgb = SLATE

    # Tabla evaluacion visual (izquierda) + criterios ML (derecha)
    add_card(s5, 0.55, 2.86, 7.25, 4.02, WHITE)
    tb5t = s5.shapes.add_textbox(Inches(0.75), Inches(2.98), Inches(6.9), Inches(0.35))
    r = tb5t.text_frame.paragraphs[0].add_run()
    r.text = "Evaluación objetiva de vistas visuales (benchmark real sobre 115.200 filas)"
    r.font.name = "Segoe UI"
    r.font.size = Pt(13.5)
    r.font.bold = True
    r.font.color.rgb = NAVY

    rows = [
        ["Vista candidata", "Prec. [8]", "Claridad", "Escalabilidad", "Utilidad", "Total"],
        ["Serie mensual + STL", "3", "3", "3 (0,59 s)", "3", "12 / 12"],
        ["Barras apiladas GEC", "3", "3", "3 (0,09 s)", "3", "12 / 12"],
        ["Heatmap hora × mes", "2", "3", "3 (0,08 s)", "3", "11 / 12"],
        ["Calendario 13 años", "1", "2", "3 (0,04 s)", "2", "8 / 12 (Desc.)"],
    ]
    tbl_shape = s5.shapes.add_table(len(rows), 6, Inches(0.75), Inches(3.45), Inches(6.85), Inches(2.65))
    tbl = tbl_shape.table
    widths = [Inches(2.15), Inches(0.85), Inches(0.85), Inches(1.15), Inches(0.80), Inches(1.05)]
    for ci, w in enumerate(widths):
        tbl.columns[ci].width = w
    for ri, rdata in enumerate(rows):
        for ci, val in enumerate(rdata):
            cell = tbl.cell(ri, ci)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            cell.fill.fore_color.rgb = BLUE if ri == 0 else (SOFT_RED if ri == 4 else (BG if ri % 2 == 0 else WHITE))
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if ci == 0 else PP_ALIGN.CENTER
            rn = p.add_run()
            rn.text = val
            rn.font.name = "Segoe UI"
            rn.font.size = Pt(11)
            rn.font.bold = (ri == 0 or ci == 5)
            rn.font.color.rgb = WHITE if ri == 0 else (CRIMSON if ri == 4 and ci == 5 else NAVY)

    tb5f = s5.shapes.add_textbox(Inches(0.75), Inches(6.25), Inches(6.85), Inches(0.45))
    rf = tb5f.text_frame.paragraphs[0].add_run()
    rf.text = "Carga completa del esquema estrella Power BI (7 tablas): 0,089 s — muy por debajo del umbral de 15 s."
    rf.font.name = "Segoe UI"
    rf.font.size = Pt(11)
    rf.font.italic = True
    rf.font.color.rgb = TEAL

    add_card(s5, 8.00, 2.86, 4.78, 4.02, WHITE, TEAL)
    tb5r = s5.shapes.add_textbox(Inches(8.22), Inches(2.98), Inches(4.4), Inches(0.35))
    rr = tb5r.text_frame.paragraphs[0].add_run()
    rr.text = "Criterios objetivos en modelos"
    rr.font.name = "Segoe UI"
    rr.font.size = Pt(14)
    rr.font.bold = True
    rr.font.color.rgb = NAVY
    add_bullets(s5, 8.22, 3.45, 4.38, 3.25, [
        ("STL robusto vs. clásico:", "Evaluado por MAD de residuos (2,81 vs 5,01 µg/m³ en Coyhaique II)."),
        ("Clustering (k = 2..6):", "K-Means, GMM y Ward comparados por Silueta, Davies–Bouldin, Calinski–Harabasz y estabilidad temporal (ARI)."),
        ("Validación explicativa:", "GridSearchCV con TimeSeriesSplit (2015–2023) y test estricto 2024–2026 (F1, PR-AUC, ROC-AUC)."),
    ], font_size=11.8, space_after=10)
    add_notes(s5, "[2:30–3:15 | 45s] Explicar los criterios objetivos que faltaban en la Presentación 1: matriz visual basada en Cleveland & McGill + tiempos reales sobre 115k filas, y métricas internas/temporales en los modelos.")

    # ---------------- SLIDE 6: RESULTADOS 1 — TENDENCIA STL Y GEC ----------------
    s6 = prs.slides.add_slide(blank)
    add_header(s6, "5. Resultados — Evolución Interanual", "Descenso histórico en Coyhaique y Aysén, repunte 2026 y alerta en Cochrane", 6)

    add_card(s6, 0.55, 1.25, 12.23, 4.38, WHITE)
    s6.shapes.add_picture(str(FIG_DIR / "slide_trends_and_gec.png"), Inches(0.75), Inches(1.32), width=Inches(11.80))

    add_kpi_box(s6, 0.55, 5.76, 3.92, 1.22, "Coyhaique II (2014–2025)", "−4,93 días/año", "Mann–Kendall p = 0,002 | 156 → 75 (2021) → 99 (2026*)", BLUE)
    add_kpi_box(s6, 4.70, 5.76, 3.92, 1.22, "Vialidad (Puerto Aysén)", "−4,38 días/año", "Invierno 2018–26 (p = 0,021) | 61 → 16 días >50", TEAL)
    add_kpi_box(s6, 8.85, 5.76, 3.93, 1.22, "Cochrane y sincronía", "110–130 días", "En 2024–25 (supera Coyhaique II) | ρ regional > 0,82", CRIMSON)
    add_notes(s6, "[3:15–4:05 | 50s] Comentar la caída significativa en Coyhaique II y Vialidad, el repunte de 2026 en Coyhaique (99 días y 33 preemergencias) y el hallazgo clave de Cochrane con 110 y 130 días en 2024-2025.")

    # ---------------- SLIDE 7: RESULTADOS 2 — CICLO DIARIO Y ESTACIONAL ----------------
    s7 = prs.slides.add_slide(blank)
    add_header(s7, "5. Resultados — Patrón Diario y Estacional", "Estacionalidad extrema (5,1×) y ciclo bimodal nocturno por uso de leña", 7)

    add_card(s7, 0.55, 1.25, 12.23, 4.42, WHITE)
    s7.shapes.add_picture(str(FIG_DIR / "slide_diurnal_heatmap.png"), Inches(0.75), Inches(1.32), width=Inches(11.80))

    add_card(s7, 0.55, 5.80, 12.23, 1.15, SOFT_BLUE, BLUE)
    add_bullets(s7, 0.78, 5.88, 11.85, 1.02, [
        ("Fuerza estacional STL > 0,80:", "Invierno (Abr–Sep) promedia 77,7 µg/m³ frente a 15,1 µg/m³ en el resto del año (5,1×)."),
        ("Ciclo diario invernal:", "Repunte matutino (08:00 h), ventilación diurna mínima a las 14:00 h (40,0 µg/m³) y pico nocturno sostenido 18:00–00:00 h (141,1 µg/m³ a las 20:00 h; 191,8 µg/m³ en junio 21:00 h)."),
    ], font_size=12.2, space_after=5)
    add_notes(s7, "[4:05–4:45 | 40s] Interpretar el heatmap hora x mes y la curva diaria: mezcla convectiva al mediodía vs. encendido masivo de estufas e inversión térmica nocturna.")

    # ---------------- SLIDE 8: RESULTADOS 3 — METEOROLOGIA Y ROSA DE VIENTOS ----------------
    s8 = prs.slides.add_slide(blank)
    add_header(s8, "5. Resultados — Clima y Viento", "En invierno el viento domina los episodios; calma de 1,1 m/s y alta persistencia", 8)

    add_card(s8, 0.55, 1.25, 12.23, 4.35, WHITE)
    s8.shapes.add_picture(str(FIG_DIR / "slide_met_ccf_wind.png"), Inches(0.85), Inches(1.34), height=Inches(4.12))

    add_kpi_box(s8, 0.55, 5.74, 3.92, 1.24, "Modulador intra-invernal", "ρ = −0,686", "Velocidad viento supera a Temp. (−0,512) en Abr–Sep", BLUE)
    add_kpi_box(s8, 4.70, 5.74, 3.92, 1.24, "Días >50 vs. normales", "−63% viento", "1,13 vs 3,04 m/s | T: 3,7 vs 9,9 °C | CO 4× (p<10⁻¹²)", CRIMSON)
    add_kpi_box(s8, 8.85, 5.74, 3.93, 1.24, "Persistencia y dirección", "ACF(1) = 0,77", "Viento climatológico O–ONO (41,2% Coyhaique II)", TEAL)
    add_notes(s8, "[4:45–5:35 | 50s] Destacar que, aunque en el año completo lidera la temperatura, dentro del invierno el viento es el factor #1 (ρ=-0,686). Explicar la rosa climatológica (41,2% O-ONO) y la persistencia AR(1).")

    # ---------------- SLIDE 9: RESULTADOS 4 — PCA, CLUSTERING Y VALIDACION ----------------
    s9 = prs.slides.add_slide(blank)
    add_header(s9, "5. Resultados — Regímenes y Validación", "K-Means (k=3) aísla el régimen anticiclónico crítico (76,5% de episodios)", 9)

    add_card(s9, 0.55, 1.25, 12.23, 4.38, WHITE)
    s9.shapes.add_picture(str(FIG_DIR / "slide_pca_and_models.png"), Inches(0.75), Inches(1.32), width=Inches(11.80))

    add_kpi_box(s9, 0.55, 5.76, 3.92, 1.22, "K-Means (k=3) — Ganador", "ARI = 0,974", "Sil. 0,246 > Ward (0,199) y GMM (0,198) | PC1+2: 78,2%", BLUE)
    add_kpi_box(s9, 4.70, 5.76, 3.92, 1.22, "C2 Frío-Estancado vs C1", "93,4% > 50", "C2: 975,3 hPa, 1,1 m/s (76,5% epis.) vs C1 frontal 967,7 hPa", CRIMSON)
    add_kpi_box(s9, 8.85, 5.76, 3.93, 1.22, "Validación 2024–2026", "PR-AUC 0,948", "Grad. Boost. solo clima (F1 0,833); +lag1 F1 0,857", TEAL)
    add_notes(s9, "[5:35–6:30 | 55s] Explicar la física de C1 (baja presión frontal ventilada) vs C2 (alta presión anticiclónica + calma = inversión térmica). Mostrar que K-Means supera a GMM y Ward y que Gradient Boosting confirma el poder explicativo del clima.")

    # ---------------- SLIDE 10: ARQUITECTURA INTERACTIVA (DASH -> POWER BI) ----------------
    s10 = prs.slides.add_slide(blank)
    add_header(s10, "6. Implementación Interactiva", "Prototipo validado en Plotly Dash y esquema estrella listo para Power BI", 10)

    add_card(s10, 0.55, 1.28, 5.95, 5.58, WHITE, BLUE)
    tb10a = s10.shapes.add_textbox(Inches(0.82), Inches(1.42), Inches(5.45), Inches(0.4))
    r = tb10a.text_frame.paragraphs[0].add_run()
    r.text = "Prototipo interactivo Python (Plotly Dash)"
    r.font.name = "Segoe UI"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = BLUE
    add_bullets(s10, 0.82, 1.92, 5.45, 4.7, [
        ("Filtros sincronizados:", "Estación (4), rango de años (2014–2026) y conmutador de ventana (YTD ene–23 oct / Invierno / Años completos)."),
        ("5 vistas integradas:", "(1) Evolución STL y barras GEC; (2) Heatmap y curva diaria; (3) Mapa regional SINCA; (4) CCF y rosa de vientos con advertencia de disponibilidad; (5) Biplot PCA y perfiles de clusters."),
        ("KPIs auditables:", "Reporta en vivo completitud (%) y porcentaje de registros preliminares/no validados."),
        ("Rendimiento probado:", "Carga del modelo completo en 0,089 s con pruebas automatizadas en todos los callbacks."),
    ], font_size=13, space_after=11)

    add_card(s10, 6.80, 1.28, 5.98, 5.58, WHITE, AMBER)
    tb10b = s10.shapes.add_textbox(Inches(7.08), Inches(1.42), Inches(5.45), Inches(0.4))
    r = tb10b.text_frame.paragraphs[0].add_run()
    r.text = "Paquete de migración a Power BI (Esquema Estrella)"
    r.font.name = "Segoe UI"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = AMBER
    add_bullets(s10, 7.08, 1.92, 5.45, 3.6, [
        ("Dimensiones:", "dim_estacion (coordenadas y rol) + dim_fecha (calendario con banderas is_winter_season, is_ytd_comparable, year_status)."),
        ("Tablas de hechos (6):", "fact_calidad_aire_diaria, fact_ciclo_horario_mensual, fact_resumen_anual_completitud, fact_stl_descomposicion, fact_clusters_pca y fact_rosa_vientos."),
        ("Medidas DAX (medidas.dax):", "Norma DS 12, categorías GEC, tasa YTD comparable, % preliminares y temperatura/viento en episodios."),
    ], font_size=13, space_after=11)

    add_card(s10, 7.05, 5.55, 5.48, 1.05, SOFT_AMBER)
    tb_repo = s10.shapes.add_textbox(Inches(7.22), Inches(5.68), Inches(5.15), Inches(0.82))
    tf_r = tb_repo.text_frame
    tf_r.word_wrap = True
    pr1 = tf_r.paragraphs[0]
    rr1 = pr1.add_run()
    rr1.text = "Repositorio documentado (código + Dash + Power BI):"
    rr1.font.name = "Segoe UI"
    rr1.font.size = Pt(11.5)
    rr1.font.bold = True
    rr1.font.color.rgb = NAVY
    pr2 = tf_r.add_paragraph()
    rr2 = pr2.add_run()
    rr2.text = "https://github.com/MaksiiDR/aysen-mp25-visualizacion"
    rr2.font.name = "Segoe UI"
    rr2.font.size = Pt(12)
    rr2.font.bold = True
    rr2.font.color.rgb = BLUE
    add_notes(s10, "[6:30–7:15 | 45s] Presentar el flujo reproducible: prototipo interactivo en Plotly Dash para validación y modelo estrella limpio + medidas DAX listo para importar en Power BI Desktop.")

    # ---------------- SLIDE 11: FORTALEZAS, LIMITACIONES Y CONCLUSIONES ----------------
    s11 = prs.slides.add_slide(blank)
    add_header(s11, "7. Cierre", "Fortalezas, limitaciones y conclusiones principales", 11)

    add_card(s11, 0.55, 1.28, 3.92, 5.55, WHITE, TEAL)
    tb11a = s11.shapes.add_textbox(Inches(0.75), Inches(1.42), Inches(3.55), Inches(0.38))
    r = tb11a.text_frame.paragraphs[0].add_run()
    r.text = "Fortalezas"
    r.font.name = "Segoe UI"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = TEAL
    add_bullets(s11, 0.75, 1.90, 3.55, 4.7, [
        ("13 años oficiales:", ">98% de completitud de MP2,5 en Coyhaique II."),
        ("Rigor en faltantes:", "Control auditable de regla DS 12, registros preliminares y cierre 2026 (YTD)."),
        ("Validación objetiva:", "Series de tiempo, K-Means estable (ARI 0,974) y selección visual cuantitativa."),
        ("Transferencia real:", "Esquema estrella y DAX listos para Power BI."),
    ], font_size=12.3, space_after=10)

    add_card(s11, 4.70, 1.28, 3.92, 5.55, WHITE, CRIMSON)
    tb11b = s11.shapes.add_textbox(Inches(4.90), Inches(1.42), Inches(3.55), Inches(0.38))
    r = tb11b.text_frame.paragraphs[0].add_run()
    r.text = "Limitaciones"
    r.font.name = "Segoe UI"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = CRIMSON
    add_bullets(s11, 4.90, 1.90, 3.55, 4.7, [
        ("Dirección del viento:", "SINCA no ofrece serie horaria; solo rosa agregada histórica."),
        ("Variables ausentes:", "Sin precipitación horaria ni altura de capa límite."),
        ("Brecha territorial:", "Solo 4 estaciones; sin meteorología en Cochrane y parcial en Vialidad (60,6%)."),
        ("Estudio observacional:", "Establece asociación climática, no causalidad directa."),
    ], font_size=12.3, space_after=10)

    add_card(s11, 8.85, 1.28, 3.93, 5.55, WHITE, BLUE)
    tb11c = s11.shapes.add_textbox(Inches(9.05), Inches(1.42), Inches(3.55), Inches(0.38))
    r = tb11c.text_frame.paragraphs[0].add_run()
    r.text = "Conclusiones y futuro"
    r.font.name = "Segoe UI"
    r.font.size = Pt(16)
    r.font.bold = True
    r.font.color.rgb = BLUE
    add_bullets(s11, 9.05, 1.90, 3.55, 4.7, [
        ("Patrón vigente:", "Baja 2014–2025 (−4,93 días/año), pero repunte 2026 (99 días) y severidad crítica en Cochrane (110–130 días)."),
        ("Mecanismo físico:", "El estancamiento anticiclónico con calma eólica explica el 76,5% de episodios (PR-AUC 0,948), coherente con [1], [2], [6]."),
        ("Trabajo futuro:", "Sumar precipitación DMC, meteorología en Cochrane, Power BI Service y modelos SARIMAX 24–48 h."),
    ], font_size=12.3, space_after=10)
    add_notes(s11, "[7:15–8:00 | 45s] Cerrar resumiendo fortalezas, limitaciones honestas, conclusión central respaldada por literatura y trabajo futuro. Agradecer y abrir preguntas.")

    prs.save(str(PPTX_PATH))
    print(f"PPTX guardado: {PPTX_PATH}")


def export_pptx_to_pdf() -> None:
    pp = win32com.client.Dispatch("PowerPoint.Application")
    try:
        deck = pp.Presentations.Open(str(PPTX_PATH.resolve()), WithWindow=False)
        deck.SaveAs(str(PDF_PATH.resolve()), 32)  # ppSaveAsPDF = 32
        deck.Close()
    finally:
        pp.Quit()
    print(f"PDF de presentacion exportado: {PDF_PATH}")


def main() -> None:
    build_presentation()
    export_pptx_to_pdf()
    assert PPTX_PATH.exists() and PDF_PATH.exists()


if __name__ == "__main__":
    main()
