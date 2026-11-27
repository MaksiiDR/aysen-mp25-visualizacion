# Guion y Distribución de Tiempo — Presentación Final (8 minutos)

**Grupo N° 2:** Maximiliano del Río Lincoñir y Patricio Aylwin Retamal  
**Asignatura:** EIN092B Visualización — Prof. Jorge Portilla  
**Fecha:** 28 de noviembre de 2026  
**Duración total objetivo:** 8:00 min (480 s) — Sugerencia: Maximiliano Slides 1–8 (4:15), Patricio Slides 9–14 (3:45).  
*Alineado 1:1 con las 14 diapositivas de `Presentacion_Final_Grupo2_Aysen_MP25.pptx` y `presentacion_aysen_mp25.html`.*

| Slide | Tema | Tiempo | Acumulado | Ideas fuerza clave |
|---:|---|---:|---:|---|
| 1 | Portada | 0:20 | 0:20 | Presentar tema, 4 estaciones SINCA (2013–2026) y arquitectura Python → Power BI. |
| 2 | Contexto y problemática | 0:35 | 0:55 | Zona saturada (DS 15), escala >115k filas, brecha de SINCA, pregunta y 3 objetivos. |
| 3 | Dataset SINCA y normativa | 0:35 | 1:30 | Fuente oficial (`sinca.mma.gob.cl`, 25 CSV, corte 23 oct 2026), tabla 4 estaciones, regla DS 12 (`>50 µg/m³ · ≥18 h`) y 5 niveles GEC. |
| 4 | Retroalimentación Pres. 1 | 0:35 | 2:05 | Mostrar explícitamente las 3 observaciones del profesor y cómo cada una se resolvió con datos reales. |
| 5 | Auditoría de datos SINCA | 0:35 | 2:40 | 98,9% Coyhaique II, exclusión NO/NOx/NO₂, ventana YTD (99,7% episodios) para 2026 (100% invierno), alerta Cochrane 2021–23. |
| 6 | Metodología y evaluación objetiva | 0:35 | 3:15 | Matriz visual (Cleveland & McGill + `<0,6 s` en 115k filas; esquema estrella `0,089 s`), criterios STL/clustering/TimeSeriesSplit. |
| 7 | Hallazgo central (síntesis) | 0:25 | 3:40 | Pausa narrativa con 3 cifras clave: `−4,93 días/año` Coyhaique II, `99 días` repunte 2026*, `130 días` Cochrane 2025. |
| 8 | Exhibit 01: STL y GEC | 0:35 | 4:15 | Fuerza estacional `>0,80`, descenso Vialidad `−4,38 d/año`, sincronía `ρ > 0,82` y repunte de preemergencias en 2026*. |
| 9 | Exhibit 02: Ciclo horario | 0:30 | 4:45 | Razón invierno/verano `5,1×`; mínimo 14:00 h (`40,0 µg/m³`) y pico nocturno `191,8 µg/m³` en junio 21:00 h. |
| 10 | Exhibit 03: Clima y viento | 0:40 | 5:25 | Dentro del invierno el viento lidera (`ρ = −0,686`); calma `1,13 m/s` (`−63%`), CO `4×`, `ACF(1) = 0,77`, viento O–ONO (`41,2%`). |
| 11 | Exhibit 04: PCA y clusters | 0:50 | 6:15 | K-Means `k=3` gana a GMM/Ward (`ARI = 0,974`); C1 frontal (`967,7 hPa`) vs C2 anticiclónico (`975,3 hPa`, `76,5%` episodios); Grad. Boost. `PR-AUC 0,948`. |
| 12 | Arquitectura Dash → Power BI PBIP | 0:40 | 6:55 | Prototipo Dash verificado + proyecto Power BI Desktop (`Aysen_MP25.pbip`: 8 tablas TMDL, 32 medidas DAX, 3 páginas PBIR, 0 errores) + link GitHub. |
| 13 | Fortalezas y limitaciones | 0:30 | 7:25 | Balance honesto: rigor en faltantes/2026 y transferencia PBIP vs. sin dirección horaria, sin precipitación y brecha Cochrane. |
| 14 | Conclusiones y cierre | 0:35 | 8:00 | Síntesis respaldada en [1], [2], [6] y 3 líneas de trabajo futuro (meteorología Cochrane, DMC + Power BI Service, SARIMAX). |

## Preguntas probables del profesor y respuestas preparadas
1. **¿Por qué eligieron K-Means con k=3 si k=2 tuvo mayor silueta (0,352 vs 0,246)?**  
   Porque `k=2` solo separa verano de invierno sin distinguir los días invernales ventilados de los días críticos; `k=3` mantiene la mejor silueta/DB/CH entre los modelos con `k ≥ 3`, logra una estabilidad temporal de `ARI = 0,974` y separa físicamente sistemas frontales (C1: 967,7 hPa) de bloqueos anticiclónicos (C2: 975,3 hPa, 93,4% episodios).
2. **¿Por qué no hicieron una rosa de vientos filtrada solo para días sobre norma?**  
   Al auditar los 25 CSV de SINCA verificamos que la plataforma no entrega dirección horaria del viento, únicamente tablas históricas agregadas de 24 sectores de 15° (y Cochrane carece de ella). Por rigor científico acotamos la rosa al régimen climatológico y usamos velocidad horaria/diaria del viento para los episodios.
3. **¿Cómo evitaron sesgar la tendencia al incluir 2026 incompleto?**  
   Mantuvimos separados los años calendario completos (2014–2025) de la ventana YTD comparable (1 ene–23 oct, que contiene el 99,7% de los episodios históricos) y la temporada invernal completa (abr–sep, con 100% de días válidos en Coyhaique y Vialidad en 2026).
4. **¿Por qué usar Python además de Power BI?**  
   Siguiendo la recomendación de la Presentación 1, Python ejecuta la limpieza auditable, descomposiciones STL robustas, pruebas de Mann–Kendall, CCF y validación `TimeSeriesSplit`, y exporta directamente el esquema estrella (`0,089 s`) que alimenta el proyecto Power BI Desktop (`Aysen_MP25.pbip`, 8 tablas TMDL, 32 medidas DAX y 3 páginas PBIR).
