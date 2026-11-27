# Guion Hablado — Presentación Final (8 minutos exactos)

**Grupo N° 2:** Maximiliano del Río Lincoñir y Patricio Aylwin Retamal  
**Asignatura:** EIN092B Visualización — Prof. Jorge Portilla (UTFSM)  
**Fecha:** 28 de noviembre de 2026  
**Duración objetivo:** 8:00 min (ritmo cómodo de ~130 palabras/min)  
**División sugerida:** **Maximiliano** Slides 1–8 (4:15) · **Patricio** Slides 9–14 (3:45)

---

## Parte 1 — Maximiliano (Slides 1 a 8 · 4:15 min)

### Slide 1 · Portada `[0:00 – 0:20 | 20 s]`
> "Buenos días profesor y compañeros. Somos el Grupo 2, integrado por Patricio Aylwin y quien les habla, Maximiliano del Río. Hoy presentamos nuestro proyecto final: **Caracterización visual y temporal de episodios de MP2,5 y clima en la Región de Aysén**, basado en 13 años de registros horarios oficiales del SINCA entre 2013 y 2026."

### Slide 2 · Contexto y Problemática `[0:20 – 0:55 | 35 s]`
> "Para partir, ¿qué es el **MP2,5**? Son partículas microscópicas de humo menores a 2,5 micrómetros —unas 25 veces más finas que un cabello— que pasan los filtros respiratorios y llegan directo al pulmón y a la sangre. En Coyhaique, su origen principal es la calefacción residencial a leña entre abril y septiembre.  
> El problema es que el portal oficial SINCA entrega más de 115 mil filas horarias por variable en tablas aisladas, sin comparar ciudades ni cruzarlas con el clima. Por eso nuestra pregunta es: **¿cómo han evolucionado estos episodios entre 2013 y 2026 y qué condiciones climáticas los explican?** Para responderla, definimos tres objetivos: caracterizar patrones horarios y estacionales, cuantificar tendencias controlando vacíos y el año 2026 incompleto, y modelar los regímenes climáticos."

### Slide 3 · Dataset SINCA y Normativa `[0:55 – 1:30 | 35 s]`
> "Trabajamos con **25 archivos públicos** descargados del Ministerio del Medio Ambiente con corte al **23 de octubre de 2026**: 22 series horarias de contaminantes y meteorología, más 3 tablas históricas de dirección del viento.  
> Como ven en la tabla, **Coyhaique II** es nuestra estación principal con 115.200 horas y meteorología completa; **Coyhaique** aporta la serie más larga; **Vialidad** en Puerto Aysén tiene clima parcial; y **Cochrane** solo mide MP2,5 desde 2021.  
> Siguiendo la norma chilena **DS N° 12/2011**, un día cuenta como válido solo si tiene al menos 18 horas medidas, y es episodio crítico cuando supera los **50 µg/m³** promedio en 24 horas, clasificándose en cinco niveles desde Bueno hasta Emergencia."

### Slide 4 · Retroalimentación Presentación 1 `[1:30 – 2:05 | 35 s]`
> "Incorporamos directamente las tres observaciones que nos dejó el profesor en la Presentación 1:  
> **Primero**, enfocamos el estudio en **series de tiempo** —descomposición STL, Mann–Kendall y correlación cruzada— y migramos la capa ejecutiva a un proyecto completo de **Power BI**.  
> **Segundo**, auditamos los datos faltantes y el año 2026 incompleto: excluimos los gases NO, NOx y NO₂ por tener más de 70% de vacíos y separamos 2026 en ventanas comparables.  
> **Tercero**, revisamos los CSV de viento y comprobamos que SINCA **no entrega dirección horaria**, solo tablas históricas agregadas en tres estaciones; por eso usamos la rosa únicamente como contexto climatológico y la velocidad horaria del viento para explicar los episodios."

### Slide 5 · Auditoría de Datos SINCA `[2:05 – 2:40 | 35 s]`
> "Este mapa resume la completitud anual de MP2,5 por estación. Coyhaique II y Coyhaique superan el **98%** de cobertura histórica.  
> El punto crítico es **2026**: como el corte es el 23 de octubre, cubre el 81% del año calendario, pero tiene **100% del invierno completo (abril a septiembre)**. Además, verificamos que entre enero y el 23 de octubre ocurre el **99,7%** de los episodios históricos de Coyhaique II, lo que nos permite comparar 2026 con años anteriores en igualdad de condiciones mediante una ventana YTD. También dejamos trazado que Cochrane entre 2021 y 2023 tiene registros no validados, por lo que sus años más fiables son 2024 y 2025."

### Slide 6 · Metodología y Selección Objetiva `[2:40 – 3:15 | 35 s]`
> "Para no elegir gráficos ni modelos al ojo, aplicamos criterios objetivos. A la izquierda evaluamos cuatro vistas candidatas según la jerarquía perceptual de Cleveland y McGill, claridad y tiempos reales medidos sobre 115.200 filas: seleccionamos la serie con tendencia STL, las barras apiladas GEC y el mapa de calor hora por mes —todas bajo **0,6 segundos**— y descartamos el calendario de 13 años por baja precisión perceptual.  
> En modelado, elegimos **STL robusto** porque redujo casi a la mitad el error mediano respecto al clásico; comparamos K-Means, GMM y Ward por métricas internas y estabilidad temporal; y validamos los clasificadores respetando el orden temporal, entrenando en 2015–2023 y probando en 2024–2026."

### Slide 7 · Hallazgo Central `[3:15 – 3:40 | 25 s]`
> "Antes de ver los gráficos en detalle, este es nuestro hallazgo principal: **Coyhaique logró reducir sus episodios durante una década —bajando a razón de casi 5 días por año—, pero en 2026 volvió a repuntar con 99 días sobre norma, y hoy Cochrane ya supera a la capital regional con 130 días críticos en 2025.**"

### Slide 8 · Exhibit 01: Tendencia STL y Categorías GEC `[3:40 – 4:15 | 35 s]`
> "Aquí vemos la evidencia. A la izquierda, la tendencia estructural STL muestra la caída sostenida en Coyhaique II y en Puerto Aysén —que bajó 4,38 días por año en invierno— junto con una estacionalidad extrema superior a 0,80 y una sincronía regional muy alta entre las ciudades, con correlación sobre 0,82.  
> A la derecha, las barras apiladas de Coyhaique II muestran la baja desde 156 días en 2014 hasta 75 en 2021, pero la barra achurada de 2026 evidencia el repunte: 99 días sobre norma, con **33 preemergencias y 15 emergencias**. Ahora le doy el pase a Patricio para los patrones horarios, el clima y la arquitectura final."

---

## Parte 2 — Patricio (Slides 9 a 14 · 3:45 min)

### Slide 9 · Exhibit 02: Ciclo Horario y Estacional `[4:15 – 4:45 | 30 s]`
> "Gracias Maximiliano. Al bajar a escala horaria en Coyhaique II vemos el sello clásico de la calefacción a leña. El promedio en invierno es **77,7 µg/m³**, más de **5 veces** el resto del año.  
> Durante un día invernal el comportamiento es bimodal: sube a las 8 de la mañana, baja al mínimo a las **14:00 horas** por ventilación solar y vuelve a dispararse entre las 18:00 y la medianoche, llegando a un promedio de **191,8 µg/m³ en junio a las 21:00 horas**."

### Slide 10 · Exhibit 03: Meteorología y Viento `[4:45 – 5:25 | 40 s]`
> "¿Qué variable climática explica mejor estos episodios? Aunque en el año completo lidera la temperatura, **dentro del invierno manda la calma del viento**, con una correlación de **−0,686** frente a −0,512 de la temperatura: en invierno siempre hace frío, pero cuando el viento cae —en días críticos baja un **63%**, de 3,04 a 1,13 metros por segundo— el humo queda atrapado y el monóxido de carbono casi se cuadruplica.  
> Además, la autocorrelación de un día al siguiente es **0,77**, lo que confirma episodios persistentes de varios días. A la derecha, la rosa climatológica histórica muestra predominio oeste-noroeste en Coyhaique II."

### Slide 11 · Exhibit 04: PCA, Clustering y Validación `[5:25 – 6:15 | 50 s]`
> "Al proyectar las seis variables diarias en componentes principales —que retienen el **78,2%** de la varianza— **K-Means con k=3** superó a Ward y GMM en todas las métricas y logró una estabilidad temporal de **0,974**.  
> Lo más valioso es su lectura física: separa días cálidos ventilados, días fríos frontales de baja presión y viento moderado, y un régimen **Frío-Estancado** de alta presión anticiclónica (975 hPa) y calma eólica que concentra el **76,5% de todos los episodios** —el 93,4% de sus días supera la norma.  
> Para validar cuánto explica el clima en años futuros 2024–2026, **Gradient Boosting** solo con meteorología alcanzó un **PR-AUC de 0,948** y F1 de 0,833, superando ampliamente al baseline de persistencia."

### Slide 12 · Arquitectura Interactiva (Python → Power BI) `[6:15 – 6:55 | 40 s]`
> "Cumpliendo la retroalimentación de la Presentación 1, separamos el flujo en dos capas reproducibles.  
> En **Python** ejecutamos la limpieza, series de tiempo, modelos y un prototipo interactivo en **Plotly Dash** con cinco vistas sincronizadas y alertas de completitud en vivo.  
> Desde ahí alimentamos directamente nuestro proyecto de **Power BI Desktop** (`Aysen_MP25.pbip`): un modelo estrella de 8 tablas que carga en **0,089 segundos**, con 32 indicadores DAX y un informe de 3 páginas y 22 visuales validado con cero errores. Todo el código, los datos procesados y el proyecto Power BI están documentados en nuestro repositorio de GitHub."

### Slide 13 · Fortalezas y Limitaciones `[6:55 – 7:25 | 30 s]`
> "Como balance crítico, nuestras principales **fortalezas** son trabajar con 13 años oficiales de alta completitud, controlar de forma auditable el cierre parcial de 2026, seleccionar vistas y modelos con métricas objetivas y entregar un proyecto Power BI completo.  
> En cuanto a **limitaciones**, SINCA no publica dirección horaria del viento ni precipitación o altura de capa límite; solo hay cuatro estaciones —sin meteorología en Cochrane—; y al ser un estudio observacional con registros 2026 parcialmente preliminares, establecemos asociación climática y no causalidad directa."

### Slide 14 · Conclusiones y Trabajo Futuro `[7:25 – 8:00 | 35 s]`
> "En conclusión, aunque Coyhaique y Puerto Aysén muestran una mejora estructural en la última década, el **estancamiento anticiclónico invernal** sigue generando episodios severos, con un repunte claro en 2026 y una situación crítica en Cochrane, en línea con la literatura previa para la cuenca de Coyhaique.  
> Como trabajo futuro proponemos tres pasos concretos: instalar meteorología completa en Cochrane y publicar dirección horaria en SINCA, sumar precipitación de la DMC desplegando el panel en Power BI Service, y evaluar modelos dinámicos SARIMAX de 24 a 48 horas.  
> Muchas gracias por su atención; quedamos atentos a sus preguntas."

---

## Respuestas Preparadas para Preguntas del Profesor

1. **¿Por qué eligieron K-Means con k=3 si k=2 tuvo mayor silueta (0,352 vs. 0,246)?**  
   > "Porque `k=2` solo divide el año en verano e invierno, sin distinguir un día frío ventilado de un episodio crítico. Con `k=3` mantenemos la mejor silueta, Davies–Bouldin y Calinski–Harabasz entre modelos con 3 o más grupos, logramos una estabilidad temporal de `0,974` y separamos físicamente frentes de baja presión (`967,7 hPa`, ventilados) de bloqueos anticiclónicos (`975,3 hPa`, donde el 93,4% de los días supera la norma)."

2. **¿Por qué no hicieron una rosa de vientos filtrada solo para días sobre norma?**  
   > "Al auditar los 25 archivos de SINCA comprobamos que la plataforma no entrega dirección horaria del viento en ninguna estación, solo tablas históricas agregadas de 24 sectores de 15° —y Cochrane ni siquiera tiene esa tabla—. Por rigor metodológico acotamos la rosa al contexto climatológico y analizamos los episodios con la velocidad horaria y diaria del viento."

3. **¿Cómo evitaron sesgar la tendencia al incluir 2026 incompleto?**  
   > "Separamos estrictamente los años completos (2014–2025) de dos ventanas justas: el invierno completo abril–septiembre (que sí tiene 100% de cobertura en 2026) y la ventana YTD del 1 de enero al 23 de octubre, donde ocurre el 99,7% de los episodios históricos de Coyhaique II."

4. **¿Por qué usar Python además de Power BI?**  
   > "Siguiendo su recomendación de la Presentación 1, Python se encarga de la auditoría de calidad, la descomposición STL robusta, las pruebas de Mann–Kendall, el clustering y la validación temporal; y exporta un esquema estrella limpio (`0,089 s`) que alimenta directamente nuestro proyecto Power BI Desktop (`Aysen_MP25.pbip`) con 32 medidas DAX y 3 páginas ejecutivas."
