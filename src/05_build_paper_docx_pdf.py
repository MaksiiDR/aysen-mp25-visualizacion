"""
05_build_paper_docx_pdf.py
--------------------------
Construye el informe final en formato IEEE Conference (doble columna,
Times New Roman, 4 paginas de contenido + 1 pagina adicional de referencias,
exactamente 3 figuras a 300 dpi + 1 tabla = 4 tablas/figuras) en `.docx`
y lo exporta a `.pdf` mediante Microsoft Word COM.
"""

from __future__ import annotations

from pathlib import Path
import win32com.client
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

BASE_DIR = Path(__file__).resolve().parent.parent
INF_DIR = BASE_DIR / "informe"
FIG_DIR = INF_DIR / "figures"
DOCX_PATH = INF_DIR / "paper_aysen_mp25.docx"
PDF_PATH = INF_DIR / "paper_aysen_mp25.pdf"


def set_columns(section, n_cols: int, space_inches: float = 0.22) -> None:
    sectPr = section._sectPr
    cols = sectPr.xpath("./w:cols")[0]
    cols.set(qn("w:num"), str(n_cols))
    cols.set(qn("w:space"), str(int(space_inches * 1440)))


def configure_margins(section) -> None:
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)
    section.top_margin = Inches(0.56)
    section.bottom_margin = Inches(0.58)
    section.left_margin = Inches(0.56)
    section.right_margin = Inches(0.56)


def add_body_para(doc: Document, text: str, first_indent: float = 0.15, space_after: float = 2.0, size: float = 8.6, justify: bool = True) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if justify else WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.first_line_indent = Inches(first_indent)
    pf.space_before = Pt(0)
    pf.space_after = Pt(space_after)
    pf.line_spacing = 1.02
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0, 0, 0)
    return p


def add_section_heading(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_before = Pt(6.5)
    pf.space_after = Pt(2.5)
    pf.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(9.5)
    r.small_caps = True
    r.bold = False
    return p


def add_subsection_heading(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = p.paragraph_format
    pf.space_before = Pt(4.5)
    pf.space_after = Pt(1.5)
    pf.keep_with_next = True
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(9.0)
    r.italic = True
    return p


def add_fullwidth_figure(doc: Document, img_path: Path, caption_text: str, width_in: float = 6.95) -> None:
    """Inserta una figura a ancho completo (1 columna temporal) y vuelve a 2 columnas."""
    sec_fig = doc.add_section(WD_SECTION.CONTINUOUS)
    configure_margins(sec_fig)
    set_columns(sec_fig, 1)

    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(3)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    p_img.add_run().add_picture(str(img_path), width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(4.5)
    p_cap.paragraph_format.line_spacing = 1.02
    r = p_cap.add_run(caption_text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(7.8)

    sec_next = doc.add_section(WD_SECTION.CONTINUOUS)
    configure_margins(sec_next)
    set_columns(sec_next, 2)


def set_table_borders_ieee(table) -> None:
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="none"/>'
        '<w:insideV w:val="none"/>'
        '<w:left w:val="none"/>'
        '<w:right w:val="none"/>'
        "</w:tblBorders>"
    )
    tblPr.append(borders)


def set_row_bottom_border(row, sz: int = 4) -> None:
    for cell in row.cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="000000"/>'
            "</w:tcBorders>"
        )
        tcPr.append(tcBorders)


def set_cell_margins(cell, top=25, bottom=25, left=45, right=45) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def add_ieee_table(doc: Document) -> None:
    """Inserta Tabla I compacta dentro de la columna actual."""
    p_t1 = doc.add_paragraph()
    p_t1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1.paragraph_format.space_before = Pt(4)
    p_t1.paragraph_format.space_after = Pt(0.5)
    p_t1.paragraph_format.keep_with_next = True
    r1 = p_t1.add_run("TABLA I")
    r1.font.name = "Times New Roman"
    r1.font.size = Pt(8.0)

    p_t2 = doc.add_paragraph()
    p_t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2.paragraph_format.space_before = Pt(0)
    p_t2.paragraph_format.space_after = Pt(2.5)
    p_t2.paragraph_format.keep_with_next = True
    r2 = p_t2.add_run("EVALUACIÓN OBJETIVA DE VISTAS VISUALES (115.200 REGISTROS) Y MODELOS EN COYHAIQUE II")
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(7.5)

    rows_data = [
        ("A. Selección visual (puntaje 1–3)", "Perc.", "Clar.", "Esc. (s)", "Total"),
        ("Serie mensual + STL", "3", "3", "3 (0,59)", "12/12*"),
        ("Barras apiladas GEC", "3", "3", "3 (0,09)", "12/12*"),
        ("Heatmap (hora × mes)", "2", "3", "3 (0,08)", "11/12*"),
        ("Calendario 13 años", "1", "2", "3 (0,04)", "8/12"),
        ("B. Clustering (k=3, n=3.949)", "Sil.↑", "DB↓", "CH↑", "ARI↑"),
        ("K-Means (k=3)", "0,246", "1,363", "2068,8", "0,974"),
        ("Ward (k=3)", "0,199", "1,498", "1713,6", "—"),
        ("GMM (k=3)", "0,198", "1,557", "1733,6", "0,742"),
        ("C. Validación test 2024–26", "F1↑", "Prec.", "Rec.", "PR-AUC"),
        ("Persistencia (t-1)", "0,739", "0,739", "0,739", "0,825"),
        ("Reg. Log. (Met.)", "0,787", "0,652", "0,993", "0,936"),
        ("Random Forest (Met.)", "0,802", "0,678", "0,983", "0,943"),
        ("Grad. Boost. (Met.)", "0,833", "0,743", "0,948", "0,948"),
        ("Grad. Boost. (Met.+lag1)", "0,857", "0,796", "0,927", "0,945"),
    ]
    header_rows = {0, 5, 9}
    bold_rows = {1, 2, 3, 6, 14}
    col_widths = [Inches(1.50), Inches(0.42), Inches(0.42), Inches(0.54), Inches(0.54)]

    tbl = doc.add_table(rows=len(rows_data), cols=5)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders_ieee(tbl)

    for r_idx, r_vals in enumerate(rows_data):
        row = tbl.rows[r_idx]
        if r_idx in header_rows:
            set_row_bottom_border(row, sz=4)
        for c_idx, val in enumerate(r_vals):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            set_cell_margins(cell, top=16, bottom=16, left=24, right=24)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            run = p.add_run(val)
            run.font.name = "Times New Roman"
            run.font.size = Pt(7.1)
            if r_idx in header_rows or (r_idx in bold_rows and c_idx in {0, 4}):
                run.bold = True

    p_fn = doc.add_paragraph()
    p_fn.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_fn.paragraph_format.space_before = Pt(1.5)
    p_fn.paragraph_format.space_after = Pt(4)
    r_fn = p_fn.add_run("*Incluye 3/3 en utilidad para los objetivos; calendario obtuvo 2/3 por saturación visual.")
    r_fn.font.name = "Times New Roman"
    r_fn.font.size = Pt(6.8)
    r_fn.italic = True


def build_docx() -> None:
    doc = Document()

    # Seccion 0: Cabecera 1 columna (Titulo + curso + autores)
    sec0 = doc.sections[0]
    configure_margins(sec0)
    set_columns(sec0, 1)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(3)
    rt = p_title.add_run("Caracterización visual y temporal de episodios de MP2,5 y clima en la Región de Aysén")
    rt.font.name = "Times New Roman"
    rt.font.size = Pt(19)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(6)
    rs = p_sub.add_run("EIN092B VISUALIZACIÓN – Profesor: Jorge Portilla")
    rs.font.name = "Times New Roman"
    rs.font.size = Pt(9.5)
    rs.bold = True

    # Tabla de autores sin bordes (2 columnas centradas)
    t_auth = doc.add_table(rows=1, cols=2)
    t_auth.alignment = WD_TABLE_ALIGNMENT.CENTER
    authors = [
        ("Maximiliano del Río Lincoñir", "Departamento de Informática", "Universidad Técnica Federico Santa María", "Chile", "mdelrio@usm.cl"),
        ("Patricio Aylwin Retamal", "Departamento de Informática", "Universidad Técnica Federico Santa María", "Chile", "paylwin@usm.cl"),
    ]
    for i, a in enumerate(authors):
        cell = t_auth.rows[0].cells[i]
        cell.width = Inches(3.5)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.05
        r0 = p.add_run(a[0] + "\n")
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10)
        for line in a[1:3]:
            r_it = p.add_run(line + "\n")
            r_it.font.name = "Times New Roman"
            r_it.font.size = Pt(8.8)
            r_it.italic = True
        r_end = p.add_run(f"{a[3]}\n{a[4]}")
        r_end.font.name = "Times New Roman"
        r_end.font.size = Pt(8.8)

    # Seccion 1: Cuerpo en 2 columnas
    sec1 = doc.add_section(WD_SECTION.CONTINUOUS)
    configure_margins(sec1)
    set_columns(sec1, 2)

    # Resumen (Abstract) <= 250 palabras
    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_abs.paragraph_format.space_before = Pt(2)
    p_abs.paragraph_format.space_after = Pt(3.5)
    p_abs.paragraph_format.line_spacing = 1.03
    ra_lbl = p_abs.add_run("Resumen—")
    ra_lbl.font.name = "Times New Roman"
    ra_lbl.font.size = Pt(8.5)
    ra_lbl.bold = True
    ra_lbl.italic = True
    abstract_body = (
        "La contaminación por material particulado fino (MP2,5) derivada de la combustión residencial de leña constituye "
        "un problema crítico de salud pública en la Región de Aysén. Este trabajo diseña y evalúa una arquitectura de "
        "análisis visual y de series de tiempo sobre 25 archivos horarios oficiales del SINCA (2013–2026) provenientes de "
        "cuatro estaciones: Coyhaique II, Coyhaique, Vialidad (Puerto Aysén) y Cochrane. La metodología incorpora una "
        "auditoría explícita de datos faltantes y del año incompleto 2026 (corte 23 de octubre) mediante ventanas "
        "comparables acumuladas (ene–oct) e invernales (abr–sep), descomposición STL robusta, pruebas de tendencia de "
        "Mann–Kendall y pendiente de Sen, correlación cruzada con variables meteorológicas, reducción de dimensionalidad "
        "mediante PCA y comparación objetiva de algoritmos de agrupamiento y validación explicativa temporal. En "
        "Coyhaique II, los días sobre la norma diaria de 50 µg/m³ descendieron significativamente entre 2014 y 2025 "
        "(p = 0,002; −4,93 días/año), aunque 2026 registró un repunte invernal (99 días sobre norma), mientras Cochrane "
        "alcanzó 110 y 130 días en 2024–2025. Dentro del invierno, la velocidad del viento surge como el principal "
        "modulador meteorológico (ρ = −0,686). El modelo K-Means (k = 3, estabilidad temporal ARI = 0,974) aisló un "
        "régimen frío-estancado que concentra el 76,5% de todos los episodios. El aporte principal consiste en un flujo "
        "reproducible en Python, un prototipo interactivo y un modelo estrella listo para Power BI con criterios "
        "cuantitativos de selección visual y analítica."
    )
    assert len(abstract_body.split()) <= 250, f"Resumen excede 250 palabras ({len(abstract_body.split())})"
    ra_txt = p_abs.add_run(abstract_body)
    ra_txt.font.name = "Times New Roman"
    ra_txt.font.size = Pt(8.5)
    ra_txt.bold = True

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_kw.paragraph_format.space_before = Pt(0)
    p_kw.paragraph_format.space_after = Pt(4)
    rkw1 = p_kw.add_run("Palabras clave—")
    rkw1.font.name = "Times New Roman"
    rkw1.font.size = Pt(8.5)
    rkw1.bold = True
    rkw1.italic = True
    rkw2 = p_kw.add_run("Calidad del aire, MP2,5, series de tiempo, visualización de datos, clustering.")
    rkw2.font.name = "Times New Roman"
    rkw2.font.size = Pt(8.5)
    rkw2.bold = True

    # I. INTRODUCCION
    add_section_heading(doc, "I. Introducción")
    add_body_para(
        doc,
        "En las ciudades del sur austral de Chile, las concentraciones de material particulado fino (MP2,5) superan de forma recurrente la norma primaria diaria de 50 µg/m³ fijada por el Decreto Supremo N° 12/2011 [3], debido principalmente al uso intensivo de leña para calefacción domiciliaria durante los meses fríos [1]. Coyhaique fue declarada zona saturada por MP2,5 en 2016 [4] y mantiene promedios invernales que exceden los estándares nacionales e internacionales [2]. Otras localidades de la Región de Aysén, como Puerto Aysén y Cochrane, también cuentan con monitoreo cuyas series son más cortas y presentan mayor proporción de vacíos o registros preliminares [5].",
        first_indent=0.0,
    )
    add_body_para(
        doc,
        "El volumen y la naturaleza multivariada de estos registros —más de 115.000 observaciones horarias por variable en Coyhaique II— dificultan su inspección en tablas estáticas. Aunque el portal SINCA permite descargar cada serie por separado, no ofrece vistas integradas que comparen estaciones, separen tendencia y estacionalidad ni vinculen episodios con meteorología local. Frente a esta brecha, el estudio responde la pregunta: ¿Cómo han evolucionado los episodios de MP2,5 en las ciudades de la Región de Aysén entre 2013 y 2026, y qué condiciones meteorológicas se asocian a su ocurrencia?",
    )
    add_body_para(
        doc,
        "El objetivo general es diseñar y evaluar un conjunto de visualizaciones y modelos de series de tiempo que caractericen la evolución y los regímenes climáticos asociados al MP2,5 en Coyhaique, Puerto Aysén y Cochrane. Los objetivos específicos son: (1) describir patrones diarios, estacionales e interestacionales; (2) cuantificar la tendencia interanual y los días sobre norma controlando vacíos y el cierre parcial de 2026; y (3) relacionar los episodios con temperatura, viento, humedad y presión mediante correlación cruzada, PCA y agrupamiento no supervisado. Los resultados evidencian descensos históricos en Coyhaique y Puerto Aysén, persistencia invernal crítica con repunte en 2026 y severidad elevada en Cochrane. El artículo se organiza en Antecedentes (Sección II), Metodología (Sección III), Resultados y Discusión (Sección IV) y Conclusiones (Sección V).",
    )

    # II. ANTECEDENTES
    add_section_heading(doc, "II. Antecedentes")
    add_subsection_heading(doc, "A. Marco conceptual y antecedentes")
    add_body_para(
        doc,
        "El MP2,5 corresponde a partículas aerotransportadas de diámetro aerodinámico inferior a 2,5 µm capaces de penetrar hasta los alvéolos pulmonares. En Chile, el DS N° 12/2011 establece un límite diario de 50 µg/m³ (promedio de 24 horas con al menos 18 horas válidas) y categorías de Gestión de Episodios Críticos (GEC): Regular (50–79), Alerta (80–109), Preemergencia (110–169) y Emergencia (≥170 µg/m³) [3]. Estudios previos en el centro-sur chileno muestran que las emisiones domiciliarias de biomasa dominan el inventario invernal [1], mientras que en Coyhaique el encajonamiento topográfico del valle favorece inversiones térmicas nocturnas que atrapan el humo cerca de la superficie [2].",
        first_indent=0.0,
    )
    add_subsection_heading(doc, "B. Estado del arte")
    add_body_para(
        doc,
        "En ciudades patagónicas y del centro-sur, Solís et al. [2] evaluaron la serie 2014–2020 de Coyhaique mediante estadísticos descriptivos estáticos, documentando la concentración invernal sin abarcar otras localidades regionales ni años recientes. En [6], Martinez-Soto et al. analizaron la influencia meteorológica sobre el MP2,5 en Temuco, confirmando que temperaturas bajas, calma eólica y estabilidad atmosférica explican los episodios extremos en urbes calefaccionadas con combustibles sólidos.",
        first_indent=0.0,
    )
    add_body_para(
        doc,
        "Desde las series de tiempo, la descomposición STL (Seasonal-Trend decomposition using Loess) [9] separa de forma robusta la tendencia de largo plazo, la estacionalidad anual y los residuos atípicos sin sufrir distorsión por picos invernales [12]. Para sintetizar variables correlacionadas y descubrir regímenes sinópticos se emplean el Análisis de Componentes Principales (PCA) [10] y agrupamiento validado con índices internos como la silueta [11]. En el plano visual, Munzner [7] y la jerarquía perceptual de Cleveland y McGill [8] fundamentan el uso de posición sobre una escala común (series y barras) para comparaciones precisas y color para grillas densas como los mapas de calor hora × mes. Este trabajo integra estas tres vertientes sobre registros hasta octubre de 2026 con salida estructurada para Power BI.",
    )

    # III. METODOLOGIA
    add_section_heading(doc, "III. Metodología")
    add_body_para(
        doc,
        "El código reproducible, los scripts de auditoría, el prototipo Dash y el paquete Power BI (esquema estrella y medidas DAX) se publican en el repositorio del proyecto (github.com/MaksiiDR/aysen-mp25-visualizacion).",
        first_indent=0.0,
    )
    add_subsection_heading(doc, "A. Datos, manejo de faltantes, año 2026 y rosa de vientos")
    add_body_para(
        doc,
        "Se procesaron 25 archivos CSV descargados del SINCA [5] en octubre de 2026: 22 series horarias y 3 tablas de frecuencias direccionales de viento para Coyhaique II (sep. 2013–oct. 2026; 115.200 filas por variable), Coyhaique (mar. 2013–oct. 2026 en MP2,5), Vialidad en Puerto Aysén (oct. 2017–oct. 2026) y Cochrane (mar. 2021–oct. 2026). Siguiendo la prioridad oficial del SINCA se consolidaron registros validados, preliminares y no validados conservando una etiqueta de trazabilidad y filtros de rango físico.",
        first_indent=0.0,
    )
    add_body_para(
        doc,
        "La auditoría inicial definió tres reglas metodológicas clave. Primero, en Coyhaique II se conservaron las variables con >91% de completitud (MP2,5 98,9%, MP10 98,5%, CO 97,6%, SO₂ 97,7%, O₃ 96,6%, presión 99,2%, viento 94,4%, humedad 91,6% y temperatura 91,5%), excluyendo NO₂ (30,0%), NO (9,2%) y NOx (10,0%). Segundo, los promedios diarios exigieron ≥18 h válidas [3] sin imputar huecos largos en indicadores normativos; como todas las series cierran el 23 de octubre de 2026 (80,8% del año en Coyhaique II, 16,6% preliminar/no validado), el año 2026 se trató como incompleto mediante tres vistas: años completos (≥75% de días, excl. 2026), ventana acumulada YTD comparable (1 ene–23 oct) e invierno completo (abr–sep, 100% de cobertura 2026 en Coyhaique y Vialidad; 94,5% en Cochrane). Tercero, se verificó que el dataset no posee dirección horaria del viento, sino tablas agregadas de 24 sectores de 15° (suma 100,0%–100,1%, ausente en Cochrane); así, la rosa de vientos representa el régimen climatológico histórico y los episodios se analizaron con la velocidad horaria/diaria del viento.",
    )
    add_subsection_heading(doc, "B. Arquitectura Python a Power BI y modelos analíticos")
    add_body_para(
        doc,
        "Atendiendo a que el estudio prioriza identificar patrones más que pronosticar en tiempo real, las pruebas preliminares, series de tiempo, agrupamiento y prototipo interactivo (Plotly Dash) se implementaron en Python, exportando un esquema estrella limpio (dim_estacion, dim_fecha con banderas YTD/invierno y seis tablas de hechos) más medidas DAX para el informe ejecutivo en Power BI.",
        first_indent=0.0,
    )
    add_body_para(
        doc,
        "El análisis temporal aplicó: (a) descomposición STL robusta mensual (periodo = 12, suavizador estacional = 13, contrastada contra STL no robusta) sobre meses con ≥75% de días válidos, interpolando solo huecos aislados para el ajuste STL; (b) prueba de Mann–Kendall y pendiente de Sen sobre promedios y conteos de días >50 µg/m³; (c) autocorrelación (ACF/PACF, 1–14 días); y (d) correlación cruzada de Spearman (CCF, rezagos k ∈ [−5, +5] días) más pruebas de Mann–Whitney entre días episodio y normales.",
    )
    add_body_para(
        doc,
        "Para descubrir regímenes diarios en Coyhaique II (n = 3.949 días completos, ago. 2015–oct. 2026) se estandarizaron seis variables con log(1 + x) en contaminantes asimétricos (log MP2,5, log CO, temperatura, humedad, viento y presión) y se aplicó PCA [10]. Se compararon K-Means, Gaussian Mixture Model (GMM, covarianza completa) y Ward jerárquico para k ∈ {2,...,6} mediante Silueta [11], Davies–Bouldin (DB), Calinski–Harabasz (CH) y estabilidad temporal (Adjusted Rand Index, ARI, ajustando en 2015–2020 y evaluando en 2021–2026). Como validación explicativa complementaria de la relación clima–episodio, se ajustaron Regresión Logística, Random Forest y Gradient Boosting mediante GridSearchCV con TimeSeriesSplit (5 particiones, optimizando F1) en 2015–2023 (n = 2.982) y prueba fuera de muestra en 2024–2026 (n = 1.021; 28,1% episodios) frente a una línea base de persistencia (t−1). Finalmente, las vistas candidatas se puntuaron de 1 a 3 en precisión perceptual [8], claridad, escalabilidad medida sobre 115.200 filas (<15 s) y utilidad.",
    )

    # IV. RESULTADOS Y DISCUSION
    add_section_heading(doc, "IV. Resultados y Discusión")
    add_subsection_heading(doc, "A. Resultados")
    add_body_para(
        doc,
        "La Fig. 1 resume la evolución temporal del MP2,5. En los 4.761 días válidos de Coyhaique II ocurrieron 1.412 días >50 µg/m³ (29,7%) y 202 emergencias (≥170 µg/m³), con máximo diario de 945,0 µg/m³. La estación Coyhaique exhibió un patrón equivalente (1.430 días >50; 28,9%; Spearman ρ = 0,958 con Coyhaique II, n = 4.732). Vialidad registró menor carga (300 días >50; 9,5% en 3.162 días; 1 emergencia), mientras Cochrane acumuló 564 días >50 en 1.609 días válidos (35,1%; 31 emergencias), alcanzando 110 y 130 días en sus únicos años completos validados (2024 y 2025). Pese a la distancia, las series diarias muestran alta sincronía regional: Coyhaique II correlaciona con Vialidad (ρ = 0,829, n = 3.148) y Cochrane (ρ = 0,822, n = 1.606, p < 0,001).",
        first_indent=0.0,
    )
    add_body_para(
        doc,
        "En la descomposición STL (Fig. 1a), la fuerza estacional superó 0,80 en todas las estaciones (0,807 en Coyhaique II; 0,803 en Coyhaique; 0,945 en Vialidad y Cochrane). La variante robusta redujo casi a la mitad la desviación mediana absoluta residual en Coyhaique II (2,81 vs. 5,01 µg/m³ no robusta). La tendencia STL descendió de 57,95 a 31,82 µg/m³ en Coyhaique II y de 27,69 a 17,82 µg/m³ en Vialidad. La prueba de Mann–Kendall en años completos de Coyhaique II (2014–2025) confirmó caídas significativas en la media anual (p = 0,0075; Sen −1,83 µg/m³/año) y en días >50 (p = 0,0020; −4,93 días/año), desde 156 días en 2014 hasta un mínimo de 75 en 2021 (Fig. 1b). Al incluir 2026 con la ventana YTD comparable (que contiene el 99,7% de los episodios históricos), el descenso en días >50 se mantiene (p = 0,0049; −3,75 días/año), pero el invierno 2026 repuntó a 77,5 µg/m³ (99 días >50, con 33 preemergencias y 15 emergencias frente a 17 y 10 en 2025), dejando la media invernal en el borde de significancia (p = 0,0586). En Vialidad el invierno 2018–2026 cayó significativamente (p = 0,0211; −4,38 días/año, de 61 a 16 días), mientras Cochrane no presentó tendencia significativa (p > 0,30).",
    )
    add_body_para(
        doc,
        "El mapa de calor hora × mes de Coyhaique II (Fig. 1c) muestra una razón invierno/verano de 5,1× (77,7 vs. 15,1 µg/m³). El ciclo diario invernal es bimodal: presenta un repunte matutino a las 08:00 h y un máximo nocturno sostenido entre 18:00 y 00:00 h, con media invernal de 141,1 µg/m³ a las 20:00 h (191,8 µg/m³ en junio a las 21:00 h) frente a un mínimo de 40,0 µg/m³ a las 14:00 h.",
    )

    # FIG 1 (full-width, compacta)
    add_fullwidth_figure(
        doc,
        FIG_DIR / "fig1_temporal_patterns.png",
        "Fig. 1. Evolución temporal y patrones de MP2,5 en la Región de Aysén (2013–2026). (a) Promedio mensual de Coyhaique II y tendencia STL robusta para Coyhaique II, Vialidad (Puerto Aysén) y Cochrane, señalando la norma DS 12 (50 µg/m³) y el corte parcial de 2026 (ene–23 oct). (b) Días sobre norma en Coyhaique II por categoría GEC; la barra achurada de 2026* cubre el 100% del invierno. (c) Mapa de calor del promedio horario de MP2,5 (hora × mes) en Coyhaique II.",
        width_in=5.85,
    )

    add_body_para(
        doc,
        "La Fig. 2 cuantifica la relación meteorológica en Coyhaique II. En la serie anual (Fig. 2a), las correlaciones contemporáneas (k = 0) alcanzan ρ = −0,780 con temperatura, −0,650 con viento, +0,655 con humedad y +0,126 con presión; sin embargo, dentro del invierno (abr–sep), la velocidad del viento lidera la asociación (ρ = −0,686), por sobre temperatura (−0,512), humedad (+0,443) y presión (+0,183). La persistencia diaria muestra estructura AR(1) marcada (ACF(1) = 0,771; PACF(1) = 0,771; PACF(2) = −0,038). En días >50 µg/m³ respecto a días normales (Fig. 2b; Mann–Whitney p < 10⁻¹²), la mediana de temperatura desciende de 9,92 a 3,74 °C (mínima 0,30 °C), el viento cae 63% (3,04 a 1,13 m/s), la humedad sube de 63,6% a 78,3%, la presión asciende de 971,7 a 973,7 hPa y el CO casi se cuadruplica (0,36 a 1,42 ppm). La rosa climatológica (Fig. 2c) confirma predominio del cuadrante O–ONO (262,5°–307,5°: 41,2%) en Coyhaique II y del OSO (217,5°–262,5°: 27,4%) en Vialidad.",
    )

    # FIG 2 (full-width, compacta)
    add_fullwidth_figure(
        doc,
        FIG_DIR / "fig2_meteorology_wind.png",
        "Fig. 2. Relación entre meteorología, persistencia y MP2,5 en Coyhaique II (2013–2026). (a) Correlación cruzada de Spearman (CCF) entre variables climáticas en t−k y MP2,5 en t, indicando ACF(1d) = 0,77. (b) Distribución diaria de temperatura y velocidad del viento en días normales (≤50 µg/m³) frente a episodios (>50 µg/m³, Mann–Whitney p < 0,001). (c) Rosa de vientos climatológica por 24 sectores de 15° en Coyhaique II y Vialidad.",
        width_in=6.15,
    )

    add_body_para(
        doc,
        "En la Fig. 3, las dos primeras componentes principales explican el 78,2% de la varianza (PC1: 58,3%; PC2: 19,9%). PC1 opone combustión y humedad (log MP2,5: +0,511; log CO: +0,465; humedad: +0,423) frente a temperatura (−0,445) y viento (−0,380); PC2 representa el eje barométrico de presión (+0,873) opuesto a humedad (−0,412). Como reporta la Tabla I, K-Means con k = 3 superó a Ward y GMM en Silueta (0,246), DB (1,363), CH (2068,8) y estabilidad temporal (ARI = 0,974). Aunque k = 2 alcanzó mayor silueta (0,352), solo divide verano e invierno; k = 3 separa tres regímenes nítidos (Fig. 3b): C0 Cálido-Ventilado (n = 1.700; mediana 9,9 µg/m³; 0,3% >50; T = 12,1 °C; viento 3,45 m/s), C1 Frío-Transición (n = 1.341; mediana 30,7 µg/m³; 19,0% >50; T = 6,6 °C; viento 2,31 m/s; presión mínima 967,7 hPa) y C2 Frío-Estancado (n = 908; mediana 102,0 µg/m³; 93,4% >50 —76,5% de todos los episodios— con T = 2,9 °C, viento 1,05 m/s, humedad 78,3%, CO 1,96 ppm y presión máxima 975,3 hPa; 97,0% en invierno).",
    )

    # FIG 3 (full-width, compacta)
    add_fullwidth_figure(
        doc,
        FIG_DIR / "fig3_pca_clusters.png",
        "Fig. 3. Agrupamiento multivariado de regímenes diarios en Coyhaique II (n = 3.949 días completos, 2015–2026). (a) Biplot PCA (78,2% de varianza explicada) coloreado según K-Means (k = 3) con vectores de carga de las seis variables estandarizadas. (b) Tasa de excedencia (>50 µg/m³), mediana de MP2,5, temperatura media y velocidad del viento media por régimen.",
        width_in=6.05,
    )

    add_body_para(
        doc,
        "La Tabla I resume también la selección visual y la validación explicativa. Todas las vistas operaron muy por debajo del límite de 15 s sobre 115.200 registros (carga completa del esquema estrella Power BI en 0,089 s), seleccionándose series STL, barras GEC y heatmap al descartar el calendario multianual por menor precisión perceptual y saturación. En prueba temporal (2024–2026), Gradient Boosting con solo meteorología y ciclo anual (profundidad 3, tasa 0,08, 100 árboles) alcanzó F1 = 0,833 y PR-AUC = 0,948 (ROC-AUC = 0,979) frente a F1 = 0,739 de la persistencia; al sumar MP2,5 en t−1 (profundidad 2, tasa 0,03, 200 árboles) subió a F1 = 0,857 (precisión 0,796; sensibilidad 0,927).",
    )

    # TABLA I (1 columna)
    add_ieee_table(doc)

    # B. DISCUSION
    add_subsection_heading(doc, "B. Discusión")
    add_body_para(
        doc,
        "El ciclo horario bimodal con máximos nocturnos sobre 175 µg/m³ en junio–julio y el aumento paralelo de CO confirman el patrón de calefacción domiciliaria a leña descrito en [1] y [2], atenuado al mediodía por mezcla convectiva. Un aporte central respecto a análisis estáticos previos en Coyhaique [2] es la separación sinóptica entre C1 y C2: durante el invierno siempre hace frío, pero la transición hacia episodios severos ocurre al pasar de frentes de baja presión ventilados (C1: 967,7 hPa; 2,31 m/s) a bloqueos anticiclónicos de alta presión y calma (C2: 975,3 hPa; 1,05 m/s). Esto concuerda con lo reportado para Temuco en [6], explica el liderazgo de la velocidad del viento en invierno (ρ = −0,686) y da sentido a la sincronía regional superior a ρ = 0,82 entre ciudades distantes 200 km.",
        first_indent=0.0,
    )
    add_body_para(
        doc,
        "Interanualmente, la caída 2014–2021 coincide con el despliegue del Plan de Descontaminación en Coyhaique, pero la meseta de 91–99 días >50 entre 2023 y 2026 y la situación de Cochrane (110–130 días en 2024–2025) muestran que la exposición crítica persiste a escala regional. Asimismo, la ventana YTD evitó subestimar 2026 y reveló el alza de preemergencias invernales.",
    )

    # C. FORTALEZAS Y LIMITACIONES
    add_subsection_heading(doc, "C. Fortalezas y limitaciones")
    add_body_para(
        doc,
        "Fortalezas: serie oficial de 13 años con >98% de completitud en MP2,5 de Coyhaique II; tratamiento transparente de vacíos y del cierre parcial 2026; integración de series de tiempo (STL, Mann–Kendall, CCF), PCA/K-Means estable (ARI = 0,974) y validación temporal objetiva; y entrega de prototipo interactivo Python más esquema estrella listo para Power BI.",
        first_indent=0.0,
    )
    add_body_para(
        doc,
        "Limitaciones: ausencia de dirección horaria del viento en SINCA (impidiendo rosas condicionadas por episodio); falta de datos de precipitación y capa límite; solo cuatro estaciones con meteorología parcial en Vialidad (60,6%) e inexistente en Cochrane; proporción de registros preliminares/no validados en 2026 (16,6% en Coyhaique II; 31,9% en Cochrane) y en Cochrane 2021–2023; y carácter observacional que establece asociación estadística y no causalidad directa.",
    )

    # V. CONCLUSIONES
    add_section_heading(doc, "V. Conclusiones")
    add_body_para(
        doc,
        "Se caracterizaron la evolución espaciotemporal del MP2,5 y sus regímenes climáticos en la Región de Aysén (2013–2026) integrando auditoría de datos faltantes, descomposición STL robusta, pruebas de tendencia, CCF, PCA/K-Means y visualización interactiva orientada a Power BI. La contaminación mantiene estacionalidad extrema (fuerza STL >0,80) y picos nocturnos ligados a combustión de leña [1], [2]. Aunque Coyhaique II redujo significativamente sus episodios entre 2014 y 2025 (−4,93 días/año, p = 0,002) y Puerto Aysén descendió en invierno (−4,38 días/año), el repunte invernal 2026 en Coyhaique (99 días >50) y la severidad en Cochrane (hasta 130 días/año) demuestran vulnerabilidad vigente. K-Means (k = 3) aisló un régimen anticiclónico frío-estancado responsable del 76,5% de los episodios, y la meteorología explicó su ocurrencia con PR-AUC = 0,948, en línea con [6]. Se recomienda incorporar instrumentación meteorológica completa en Cochrane y publicar dirección horaria de viento en SINCA. Como trabajo futuro se plantea integrar precipitación de la DMC, desplegar el panel en Power BI Service con refresco periódico y evaluar modelos SARIMAX para alertas tempranas de 24–48 horas.",
        first_indent=0.0,
    )

    # PAGINA 5: REFERENCIAS (salto de pagina explicito para respetar 4 paginas contenido + 1 pagina referencias)
    doc.add_page_break()
    add_section_heading(doc, "Referencias")

    refs = [
        '[1] C. Molina, R. Toro A., R. G. E. Morales S., C. Manzano, and M. A. Leiva-Guzmán, "Particulate matter in urban areas of south-central Chile exceeds air quality standards," Air Qual. Atmos. Health, vol. 10, no. 5, pp. 653–667, Jun. 2017.',
        '[2] R. Solís et al., "Long-term airborne particle pollution assessment in the city of Coyhaique, Patagonia, Chile," Urban Climate, vol. 43, Art. no. 101144, May 2022, doi: 10.1016/j.uclim.2022.101144.',
        '[3] Ministerio del Medio Ambiente, "Decreto Supremo N° 12: Establece norma primaria de calidad ambiental para material particulado fino respirable MP2,5," Diario Oficial de la República de Chile, Santiago, Chile, 2011.',
        '[4] Ministerio del Medio Ambiente, "Decreto Supremo N° 15: Declara zona saturada por MP2,5 como concentración de 24 horas a la ciudad de Coyhaique y su zona circundante," Santiago, Chile, 2016.',
        '[5] Ministerio del Medio Ambiente, "Sistema de Información Nacional de Calidad del Aire (SINCA)." https://sinca.mma.gob.cl (accedido oct. 2026).',
        '[6] A. Martinez-Soto, M. F. Jentsch, V. Martinez-Gallegos, J. Duchêne, and A. Zipf, "Influence of meteorological variables on PM2.5 concentrations in cities heated with solid fuels: A case study from Temuco, Chile," Atmos. Environ. X, vol. 25, Art. no. 100401, 2025, doi: 10.1016/j.aeaoa.2025.100401.',
        '[7] T. Munzner, Visualization Analysis and Design. Boca Raton, FL, USA: CRC Press, 2014.',
        '[8] W. S. Cleveland and R. McGill, "Graphical perception: Theory, experimentation, and application to the development of graphical methods," J. Amer. Statist. Assoc., vol. 79, no. 387, pp. 531–554, Sep. 1984.',
        '[9] R. B. Cleveland, W. S. Cleveland, J. E. McRae, and I. Terpenning, "STL: A seasonal-trend decomposition procedure based on Loess," J. Official Statist., vol. 6, no. 1, pp. 3–73, 1990.',
        '[10] I. T. Jolliffe and J. Cadima, "Principal component analysis: A review and recent developments," Phil. Trans. Roy. Soc. A, vol. 374, no. 2065, Art. no. 20150202, Apr. 2016.',
        '[11] P. J. Rousseeuw, "Silhouettes: A graphical aid to the interpretation and validation of cluster analysis," J. Comput. Appl. Math., vol. 20, pp. 53–65, Nov. 1987.',
        '[12] R. J. Hyndman and G. Athanasopoulos, Forecasting: Principles and Practice, 3rd ed. Melbourne, Australia: OTexts, 2021.',
    ]
    for ref in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = p.paragraph_format
        pf.left_indent = Inches(0.22)
        pf.first_line_indent = Inches(-0.22)
        pf.space_before = Pt(0)
        pf.space_after = Pt(2.8)
        pf.line_spacing = 1.04
        r = p.add_run(ref)
        r.font.name = "Times New Roman"
        r.font.size = Pt(8.0)

    doc.save(str(DOCX_PATH))
    print(f"DOCX guardado: {DOCX_PATH}")


def export_pdf_via_word() -> int:
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(DOCX_PATH.resolve()))
        doc.Repaginate()
        n_pages = int(doc.ComputeStatistics(2))  # wdStatisticPages = 2
        doc.SaveAs(str(PDF_PATH.resolve()), FileFormat=17)  # wdFormatPDF = 17
        doc.Close(False)
        return n_pages
    finally:
        word.Quit()


def main() -> None:
    build_docx()
    n_pages = export_pdf_via_word()
    print(f"PDF exportado: {PDF_PATH} | Total paginas = {n_pages}")
    assert PDF_PATH.exists() and PDF_PATH.stat().st_size > 50000


if __name__ == "__main__":
    main()
