# Guion Hablado (Versión Clara) — Presentación Final (8 min)

**Grupo N° 2:** Maximiliano del Río Lincoñir y Patricio Aylwin Retamal  
**Asignatura:** EIN092B Visualización — Prof. Jorge Portilla (UTFSM)  
**División sugerida:** **Patricio** Slides 1–8 (4:15) · **Maximiliano** Slides 9–14 (3:45)  
*Al final del documento viene el **Glosario rápido** con qué significa y cómo se dice cada sigla técnica.*

---

## Parte 1 — Patricio (Slides 1 a 8 · 4:15 min)

### Slide 1 · Portada `[0:00 – 0:20 | 20 s]`
> "Buenos días profesor y compañeros. Somos el Grupo 2, integrado por Maximiliano del Río y quien les habla, Patricio Aylwin. Hoy presentamos nuestro análisis visual y temporal de los episodios de **MP2,5 y clima en la Región de Aysén**, usando 13 años de datos oficiales del SINCA entre 2013 y 2026."

### Slide 2 · Contexto y Problemática `[0:20 – 0:55 | 35 s]`
> "Partamos por qué es el **MP2,5**: son partículas microscópicas de humo —unas 25 veces más finas que un cabello— que pasan los filtros de la nariz y llegan directo al pulmón y a la sangre. En Coyhaique vienen principalmente de la calefacción a leña entre abril y septiembre.  
> El problema es que el portal SINCA entrega más de 115 mil filas horarias por variable en tablas sueltas, sin comparar ciudades ni cruzar los datos con el clima. Por eso buscamos responder **cómo han evolucionado estos episodios entre 2013 y 2026 y qué condiciones climáticas los acompañan**, cumpliendo tres objetivos: ver patrones horarios, medir tendencias limpias y detectar qué combinaciones de clima disparan los episodios."

### Slide 3 · Dataset SINCA y Normativa `[0:55 – 1:30 | 35 s]`
> "Trabajamos con **25 archivos públicos** del Ministerio del Medio Ambiente cortados al **23 de octubre de 2026**: 22 series horarias y 3 tablas históricas de dirección del viento.  
> Como muestra la tabla, **Coyhaique II** es la estación más completa con 115.200 horas y todas las variables climáticas; **Coyhaique** tiene la serie más larga; **Vialidad** en Puerto Aysén tiene clima parcial; y **Cochrane** solo mide MP2,5 desde 2021.  
> Según la norma chilena **DS N° 12**, un día es válido solo si tiene al menos 18 horas medidas, y supera la norma cuando pasa los **50 µg/m³** en promedio diario, clasificándose en cinco niveles desde Bueno hasta Emergencia."

### Slide 4 · Retroalimentación Presentación 1 `[1:30 – 2:05 | 35 s]`
> "Atendimos directamente las tres observaciones que nos dejó el profesor en la Presentación 1:  
> **Primero**, enfocamos el trabajo en **análisis de series de tiempo** —para separar tendencia, estacionalidad y relación con el clima— y armamos el informe final en **Power BI**.  
> **Segundo**, auditamos los datos faltantes y el año 2026 incompleto: descartamos los gases de óxidos de nitrógeno (NO, NOx y NO₂) porque tenían más de 70% de vacíos, y separamos 2026 en ventanas comparables.  
> **Tercero**, comprobamos que SINCA no entrega dirección horaria del viento, solo tablas históricas resumidas en tres estaciones; así que usamos la rosa solo como referencia histórica y la velocidad del viento para analizar episodios."

### Slide 5 · Auditoría de Datos SINCA `[2:05 – 2:40 | 35 s]`
> "Este mapa muestra qué porcentaje de días válidos tiene cada estación por año. Coyhaique II y Coyhaique superan el **98%** de cobertura.  
> El punto clave es **2026**: como los datos llegan hasta el 23 de octubre, el año está al 81%, pero el **invierno completo de abril a septiembre está al 100%**. Además, entre el 1 de enero y el 23 de octubre ocurre el **99,7%** de los episodios históricos de Coyhaique II; por eso usamos esa ventana acumulada —llamada **YTD**— para comparar 2026 con años anteriores sin sesgo. También dejamos transparente que Cochrane entre 2021 y 2023 tiene datos no validados, por lo que sus años confiables son 2024 y 2025."

### Slide 6 · Metodología y Selección Objetiva `[2:40 – 3:15 | 35 s]`
> "Para no elegir gráficos ni modelos al ojo, usamos criterios medibles. A la izquierda evaluamos cuatro gráficos candidatos según qué tan preciso los lee el ojo humano —la regla de Cleveland y McGill—, su claridad y su velocidad real sobre 115 mil filas: elegimos la serie con tendencia, las barras apiladas y el mapa de calor —todos bajo **0,6 segundos**— y descartamos el calendario de 13 años porque cuesta mucho comparar colores pequeños.  
> En modelos, elegimos la descomposición **STL robusta** porque redujo casi a la mitad el error; probamos tres algoritmos de agrupación (K-Means, GMM y Ward); y validamos los clasificadores entrenando en 2015–2023 y probando en años futuros 2024–2026."

### Slide 7 · Hallazgo Central `[3:15 – 3:40 | 25 s]`
> "En una frase, este es nuestro resultado principal: **Coyhaique bajó sus días contaminados durante una década —casi 5 días menos por año—, pero en 2026 volvió a subir a 99 días sobre norma, y hoy Cochrane ya supera a la capital con 130 días críticos en 2025.**"

### Slide 8 · Exhibit 01: Tendencia STL y Categorías GEC `[3:40 – 4:15 | 35 s]`
> "Aquí se ve la evidencia. A la izquierda, la línea de tendencia limpia muestra la baja sostenida en Coyhaique II y en Puerto Aysén —que bajó 4,4 días por año en invierno— y confirma que las ciudades se mueven muy sincronizadas, con correlación sobre 0,82.  
> A la derecha, las barras apiladas de Coyhaique II muestran la caída desde 156 días en 2014 hasta 75 en 2021, pero la barra achurada de 2026 marca el repunte: 99 días sobre norma, con **33 preemergencias y 15 emergencias**. Ahora sigue Maximiliano con el ciclo diario, el clima y el cierre."

---

## Parte 2 — Maximiliano (Slides 9 a 14 · 3:45 min)

### Slide 9 · Exhibit 02: Ciclo Horario y Estacional `[4:15 – 4:45 | 30 s]`
> "Gracias Patricio. Al mirar las horas del día en Coyhaique II aparece el patrón típico de la leña. En invierno el promedio es **77,7 µg/m³**, más de **5 veces** el resto del año.  
> Dentro de un día de invierno hay dos subidas: una a las 8 de la mañana, un mínimo a las **14:00 horas** cuando el sol ventila el aire, y un salto fuerte desde las 18:00 hasta la medianoche, llegando en junio a un promedio de **191,8 µg/m³ a las 9 de la noche**."

### Slide 10 · Exhibit 03: Meteorología y Viento `[4:45 – 5:25 | 40 s]`
> "¿Qué factor climático manda en los episodios? Aunque en el año completo pesa más la temperatura, **dentro del invierno manda la falta de viento**, con correlación de **−0,686** frente a −0,512 de la temperatura: en invierno siempre hace frío, pero cuando el viento baja —en días críticos cae un **63%**, de 3,04 a 1,13 metros por segundo— el humo queda encerrado y el monóxido de carbono casi se cuadruplica.  
> Además, un día contaminado tiende a repetirse al día siguiente (autocorrelación de **0,77**), y la rosa histórica muestra que el viento suele llegar desde el oeste-noroeste."

### Slide 11 · Exhibit 04: PCA, Clustering y Validación `[5:25 – 6:15 | 50 s]`
> "En esta lámina resumimos las seis variables diarias del clima en un plano de dos ejes —que captura el **78,2%** de la información— y probamos tres métodos para agrupar automáticamente los días parecidos: **K-Means, Ward y GMM**.  
> **K-Means con 3 grupos** ganó en todas las pruebas y mantuvo casi los mismos grupos entre 2015–2020 y 2021–2026 (estabilidad de **0,974**).  
> ¿Qué significan los tres colores de la izquierda? **Verde** son días cálidos y ventilados; **amarillo**, días fríos con viento moderado; y **rojo**, días fríos, con alta presión y viento casi nulo que concentran el **76,5% de todos los episodios** —9 de cada 10 días rojos superan la norma.  
> A la derecha comprobamos cuánto explica el clima en años futuros 2024–2026: el modelo **Gradient Boosting** solo con clima logró una precisión global (**PR-AUC**) de **0,948** sobre 1, superando claramente a simplemente repetir el día anterior."

### Slide 12 · Arquitectura Interactiva (Python → Power BI) `[6:15 – 6:55 | 40 s]`
> "Cumpliendo la observación de la Presentación 1, dividimos el sistema en dos capas.  
> En **Python** corre la limpieza, las series de tiempo, los modelos y un prototipo interactivo en **Plotly Dash** con cinco vistas sincronizadas.  
> Desde ahí exportamos los datos limpios a nuestro proyecto de **Power BI Desktop** (`Aysen_MP25.pbip`): un modelo de 8 tablas que carga en **0,089 segundos**, con 32 indicadores DAX y 3 páginas de reporte interactivo listas para abrir y filtrar. Todo está documentado en nuestro repositorio de GitHub."

### Slide 13 · Fortalezas y Limitaciones `[6:55 – 7:25 | 30 s]`
> "En resumen, nuestras **fortalezas** son trabajar con 13 años oficiales de alta cobertura, controlar de forma transparente el año 2026 incompleto, entregar el proyecto Power BI listo, y mantener **rigor cuantitativo** —es decir, no elegimos ningún gráfico ni modelo al ojo, sino comparando métricas de error, estabilidad y velocidad real.  
> Como **limitaciones**, SINCA no publica dirección horaria del viento ni lluvia o altura de inversión térmica; solo hay cuatro estaciones —sin clima en Cochrane—; y como es un estudio observacional con datos 2026 parcialmente preliminares, mostramos asociación climática y no causalidad directa."

### Slide 14 · Conclusiones y Trabajo Futuro `[7:25 – 8:00 | 35 s]`
> "Para cerrar: aunque Coyhaique y Puerto Aysén mejoraron en la última década, los días fríos sin viento siguen provocando episodios severos, con un repunte claro en 2026 y una situación crítica en Cochrane, coherente con la literatura científica local.  
> Como trabajo futuro proponemos instalar sensores climáticos en Cochrane y publicar dirección horaria de viento en SINCA, integrar lluvias de la DMC llevando el panel a Power BI Service, y probar modelos de pronóstico a 24 y 48 horas.  
> Muchas gracias por su atención; quedamos atentos a sus preguntas."

---

## Glosario Rápido para Ustedes (Qué es y Cómo se Dice)

1. **Descomposición STL** (*se dice "ese-te-ele"*): Técnica que divide una serie de tiempo en tres partes: la **tendencia** de largo plazo (si sube o baja), la **estacionalidad** (el sube y baja repetido cada invierno) y el **ruido** (variaciones sueltas).
2. **Prueba de Mann–Kendall** (*"Man-Kéndal"*): Test estadístico que dice si una tendencia a subir o bajar a lo largo de los años es real o solo casualidad (si `p < 0,05`, es real).
3. **Correlación cruzada (CCF)**: Mide si un cambio en el clima (por ejemplo, baja el viento hoy) se asocia con más contaminación hoy o 1–2 días después.
4. **NO, NOx y NO₂**: Son **óxidos de nitrógeno**, gases contaminantes típicos de vehículos y combustión. Los sacamos del modelo porque les faltaba más del 70% de los datos.
5. **YTD** (*"Year-To-Date"*, o digan simplemente *"ventana acumulada"*): Comparar todos los años usando solo el tramo **1 de enero al 23 de octubre**, para que 2026 (que termina el 23 de octubre) compita en igualdad de condiciones.
6. **Jerarquía perceptual de Cleveland y McGill**: Regla clásica de visualización de datos que demuestra que el ojo humano compara con mucha más precisión **posiciones y largos de barras** que **tonos de color** en un calendario.
7. **K-Means, GMM y Ward**: Son **tres algoritmos distintos para agrupar días parecidos** (*clustering*). K-Means agrupa por distancia al centro; GMM (*Gaussian Mixture Model*) asume grupos con forma elíptica/probabilística; y Ward agrupa jerárquicamente paso a paso. Probamos los tres para elegir objetivamente el mejor (ganó K-Means).
8. **PR-AUC** (*se dice "pe-erre a-u-ce"*, Área bajo la curva Precisión-Recall): Nota entre **0 y 1** que mide qué tan bien un modelo detecta los días contaminados sin dar falsas alarmas. Un **0,948** significa que acierta casi siempre.
9. **ARI** (*"a-erre-i"*, Índice de Rand Ajustado): Nota entre **0 y 1** que mide si los grupos de K-Means salen iguales en 2015–2020 y en 2021–2026. **0,974** significa que los patrones climáticos son casi idénticos en el tiempo.
10. **Rigor cuantitativo**: Significa que ninguna decisión del proyecto se tomó "por tincada": cada gráfico se eligió con puntajes y tiempos medidos, y cada modelo se eligió comparando métricas de error y estabilidad.
