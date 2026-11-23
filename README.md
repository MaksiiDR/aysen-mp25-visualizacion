# Caracterización visual y temporal de episodios de MP2,5 y clima en la Región de Aysén (2013–2026)

**Asignatura:** EIN092B Visualización — Ingeniería en Informática, Universidad Técnica Federico Santa María (UTFSM)  
**Profesor:** Jorge Portilla  
**Grupo N° 2:** Maximiliano del Río Lincoñir (`mdelrio@usm.cl`) y Patricio Aylwin Retamal (`paylwin@usm.cl`)

---

## Descripción general

Este repositorio contiene el flujo completo y reproducible para el análisis visual, de series de tiempo y de agrupamiento multivariado de los episodios de material particulado fino (**MP2,5**) y su relación con variables meteorológicas en cuatro estaciones oficiales del **SINCA** (Ministerio del Medio Ambiente) en la Región de Aysén:

- **Coyhaique II** (sep. 2013 – oct. 2026; 115.200 registros horarios por variable; 98,9% completitud en MP2,5)
- **Coyhaique** (mar. 2013 – oct. 2026 en MP2,5; 99,2% completitud)
- **Vialidad — Puerto Aysén** (oct. 2017 – oct. 2026; 96,3% MP2,5; meteorología parcial 60,6%)
- **Cochrane** (mar. 2021 – oct. 2026; solo MP2,5; 78,6% completitud)

### Incorporación de retroalimentación (Presentación 1)
1. **Enfoque en series de tiempo + migración a Power BI:** Se aplican descomposición STL robusta, pruebas no paramétricas de Mann–Kendall y pendiente de Sen, ACF/PACF, correlación cruzada (CCF), PCA y comparación objetiva de clustering (K-Means, GMM, Ward) en Python, exportando un **esquema estrella normalizado** y **medidas DAX** listos para Power BI Desktop (`powerbi/`), además de un prototipo interactivo en Plotly Dash (`dashboard/app.py`).
2. **Manejo explícito de datos faltantes y año incompleto 2026:** Se auditan registros validados, preliminares y no validados, se aplica estrictamente la regla DS N° 12/2011 (`≥ 18 h válidas` por día), se descartan variables con `> 70%` de vacíos (`NO`, `NOx`, `NO₂`), y se controla el cierre parcial del 23 de octubre de 2026 mediante ventanas comparables acumuladas (**YTD ene–23 oct**) e **invernales (abr–sep, 100% cobertura 2026)**.
3. **Verificación de rosa de vientos:** La auditoría confirmó que SINCA no entrega dirección horaria del viento, sino tablas históricas agregadas de 24 sectores de 15° (ausentes en Cochrane). Por ello, la rosa muestra el régimen climatológico predominante y la asociación con episodios se analiza mediante velocidad horaria/diaria del viento.

---

## Estructura del repositorio

```text
.
├── src/
│   ├── 01_clean_and_audit.py       # Ingesta de 25 CSV SINCA, auditoría de calidad/2026 YTD y exportación esquema estrella
│   ├── 02_timeseries_and_ml.py     # STL robusto, Mann–Kendall/Sen, ACF/CCF, PCA, K-Means/GMM/Ward, TimeSeriesSplit
│   ├── 03_generate_figures.py      # Figuras 300 dpi para informe IEEE (3 figs) y presentación (5 figs)
│   ├── 04_verify_all.py            # Pruebas de integridad, callbacks del dashboard y benchmark de escalabilidad
│   ├── 05_build_paper_docx_pdf.py  # Generación del paper IEEE (.docx y .pdf)
│   └── 06_build_presentation.py    # Generación de la presentación final (.pptx y .pdf)
├── dashboard/
│   └── app.py                      # Prototipo interactivo en Plotly Dash (5 pestañas + filtros YTD/invierno)
├── powerbi/
│   ├── data/                       # Esquema estrella (dim_estacion, dim_fecha y 6 tablas de hechos CSV)
│   ├── medidas.dax                 # Medidas DAX (norma DS 12, GEC, YTD comparable, completitud)
│   └── README_PowerBI.md           # Guía de modelado, relaciones y diseño de páginas en Power BI Desktop
├── data_processed/                 # Resúmenes reproducibles, resultados JSON y métricas de evaluación
├── informe/
│   ├── paper_aysen_mp25.pdf        # Informe final IEEE en español (4 páginas contenido + 1 página referencias)
│   ├── paper_aysen_mp25.docx       # Versión Word IEEE doble columna
│   ├── paper_aysen_mp25.tex        # Fuente LaTeX IEEEtran (listo para Overleaf)
│   ├── referencias.bib             # Bibliografía en formato IEEE numérico
│   └── figures/                    # 3 figuras en alta resolución (300 dpi)
├── presentacion/
│   ├── presentacion_aysen_mp25.html                # Presentación web interactiva estilo editorial pergamino (14 slides, 1920×1080)
│   ├── Presentacion_Final_Grupo2_Aysen_MP25.pptx
│   ├── Presentacion_Final_Grupo2_Aysen_MP25.pdf
│   ├── guion_8min.md                               # Distribución de tiempos (8:00 min) y respuestas preparadas
│   └── figures/                                    # Gráficos widescreen a 300 dpi
└── requirements.txt
```

---

## Reproducción rápida

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Ejecutar pipeline completo (requiere carpeta ../datos con los 25 CSV de SINCA)
python src/01_clean_and_audit.py
python src/02_timeseries_and_ml.py
python src/03_generate_figures.py
python src/04_verify_all.py

# 3. Lanzar prototipo interactivo Plotly Dash (http://127.0.0.1:8050)
python dashboard/app.py
```

> Nota: Las tablas agregadas del esquema estrella (`powerbi/data/`) y los resultados resumidos (`data_processed/*.csv`, `*.json`) ya están incluidos en el repositorio para permitir ejecutar el dashboard y montar Power BI sin descargar nuevamente los archivos crudos del SINCA.

---

## Resultados principales

- **Tendencia interanual (Mann–Kendall / Sen):** Coyhaique II descendió significativamente entre 2014 y 2025 (`−4,93 días/año`, `p = 0,0020`), y Vialidad (Puerto Aysén) en invierno 2018–2026 (`−4,38 días/año`, `p = 0,0211`). Sin embargo, Coyhaique II registró un repunte en el invierno 2026 (`99 días > 50 µg/m³`, 33 preemergencias) y Cochrane alcanzó `110` y `130 días > 50` en 2024–2025.
- **Ciclo horario y estacional:** Fuerza estacional STL `> 0,80` en todas las estaciones; razón invierno/verano de `5,1×` en Coyhaique II (`77,7` vs. `15,1 µg/m³`), con pico nocturno promedio de `141,1 µg/m³` a las 20:00 h (`191,8 µg/m³` en junio a las 21:00 h).
- **Meteorología y regímenes (PCA + K-Means):** En invierno, la velocidad del viento lidera la correlación con MP2,5 (`ρ = −0,686`). **K-Means (`k = 3`, ARI temporal `0,974`)** superó a Ward y GMM, aislando un régimen anticiclónico **Frío-Estancado** (`T = 2,9 °C`, `viento = 1,05 m/s`, `presión = 975,3 hPa`) que concentra el **76,5%** de todos los episodios (`93,4%` de sus días superan `50 µg/m³`).
- **Validación explicativa temporal (test 2024–2026):** `Gradient Boosting` usando solo meteorología alcanzó `PR-AUC = 0,948` (`F1 = 0,833`), y `F1 = 0,857` al agregar `MP2,5(t−1)`.
- **Escalabilidad verificada:** Carga completa del esquema estrella Power BI en `0,089 s` y generación de vistas desde 115.200 filas horarias en `< 0,6 s`.
