# Implementacion en Power BI — Episodios de MP2,5 y Clima en la Region de Aysen

Siguiendo la retroalimentacion de la Presentacion 1, el flujo de trabajo separa:
1. **Pruebas preliminares, limpieza, auditoria de datos faltantes, descomposicion de series de tiempo (STL, ACF/CCF) y modelado (PCA/clustering/validacion)** en **Python** (`src/` y prototipo interactivo en `dashboard/app.py`).
2. **Implementacion final de visualizacion ejecutiva** en **Power BI Desktop** sobre un modelo estrella limpio y pre-validado (`powerbi/data/`).

## 1. Modelo de Datos (Esquema Estrella)

Importar desde `powerbi/data/` los siguientes archivos CSV (separador `,`, codificacion UTF-8):

| Tabla | Rol | Clave | Descripcion |
|---|---|---|---|
| `dim_estacion.csv` | Dimension | `station_id` | Metadatos y coordenadas geograficas de Coyhaique II, Coyhaique, Vialidad y Cochrane. |
| `dim_fecha.csv` | Dimension | `date` | Calendario continuo 2013–2026 con banderas `is_winter_season` (Abr–Sep), `is_ytd_comparable` (Ene 1–Oct 23) y `year_status`. |
| `fact_calidad_aire_diaria.csv` | Hechos | `date`, `station_id` | Promedios diarios (regla DS 12: >= 18 h validas), categorias GEC, estado de validacion SINCA y meteorologia diaria. |
| `fact_ciclo_horario_mensual.csv` | Hechos (agregada) | `station_id`, `month`, `hour` | Matriz 12 × 24 pre-agregada para mapa de calor de ciclo diario y estacional (evita cargar >360 mil filas horarias). |
| `fact_resumen_anual_completitud.csv` | Hechos (agregada) | `station_id`, `year` | Completitud anual, invernal y YTD por estacion para auditar anos parciales (2013, 2026). |
| `fact_stl_descomposicion.csv` | Hechos (series) | `date`, `station_id` | Componentes STL (tendencia, estacionalidad y residuo) generados en Python (`02_timeseries_and_ml.py`). |
| `fact_clusters_pca.csv` | Hechos (ML) | `date`, `station_id` | Coordenadas PC1/PC2 y asignacion de cluster de regimenes climatico-contaminantes (Coyhaique II). |
| `fact_rosa_vientos.csv` | Hechos (estatica) | `station_id`, `angle_center_deg` | Frecuencia direccional historica por 24 sectores de 15° (solo Coyhaique II, Coyhaique y Vialidad; SINCA no entrega direccion horaria). |

### Relaciones a configurar en Vista de Modelo
- `dim_estacion[station_id]` (1) → (*) `fact_calidad_aire_diaria[station_id]`
- `dim_fecha[date]` (1) → (*) `fact_calidad_aire_diaria[date]`
- `dim_estacion[station_id]` (1) → (*) `fact_ciclo_horario_mensual[station_id]`
- `dim_estacion[station_id]` (1) → (*) `fact_stl_descomposicion[station_id]` y `dim_fecha[date]` (1) → (*) `fact_stl_descomposicion[date]`
- `dim_estacion[station_id]` (1) → (*) `fact_clusters_pca[station_id]` y `dim_fecha[date]` (1) → (*) `fact_clusters_pca[date]`
- `dim_estacion[station_id]` (1) → (*) `fact_rosa_vientos[station_id]`

## 2. Medidas DAX
Copiar y crear una tabla de medidas (`_Medidas`) con las formulas de [`medidas.dax`](medidas.dax), incluyendo:
- Cumplimiento normativo DS 12 (`Dias Sobre Norma (>50 ug/m3)`, `Tasa Episodios (%)`).
- Comparacion justa del ano incompleto 2026 (`Dias Sobre Norma YTD Comparable`, `MP25 Promedio Invierno (Abr-Sep)`).
- Transparencia de calidad (`Completitud MP25 (%)`, `Porcentaje Datos Preliminares o No Validados`).

## 3. Estructura de Paginas del Informe Power BI
1. **Resumen Regional y Episodios**: Tarjetas KPI, Mapa de estaciones (`lat`/`lon`, tamano por dias >50), barras apiladas anuales por categoria GEC con selector `Ano completo vs. YTD comparable (Ene–Oct)` y advertencia automatica de 2026 incompleto.
2. **Patrones Temporales y STL**: Serie de tiempo mensual + linea de tendencia STL (`fact_stl_descomposicion`), matriz con formato condicional (heatmap `hora × mes` desde `fact_ciclo_horario_mensual`) y filtro por estacion.
3. **Clima, Regimenes (PCA/Clusters) y Viento**: Dispersion `PC1 vs. PC2` coloreada por cluster (`fact_clusters_pca`), cajas/dispersion de `MP2,5 vs. Temperatura` y `MP2,5 vs. Velocidad del Viento`, y grafico polar/barras circulares de frecuencia climatologica (`fact_rosa_vientos`) con nota explicita de disponibilidad historica agregada.
