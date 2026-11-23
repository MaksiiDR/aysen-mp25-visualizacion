# Guion y Distribución de Tiempo — Presentación Final (8 minutos)

**Grupo N° 2:** Maximiliano del Río Lincoñir y Patricio Aylwin Retamal  
**Asignatura:** EIN092B Visualización — Prof. Jorge Portilla  
**Fecha:** 28 de noviembre de 2026  
**Duración total objetivo:** 8:00 min (480 s) — Sugerencia: Maximiliano Slides 1–6 (4:05), Patricio Slides 7–11 (3:55).

| Slide | Tema | Tiempo | Acumulado | Ideas fuerza clave |
|---:|---|---:|---:|---|
| 1 | Portada | 0:25 | 0:25 | Presentar tema, 4 estaciones SINCA (2013–2026) y arquitectura Python → Power BI. |
| 2 | Problema y objetivos | 0:40 | 1:05 | Zona saturada (DS 15), norma 50 µg/m³ (DS 12), brecha de SINCA, pregunta y 3 objetivos. |
| 3 | Retroalimentación Pres. 1 | 0:45 | 1:50 | Mostrar explícitamente las 3 observaciones del profesor y cómo cada una se resolvió con datos reales. |
| 4 | Auditoría de datos SINCA | 0:40 | 2:30 | 25 CSV, 98,9% en Coyhaique II, exclusión NO/NOx/NO₂, ventana YTD para 2026 (100% invierno), alerta Cochrane 2021–23. |
| 5 | Metodología y evaluación objetiva | 0:45 | 3:15 | Pipeline 4 etapas, matriz visual (Cleveland & McGill + `<0,6 s` en 115k filas; esquema estrella `0,089 s`), métricas ML. |
| 6 | Resultados 1: STL y GEC | 0:50 | 4:05 | Coyhaique II −4,93 días/año (p=0,002), repunte 2026 (99 días, 33 preemerg.); Vialidad −4,38 días/año; Cochrane 110–130 días; sincronía ρ>0,82. |
| 7 | Resultados 2: Ciclo diario | 0:40 | 4:45 | Razón invierno/verano 5,1×; bimodal 08:00 y 20:00–21:00 h (191,8 µg/m³ en junio); valle 14:00 h por ventilación. |
| 8 | Resultados 3: Clima y viento | 0:50 | 5:35 | Dentro del invierno el viento lidera (ρ=−0,686); calma de 1,13 m/s (−63%), CO 4×, ACF(1)=0,77, viento O–ONO (41,2%). |
| 9 | Resultados 4: PCA y clusters | 0:55 | 6:30 | K-Means k=3 gana a GMM/Ward (ARI=0,974); contraste físico C1 frontal (967,7 hPa) vs C2 anticiclónico (975,3 hPa, 76,5% episodios); Grad. Boost. PR-AUC 0,948. |
| 10 | Dash → Power BI | 0:45 | 7:15 | Prototipo Dash verificado + esquema estrella (8 tablas) y medidas DAX listos para Power BI Desktop + link GitHub. |
| 11 | Fortalezas, limitaciones y cierre | 0:45 | 8:00 | Balance honesto, conclusiones respaldadas en [1], [2], [6] y trabajo futuro (DMC, Cochrane, Power BI Service, SARIMAX). |

## Preguntas probables del profesor y respuestas preparadas
1. **¿Por qué eligieron K-Means con k=3 si k=2 tuvo mayor silueta (0,352 vs 0,246)?**  
   Porque `k=2` solo separa verano de invierno sin distinguir los días invernales ventilados de los días críticos; `k=3` mantiene la mejor silueta/DB/CH entre los modelos con `k ≥ 3`, logra una estabilidad temporal de `ARI = 0,974` y separa físicamente sistemas frontales (C1: 967,7 hPa) de bloqueos anticiclónicos (C2: 975,3 hPa, 93,4% episodios).
2. **¿Por qué no hicieron una rosa de vientos filtrada solo para días sobre norma?**  
   Al auditar los 25 CSV de SINCA verificamos que la plataforma no entrega dirección horaria del viento, únicamente tablas históricas agregadas de 24 sectores de 15° (y Cochrane carece de ella). Por rigor científico acotamos la rosa al régimen climatológico y usamos velocidad horaria/diaria del viento para los episodios.
3. **¿Cómo evitaron sesgar la tendencia al incluir 2026 incompleto?**  
   Mantuvimos separados los años calendario completos (2014–2025) de la ventana YTD comparable (1 ene–23 oct, que contiene el 99,7% de los episodios históricos) y la temporada invernal completa (abr–sep, con 100% de días válidos en Coyhaique y Vialidad en 2026).
4. **¿Por qué usar Python además de Power BI?**  
   Siguiendo la recomendación de la Presentación 1, Python ejecuta la limpieza auditable, descomposiciones STL robustas, pruebas de Mann–Kendall, CCF y validación `TimeSeriesSplit`, y exporta un esquema estrella optimizado (`0,089 s`) con medidas DAX para la capa ejecutiva de Power BI.
