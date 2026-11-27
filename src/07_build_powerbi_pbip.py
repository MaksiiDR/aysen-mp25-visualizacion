"""Build the Power BI Project (PBIP + TMDL semantic model + PBIR 3-page report).

Generates:
  - powerbi/Aysen_MP25/Aysen_MP25.SemanticModel/ (TMDL star schema + DAX measures)
  - powerbi/Aysen_MP25/Aysen_MP25.Report/        (PBIR 3-page report + custom theme)

All Power Query M partitions read CSVs from the `CarpetaDatos` parameter using
explicit UTF-8 (65001) and "en-US" culture so decimal dots parse reliably on
Spanish/Chilean Power BI Desktop installations.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "powerbi" / "data"
PBIP_DIR = ROOT / "powerbi" / "Aysen_MP25"
MODEL_DIR = PBIP_DIR / "Aysen_MP25.SemanticModel"
REPORT_DIR = PBIP_DIR / "Aysen_MP25.Report"

VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/visualContainer/2.9.0/schema.json"
)
PAGE_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/page/2.1.0/schema.json"
)
PAGES_META_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/pagesMetadata/1.1.0/schema.json"
)
REPORT_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/report/3.3.0/schema.json"
)

THEME_FILE = "AysenEditorialTheme-8c4a2e1f.json"

PAGE1_ID = "cce115778f914a6e8133"  # Scaffolded page 1 ID preserved
PAGE2_ID = "a2048f91c23e4d8b9012"
PAGE3_ID = "b3159e02d34f5e9c0123"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def write_json(path: Path, obj: dict) -> None:
    write_text(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# 1. Semantic Model (TMDL)
# ---------------------------------------------------------------------------


def m_csv_partition(
    table_tmdl_name: str,
    csv_filename: str,
    columns: list[tuple[str, str]],
) -> str:
    """Build an Import-mode M partition reading a UTF-8 CSV with en-US typing."""
    col_count = len(columns)
    type_pairs = ", ".join(f'{{"{col}", {m_type}}}' for col, m_type in columns)
    lines = [
        f"\tpartition {table_tmdl_name} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\tlet",
        f'\t\t\t\tSource = Csv.Document(File.Contents(#"CarpetaDatos" & "\\{csv_filename}"), [Delimiter=",", Columns={col_count}, Encoding=65001, QuoteStyle=QuoteStyle.None]),',
        '\t\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'\t\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{{type_pairs}}}, "en-US")',
        "\t\t\tin",
        '\t\t\t\t#"Changed Type"',
    ]
    return "\n".join(lines)


def build_semantic_model() -> None:
    write_json(
        MODEL_DIR / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {"type": "SemanticModel", "displayName": "Aysen_MP25"},
            "config": {
                "version": "2.0",
                "logicalId": "7e41c92a-5b3f-48d1-a6e2-91f8c4d03b57",
            },
        },
    )

    write_json(
        MODEL_DIR / "definition.pbism",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.2",
            "settings": {"qnaEnabled": True},
        },
    )

    defn = MODEL_DIR / "definition"

    write_text(
        defn / "database.tmdl",
        "\n".join(
            [
                "database 6b92d4e1-8f3a-4c72-9e51-20a4b7c8d109",
                "\tcompatibilityLevel: 1702",
                "\tcompatibilityMode: powerBI",
                "\tlanguage: 1033",
                "",
            ]
        ),
    )

    data_path_str = str(DATA_DIR)
    write_text(
        defn / "expressions.tmdl",
        "\n".join(
            [
                "/// Ruta local a la carpeta powerbi\\data con los 8 CSV del modelo estrella.",
                f'expression CarpetaDatos = "{data_path_str}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
                "",
            ]
        ),
    )

    write_text(
        defn / "model.tmdl",
        "\n".join(
            [
                "model Model",
                "\tculture: es-CL",
                "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
                "\tsourceQueryCulture: en-US",
                "\tdiscourageImplicitMeasures",
                "",
                "ref table Estacion",
                "ref table Calendario",
                "ref table 'Calidad Aire Diaria'",
                "ref table 'Ciclo Horario Mensual'",
                "ref table 'Resumen Anual'",
                "ref table 'Descomposicion STL'",
                "ref table 'Clusters PCA'",
                "ref table 'Rosa Vientos'",
                "",
            ]
        ),
    )

    write_text(
        defn / "relationships.tmdl",
        "\n".join(
            [
                "relationship 'Calidad Aire Diaria a Estacion'",
                "\tfromColumn: 'Calidad Aire Diaria'.'Estacion ID'",
                "\ttoColumn: Estacion.'Estacion ID'",
                "",
                "relationship 'Calidad Aire Diaria a Calendario'",
                "\tfromColumn: 'Calidad Aire Diaria'.Fecha",
                "\ttoColumn: Calendario.Fecha",
                "",
                "relationship 'Ciclo Horario Mensual a Estacion'",
                "\tfromColumn: 'Ciclo Horario Mensual'.'Estacion ID'",
                "\ttoColumn: Estacion.'Estacion ID'",
                "",
                "relationship 'Resumen Anual a Estacion'",
                "\tfromColumn: 'Resumen Anual'.'Estacion ID'",
                "\ttoColumn: Estacion.'Estacion ID'",
                "",
                "relationship 'Descomposicion STL a Estacion'",
                "\tfromColumn: 'Descomposicion STL'.'Estacion ID'",
                "\ttoColumn: Estacion.'Estacion ID'",
                "",
                "relationship 'Descomposicion STL a Calendario'",
                "\tfromColumn: 'Descomposicion STL'.Fecha",
                "\ttoColumn: Calendario.Fecha",
                "",
                "relationship 'Clusters PCA a Estacion'",
                "\tfromColumn: 'Clusters PCA'.'Estacion ID'",
                "\ttoColumn: Estacion.'Estacion ID'",
                "",
                "relationship 'Clusters PCA a Calendario'",
                "\tfromColumn: 'Clusters PCA'.Fecha",
                "\ttoColumn: Calendario.Fecha",
                "",
                "relationship 'Rosa Vientos a Estacion'",
                "\tfromColumn: 'Rosa Vientos'.'Estacion ID'",
                "\ttoColumn: Estacion.'Estacion ID'",
                "",
            ]
        ),
    )

    tables_dir = defn / "tables"

    # --- Table 1: Estacion ---
    write_text(
        tables_dir / "Estacion.tmdl",
        "\n".join(
            [
                "/// Dimension de estaciones de monitoreo SINCA en la Region de Aysen.",
                "table Estacion",
                "",
                "\t/// Identificador tecnico de la estacion SINCA.",
                "\tcolumn 'Estacion ID'",
                "\t\tdataType: string",
                "\t\tisKey",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_id",
                "",
                "\t/// Nombre visible de la estacion.",
                "\tcolumn Estacion",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_name",
                "",
                "\t/// Ciudad de ubicacion de la estacion.",
                "\tcolumn Ciudad",
                "\t\tdataType: string",
                "\t\tdataCategory: City",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: city",
                "",
                "\t/// Latitud geografica (grados decimales).",
                "\tcolumn Latitud",
                "\t\tdataType: decimal",
                "\t\tdataCategory: Latitude",
                "\t\tformatString: 0.0000",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: lat",
                "",
                "\t/// Longitud geografica (grados decimales).",
                "\tcolumn Longitud",
                "\t\tdataType: decimal",
                "\t\tdataCategory: Longitude",
                "\t\tformatString: 0.0000",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: lon",
                "",
                "\t/// Indica si la estacion dispone de rosa de vientos historica SINCA.",
                "\tcolumn 'Tiene Rosa Vientos'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: has_wind_rose",
                "",
                "\t/// Indica si la estacion dispone de meteorologia horaria.",
                "\tcolumn 'Tiene Meteorologia Horaria'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: has_met_hourly",
                "",
                "\t/// Rol analitico de la estacion en el estudio.",
                "\tcolumn Rol",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: role",
                "",
                m_csv_partition(
                    "Estacion",
                    "dim_estacion.csv",
                    [
                        ("station_id", "type text"),
                        ("station_name", "type text"),
                        ("city", "type text"),
                        ("lat", "type number"),
                        ("lon", "type number"),
                        ("has_wind_rose", "type logical"),
                        ("has_met_hourly", "type logical"),
                        ("role", "type text"),
                    ],
                ),
                "",
            ]
        ),
    )

    # --- Table 2: Calendario ---
    write_text(
        tables_dir / "Calendario.tmdl",
        "\n".join(
            [
                "/// Dimension calendario oficial con indicadores de temporada invernal y ventana YTD comparable.",
                "table Calendario",
                "\tdataCategory: Time",
                "",
                "\t/// Fecha calendario (clave primaria).",
                "\tcolumn Fecha",
                "\t\tdataType: dateTime",
                "\t\tisKey",
                "\t\tformatString: yyyy-mm-dd",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: date",
                "",
                "\t/// Ano calendario.",
                "\tcolumn Ano",
                "\t\tdataType: int64",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: year",
                "",
                "\t/// Numero de mes (1 a 12).",
                "\tcolumn Mes",
                "\t\tdataType: int64",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: month",
                "",
                "\t/// Nombre abreviado del mes ordenado cronologicamente.",
                "\tcolumn 'Mes Nombre'",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: month_name",
                "\t\tsortByColumn: Mes",
                "",
                "\t/// Trimestre calendario (T1 a T4).",
                "\tcolumn Trimestre",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: quarter",
                "",
                "\t/// Dia de la semana (0=Lun a 6=Dom).",
                "\tcolumn 'Dia Semana'",
                "\t\tdataType: int64",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: day_of_week",
                "",
                "\t/// Indica si corresponde a fin de semana.",
                "\tcolumn 'Es Fin de Semana'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_weekend",
                "",
                "\t/// Temporada invernal de gestion de episodios criticos (abril a septiembre).",
                "\tcolumn 'Temporada Invernal'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_winter_season",
                "",
                "\t/// Ventana comparable 1 ene - 23 oct para comparar 2026 sin sesgo con anos previos.",
                "\tcolumn 'Ventana YTD Comparable'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_ytd_comparable",
                "",
                "\t/// Estado de completitud del ano calendario (Completo vs Parcial hasta 23-oct-2026).",
                "\tcolumn 'Estado Ano'",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: year_status",
                "",
                m_csv_partition(
                    "Calendario",
                    "dim_fecha.csv",
                    [
                        ("date", "type date"),
                        ("year", "Int64.Type"),
                        ("month", "Int64.Type"),
                        ("month_name", "type text"),
                        ("quarter", "type text"),
                        ("day_of_week", "Int64.Type"),
                        ("is_weekend", "type logical"),
                        ("is_winter_season", "type logical"),
                        ("is_ytd_comparable", "type logical"),
                        ("year_status", "type text"),
                    ],
                ),
                "",
            ]
        ),
    )

    # --- Table 3: Calidad Aire Diaria ---
    write_text(
        tables_dir / "Calidad Aire Diaria.tmdl",
        "\n".join(
            [
                "/// Tabla de hechos diaria de MP2,5, otros contaminantes y meteorologia (regla DS N 12/2011 >=18h).",
                "table 'Calidad Aire Diaria'",
                "",
                "\t/// Promedio diario 24h de MP2,5 en ug/m3 sobre dias validos (>=18 horas).",
                "\tmeasure 'MP2,5 Promedio 24h' = AVERAGE('Calidad Aire Diaria'[MP2,5 24h])",
                '\t\tformatString: #,##0.0 "ug/m3"',
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Mediana diaria 24h de MP2,5 en ug/m3.",
                "\tmeasure 'MP2,5 Mediana 24h' = MEDIAN('Calidad Aire Diaria'[MP2,5 24h])",
                '\t\tformatString: #,##0.0 "ug/m3"',
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Percentil 90 de concentracion diaria 24h de MP2,5.",
                "\tmeasure 'MP2,5 Percentil 90' = ```",
                "\t\t\tPERCENTILEX.INC(",
                "\t\t\t\tFILTER('Calidad Aire Diaria', NOT(ISBLANK('Calidad Aire Diaria'[MP2,5 24h]))),",
                "\t\t\t\t'Calidad Aire Diaria'[MP2,5 24h],",
                "\t\t\t\t0.90",
                "\t\t\t)",
                "\t\t\t```",
                '\t\tformatString: #,##0.0 "ug/m3"',
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Cantidad de dias con al menos 18 horas validas de medicion MP2,5.",
                "\tmeasure 'Dias Validos' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\tCOUNTROWS('Calidad Aire Diaria'),",
                "\t\t\t\t'Calidad Aire Diaria'[Dia Valido MP2,5] = TRUE()",
                "\t\t\t)",
                "\t\t\t```",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Cantidad de dias validos que superan la norma diaria DS 12 (>50 ug/m3).",
                "\tmeasure 'Dias Sobre Norma' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\tCOUNTROWS('Calidad Aire Diaria'),",
                "\t\t\t\t'Calidad Aire Diaria'[Sobre Norma 50] = 1",
                "\t\t\t)",
                "\t\t\t```",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Porcentaje de dias validos que superan los 50 ug/m3.",
                "\tmeasure 'Tasa Episodios' = DIVIDE([Dias Sobre Norma], [Dias Validos], 0)",
                "\t\tformatString: 0.0%",
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Dias sobre norma dentro de la ventana comparable 1 ene - 23 oct.",
                "\tmeasure 'Dias Sobre Norma YTD' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\t[Dias Sobre Norma],",
                "\t\t\t\tCalendario[Ventana YTD Comparable] = TRUE()",
                "\t\t\t)",
                "\t\t\t```",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Promedio 24h de MP2,5 restringido a temporada invernal (abril-septiembre).",
                "\tmeasure 'MP2,5 Promedio Invierno' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\t[MP2,5 Promedio 24h],",
                "\t\t\t\tCalendario[Temporada Invernal] = TRUE()",
                "\t\t\t)",
                "\t\t\t```",
                '\t\tformatString: #,##0.0 "ug/m3"',
                "\t\tdisplayFolder: Calidad del Aire",
                "",
                "\t/// Dias clasificados en Alerta ambiental GEC (80-109 ug/m3).",
                "\tmeasure 'Dias Alerta' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\tCOUNTROWS('Calidad Aire Diaria'),",
                "\t\t\t\t'Calidad Aire Diaria'[Categoria GEC] = \"Alerta (80-109)\"",
                "\t\t\t)",
                "\t\t\t```",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Episodios GEC",
                "",
                "\t/// Dias clasificados en Preemergencia ambiental GEC (110-169 ug/m3).",
                "\tmeasure 'Dias Preemergencia' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\tCOUNTROWS('Calidad Aire Diaria'),",
                "\t\t\t\t'Calidad Aire Diaria'[Categoria GEC] = \"Preemergencia (110-169)\"",
                "\t\t\t)",
                "\t\t\t```",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Episodios GEC",
                "",
                "\t/// Dias clasificados en Emergencia ambiental GEC (>=170 ug/m3).",
                "\tmeasure 'Dias Emergencia' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\tCOUNTROWS('Calidad Aire Diaria'),",
                "\t\t\t\t'Calidad Aire Diaria'[Categoria GEC] = \"Emergencia (>=170)\"",
                "\t\t\t)",
                "\t\t\t```",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Episodios GEC",
                "",
                "\t/// Porcentaje de dias calendario registrados que cumplen criterio >=18 horas validas.",
                "\tmeasure 'Completitud MP2,5' = DIVIDE([Dias Validos], COUNTROWS('Calidad Aire Diaria'), 0)",
                "\t\tformatString: 0.0%",
                "\t\tdisplayFolder: Calidad de Datos",
                "",
                "\t/// Proporcion de dias validos con estado preliminar o no validado en SINCA.",
                "\tmeasure 'Datos Preliminares' = ```",
                "\t\t\tVAR DiasNoVal =",
                "\t\t\t\tCALCULATE(",
                "\t\t\t\t\tCOUNTROWS('Calidad Aire Diaria'),",
                "\t\t\t\t\t'Calidad Aire Diaria'[Dia Valido MP2,5] = TRUE(),",
                "\t\t\t\t\t'Calidad Aire Diaria'[Calidad Dato Dia] <> \"validado\"",
                "\t\t\t\t)",
                "\t\t\tRETURN",
                "\t\t\t\tDIVIDE(DiasNoVal, [Dias Validos], 0)",
                "\t\t\t```",
                "\t\tformatString: 0.0%",
                "\t\tdisplayFolder: Calidad de Datos",
                "",
                "\t/// Temperatura media diaria en grados Celsius.",
                "\tmeasure 'Temperatura Media' = AVERAGE('Calidad Aire Diaria'[Temperatura])",
                '\t\tformatString: 0.0 "C"',
                "\t\tdisplayFolder: Meteorologia",
                "",
                "\t/// Temperatura media en dias con episodios sobre norma (>50 ug/m3).",
                "\tmeasure 'Temperatura en Episodios' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\tAVERAGE('Calidad Aire Diaria'[Temperatura]),",
                "\t\t\t\t'Calidad Aire Diaria'[Sobre Norma 50] = 1",
                "\t\t\t)",
                "\t\t\t```",
                '\t\tformatString: 0.0 "C"',
                "\t\tdisplayFolder: Meteorologia",
                "",
                "\t/// Velocidad media diaria del viento en m/s.",
                "\tmeasure 'Viento Medio' = AVERAGE('Calidad Aire Diaria'[Velocidad Viento])",
                '\t\tformatString: 0.00 "m/s"',
                "\t\tdisplayFolder: Meteorologia",
                "",
                "\t/// Velocidad media del viento durante dias con episodios (>50 ug/m3).",
                "\tmeasure 'Viento en Episodios' = ```",
                "\t\t\tCALCULATE(",
                "\t\t\t\tAVERAGE('Calidad Aire Diaria'[Velocidad Viento]),",
                "\t\t\t\t'Calidad Aire Diaria'[Sobre Norma 50] = 1",
                "\t\t\t)",
                "\t\t\t```",
                '\t\tformatString: 0.00 "m/s"',
                "\t\tdisplayFolder: Meteorologia",
                "",
                "\t/// Humedad relativa media diaria en porcentaje.",
                "\tmeasure 'Humedad Media' = AVERAGE('Calidad Aire Diaria'[Humedad])",
                '\t\tformatString: 0.0 "%"',
                "\t\tdisplayFolder: Meteorologia",
                "",
                "\tcolumn Fecha",
                "\t\tdataType: dateTime",
                "\t\tisHidden",
                "\t\tformatString: yyyy-mm-dd",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: date",
                "",
                "\tcolumn 'Estacion ID'",
                "\t\tdataType: string",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_id",
                "",
                "\tcolumn Ano",
                "\t\tdataType: int64",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: year",
                "",
                "\tcolumn Mes",
                "\t\tdataType: int64",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: month",
                "",
                "\tcolumn Dia",
                "\t\tdataType: int64",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: day",
                "",
                "\tcolumn 'Es Invierno'",
                "\t\tdataType: boolean",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_winter_season",
                "",
                "\tcolumn 'Es YTD'",
                "\t\tdataType: boolean",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_ytd_window",
                "",
                "\tcolumn 'Horas Validas MP2,5'",
                "\t\tdataType: int64",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_count",
                "",
                "\tcolumn 'Dia Valido MP2,5'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_valid_day",
                "",
                "\tcolumn 'MP2,5 24h'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_24h",
                "",
                "\tcolumn 'MP2,5 Max Horario'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_max",
                "",
                "\tcolumn 'Sobre Norma 50'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: over_norm_50",
                "",
                "\t/// Categoria oficial de Gestion de Episodios Criticos (DS N 12/2011).",
                "\tcolumn 'Categoria GEC'",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: gec_category",
                "",
                "\t/// Estado de validacion del registro diario en SINCA.",
                "\tcolumn 'Calidad Dato Dia'",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_day_quality",
                "",
                "\tcolumn MP10",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp10",
                "",
                "\tcolumn CO",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.00",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: co",
                "",
                "\tcolumn SO2",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: so2",
                "",
                "\tcolumn O3",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: o3",
                "",
                "\tcolumn Temperatura",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: temp",
                "",
                "\tcolumn 'Temperatura Minima 24h'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: temp_min_24h",
                "",
                "\tcolumn Humedad",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: humedad",
                "",
                "\tcolumn Presion",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: presion",
                "",
                "\tcolumn 'Velocidad Viento'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.00",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: velviento",
                "",
                "\tcolumn 'Velocidad Viento Max 24h'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.00",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: velviento_max_24h",
                "",
                "\tcolumn 'Ano Mes'",
                "\t\tdataType: dateTime",
                "\t\tisHidden",
                "\t\tformatString: yyyy-mm",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: year_month",
                "",
                m_csv_partition(
                    "'Calidad Aire Diaria'",
                    "fact_calidad_aire_diaria.csv",
                    [
                        ("date", "type date"),
                        ("station_id", "type text"),
                        ("year", "Int64.Type"),
                        ("month", "Int64.Type"),
                        ("day", "Int64.Type"),
                        ("is_winter_season", "type logical"),
                        ("is_ytd_window", "type logical"),
                        ("mp25_count", "Int64.Type"),
                        ("mp25_valid_day", "type logical"),
                        ("mp25_24h", "type number"),
                        ("mp25_max", "type number"),
                        ("over_norm_50", "type number"),
                        ("gec_category", "type text"),
                        ("mp25_day_quality", "type text"),
                        ("mp10", "type number"),
                        ("co", "type number"),
                        ("so2", "type number"),
                        ("o3", "type number"),
                        ("temp", "type number"),
                        ("temp_min_24h", "type number"),
                        ("humedad", "type number"),
                        ("presion", "type number"),
                        ("velviento", "type number"),
                        ("velviento_max_24h", "type number"),
                        ("year_month", "type date"),
                    ],
                ),
                "",
            ]
        ),
    )

    # --- Table 4: Ciclo Horario Mensual ---
    write_text(
        tables_dir / "Ciclo Horario Mensual.tmdl",
        "\n".join(
            [
                "/// Perfil horario por mes del MP2,5 (24 horas x 12 meses por estacion).",
                "table 'Ciclo Horario Mensual'",
                "",
                "\t/// Promedio horario de MP2,5 en ug/m3 para la combinacion estacion-mes-hora.",
                "\tmeasure 'MP2,5 Horario Promedio' = AVERAGE('Ciclo Horario Mensual'[MP2,5 Medio])",
                "\t\tformatString: #,##0.0",
                "\t\tdisplayFolder: Ciclo Diario",
                "",
                "\t/// Percentil 90 horario de MP2,5 en ug/m3.",
                "\tmeasure 'MP2,5 Horario P90' = AVERAGE('Ciclo Horario Mensual'[MP2,5 P90])",
                "\t\tformatString: #,##0.0",
                "\t\tdisplayFolder: Ciclo Diario",
                "",
                "\tcolumn 'Estacion ID'",
                "\t\tdataType: string",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_id",
                "",
                "\tcolumn Mes",
                "\t\tdataType: int64",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: month",
                "",
                "\tcolumn Hora",
                "\t\tdataType: int64",
                "\t\tformatString: 00",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: hour",
                "",
                "\tcolumn 'MP2,5 Medio'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_mean",
                "",
                "\tcolumn 'MP2,5 Mediana'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_median",
                "",
                "\tcolumn 'MP2,5 P90'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_p90",
                "",
                "\tcolumn Observaciones",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: n_obs",
                "",
                m_csv_partition(
                    "'Ciclo Horario Mensual'",
                    "fact_ciclo_horario_mensual.csv",
                    [
                        ("station_id", "type text"),
                        ("month", "Int64.Type"),
                        ("hour", "Int64.Type"),
                        ("mp25_mean", "type number"),
                        ("mp25_median", "type number"),
                        ("mp25_p90", "type number"),
                        ("n_obs", "Int64.Type"),
                    ],
                ),
                "",
            ]
        ),
    )

    # --- Table 5: Resumen Anual ---
    write_text(
        tables_dir / "Resumen Anual.tmdl",
        "\n".join(
            [
                "/// Auditoria anual de completitud de datos, estado de validacion y episodios YTD por estacion.",
                "table 'Resumen Anual'",
                "",
                "\t/// Porcentaje de dias validos del ano calendario.",
                "\tmeasure 'Completitud Anual' = AVERAGE('Resumen Anual'[Completitud Ano Pct]) / 100",
                "\t\tformatString: 0.0%",
                "\t\tdisplayFolder: Auditoria Anual",
                "",
                "\t/// Porcentaje de dias validos en temporada invernal (abr-sep).",
                "\tmeasure 'Completitud Invierno' = AVERAGE('Resumen Anual'[Completitud Invierno Pct]) / 100",
                "\t\tformatString: 0.0%",
                "\t\tdisplayFolder: Auditoria Anual",
                "",
                "\t/// Dias sobre norma (>50 ug/m3) en la ventana comparable 1 ene - 23 oct.",
                "\tmeasure 'Dias >50 YTD' = SUM('Resumen Anual'[Dias Sobre 50 YTD])",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Auditoria Anual",
                "",
                "\t/// Promedio invernal anual de MP2,5 (ug/m3).",
                "\tmeasure 'MP2,5 Invierno Anual' = AVERAGE('Resumen Anual'[MP2,5 Medio Invierno])",
                "\t\tformatString: #,##0.0",
                "\t\tdisplayFolder: Auditoria Anual",
                "",
                "\tcolumn 'Estacion ID'",
                "\t\tdataType: string",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_id",
                "",
                "\tcolumn Ano",
                "\t\tdataType: int64",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: year",
                "",
                "\tcolumn 'Dias Esperados'",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: expected_days",
                "",
                "\tcolumn 'Dias Validos MP2,5'",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: valid_days_mp25",
                "",
                "\tcolumn 'Completitud Ano Pct'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: completeness_year_pct",
                "",
                "\tcolumn 'Dias Validos Invierno'",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: valid_days_winter",
                "",
                "\tcolumn 'Completitud Invierno Pct'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: completeness_winter_pct",
                "",
                "\tcolumn 'Dias Validos YTD'",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: valid_days_ytd",
                "",
                "\tcolumn 'Completitud YTD Pct'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: completeness_ytd_pct",
                "",
                "\tcolumn 'Ano Completo'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_complete_year",
                "",
                "\tcolumn 'Invierno Completo'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_complete_winter",
                "",
                "\tcolumn 'YTD Completo'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: is_complete_ytd",
                "",
                "\tcolumn 'MP2,5 Medio Anual'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mean_mp25_all",
                "",
                "\tcolumn 'MP2,5 Medio Invierno'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mean_mp25_winter",
                "",
                "\tcolumn 'MP2,5 Medio YTD'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mean_mp25_ytd",
                "",
                "\tcolumn 'Dias Sobre 50 Anual'",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: days_over_50_all",
                "",
                "\tcolumn 'Dias Sobre 50 Invierno'",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: days_over_50_winter",
                "",
                "\tcolumn 'Dias Sobre 50 YTD'",
                "\t\tdataType: int64",
                "\t\tformatString: #,##0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: days_over_50_ytd",
                "",
                "\tcolumn 'Pct Preliminar o No Validado'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: pct_days_prelim_or_noval",
                "",
                m_csv_partition(
                    "'Resumen Anual'",
                    "fact_resumen_anual_completitud.csv",
                    [
                        ("station_id", "type text"),
                        ("year", "Int64.Type"),
                        ("expected_days", "Int64.Type"),
                        ("valid_days_mp25", "Int64.Type"),
                        ("completeness_year_pct", "type number"),
                        ("valid_days_winter", "Int64.Type"),
                        ("completeness_winter_pct", "type number"),
                        ("valid_days_ytd", "Int64.Type"),
                        ("completeness_ytd_pct", "type number"),
                        ("is_complete_year", "type logical"),
                        ("is_complete_winter", "type logical"),
                        ("is_complete_ytd", "type logical"),
                        ("mean_mp25_all", "type number"),
                        ("mean_mp25_winter", "type number"),
                        ("mean_mp25_ytd", "type number"),
                        ("days_over_50_all", "Int64.Type"),
                        ("days_over_50_winter", "Int64.Type"),
                        ("days_over_50_ytd", "Int64.Type"),
                        ("pct_days_prelim_or_noval", "type number"),
                    ],
                ),
                "",
            ]
        ),
    )

    # --- Table 6: Descomposicion STL ---
    write_text(
        tables_dir / "Descomposicion STL.tmdl",
        "\n".join(
            [
                "/// Descomposicion estacional-tendencia robusta (STL) mensual del MP2,5 por estacion.",
                "table 'Descomposicion STL'",
                "",
                "\t/// Promedio mensual observado de MP2,5 (ug/m3).",
                "\tmeasure 'MP2,5 Mensual Observado' = AVERAGE('Descomposicion STL'[Observado MP2,5])",
                "\t\tformatString: #,##0.0",
                "\t\tdisplayFolder: Series de Tiempo",
                "",
                "\t/// Componente de tendencia estructural extraido mediante STL robusto.",
                "\tmeasure 'Tendencia STL' = AVERAGE('Descomposicion STL'[Tendencia])",
                "\t\tformatString: #,##0.0",
                "\t\tdisplayFolder: Series de Tiempo",
                "",
                "\t/// Componente estacional mensual extraido mediante STL robusto.",
                "\tmeasure 'Estacionalidad STL' = AVERAGE('Descomposicion STL'[Estacionalidad])",
                "\t\tformatString: #,##0.0",
                "\t\tdisplayFolder: Series de Tiempo",
                "",
                "\tcolumn Fecha",
                "\t\tdataType: dateTime",
                "\t\tisHidden",
                "\t\tformatString: yyyy-mm-dd",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: date",
                "",
                "\tcolumn 'Estacion ID'",
                "\t\tdataType: string",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_id",
                "",
                "\tcolumn 'Observado MP2,5'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: observed_mp25",
                "",
                "\tcolumn 'Entrada STL'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: stl_input_mp25",
                "",
                "\tcolumn 'Fue Interpolado'",
                "\t\tdataType: boolean",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: was_interpolated",
                "",
                "\tcolumn Tendencia",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: trend",
                "",
                "\tcolumn Estacionalidad",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: seasonal",
                "",
                "\tcolumn Residuo",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: resid",
                "",
                m_csv_partition(
                    "'Descomposicion STL'",
                    "fact_stl_descomposicion.csv",
                    [
                        ("date", "type date"),
                        ("station_id", "type text"),
                        ("observed_mp25", "type number"),
                        ("stl_input_mp25", "type number"),
                        ("was_interpolated", "type logical"),
                        ("trend", "type number"),
                        ("seasonal", "type number"),
                        ("resid", "type number"),
                    ],
                ),
                "",
            ]
        ),
    )

    # --- Table 7: Clusters PCA ---
    write_text(
        tables_dir / "Clusters PCA.tmdl",
        "\n".join(
            [
                "/// Regimenes ambientales diarios identificados por PCA + K-Means (k=3) en Coyhaique II (2015-2026).",
                "table 'Clusters PCA'",
                "",
                "\t/// Promedio de la primera componente principal (gradiente termico y viento).",
                "\tmeasure 'PC1 Promedio' = AVERAGE('Clusters PCA'[PC1])",
                "\t\tformatString: 0.00",
                "\t\tdisplayFolder: Regimenes PCA",
                "",
                "\t/// Promedio de la segunda componente principal (humedad y presion atmosferica).",
                "\tmeasure 'PC2 Promedio' = AVERAGE('Clusters PCA'[PC2])",
                "\t\tformatString: 0.00",
                "\t\tdisplayFolder: Regimenes PCA",
                "",
                "\t/// Cantidad de dias asignados al regimen ambiental.",
                "\tmeasure 'Dias en Regimen' = COUNTROWS('Clusters PCA')",
                "\t\tformatString: #,##0",
                "\t\tdisplayFolder: Regimenes PCA",
                "",
                "\t/// Concentracion media 24h de MP2,5 (ug/m3) dentro del regimen.",
                "\tmeasure 'MP2,5 Promedio Regimen' = AVERAGE('Clusters PCA'[MP2,5 24h])",
                "\t\tformatString: #,##0.0",
                "\t\tdisplayFolder: Regimenes PCA",
                "",
                "\tcolumn Fecha",
                "\t\tdataType: dateTime",
                "\t\tisHidden",
                "\t\tformatString: yyyy-mm-dd",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: date",
                "",
                "\tcolumn 'Estacion ID'",
                "\t\tdataType: string",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_id",
                "",
                "\tcolumn PC1",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.00",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: PC1",
                "",
                "\tcolumn PC2",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.00",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: PC2",
                "",
                "\tcolumn PC3",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.00",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: PC3",
                "",
                "\tcolumn 'Cluster ID'",
                "\t\tdataType: int64",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: cluster_id",
                "",
                "\t/// Nombre interpretativo del regimen ambiental.",
                "\tcolumn Regimen",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: cluster_name",
                "\t\tsortByColumn: 'Cluster ID'",
                "",
                "\tcolumn 'MP2,5 24h'",
                "\t\tdataType: decimal",
                "\t\tformatString: #,##0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: mp25_24h",
                "",
                "\tcolumn 'Sobre Norma 50'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: over_norm_50",
                "",
                m_csv_partition(
                    "'Clusters PCA'",
                    "fact_clusters_pca.csv",
                    [
                        ("date", "type date"),
                        ("station_id", "type text"),
                        ("PC1", "type number"),
                        ("PC2", "type number"),
                        ("PC3", "type number"),
                        ("cluster_id", "Int64.Type"),
                        ("cluster_name", "type text"),
                        ("mp25_24h", "type number"),
                        ("over_norm_50", "type number"),
                    ],
                ),
                "",
            ]
        ),
    )

    # --- Table 8: Rosa Vientos ---
    write_text(
        tables_dir / "Rosa Vientos.tmdl",
        "\n".join(
            [
                "/// Frecuencias climatologicas historicas de direccion del viento (24 sectores de 15 grados, SINCA).",
                "table 'Rosa Vientos'",
                "",
                "\t/// Frecuencia porcentual climatologica del viento por sector direccional.",
                "\tmeasure 'Frecuencia Viento' = SUM('Rosa Vientos'[Frecuencia Pct]) / 100",
                "\t\tformatString: 0.0%",
                "\t\tdisplayFolder: Viento Climatologico",
                "",
                "\tcolumn 'Estacion ID'",
                "\t\tdataType: string",
                "\t\tisHidden",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: station_id",
                "",
                "\t/// Sector direccional de 15 grados ordenado por angulo central.",
                "\tcolumn Sector",
                "\t\tdataType: string",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: sector_label",
                "\t\tsortByColumn: 'Angulo Centro'",
                "",
                "\tcolumn 'Angulo Inicio'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: angle_start_deg",
                "",
                "\tcolumn 'Angulo Fin'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: angle_end_deg",
                "",
                "\tcolumn 'Angulo Centro'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: angle_center_deg",
                "",
                "\tcolumn 'Frecuencia Pct'",
                "\t\tdataType: decimal",
                "\t\tformatString: 0.0",
                "\t\tsummarizeBy: none",
                "\t\tsourceColumn: freq_pct",
                "",
                m_csv_partition(
                    "'Rosa Vientos'",
                    "fact_rosa_vientos.csv",
                    [
                        ("station_id", "type text"),
                        ("sector_label", "type text"),
                        ("angle_start_deg", "type number"),
                        ("angle_end_deg", "type number"),
                        ("angle_center_deg", "type number"),
                        ("freq_pct", "type number"),
                    ],
                ),
                "",
            ]
        ),
    )


# ---------------------------------------------------------------------------
# 2. Report (PBIR) Helpers & Builders
# ---------------------------------------------------------------------------


def lit(val: str) -> dict:
    return {"expr": {"Literal": {"Value": val}}}


def solid(hex_color: str) -> dict:
    return {"solid": {"color": lit(f"'{hex_color}'")}}


def col_proj(entity: str, prop: str, active: bool | None = None) -> dict:
    p: dict = {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}},
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop,
    }
    if active is not None:
        p["active"] = active
    return p


def meas_proj(entity: str, prop: str, active: bool | None = None) -> dict:
    p: dict = {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}},
        "queryRef": f"{entity}.{prop}",
        "nativeQueryRef": prop,
    }
    if active is not None:
        p["active"] = active
    return p


def agg_proj(entity: str, prop: str, func: int, label: str, active: bool | None = None) -> dict:
    fn_name = {0: "Sum", 1: "Avg", 2: "Count", 3: "Min", 4: "Max"}[func]
    p: dict = {
        "field": {
            "Aggregation": {
                "Expression": {
                    "Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}
                },
                "Function": func,
            }
        },
        "queryRef": f"{fn_name}({entity}.{prop})",
        "nativeQueryRef": label,
    }
    if active is not None:
        p["active"] = active
    return p


def card_vco(title: str | None = None, subtitle: str | None = None, show_bg: bool = True) -> dict:
    vco: dict = {
        "background": [
            {
                "properties": {
                    "show": lit("true" if show_bg else "false"),
                    "color": solid("#FFFFFF"),
                    "transparency": lit("0D"),
                }
            }
        ],
        "border": [
            {
                "properties": {
                    "show": lit("true" if show_bg else "false"),
                    "color": solid("#D6D1C4"),
                    "radius": lit("6D"),
                }
            }
        ],
        "padding": [
            {
                "properties": {
                    "top": lit("8D"),
                    "bottom": lit("8D"),
                    "left": lit("10D"),
                    "right": lit("10D"),
                }
            }
        ],
    }
    if title:
        vco["title"] = [
            {
                "properties": {
                    "show": lit("true"),
                    "text": lit(f"'{title}'"),
                    "fontColor": solid("#18211A"),
                    "fontSize": lit("11D"),
                    "bold": lit("true"),
                }
            }
        ]
    if subtitle:
        vco["subTitle"] = [
            {
                "properties": {
                    "show": lit("true"),
                    "text": lit(f"'{subtitle}'"),
                    "fontColor": solid("#4A554E"),
                    "fontSize": lit("9D"),
                }
            }
        ]
    return vco


def make_textbox(
    vid: str,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    subtitle: str | None = None,
    title_size: str = "18px",
    sub_size: str = "11px",
    with_card: bool = False,
    tab: int = 0,
) -> dict:
    paragraphs = [
        {
            "textRuns": [
                {
                    "value": title,
                    "textStyle": {
                        "fontFamily": "Segoe UI Semibold",
                        "fontSize": title_size,
                        "color": "#18211A",
                    },
                }
            ],
            "horizontalTextAlignment": "left",
        }
    ]
    if subtitle:
        paragraphs.append(
            {
                "textRuns": [
                    {
                        "value": subtitle,
                        "textStyle": {
                            "fontFamily": "Segoe UI",
                            "fontSize": sub_size,
                            "color": "#3B473F",
                        },
                    }
                ],
                "horizontalTextAlignment": "left",
            }
        )

    vco = (
        card_vco(show_bg=True)
        if with_card
        else {
            "background": [{"properties": {"show": lit("false")}}],
            "border": [{"properties": {"show": lit("false")}}],
            "padding": [
                {
                    "properties": {
                        "top": lit("0D"),
                        "bottom": lit("0D"),
                        "left": lit("0D"),
                        "right": lit("0D"),
                    }
                }
            ],
        }
    )

    return {
        "$schema": VISUAL_SCHEMA,
        "name": vid,
        "position": {"x": x, "y": y, "z": 1000 + tab, "height": h, "width": w, "tabOrder": tab},
        "visual": {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": paragraphs}}]},
            "visualContainerObjects": vco,
        },
    }


def make_dropdown_slicer(
    vid: str,
    x: int,
    y: int,
    w: int,
    entity: str,
    prop: str,
    header_text: str,
    tab: int,
) -> dict:
    return {
        "$schema": VISUAL_SCHEMA,
        "name": vid,
        "position": {"x": x, "y": y, "z": 1000 + tab, "height": 80, "width": w, "tabOrder": tab},
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [col_proj(entity, prop)]}}},
            "objects": {
                "data": [{"properties": {"mode": lit("'Dropdown'")}}],
                "header": [
                    {
                        "properties": {
                            "show": lit("true"),
                            "text": lit(f"'{header_text}'"),
                            "fontColor": solid("#18211A"),
                        }
                    }
                ],
            },
            "visualContainerObjects": {
                "background": [
                    {
                        "properties": {
                            "show": lit("true"),
                            "color": solid("#FFFFFF"),
                            "transparency": lit("0D"),
                        }
                    }
                ],
                "border": [
                    {
                        "properties": {
                            "show": lit("true"),
                            "color": solid("#D6D1C4"),
                            "radius": lit("6D"),
                        }
                    }
                ],
                "padding": [
                    {
                        "properties": {
                            "top": lit("8D"),
                            "bottom": lit("8D"),
                            "left": lit("8D"),
                            "right": lit("8D"),
                        }
                    }
                ],
            },
        },
    }


def make_kpi_strip(
    vid: str,
    x: int,
    y: int,
    w: int,
    measures: list[tuple[str, str]],
    tab: int,
) -> dict:
    """Multi-value cardVisual sized with official 720px canvas formula (height=88)."""
    return {
        "$schema": VISUAL_SCHEMA,
        "name": vid,
        "position": {"x": x, "y": y, "z": 1000 + tab, "height": 88, "width": w, "tabOrder": tab},
        "visual": {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {"projections": [meas_proj(ent, m) for ent, m in measures]}
                }
            },
            "objects": {
                "value": [
                    {
                        "properties": {
                            "fontSize": lit("20D"),
                            "fontColor": solid("#18211A"),
                            "bold": lit("true"),
                        },
                        "selector": {"id": "default"},
                    }
                ],
                "label": [
                    {
                        "properties": {
                            "fontSize": lit("10D"),
                            "fontColor": solid("#4A554E"),
                        },
                        "selector": {"id": "default"},
                    }
                ],
                "padding": [
                    {
                        "properties": {"paddingUniform": lit("8D")},
                        "selector": {"id": "default"},
                    }
                ],
                "layout": [
                    {
                        "properties": {"paddingUniform": lit("0D")},
                        "selector": {"id": "default"},
                    }
                ],
            },
            "visualContainerObjects": {
                "background": [
                    {
                        "properties": {
                            "show": lit("true"),
                            "color": solid("#FFFFFF"),
                            "transparency": lit("0D"),
                        }
                    }
                ],
                "border": [
                    {
                        "properties": {
                            "show": lit("true"),
                            "color": solid("#D6D1C4"),
                            "radius": lit("6D"),
                        }
                    }
                ],
                "padding": [
                    {
                        "properties": {
                            "top": lit("8D"),
                            "bottom": lit("8D"),
                            "left": lit("8D"),
                            "right": lit("8D"),
                        },
                        "selector": {"id": "default"},
                    }
                ],
                "spacing": [
                    {
                        "properties": {
                            "customizeSpacing": lit("true"),
                            "verticalSpacing": lit("2D"),
                        },
                        "selector": {"id": "default"},
                    }
                ],
            },
        },
    }


def make_page(page_id: str, display_name: str) -> dict:
    return {
        "$schema": PAGE_SCHEMA,
        "name": page_id,
        "displayName": display_name,
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
        "objects": {
            "background": [
                {
                    "properties": {
                        "color": solid("#EFECE4"),
                        "transparency": lit("0D"),
                    }
                }
            ],
            "outspace": [
                {
                    "properties": {
                        "color": solid("#E5E1D6"),
                        "transparency": lit("0D"),
                    }
                }
            ],
        },
    }


def build_report() -> None:
    # Custom editorial theme (uniform parchment light theme, single Segoe UI font, high-contrast dark text)
    theme_obj = {
        "name": THEME_FILE,
        "dataColors": [
            "#1B4332",
            "#0F4C81",
            "#2A9D8F",
            "#B5830A",
            "#9B2226",
            "#4A5568",
            "#3D5A80",
            "#6B4C9A",
        ],
        "good": "#1B4332",
        "neutral": "#B5830A",
        "bad": "#9B2226",
        "background": "#FFFFFF",
        "foreground": "#18211A",
        "tableAccent": "#1B4332",
        "textClasses": {
            "callout": {"fontFace": "Segoe UI", "fontSize": 20, "color": "#18211A"},
            "title": {"fontFace": "Segoe UI", "fontSize": 12, "color": "#18211A"},
            "header": {"fontFace": "Segoe UI", "fontSize": 11, "color": "#18211A"},
            "label": {"fontFace": "Segoe UI", "fontSize": 10, "color": "#3B473F"},
        },
        "visualStyles": {
            "tableEx": {
                "*": {
                    "columnHeaders": [
                        {"autoSizeColumnWidth": True, "columnAdjustment": "growToFit"}
                    ]
                }
            },
            "pivotTable": {
                "*": {
                    "columnHeaders": [
                        {"autoSizeColumnWidth": True, "columnAdjustment": "growToFit"}
                    ]
                }
            },
        },
    }
    write_json(REPORT_DIR / "StaticResources" / "RegisteredResources" / THEME_FILE, theme_obj)

    # Register theme in report.json preserving scaffolded baseTheme & settings
    report_json_path = REPORT_DIR / "definition" / "report.json"
    report_json = json.loads(report_json_path.read_text(encoding="utf-8"))
    report_json["$schema"] = REPORT_SCHEMA
    report_json["themeCollection"]["customTheme"] = {
        "name": THEME_FILE,
        "reportVersionAtImport": {
            "visual": "2.11.0",
            "report": "3.4.0",
            "page": "2.3.1",
        },
        "type": "RegisteredResources",
    }
    pkgs = [p for p in report_json.get("resourcePackages", []) if p.get("name") != "RegisteredResources"]
    pkgs.append(
        {
            "name": "RegisteredResources",
            "type": "RegisteredResources",
            "items": [{"name": THEME_FILE, "path": THEME_FILE, "type": "CustomTheme"}],
        }
    )
    report_json["resourcePackages"] = pkgs
    write_json(report_json_path, report_json)

    pages_dir = REPORT_DIR / "definition" / "pages"
    write_json(
        pages_dir / "pages.json",
        {
            "$schema": PAGES_META_SCHEMA,
            "pageOrder": [PAGE1_ID, PAGE2_ID, PAGE3_ID],
            "activePageName": PAGE1_ID,
        },
    )

    # ------------------------------------------------------------------
    # Page 1: Resumen Regional
    # ------------------------------------------------------------------
    p1_dir = pages_dir / PAGE1_ID
    write_json(p1_dir / "page.json", make_page(PAGE1_ID, "Resumen Regional"))

    p1_visuals = [
        make_textbox(
            "p1000000000000000001",
            x=24,
            y=16,
            w=1232,
            h=40,
            title="Monitoreo Regional de MP2,5 y Episodios GEC - Aysen (SINCA 2013-2026)",
            subtitle="Norma primaria diaria DS N 12/2011 (50 ug/m3, >=18h validas/dia) | Grupo 2 EIN092B UTFSM",
            title_size="17px",
            sub_size="10px",
            tab=1,
        ),
        make_dropdown_slicer(
            "p1000000000000000002", 24, 64, 264, "Estacion", "Estacion", "Estacion SINCA", 2
        ),
        make_dropdown_slicer(
            "p1000000000000000003", 304, 64, 184, "Calendario", "Ano", "Ano", 3
        ),
        make_dropdown_slicer(
            "p1000000000000000004",
            504,
            64,
            232,
            "Calendario",
            "Ventana YTD Comparable",
            "Ventana YTD (1 ene - 23 oct)",
            4,
        ),
        make_textbox(
            "p1000000000000000005",
            x=752,
            y=64,
            w=504,
            h=80,
            title="Nota metodologica de comparabilidad",
            subtitle="2026 cubre hasta el 23 de octubre (invierno abr-sep completo). Active Ventana YTD = True para comparar conteos anuales sin sesgo de cierre.",
            title_size="11px",
            sub_size="10px",
            with_card=True,
            tab=5,
        ),
        make_kpi_strip(
            "p1000000000000000006",
            x=24,
            y=156,
            w=1232,
            measures=[
                ("Calidad Aire Diaria", "MP2,5 Promedio 24h"),
                ("Calidad Aire Diaria", "Dias Sobre Norma"),
                ("Calidad Aire Diaria", "Tasa Episodios"),
                ("Calidad Aire Diaria", "Completitud MP2,5"),
                ("Calidad Aire Diaria", "Datos Preliminares"),
            ],
            tab=6,
        ),
        # Stacked column chart: Exceedance days by Year and GEC Category
        {
            "$schema": VISUAL_SCHEMA,
            "name": "p1000000000000000007",
            "position": {"x": 24, "y": 256, "z": 1007, "height": 440, "width": 696, "tabOrder": 7},
            "visual": {
                "visualType": "columnChart",
                "query": {
                    "queryState": {
                        "Category": {"projections": [col_proj("Calendario", "Ano", active=True)]},
                        "Series": {"projections": [col_proj("Calidad Aire Diaria", "Categoria GEC")]},
                        "Y": {"projections": [meas_proj("Calidad Aire Diaria", "Dias Sobre Norma")]},
                    }
                },
                "objects": {
                    "legend": [
                        {
                            "properties": {
                                "show": lit("true"),
                                "position": lit("'Top'"),
                                "showTitle": lit("false"),
                            }
                        }
                    ],
                    "categoryAxis": [
                        {"properties": {"show": lit("true"), "axisType": lit("'Categorical'")}}
                    ],
                    "valueAxis": [{"properties": {"show": lit("true")}}],
                },
                "visualContainerObjects": card_vco(
                    "Dias sobre norma (>50 ug/m3) por ano y categoria GEC",
                    "Desglose anual de episodios criticos (Regular, Alerta, Preemergencia, Emergencia)",
                ),
            },
        },
        # Clustered Bar Chart by Station (offline-friendly replacement for Azure Map, no login required)
        {
            "$schema": VISUAL_SCHEMA,
            "name": "p1000000000000000008",
            "position": {"x": 736, "y": 256, "z": 1008, "height": 440, "width": 520, "tabOrder": 8},
            "visual": {
                "visualType": "clusteredBarChart",
                "query": {
                    "queryState": {
                        "Category": {"projections": [col_proj("Estacion", "Estacion", active=True)]},
                        "Y": {
                            "projections": [
                                meas_proj("Calidad Aire Diaria", "Dias Sobre Norma", active=True)
                            ]
                        },
                        "Tooltips": {
                            "projections": [
                                meas_proj("Calidad Aire Diaria", "MP2,5 Promedio 24h"),
                                meas_proj("Calidad Aire Diaria", "Completitud MP2,5"),
                            ]
                        },
                    }
                },
                "objects": {
                    "labels": [{"properties": {"show": lit("true")}}],
                    "dataPoint": [
                        {
                            "properties": {"fill": solid("#1B4332")},
                            "selector": {"metadata": "Calidad Aire Diaria.Dias Sobre Norma"},
                        }
                    ],
                },
                "visualContainerObjects": card_vco(
                    "Comparacion regional de dias sobre norma (>50 ug/m3)",
                    "Total de dias criticos por estacion SINCA (sin requerir inicio de sesion)",
                ),
            },
        },
    ]

    for v in p1_visuals:
        write_json(p1_dir / "visuals" / v["name"] / "visual.json", v)

    # ------------------------------------------------------------------
    # Page 2: Series de Tiempo y Ciclo
    # ------------------------------------------------------------------
    p2_dir = pages_dir / PAGE2_ID
    write_json(p2_dir / "page.json", make_page(PAGE2_ID, "Series de Tiempo y Ciclo"))

    p2_visuals = [
        make_textbox(
            "p2000000000000000001",
            x=24,
            y=16,
            w=1232,
            h=40,
            title="Descomposicion STL, Ciclo Horario-Estacional y Auditoria de Completitud",
            subtitle="Evolucion mensual estructural, patron vespertino de calefaccion a lena y cobertura interanual",
            title_size="17px",
            sub_size="10px",
            tab=1,
        ),
        make_dropdown_slicer(
            "p2000000000000000002", 24, 64, 280, "Estacion", "Estacion", "Estacion SINCA", 2
        ),
        make_dropdown_slicer(
            "p2000000000000000003",
            320,
            64,
            232,
            "Calendario",
            "Temporada Invernal",
            "Temporada Invernal (Abr-Sep)",
            3,
        ),
        make_textbox(
            "p2000000000000000004",
            x=568,
            y=64,
            w=688,
            h=80,
            title="Guia de lectura temporal",
            subtitle="La tendencia STL separa el cambio estructural de los ciclos anuales de invierno. La matriz inferior muestra el promedio horario (0-23h) por mes (1-12) con maximos nocturnos entre las 20:00 y 01:00 h.",
            title_size="11px",
            sub_size="10px",
            with_card=True,
            tab=4,
        ),
        # Line chart: Monthly Observed vs STL Trend
        {
            "$schema": VISUAL_SCHEMA,
            "name": "p2000000000000000005",
            "position": {"x": 24, "y": 156, "z": 1005, "height": 256, "width": 1232, "tabOrder": 5},
            "visual": {
                "visualType": "lineChart",
                "query": {
                    "queryState": {
                        "Category": {"projections": [col_proj("Calendario", "Fecha", active=True)]},
                        "Y": {
                            "projections": [
                                meas_proj("Descomposicion STL", "MP2,5 Mensual Observado"),
                                meas_proj("Descomposicion STL", "Tendencia STL"),
                            ]
                        },
                    }
                },
                "objects": {
                    "legend": [
                        {
                            "properties": {
                                "show": lit("true"),
                                "position": lit("'Top'"),
                                "showTitle": lit("false"),
                            }
                        }
                    ],
                    "dataPoint": [
                        {
                            "properties": {"fill": solid("#64748B")},
                            "selector": {"metadata": "Descomposicion STL.MP2,5 Mensual Observado"},
                        },
                        {
                            "properties": {"fill": solid("#1B4332")},
                            "selector": {"metadata": "Descomposicion STL.Tendencia STL"},
                        },
                    ],
                },
                "visualContainerObjects": card_vco(
                    "Serie mensual de MP2,5 observado y tendencia estructural STL (ug/m3)",
                    "Descomposicion robusta sobre series mensuales con auditoria de brechas",
                ),
            },
        },
        # Matrix: Hour x Month MP2.5 profile
        {
            "$schema": VISUAL_SCHEMA,
            "name": "p2000000000000000006",
            "position": {"x": 24, "y": 424, "z": 1006, "height": 272, "width": 616, "tabOrder": 6},
            "visual": {
                "visualType": "pivotTable",
                "query": {
                    "queryState": {
                        "Rows": {"projections": [col_proj("Ciclo Horario Mensual", "Hora")]},
                        "Columns": {"projections": [col_proj("Ciclo Horario Mensual", "Mes")]},
                        "Values": {
                            "projections": [
                                meas_proj("Ciclo Horario Mensual", "MP2,5 Horario Promedio")
                            ]
                        },
                    }
                },
                "objects": {
                    "columnHeaders": [
                        {
                            "properties": {
                                "columnAdjustment": lit("'growToFit'"),
                                "autoSizeColumnWidth": lit("true"),
                            }
                        }
                    ]
                },
                "visualContainerObjects": card_vco(
                    "Matriz ciclo horario vs mes (MP2,5 ug/m3)",
                    "Filas: Hora (00-23) | Columnas: Mes (1-12)",
                ),
            },
        },
        # Table: Annual completeness audit
        {
            "$schema": VISUAL_SCHEMA,
            "name": "p2000000000000000007",
            "position": {"x": 656, "y": 424, "z": 1007, "height": 272, "width": 600, "tabOrder": 7},
            "visual": {
                "visualType": "tableEx",
                "query": {
                    "queryState": {
                        "Values": {
                            "projections": [
                                col_proj("Estacion", "Estacion"),
                                col_proj("Resumen Anual", "Ano"),
                                meas_proj("Resumen Anual", "Completitud Anual"),
                                meas_proj("Resumen Anual", "Completitud Invierno"),
                                meas_proj("Resumen Anual", "Dias >50 YTD"),
                                meas_proj("Resumen Anual", "MP2,5 Invierno Anual"),
                            ]
                        }
                    }
                },
                "objects": {
                    "columnHeaders": [
                        {
                            "properties": {
                                "columnAdjustment": lit("'growToFit'"),
                                "autoSizeColumnWidth": lit("true"),
                            }
                        }
                    ]
                },
                "visualContainerObjects": card_vco(
                    "Auditoria anual de completitud y episodios YTD",
                    "Evaluacion transparente de brechas de monitoreo por estacion y ano",
                ),
            },
        },
    ]

    for v in p2_visuals:
        write_json(p2_dir / "visuals" / v["name"] / "visual.json", v)

    # ------------------------------------------------------------------
    # Page 3: Clima, Regimenes PCA y Viento
    # ------------------------------------------------------------------
    p3_dir = pages_dir / PAGE3_ID
    write_json(p3_dir / "page.json", make_page(PAGE3_ID, "Clima, Regimenes PCA y Viento"))

    p3_visuals = [
        make_textbox(
            "p3000000000000000001",
            x=24,
            y=16,
            w=1232,
            h=40,
            title="Meteorologia de Episodios, Regimenes PCA (Coyhaique II) y Rosa de Vientos",
            subtitle="Relacion entre estancamiento termico-eolico, conglomerados PCA + K-Means (k=3) y vientos climatologicos",
            title_size="17px",
            sub_size="10px",
            tab=1,
        ),
        make_dropdown_slicer(
            "p3000000000000000002", 24, 64, 320, "Clusters PCA", "Regimen", "Regimen PCA (K-Means)", 2
        ),
        make_dropdown_slicer(
            "p3000000000000000003",
            360,
            64,
            232,
            "Calendario",
            "Temporada Invernal",
            "Temporada Invernal (Abr-Sep)",
            3,
        ),
        make_textbox(
            "p3000000000000000004",
            x=608,
            y=64,
            w=648,
            h=80,
            title="Alcance analitico de clima y viento",
            subtitle="Los regimenes PCA cubren Coyhaique II (2015-2026) con meteorologia completa. La rosa de vientos representa frecuencias climatologicas historicas publicadas por SINCA (estaticas por estacion).",
            title_size="11px",
            sub_size="10px",
            with_card=True,
            tab=4,
        ),
        make_kpi_strip(
            "p3000000000000000005",
            x=24,
            y=156,
            w=1232,
            measures=[
                ("Calidad Aire Diaria", "Temperatura Media"),
                ("Calidad Aire Diaria", "Temperatura en Episodios"),
                ("Calidad Aire Diaria", "Viento Medio"),
                ("Calidad Aire Diaria", "Viento en Episodios"),
            ],
            tab=5,
        ),
        # Scatter chart: PC1 vs PC2 colored by Regimen (1 bubble per date)
        {
            "$schema": VISUAL_SCHEMA,
            "name": "p3000000000000000006",
            "position": {"x": 24, "y": 256, "z": 1006, "height": 440, "width": 648, "tabOrder": 6},
            "visual": {
                "visualType": "scatterChart",
                "query": {
                    "queryState": {
                        "Category": {"projections": [col_proj("Calendario", "Fecha")]},
                        "Series": {"projections": [col_proj("Clusters PCA", "Regimen")]},
                        "X": {"projections": [meas_proj("Clusters PCA", "PC1 Promedio")]},
                        "Y": {"projections": [meas_proj("Clusters PCA", "PC2 Promedio")]},
                        "Size": {"projections": [meas_proj("Clusters PCA", "MP2,5 Promedio Regimen")]},
                    }
                },
                "objects": {
                    "legend": [
                        {
                            "properties": {
                                "show": lit("true"),
                                "position": lit("'Top'"),
                                "showTitle": lit("false"),
                            }
                        }
                    ]
                },
                "visualContainerObjects": card_vco(
                    "Proyeccion diaria PCA (PC1 vs PC2) por regimen ambiental",
                    "Cada punto representa un dia en Coyhaique II; tamano proporcional al MP2,5 24h",
                ),
            },
        },
        # Clustered Bar Chart: Wind Rose climatological frequency by sector & station
        {
            "$schema": VISUAL_SCHEMA,
            "name": "p3000000000000000007",
            "position": {"x": 688, "y": 256, "z": 1007, "height": 440, "width": 568, "tabOrder": 7},
            "visual": {
                "visualType": "clusteredBarChart",
                "query": {
                    "queryState": {
                        "Category": {"projections": [col_proj("Rosa Vientos", "Sector", active=True)]},
                        "Series": {"projections": [col_proj("Estacion", "Estacion")]},
                        "Y": {"projections": [meas_proj("Rosa Vientos", "Frecuencia Viento")]},
                    }
                },
                "objects": {
                    "legend": [
                        {
                            "properties": {
                                "show": lit("true"),
                                "position": lit("'Top'"),
                                "showTitle": lit("false"),
                            }
                        }
                    ]
                },
                "visualContainerObjects": card_vco(
                    "Frecuencia climatologica de direccion del viento (%)",
                    "Sectores de 15 grados (SINCA historico) para Coyhaique I y Coyhaique II",
                ),
            },
        },
    ]

    for v in p3_visuals:
        write_json(p3_dir / "visuals" / v["name"] / "visual.json", v)


# ---------------------------------------------------------------------------
# 3. Structural Self-Checks (TMDL <-> CSV <-> PBIR cross-validation)
# ---------------------------------------------------------------------------


def verify_consistency() -> None:
    import pandas as pd

    tables_dir = MODEL_DIR / "definition" / "tables"
    model_tmdl = (MODEL_DIR / "definition" / "model.tmdl").read_text(encoding="utf-8")
    rel_tmdl = (MODEL_DIR / "definition" / "relationships.tmdl").read_text(encoding="utf-8")

    # 1. Parse all tables, columns, measures, sourceColumns, and CSV files from TMDL
    schema: dict[str, dict[str, set[str]]] = {}
    col_types: dict[tuple[str, str], str] = {}

    for tmdl_path in sorted(tables_dir.glob("*.tmdl")):
        txt = tmdl_path.read_text(encoding="utf-8")
        # Ensure tab-only indentation (no leading spaces)
        for lineno, line in enumerate(txt.splitlines(), 1):
            assert not line.startswith(" "), f"Leading space in {tmdl_path.name}:{lineno}"

        m_table = re.search(r"^table (?:'([^']+)'|(\S+))", txt, re.M)
        assert m_table, f"No table declaration in {tmdl_path.name}"
        tname = m_table.group(1) or m_table.group(2)
        schema[tname] = {"columns": set(), "measures": set()}

        csv_match = re.search(r'& "\\([^"]+\.csv)"', txt)
        assert csv_match, f"No CSV reference in {tmdl_path.name}"
        csv_file = DATA_DIR / csv_match.group(1)
        assert csv_file.exists(), f"Missing CSV: {csv_file}"
        csv_cols = set(pd.read_csv(csv_file, nrows=1).columns)

        current_col = None
        for line in txt.splitlines():
            mm = re.match(r"^\tmeasure (?:'([^']+)'|(\S+)) =", line)
            if mm:
                schema[tname]["measures"].add(mm.group(1) or mm.group(2))
                current_col = None
                continue
            mc = re.match(r"^\tcolumn (?:'([^']+)'|(\S+))$", line)
            if mc:
                current_col = mc.group(1) or mc.group(2)
                schema[tname]["columns"].add(current_col)
                continue
            if current_col:
                mt = re.match(r"^\t\tdataType:\s*(\S+)", line)
                if mt:
                    col_types[(tname, current_col)] = mt.group(1)
                ms = re.match(r"^\t\tsourceColumn:\s*(\S+)", line)
                if ms:
                    sc = ms.group(1)
                    assert sc in csv_cols, f"{tname}.{current_col} sourceColumn '{sc}' not in {csv_file.name}"

    # 2. Verify every ref table in model.tmdl exists
    for m_ref in re.finditer(r"^ref table (?:'([^']+)'|(\S+))", model_tmdl, re.M):
        rname = m_ref.group(1) or m_ref.group(2)
        assert rname in schema, f"ref table '{rname}' missing .tmdl file"

    # 3. Verify relationships refer to valid columns with matching dataType
    rel_blocks = re.split(r"(?m)^relationship ", rel_tmdl)[1:]
    assert len(rel_blocks) == 9, f"Expected 9 relationships, found {len(rel_blocks)}"
    col_ref_re = r"(?:'([^']+)'|([^.\s]+))\.(?:'([^']+)'|(\S+))"
    for blk in rel_blocks:
        mf = re.search(rf"fromColumn:\s*{col_ref_re}", blk)
        mt = re.search(rf"toColumn:\s*{col_ref_re}", blk)
        assert mf and mt, f"Malformed relationship block:\n{blk}"
        ft, fc = mf.group(1) or mf.group(2), mf.group(3) or mf.group(4)
        tt, tc = mt.group(1) or mt.group(2), mt.group(3) or mt.group(4)
        assert fc in schema[ft]["columns"], f"Missing fromColumn {ft}.{fc}"
        assert tc in schema[tt]["columns"], f"Missing toColumn {tt}.{tc}"
        assert col_types[(ft, fc)] == col_types[(tt, tc)], (
            f"Type mismatch on relationship {ft}.{fc} ({col_types[(ft, fc)]}) -> {tt}.{tc} ({col_types[(tt, tc)]})"
        )

    # 4. Verify every date in fact tables exists in dim_fecha.csv
    dim_dates = set(pd.read_csv(DATA_DIR / "dim_fecha.csv")["date"])
    for fn in ["fact_calidad_aire_diaria.csv", "fact_stl_descomposicion.csv", "fact_clusters_pca.csv"]:
        f_dates = set(pd.read_csv(DATA_DIR / fn)["date"])
        missing = f_dates - dim_dates
        assert not missing, f"{fn} has {len(missing)} dates not in dim_fecha.csv"

    # 5. Verify every PBIR visual entity/property exists in TMDL
    def walk_fields(node: object, vpath: str) -> None:
        if isinstance(node, dict):
            for kind, bucket in (("Column", "columns"), ("Measure", "measures")):
                if kind in node and isinstance(node[kind], dict) and "Property" in node[kind]:
                    ent = node[kind]["Expression"]["SourceRef"]["Entity"]
                    prop = node[kind]["Property"]
                    assert ent in schema, f"{vpath}: unknown entity '{ent}'"
                    assert prop in schema[ent][bucket], f"{vpath}: unknown {kind} '{ent}.{prop}'"
            for v in node.values():
                walk_fields(v, vpath)
        elif isinstance(node, list):
            for item in node:
                walk_fields(item, vpath)

    visual_files = list((REPORT_DIR / "definition" / "pages").glob("*/visuals/*/visual.json"))
    assert len(visual_files) == 22, f"Expected 22 visuals across 3 pages, found {len(visual_files)}"
    for vf in visual_files:
        walk_fields(json.loads(vf.read_text(encoding="utf-8")), str(vf.relative_to(REPORT_DIR)))

    print(
        f"[OK] PBIP build verified: {len(schema)} TMDL tables, {sum(len(v['measures']) for v in schema.values())} DAX measures, "
        f"{len(rel_blocks)} relationships, 3 PBIR pages, {len(visual_files)} visuals."
    )


if __name__ == "__main__":
    build_semantic_model()
    build_report()
    verify_consistency()
