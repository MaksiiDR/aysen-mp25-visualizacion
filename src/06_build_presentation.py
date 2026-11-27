"""
06_build_presentation.py
------------------------
Genera la presentacion final de 8 minutos (14 diapositivas widescreen 16:9)
en PowerPoint (.pptx) alineada con el diseno editorial de presentacion_aysen_mp25.html:
  - Fondo pergamino uniforme (#E8E4D6) en todas las diapositivas
  - Tipografia unica (Segoe UI)
  - Tinta uniforme de alto contraste (#18211A), sin naranja ni cambios de color dentro de un parrafo
  - Incluye contexto completo del dataset SINCA (Slide 3) y proyecto Power BI PBIP validado (Slide 12)
Exporta tambien a PDF mediante PowerPoint COM para verificacion visual.
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

# Paleta Editorial Pergamino (alto contraste, sin naranja ni fondos oscuros)
PARCHMENT = RGBColor(232, 228, 214)      # #E8E4D6 fondo uniforme
PARCHMENT_ALT = RGBColor(222, 217, 202)  # #DED9CA recuadros editoriales
WHITE = RGBColor(255, 255, 255)          # Lamina limpia para figuras PNG
INK = RGBColor(24, 33, 26)               # #18211A texto principal (WCAG AAA)
INK_SUB = RGBColor(62, 72, 65)           # #3E4841 texto secundario / kickers
INK_FAINT = RGBColor(105, 112, 106)      # Fila descartada en tabla
HAIRLINE = RGBColor(189, 184, 170)       # Lineas divisorias finas
RULE_ACCENT = RGBColor(122, 35, 29)      # #7A231D solo barra corta estructural (nunca texto naranja)
WATERMARK = RGBColor(219, 214, 200)      # Numeral grande sutil de fondo

FONT_MAIN = "Segoe UI"
TOTAL_SLIDES = 14


def set_slide_bg(slide, color: RGBColor = PARCHMENT) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_line(slide, left: float, top: float, width: float, height: float, color: RGBColor) -> None:
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    bar.fill.solid()
    bar.fill.fore_color.rgb = color
    bar.line.fill.background()
    bar.shadow.inherit = False


def add_rect(slide, left: float, top: float, width: float, height: float, fill_color: RGBColor, border_color: RGBColor | None = HAIRLINE):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_color
    if border_color is not None:
        shp.line.color.rgb = border_color
        shp.line.width = Pt(0.75)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def add_text(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    text: str,
    size: float = 14,
    bold: bool = False,
    italic: bool = False,
    color: RGBColor = INK,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    line_spacing: float = 1.18,
):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    r.font.name = FONT_MAIN
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    return tb


def add_watermark(slide, num_str: str) -> None:
    add_text(
        slide,
        left=9.6,
        top=4.65,
        width=3.2,
        height=2.6,
        text=num_str,
        size=180,
        bold=False,
        color=WATERMARK,
        align=PP_ALIGN.RIGHT,
        line_spacing=0.9,
    )


def add_chrome(
    slide,
    top_left: str,
    top_right: str,
    foot_left: str,
    slide_num: int,
    with_rules: bool = True,
) -> None:
    set_slide_bg(slide, PARCHMENT)
    add_text(slide, 0.72, 0.34, 6.2, 0.26, top_left.upper(), size=9.5, bold=True, color=INK_SUB)
    add_text(slide, 6.95, 0.34, 5.66, 0.26, top_right.upper(), size=9.5, bold=True, color=INK_SUB, align=PP_ALIGN.RIGHT)
    if with_rules:
        add_line(slide, 0.72, 0.66, 11.89, 0.014, HAIRLINE)

    if with_rules:
        add_line(slide, 0.72, 6.90, 11.89, 0.014, HAIRLINE)
    add_text(slide, 0.72, 6.98, 9.2, 0.26, foot_left.upper(), size=9.0, bold=True, color=INK_SUB)
    add_text(
        slide,
        10.4,
        6.98,
        2.21,
        0.26,
        f"{slide_num:02d} / {TOTAL_SLIDES:02d}",
        size=9.0,
        bold=True,
        color=INK_SUB,
        align=PP_ALIGN.RIGHT,
    )


def add_section_heading(slide, left: float, top: float, width: float, kicker: str, title: str, title_size: float = 26) -> None:
    add_text(slide, left, top, width, 0.24, kicker.upper(), size=9.5, bold=True, color=INK_SUB)
    add_line(slide, left, top + 0.30, 0.42, 0.028, RULE_ACCENT)
    add_text(slide, left, top + 0.42, width, 0.90, title, size=title_size, bold=True, color=INK, line_spacing=1.10)


def add_em_bullets(
    slide,
    left: float,
    top: float,
    width: float,
    height: float,
    items: list[tuple[str, str]],
    font_size: float = 13.0,
    space_after: float = 9.0,
    color: RGBColor = INK,
) -> None:
    """Lista editorial con guion largo; cada parrafo conserva UN solo color uniforme."""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0)
    tf.margin_right = Inches(0)
    tf.margin_top = Inches(0)
    tf.margin_bottom = Inches(0)
    for idx, (lead, body) in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.24
        r0 = p.add_run()
        r0.text = "—  "
        r0.font.name = FONT_MAIN
        r0.font.size = Pt(font_size)
        r0.font.bold = True
        r0.font.color.rgb = color
        if lead:
            r1 = p.add_run()
            r1.text = lead + " "
            r1.font.name = FONT_MAIN
            r1.font.size = Pt(font_size)
            r1.font.bold = True
            r1.font.color.rgb = color
        r2 = p.add_run()
        r2.text = body
        r2.font.name = FONT_MAIN
        r2.font.size = Pt(font_size)
        r2.font.color.rgb = color


def add_finding_strip(slide, top: float, items: list[tuple[str, str, str]]) -> None:
    """Tres columnas editoriales inferiores con linea superior fina."""
    col_w = 3.74
    gap = 0.335
    for i, (kicker, val, txt) in enumerate(items):
        x = 0.72 + i * (col_w + gap)
        add_line(slide, x, top, col_w, 0.015, HAIRLINE)
        add_text(slide, x, top + 0.09, col_w, 0.22, kicker.upper(), size=8.8, bold=True, color=INK_SUB)
        add_text(slide, x, top + 0.31, col_w, 0.38, val, size=18.5, bold=True, color=INK)
        add_text(slide, x, top + 0.70, col_w, 0.72, txt, size=10.5, color=INK_SUB, line_spacing=1.22)


def add_exhibit_image(slide, img_name: str, left: float, top: float, width: float, height: float) -> None:
    """Monta la figura PNG sobre lamina blanca limpia con borde fino sobre el pergamino."""
    add_rect(slide, left, top, width, height, WHITE, HAIRLINE)
    pad_x = 0.12
    pad_y = 0.08
    pic_path = str(FIG_DIR / img_name)
    # Inserta ajustando por altura o ancho sin deformar relacion de aspecto
    pic = slide.shapes.add_picture(pic_path, Inches(left + pad_x), Inches(top + pad_y))
    max_w = Inches(width - 2 * pad_x)
    max_h = Inches(height - 2 * pad_y)
    scale = min(max_w / pic.width, max_h / pic.height)
    pic.width = int(pic.width * scale)
    pic.height = int(pic.height * scale)
    pic.left = int(Inches(left) + (Inches(width) - pic.width) / 2)
    pic.top = int(Inches(top) + (Inches(height) - pic.height) / 2)


def add_notes(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text


def style_table(tbl, widths: list[float], rows: list[list[str]], align_right_cols: set[int], discarded_row: int | None = None, font_size: float = 11.0) -> None:
    for ci, w in enumerate(widths):
        tbl.columns[ci].width = Inches(w)
    for ri, rdata in enumerate(rows):
        for ci, val in enumerate(rdata):
            cell = tbl.cell(ri, ci)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.06)
            cell.margin_bottom = Inches(0.06)
            cell.fill.solid()
            if ri == 0:
                cell.fill.fore_color.rgb = PARCHMENT_ALT
            else:
                cell.fill.fore_color.rgb = PARCHMENT
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT if ci in align_right_cols else PP_ALIGN.LEFT
            rn = p.add_run()
            rn.text = val
            rn.font.name = FONT_MAIN
            rn.font.size = Pt(9.5 if ri == 0 else font_size)
            rn.font.bold = (ri == 0 or (ci == 0 and ri > 0 and discarded_row != ri) or (ci == len(rdata) - 1 and ri > 0 and discarded_row != ri))
            rn.font.color.rgb = INK_FAINT if (discarded_row is not None and ri == discarded_row) else INK


def build_presentation() -> None:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ---------------- SLIDE 01: PORTADA ----------------
    s1 = prs.slides.add_slide(blank)
    set_slide_bg(s1, PARCHMENT)
    add_watermark(s1, "01")
    add_text(s1, 0.72, 0.42, 6.2, 0.26, "EIN092B VISUALIZACIÓN · UTFSM", size=9.5, bold=True, color=INK_SUB)
    add_text(s1, 7.0, 0.42, 5.61, 0.26, "28 DE NOVIEMBRE DE 2026", size=9.5, bold=True, color=INK_SUB, align=PP_ALIGN.RIGHT)

    add_text(s1, 0.72, 1.85, 10.5, 0.26, "INFORME FINAL · GRUPO N° 2 · REGIÓN DE AYSÉN", size=10.0, bold=True, color=INK_SUB)
    add_line(s1, 0.72, 2.18, 0.46, 0.032, RULE_ACCENT)
    add_text(s1, 0.72, 2.38, 10.8, 1.95, "MP2,5 y Clima en la\nRegión de Aysén", size=48, bold=True, color=INK, line_spacing=1.06)
    add_text(
        s1,
        0.72,
        4.48,
        8.9,
        0.95,
        "Caracterización visual, descomposición de series de tiempo y regímenes meteorológicos sobre 13 años de registros horarios oficiales del SINCA (2013–2026).",
        size=15.5,
        color=INK_SUB,
        line_spacing=1.35,
    )

    add_line(s1, 0.72, 6.56, 11.89, 0.014, HAIRLINE)
    add_text(s1, 0.72, 6.68, 6.5, 0.28, "MAXIMILIANO DEL RÍO LINCOÑIR  ·  PATRICIO AYLWIN RETAMAL", size=9.5, bold=True, color=INK_SUB)
    add_text(s1, 7.2, 6.68, 5.41, 0.28, "PROF. JORGE PORTILLA  ·  GITHUB.COM/MAKSIIDR/AYSEN-MP25-VISUALIZACION", size=9.0, bold=True, color=INK_SUB, align=PP_ALIGN.RIGHT)
    add_notes(s1, "[0:00–0:20 | 20s] Presentar el título, el Grupo N° 2 y el alcance: 13 años de datos SINCA (2013–2026) en cuatro estaciones de la Región de Aysén con series de tiempo y arquitectura Python → Power BI.")

    # ---------------- SLIDE 02: CONTEXTO Y PROBLEMÁTICA ----------------
    s2 = prs.slides.add_slide(blank)
    add_chrome(s2, "01 · Contexto y Problemática", "Región de Aysén · DS N° 12/2011", "MP2,5 y Clima · Región de Aysén", 2)

    add_section_heading(s2, 0.72, 1.05, 5.65, "Problema de salud pública", "Una crisis invernal oculta en tablas estáticas", 26)
    add_em_bullets(
        s2,
        0.72,
        2.58,
        5.55,
        3.95,
        [
            ("Zona saturada por MP2,5:", "Coyhaique supera reiteradamente la norma diaria de 50 µg/m³ por combustión residencial de leña entre abril y septiembre [1]–[4]."),
            ("Escala multivariada:", "Más de 115.200 registros horarios por serie en Coyhaique II, imposibles de diagnosticar en planillas planas."),
            ("Brecha del portal SINCA:", "Descarga series aisladas sin comparar ciudades, separar tendencia STL ni vincular episodios con la meteorología local."),
        ],
        font_size=13.2,
        space_after=14,
    )

    add_line(s2, 6.58, 1.05, 0.015, 5.55, HAIRLINE)

    add_rect(s2, 6.95, 1.08, 5.66, 2.05, PARCHMENT_ALT, HAIRLINE)
    add_text(s2, 7.22, 1.22, 5.1, 0.24, "PREGUNTA DE INVESTIGACIÓN", size=9.0, bold=True, color=INK_SUB)
    add_text(
        s2,
        7.22,
        1.54,
        5.12,
        1.42,
        "“¿Cómo han evolucionado los episodios de MP2,5 en Aysén entre 2013 y 2026, y qué condiciones climáticas se asocian a ellos?”",
        size=16.5,
        italic=True,
        bold=True,
        color=INK,
        line_spacing=1.28,
    )

    add_text(s2, 6.95, 3.48, 5.6, 0.26, "OBJETIVOS ESPECÍFICOS", size=9.5, bold=True, color=INK_SUB)
    add_em_bullets(
        s2,
        6.95,
        3.86,
        5.66,
        2.85,
        [
            ("OE1 · Patrones:", "Describir ciclos diarios, estacionales y sincronía entre Coyhaique, Puerto Aysén y Cochrane."),
            ("OE2 · Tendencias:", "Cuantificar tendencias interanuales controlando vacíos y el año incompleto 2026."),
            ("OE3 · Regímenes:", "Asociar episodios con clima mediante CCF, PCA y clustering validado objetivamente."),
        ],
        font_size=13.0,
        space_after=12,
    )
    add_notes(s2, "[0:20–0:55 | 35s] Contextualizar la contaminación invernal por leña en Coyhaique (zona saturada DS 15), la escala de 115.200 filas por variable, la brecha de SINCA y los 3 objetivos.")

    # ---------------- SLIDE 03: DATASET SINCA Y CONTEXTO DE DATOS ----------------
    s3 = prs.slides.add_slide(blank)
    add_chrome(s3, "02 · Dataset y Contexto de Datos", "Fuente Oficial: SINCA · Ministerio del Medio Ambiente", "Dataset SINCA · Contexto y Normativa", 3)

    add_section_heading(s3, 0.72, 0.88, 11.89, "Base de datos pública (Octubre 2026)", "25 archivos horarios oficiales de cuatro estaciones en Aysén", 25)
    add_text(
        s3,
        0.72,
        1.88,
        11.89,
        0.34,
        "Registros horarios de contaminantes y meteorología desde sinca.mma.gob.cl (licencia de datos públicos, corte al 23 de octubre de 2026).",
        size=12.0,
        color=INK_SUB,
    )

    rows_ds = [
        ["ESTACIÓN", "CIUDAD", "VARIABLES DISPONIBLES", "PERÍODO", "REGISTROS MP2,5"],
        ["Coyhaique II", "Coyhaique", "MP2,5, MP10, CO, SO₂, O₃, temp., humedad, presión, vel. viento + rosa estática", "Sep. 2013 – Oct. 2026", "115.200 h"],
        ["Coyhaique", "Coyhaique", "MP2,5, MP10 (desde 2007), temperatura, humedad, vel. viento + rosa estática", "Mar. 2013 – Oct. 2026", "119.616 h"],
        ["Vialidad", "Puerto Aysén", "MP2,5; meteorología parcial (hasta 2023–2024) + rosa estática", "Oct. 2017 – Oct. 2026", "78.864 h"],
        ["Cochrane", "Cochrane", "Solo MP2,5 (sin sensores meteorológicos ni rosa de vientos en SINCA)", "Mar. 2021 – Oct. 2026", "49.272 h"],
    ]
    t3 = s3.shapes.add_table(len(rows_ds), 5, Inches(0.72), Inches(2.38), Inches(11.89), Inches(2.58)).table
    style_table(t3, [1.65, 1.45, 5.29, 2.05, 1.45], rows_ds, align_right_cols={4}, font_size=11.0)

    add_finding_strip(
        s3,
        5.22,
        [
            ("Definición de episodio (DS N° 12/2011)", "> 50 µg/m³ · ≥ 18 h", "Un día sobre norma requiere promedio de 24 h mayor a 50 µg/m³ calculado con al menos 18 horas válidas (75% del día)."),
            ("Categorías oficiales GEC", "5 niveles de riesgo", "Bueno (≤50), Regular (50–79), Alerta (80–109), Preemergencia (110–169) y Emergencia (≥170 µg/m³)."),
            ("Estructura de validación SINCA", "3 estados de dato", "Cada CSV separa registros validados, preliminares y no validados; se preservan etiquetas y no se imputan huecos largos."),
        ],
    )
    add_notes(s3, "[0:55–1:30 | 35s] Explicar la fuente SINCA (datos públicos descargados en oct. 2026), las 4 estaciones con sus periodos/variables y las reglas DS N° 12/2011 (50 µg/m³, ≥18 h válidas) y GEC.")

    # ---------------- SLIDE 04: RETROALIMENTACIÓN PRESENTACIÓN 1 ----------------
    s4 = prs.slides.add_slide(blank)
    add_chrome(s4, "03 · Retroalimentación Presentación 1", "Ajustes Metodológicos Verificados", "Incorporación de Retroalimentación", 4)
    add_watermark(s4, "04")

    add_section_heading(s4, 0.72, 0.90, 11.89, "Respuesta a las observaciones", "Tres correcciones que elevaron el rigor del estudio", 26)

    obs = [
        (
            "OBSERVACIÓN 01",
            "Series de tiempo y Power BI",
            "“Explorar soluciones basadas en series de tiempo y migrar la implementación visual final a Power BI.”",
            [
                ("", "Descomposición STL robusta, Mann–Kendall + Sen, ACF/PACF y CCF."),
                ("", "Pruebas y Dash en Python → proyecto Power BI PBIP (8 tablas TMDL + 32 medidas DAX + 3 páginas PBIR)."),
                ("", "Clasificación temporal solo como validación explicativa del clima."),
            ],
        ),
        (
            "OBSERVACIÓN 02",
            "Faltantes y año 2026",
            "“Falta manejo en cuanto a datos faltantes o incompletos (año presente).”",
            [
                ("", "Auditoría completa de 25 CSV: exclusión de NO, NOx y NO₂ (>70% vacíos)."),
                ("", "Regla DS 12 estricta (≥18 h válidas); sin imputación de huecos largos."),
                ("", "2026 (corte 23 oct) separado en años completos, ventana YTD e invierno (100%)."),
            ],
        ),
        (
            "OBSERVACIÓN 03",
            "Verificación de viento",
            "“La rosa de los vientos necesita dirección; asegurarse de que el dataset posea esos datos.”",
            [
                ("", "Verificado en los CSV: SINCA no entrega dirección horaria en ninguna estación."),
                ("", "Solo existen tablas agregadas de 24 sectores (ausentes en Cochrane)."),
                ("", "Rosa acotada al régimen histórico; episodios estudiados con velocidad del viento."),
            ],
        ),
    ]
    col_w = 3.74
    gap = 0.335
    for i, (tag, head, quote, bullets) in enumerate(obs):
        x = 0.72 + i * (col_w + gap)
        if i > 0:
            add_line(s4, x - gap / 2, 2.25, 0.015, 4.35, HAIRLINE)
        add_text(s4, x, 2.25, col_w, 0.22, tag, size=9.0, bold=True, color=INK_SUB)
        add_text(s4, x, 2.50, col_w, 0.42, head, size=16.5, bold=True, color=INK)
        add_line(s4, x, 3.04, 0.025, 0.88, RULE_ACCENT)
        add_text(s4, x + 0.14, 3.02, col_w - 0.14, 0.96, quote, size=11.0, italic=True, color=INK_SUB, line_spacing=1.22)
        add_em_bullets(s4, x, 4.14, col_w, 2.55, bullets, font_size=11.8, space_after=8)
    add_notes(s4, "[1:30–2:05 | 35s] Mostrar directamente cómo resolvimos las 3 observaciones de la Presentación 1: series de tiempo + Power BI PBIP real, control del año 2026 y auditoría de la rosa de vientos.")

    # ---------------- SLIDE 05: AUDITORÍA DE DATOS SINCA ----------------
    s5 = prs.slides.add_slide(blank)
    add_chrome(s5, "04 · Auditoría de Datos SINCA", "Cobertura, Completitud y Corte 2026", "Auditoría de Calidad · 4 Estaciones SINCA", 5)

    add_section_heading(s5, 0.72, 0.88, 5.6, "Calidad y trazabilidad", "Cobertura histórica y control del corte 2026", 23.5)

    kpis = [("25", "ARCHIVOS CSV"), ("98,9%", "COYHAIQUE II"), ("23 oct", "CORTE 2026*"), ("78,6%", "COCHRANE")]
    for i, (val, lbl) in enumerate(kpis):
        x = 6.72 + i * 1.49
        add_text(s5, x, 0.96, 1.38, 0.48, val, size=23, bold=True, color=INK)
        add_text(s5, x, 1.46, 1.38, 0.24, lbl, size=8.5, bold=True, color=INK_SUB)
        add_line(s5, x, 1.76, 1.35, 0.014, HAIRLINE)

    add_exhibit_image(s5, "slide_completeness_audit.png", 0.72, 2.30, 7.35, 4.35)

    add_text(s5, 8.38, 2.34, 4.23, 0.26, "REGLAS DE PREPROCESAMIENTO", size=9.5, bold=True, color=INK_SUB)
    add_em_bullets(
        s5,
        8.38,
        2.72,
        4.23,
        3.95,
        [
            ("Ventana YTD comparable:", "Del 1 de enero al 23 de octubre se concentra el 99,7% de los episodios históricos de Coyhaique II, habilitando evaluar 2026 sin sesgo."),
            ("Depuración de gases:", "NO (9,2%), NOx (10,0%) y NO₂ (30,0%) se descartaron del análisis multivariado."),
            ("Trazabilidad SINCA:", "16,6% de días 2026 en Coyhaique II y 100% de Cochrane 2021–2023 son preliminares o no validados."),
        ],
        font_size=12.4,
        space_after=13,
    )
    add_notes(s5, "[2:05–2:40 | 35s] Revisar la matriz de completitud anual. Destacar el 100% de cobertura invernal en 2026 y la advertencia sobre Cochrane 2021–2023.")

    # ---------------- SLIDE 06: METODOLOGÍA Y SELECCIÓN OBJETIVA ----------------
    s6 = prs.slides.add_slide(blank)
    add_chrome(s6, "05 · Metodología y Selección Objetiva", "Benchmark Real Sobre 115.200 Registros Horarios", "Evaluación Objetiva · Visualización y Modelado", 6)

    add_section_heading(s6, 0.72, 0.90, 6.8, "Selección de visualizaciones", "Criterios cuantitativos sobre vistas candidatas", 24)

    rows_eval = [
        ["VISTA CANDIDATA", "PERC. [8]", "CLAR.", "ESC. (S)", "TOTAL"],
        ["Serie mensual + tendencia STL", "3", "3", "0,59 s", "12 / 12"],
        ["Barras apiladas GEC (DS 12)", "3", "3", "0,09 s", "12 / 12"],
        ["Mapa de calor (hora × mes)", "2", "3", "0,08 s", "11 / 12"],
        ["Calendario diario 13 años (descartado)", "1", "2", "0,04 s", "8 / 12"],
    ]
    t6 = s6.shapes.add_table(len(rows_eval), 5, Inches(0.72), Inches(2.42), Inches(6.85), Inches(2.85)).table
    style_table(t6, [3.15, 0.92, 0.78, 1.00, 1.00], rows_eval, align_right_cols={1, 2, 3, 4}, discarded_row=4, font_size=11.5)

    add_text(
        s6,
        0.72,
        5.50,
        6.85,
        0.80,
        "Carga completa del esquema estrella Power BI (8 tablas): 0,089 s — 160× más rápido que el umbral propuesto de 15 s.",
        size=12.0,
        color=INK_SUB,
        line_spacing=1.28,
    )

    add_line(s6, 7.82, 1.05, 0.015, 5.55, HAIRLINE)

    add_text(s6, 8.12, 1.05, 4.49, 0.24, "MODELOS Y AJUSTE DE HIPERPARÁMETROS", size=9.5, bold=True, color=INK_SUB)
    add_text(s6, 8.12, 1.40, 4.49, 0.60, "Selección objetiva de series y ML", size=19, bold=True, color=INK)
    add_em_bullets(
        s6,
        8.12,
        2.15,
        4.49,
        4.35,
        [
            ("STL robusto vs. clásico:", "Elegido por reducir casi a la mitad el residuo MAD en Coyhaique II (2,81 vs. 5,01 µg/m³)."),
            ("Clustering (k = 2..6):", "K-Means, GMM y Ward contrastados con Silueta, Davies–Bouldin, Calinski–Harabasz y estabilidad temporal (ARI entre 2015–20 y 2021–26)."),
            ("Validación explicativa:", "GridSearchCV con TimeSeriesSplit (5 particiones, 2015–2023) y test estricto 2024–2026 (F1, PR-AUC, ROC-AUC)."),
        ],
        font_size=12.4,
        space_after=13,
    )
    add_notes(s6, "[2:40–3:15 | 35s] Presentar los criterios objetivos: matriz visual basada en Cleveland & McGill + tiempos reales sobre 115k filas (<0,6 s) y métricas internas/temporales para los modelos.")

    # ---------------- SLIDE 07: HALLAZGO CENTRAL ----------------
    s7 = prs.slides.add_slide(blank)
    add_chrome(s7, "06 · Hallazgo Central", "Síntesis Regional 2013–2026", "Resultados · Evolución Interanual", 7, with_rules=False)
    add_watermark(s7, "07")

    add_text(s7, 0.72, 1.28, 8.0, 0.24, "EVOLUCIÓN INTERANUAL", size=9.5, bold=True, color=INK_SUB)
    add_line(s7, 0.72, 1.60, 0.44, 0.030, RULE_ACCENT)
    add_text(
        s7,
        0.72,
        1.82,
        11.2,
        1.85,
        "Coyhaique redujo sus episodios durante una década — pero 2026 repuntó y Cochrane ya supera a la capital.",
        size=32,
        bold=True,
        color=INK,
        line_spacing=1.15,
    )

    stats7 = [
        ("−4,93", "DÍAS / AÑO · COYHAIQUE II (2014–2025)", "Tendencia decreciente significativa (Mann–Kendall p = 0,002), bajando de 156 a 75 días en 2021."),
        ("99", "DÍAS > 50 · COYHAIQUE II (2026 YTD*)", "33 preemergencias y 15 emergencias en el invierno 2026, casi el doble de preemergencias que en 2025."),
        ("130", "DÍAS > 50 · COCHRANE (2025)", "110 días en 2024 y 130 en 2025 (35,1% de días válidos), con sincronía regional ρ > 0,82 a 200 km."),
    ]
    for i, (val, lbl, sub) in enumerate(stats7):
        x = 0.72 + i * 4.07
        add_text(s7, x, 4.18, 3.74, 0.78, val, size=40, bold=True, color=INK)
        add_text(s7, x, 5.02, 3.74, 0.28, lbl, size=9.0, bold=True, color=INK)
        add_text(s7, x, 5.34, 3.74, 0.92, sub, size=11.5, color=INK_SUB, line_spacing=1.28)
        add_line(s7, x, 6.32, 3.74, 0.014, HAIRLINE)
    add_notes(s7, "[3:15–3:40 | 25s] Pausa narrativa de alto impacto antes de los gráficos: sintetizar la evolución regional en tres cifras clave.")

    # ---------------- SLIDE 08: EXHIBIT 01 — STL Y GEC ----------------
    s8 = prs.slides.add_slide(blank)
    add_chrome(s8, "06 · Resultados — Series de Tiempo", "Tendencia STL Robusta y Categorías GEC", "Exhibit 01 · Tendencias y Episodios Críticos", 8)

    add_section_heading(s8, 0.72, 0.80, 11.89, "Descomposición temporal", "Tendencia STL regional y días sobre norma DS 12", 24)
    add_exhibit_image(s8, "slide_trends_and_gec.png", 0.72, 1.82, 11.89, 3.45)
    add_finding_strip(
        s8,
        5.42,
        [
            ("Fuerza estacional STL", "> 0,80", "Domina en las 4 estaciones (0,807 en Coyhaique II; 0,945 en Vialidad y Cochrane)."),
            ("Puerto Aysén (Vialidad)", "−4,38 d/año", "Descenso invernal significativo 2018–2026 (p = 0,021), pasando de 61 a 16 días >50."),
            ("Sincronía regional", "ρ > 0,82", "Coyhaique II correlaciona con Vialidad (0,829) y Cochrane (0,822; p < 0,001)."),
        ],
    )
    add_notes(s8, "[3:40–4:15 | 35s] Recorrer tendencia STL (caída en Coyhaique II y Vialidad) y barras GEC con la barra achurada de 2026* y su repunte de preemergencias.")

    # ---------------- SLIDE 09: EXHIBIT 02 — CICLO DIARIO ----------------
    s9 = prs.slides.add_slide(blank)
    add_chrome(s9, "07 · Resultados — Ciclo Horario y Estacional", "Coyhaique II · 115.200 Registros Horarios", "Exhibit 02 · Mapa de Calor y Perfil Diario", 9)

    add_section_heading(s9, 0.72, 0.80, 11.89, "Patrón intradiario", "Estacionalidad 5,1× y pulso nocturno de la leña", 24)
    add_exhibit_image(s9, "slide_diurnal_heatmap.png", 0.72, 1.82, 11.89, 3.45)
    add_finding_strip(
        s9,
        5.42,
        [
            ("Brecha estacional", "77,7 vs. 15,1", "µg/m³ promedio horario en invierno (Abr–Sep) frente al resto del año (Oct–Mar)."),
            ("Máximo nocturno", "191,8 µg/m³", "Pico promedio en junio a las 21:00 h (media invernal 141,1 µg/m³ a las 20:00 h)."),
            ("Ventana de ventilación", "14:00 h · 40,0", "Mínimo vespertino invernal por mezcla convectiva diurna (oscilación 3,5× en el día)."),
        ],
    )
    add_notes(s9, "[4:15–4:45 | 30s] Explicar el heatmap hora × mes y la curva invernal: razón 5,1×, mínimo a las 14:00 h y pico nocturno de 191,8 µg/m³ en junio a las 21:00 h.")

    # ---------------- SLIDE 10: EXHIBIT 03 — METEOROLOGÍA Y VIENTO ----------------
    s10 = prs.slides.add_slide(blank)
    add_chrome(s10, "08 · Resultados — Meteorología y Viento", "Correlación Cruzada (CCF) y Rosa Climatológica", "Exhibit 03 · Relación Meteorológica y Rosa de Vientos", 10)

    add_section_heading(s10, 0.72, 0.80, 11.89, "Asociación climática", "En invierno, la calma eólica manda sobre el frío", 24)
    add_exhibit_image(s10, "slide_met_ccf_wind.png", 0.72, 1.82, 11.89, 3.45)
    add_finding_strip(
        s10,
        5.42,
        [
            ("Modulador invernal", "ρ = −0,686", "En Abr–Sep la velocidad del viento supera a la temperatura (−0,512) y humedad (+0,443)."),
            ("Días >50 vs. normales", "−63% viento", "Mediana cae de 3,04 a 1,13 m/s; T baja a 3,7 °C y CO casi se cuadruplica (p < 10⁻¹²)."),
            ("Persistencia y dirección", "ACF(1) = 0,77", "Estructura AR(1) clara; viento climatológico O–ONO domina el 41,2% en Coyhaique II."),
        ],
    )
    add_notes(s10, "[4:45–5:25 | 40s] Destacar que dentro del invierno el viento lidera (ρ=−0,686), la calma cae 63% a 1,13 m/s, la persistencia AR(1) es 0,77 y la rosa climatológica marca 41,2% O–ONO.")

    # ---------------- SLIDE 11: EXHIBIT 04 — PCA, CLUSTERING Y VALIDACIÓN ----------------
    s11 = prs.slides.add_slide(blank)
    add_chrome(s11, "09 · Resultados — PCA, Clustering y Validación", "Coyhaique II · 3.949 Días Completos (2015–2026)", "Exhibit 04 · Agrupamiento y Validación Explicativa", 11)

    add_section_heading(s11, 0.72, 0.80, 11.89, "Regímenes sinópticos", "K-Means (k = 3) aísla el régimen anticiclónico crítico", 24)
    add_exhibit_image(s11, "slide_pca_and_models.png", 0.72, 1.82, 11.89, 3.45)
    add_finding_strip(
        s11,
        5.42,
        [
            ("K-Means (k=3) · Ganador", "ARI = 0,974", "Supera a Ward y GMM (Silueta 0,246; DB 1,363; CH 2068,8); PC1+PC2 = 78,2% varianza."),
            ("C2 Frío-Estancado vs. C1", "76,5% episodios", "C2 (975,3 hPa; 1,05 m/s; 93,4% >50) vs. C1 frontal ventilado (967,7 hPa; 2,31 m/s)."),
            ("Validación test 2024–26", "PR-AUC 0,948", "Gradient Boosting solo clima logra F1 = 0,833 (y 0,857 con lag-1) vs. 0,739 persistencia."),
        ],
    )
    add_notes(s11, "[5:25–6:15 | 50s] Explicar la física de C1 frontal ventilado (967,7 hPa) vs. C2 anticiclónico estancado (975,3 hPa, 93,4% episodios) y la confirmación explicativa con Gradient Boosting (PR-AUC 0,948).")

    # ---------------- SLIDE 12: ARQUITECTURA INTERACTIVA (DASH -> POWER BI PBIP) ----------------
    s12 = prs.slides.add_slide(blank)
    add_chrome(s12, "10 · Arquitectura Interactiva", "De Python a Power BI Desktop (PBIP)", "Implementación Interactiva y Repositorio", 12)
    add_watermark(s12, "12")

    add_section_heading(s12, 0.72, 0.90, 11.89, "Transferencia visual", "Prototipo Plotly Dash y proyecto Power BI (PBIP) validado", 25)

    add_text(s12, 0.72, 2.24, 5.55, 0.26, "CAPA 1 · PROTOTIPO INTERACTIVO (PYTHON)", size=9.5, bold=True, color=INK_SUB)
    add_em_bullets(
        s12,
        0.72,
        2.62,
        5.55,
        3.95,
        [
            ("Filtros sincronizados:", "Selección de 4 estaciones, rango 2014–2026 y conmutador YTD / Invierno / Años completos."),
            ("5 vistas validadas:", "STL y GEC, Heatmap horario, Mapa regional SINCA, CCF + Rosa climatológica y Biplot PCA/Clusters."),
            ("Transparencia en vivo:", "Tarjetas KPI reportan completitud (%) y fracción de datos preliminares en cada consulta."),
        ],
        font_size=12.8,
        space_after=14,
    )

    add_line(s12, 6.58, 2.22, 0.015, 4.35, HAIRLINE)

    add_text(s12, 6.95, 2.24, 5.66, 0.26, "CAPA 2 · PROYECTO POWER BI DESKTOP (PBIP + TMDL + PBIR)", size=9.5, bold=True, color=INK_SUB)
    add_em_bullets(
        s12,
        6.95,
        2.62,
        5.66,
        2.70,
        [
            ("Modelo estrella TMDL:", "8 tablas (2 dimensiones + 6 hechos), 9 relaciones 1→* y 32 medidas DAX con parámetro CarpetaDatos (carga 0,089 s)."),
            ("Informe PBIR (3 páginas, 22 visuales):", "Resumen Regional + Azure Map, Series STL/Matriz Horaria y Clima/PCA/Viento."),
            ("Validación oficial CLI:", "Esquema verificado con 0 errores y 0 advertencias (Aysen_MP25.pbip listo para abrir y actualizar)."),
        ],
        font_size=12.5,
        space_after=11,
    )

    add_rect(s12, 6.95, 5.52, 5.66, 0.98, PARCHMENT_ALT, HAIRLINE)
    add_text(s12, 7.18, 5.66, 5.20, 0.24, "REPOSITORIO REPRODUCIBLE (CÓDIGO + DASH + POWER BI PBIP)", size=8.8, bold=True, color=INK_SUB)
    add_text(s12, 7.18, 5.98, 5.20, 0.36, "https://github.com/MaksiiDR/aysen-mp25-visualizacion", size=12.5, bold=True, color=INK)
    add_notes(s12, "[6:15–6:55 | 40s] Mostrar la transferencia completa: prototipo Dash verificado en Python + proyecto Power BI Desktop Aysen_MP25.pbip (8 tablas TMDL, 32 medidas DAX, 3 páginas PBIR y 0 errores de esquema).")

    # ---------------- SLIDE 13: FORTALEZAS Y LIMITACIONES ----------------
    s13 = prs.slides.add_slide(blank)
    add_chrome(s13, "11 · Evaluación Crítica", "Fortalezas y Limitaciones del Estudio", "Fortalezas y Limitaciones", 13)

    add_section_heading(s13, 0.72, 0.90, 11.89, "Balance metodológico", "Lo que el análisis demuestra y sus fronteras", 26)

    add_text(s13, 0.72, 2.28, 5.55, 0.26, "FORTALEZAS", size=9.5, bold=True, color=INK_SUB)
    add_em_bullets(
        s13,
        0.72,
        2.66,
        5.55,
        3.95,
        [
            ("13 años oficiales:", "Más de 98% de completitud de MP2,5 en Coyhaique II y auditoría de 25 series SINCA."),
            ("Control del año 2026:", "Tratamiento auditable de vacíos, regla DS 12 y ventana YTD comparable sin sesgos."),
            ("Rigor cuantitativo:", "STL robusto, K-Means estable (ARI 0,974), validación temporal y selección visual objetiva."),
            ("Transferencia completa:", "Proyecto Power BI (PBIP + TMDL + PBIR) construido y validado con esquema estrella y 32 medidas DAX."),
        ],
        font_size=12.6,
        space_after=13,
    )

    add_line(s13, 6.58, 2.25, 0.015, 4.35, HAIRLINE)

    add_text(s13, 6.95, 2.28, 5.66, 0.26, "LIMITACIONES", size=9.5, bold=True, color=INK_SUB)
    add_em_bullets(
        s13,
        6.95,
        2.66,
        5.66,
        3.95,
        [
            ("Sin dirección horaria:", "SINCA solo entrega rosa agregada histórica; impide filtrar direcciones por episodio."),
            ("Variables ausentes:", "No se cuenta con precipitación horaria ni altura de capa límite atmosférica."),
            ("Brecha territorial:", "Solo 4 estaciones; meteorología incompleta en Vialidad (60,6%) e inexistente en Cochrane."),
            ("Asociación, no causalidad:", "Diseño observacional con datos preliminares en 2026 (16,6%–31,9%)."),
        ],
        font_size=12.6,
        space_after=13,
    )
    add_notes(s13, "[6:55–7:25 | 30s] Balance transparente de fortalezas metodológicas y limitaciones reales del dataset SINCA.")

    # ---------------- SLIDE 14: CONCLUSIONES Y CIERRE ----------------
    s14 = prs.slides.add_slide(blank)
    add_chrome(s14, "12 · Conclusiones y Trabajo Futuro", "Fin de la Presentación", "Muchas Gracias · Maximiliano del Río Lincoñir & Patricio Aylwin Retamal", 14, with_rules=False)
    add_watermark(s14, "14")

    add_text(s14, 0.72, 1.25, 8.0, 0.24, "SÍNTESIS FINAL", size=9.5, bold=True, color=INK_SUB)
    add_line(s14, 0.72, 1.57, 0.44, 0.030, RULE_ACCENT)
    add_text(
        s14,
        0.72,
        1.78,
        11.2,
        1.95,
        "La contaminación disminuyó en una década, pero el estancamiento anticiclónico invernal mantiene en riesgo a Coyhaique y Cochrane.",
        size=31,
        bold=True,
        color=INK,
        line_spacing=1.15,
    )

    add_line(s14, 0.72, 4.10, 11.89, 0.014, HAIRLINE)

    future = [
        ("RECOMENDACIÓN 01", "Ampliar instrumentación meteorológica completa a Cochrane y publicar dirección horaria de viento en SINCA."),
        ("TRABAJO FUTURO 02", "Integrar series de precipitación de la DMC y desplegar el proyecto PBIP en Power BI Service con actualización periódica."),
        ("TRABAJO FUTURO 03", "Evaluar modelos dinámicos SARIMAX de 24–48 horas apoyados en la persistencia AR(1) y el régimen sinóptico."),
    ]
    for i, (tag, txt) in enumerate(future):
        x = 0.72 + i * 4.07
        if i > 0:
            add_line(s14, x - 0.17, 4.38, 0.015, 1.90, HAIRLINE)
        add_text(s14, x, 4.40, 3.74, 0.24, tag, size=9.0, bold=True, color=INK_SUB)
        add_text(s14, x, 4.74, 3.74, 1.55, txt, size=12.8, color=INK, line_spacing=1.32)

    add_line(s14, 0.72, 6.76, 11.89, 0.014, HAIRLINE)
    add_notes(s14, "[7:25–8:00 | 35s] Cerrar con la síntesis respaldada en [1], [2], [6], las tres líneas concretas de recomendación/trabajo futuro y abrir preguntas.")

    prs.save(str(PPTX_PATH))
    print(f"PPTX guardado ({len(prs.slides)} slides): {PPTX_PATH}")


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
    # Self-check: 14 slides, uniform background, single font, uniform color per paragraph
    prs = Presentation(str(PPTX_PATH))
    assert len(prs.slides) == TOTAL_SLIDES, f"Esperadas {TOTAL_SLIDES} slides, hay {len(prs.slides)}"
    for si, slide in enumerate(prs.slides, 1):
        assert slide.background.fill.fore_color.rgb == PARCHMENT, f"Slide {si} no usa fondo pergamino"
        for shp in slide.shapes:
            if shp.has_text_frame:
                for p in shp.text_frame.paragraphs:
                    colors = {r.font.color.rgb for r in p.runs if r.text.strip()}
                    assert len(colors) <= 1, f"Slide {si} mezcla colores en un parrafo: {colors}"
                    for r in p.runs:
                        if r.text.strip():
                            assert r.font.name == FONT_MAIN, f"Slide {si} usa fuente distinta: {r.font.name}"
    assert PDF_PATH.exists() and PDF_PATH.stat().st_size > 100_000
    print("[OK] Verificacion PPTX/PDF superada: 14 slides, 1 fuente, 1 color por parrafo, fondo uniforme.")


if __name__ == "__main__":
    main()
