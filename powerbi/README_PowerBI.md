# Proyecto Power BI (PBIP) — Episodios de MP2,5 y Clima en la Región de Aysén

Este directorio incluye el **proyecto completo de Power BI Desktop en formato PBIP + TMDL + PBIR** ya armado, listo para abrir y actualizar sin configuración manual:

- [`Aysen_MP25/Aysen_MP25.pbip`](Aysen_MP25/Aysen_MP25.pbip) — acceso directo al proyecto Power BI.
- [`Aysen_MP25/Aysen_MP25.SemanticModel/`](Aysen_MP25/Aysen_MP25.SemanticModel/) — modelo estrella en **TMDL** (8 tablas, 9 relaciones 1→\*, 32 medidas DAX con descripciones y formato, parámetro Power Query `CarpetaDatos` con cultura `"en-US"` y UTF-8).
- [`Aysen_MP25/Aysen_MP25.Report/`](Aysen_MP25/Aysen_MP25.Report/) — informe **PBIR** de 3 páginas (22 visuales, tema editorial de alto contraste `AysenEditorialTheme-8c4a2e1f.json`), validado con 0 errores y 0 advertencias mediante `@microsoft/powerbi-report-authoring-cli`.
- [`data/`](data/) — los 8 archivos CSV limpios y auditados del esquema estrella.
- [`medidas.dax`](medidas.dax) — respaldo legible de las fórmulas DAX base.

---

## Cómo abrir el reporte en Power BI Desktop (3 pasos)

1. **Habilitar formato PBIP/PBIR (si tu Power BI Desktop es anterior a 2025):**
   - `Archivo` → `Opciones y configuración` → `Opciones` → `Características de versión preliminar` → activar **Guardar proyecto de Power BI (.pbip)** y **Almacenar informes con el formato de metadatos mejorado (PBIR)**, y reiniciar Desktop.
2. **Abrir [`Aysen_MP25/Aysen_MP25.pbip`](Aysen_MP25/Aysen_MP25.pbip)** haciendo doble clic o desde `Archivo` → `Abrir`.
3. **Actualizar datos (y ajustar ruta si lo abres en otro PC):**
   - Si clonaste el repositorio en otra ruta de Windows, haz clic en `Transformar datos` → `Editar parámetros` → cambia **`CarpetaDatos`** a tu carpeta local `...\powerbi\data` (sin barra final) y haz clic en `Aplicar cambios`.
   - Haz clic en **`Actualizar`** (Refresh) para cargar los 8 CSV al modelo Import.

> **Nota sobre regeneración reproducible:** El proyecto completo se genera de forma determinista con `python src/07_build_powerbi_pbip.py`.

---

## Estructura del Modelo Estrella (TMDL)

| Tabla en Modelo | Archivo CSV en `powerbi/data/` | Rol | Relaciones (1→\*) |
|---|---|---|---|
| `Estacion` | `dim_estacion.csv` | Dimensión | Clave `Estacion ID` hacia las 6 tablas de hechos |
| `Calendario` | `dim_fecha.csv` | Dimensión (`Time`) | Clave `Fecha` hacia `Calidad Aire Diaria`, `Descomposicion STL` y `Clusters PCA` |
| `Calidad Aire Diaria` | `fact_calidad_aire_diaria.csv` | Hechos diarios | `Estacion`, `Calendario` (18 medidas DAX: MP2,5, GEC, completitud, clima) |
| `Ciclo Horario Mensual` | `fact_ciclo_horario_mensual.csv` | Hechos agregados | `Estacion` (matriz 24 h × 12 meses) |
| `Resumen Anual` | `fact_resumen_anual_completitud.csv` | Hechos auditoría | `Estacion` (completitud anual/invierno/YTD) |
| `Descomposicion STL` | `fact_stl_descomposicion.csv` | Hechos series | `Estacion`, `Calendario` (observado, tendencia, estacionalidad STL) |
| `Clusters PCA` | `fact_clusters_pca.csv` | Hechos ML | `Estacion`, `Calendario` (PC1/PC2/PC3 y regímenes K-Means en Coyhaique II) |
| `Rosa Vientos` | `fact_rosa_vientos.csv` | Hechos climatología | `Estacion` (24 sectores de 15° históricos SINCA, sin dimensión temporal) |

---

## Páginas del Informe PBIR (1280 × 720)

1. **`Resumen Regional`**: Filtros desplegables (`Estacion`, `Ano`, `Ventana YTD`), tarjeta KPI de 5 indicadores (`MP2,5 Promedio 24h`, `Dias Sobre Norma`, `Tasa Episodios`, `Completitud MP2,5`, `Datos Preliminares`), columnas apiladas por año y categoría GEC, y `azureMap` con coordenadas oficiales (`Latitud`/`Longitud`).
2. **`Series de Tiempo y Ciclo`**: Filtros (`Estacion`, `Temporada Invernal`), gráfico de líneas (`MP2,5 Mensual Observado` vs `Tendencia STL`), matriz `Hora × Mes` (`MP2,5 Horario Promedio`) y tabla de auditoría anual de completitud y episodios YTD.
3. **`Clima, Regimenes PCA y Viento`**: Filtros (`Regimen`, `Temporada Invernal`), tarjeta KPI meteorológica (4 métricas), dispersión `PC1 vs PC2` diaria por régimen ambiental (Coyhaique II) y barras agrupadas de frecuencia climatológica de viento por sector de 15°.
