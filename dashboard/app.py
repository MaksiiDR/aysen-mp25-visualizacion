"""
dashboard/app.py
----------------
Prototipo interactivo en Plotly Dash para explorar la evolucion de episodios de
MP2,5 y su relacion con la meteorologia en la Region de Aysen (2013-2026).

Sirve como herramienta de validacion visual preliminar en Python previa a la
implementacion ejecutiva en Power BI (ver powerbi/README_PowerBI.md).

Ejecucion:
    python dashboard/app.py
"""

from __future__ import annotations

import json
from pathlib import Path

import dash
from dash import Dash, Input, Output, dash_table, dcc, html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data_processed"
PBI_DIR = BASE_DIR / "powerbi" / "data"

# Carga rapida desde tablas pre-procesadas (<1 s)
DAILY = pd.read_csv(PROC_DIR / "all_stations_daily.csv", parse_dates=["date"])
YEARLY = pd.read_csv(PROC_DIR / "yearly_summary_completeness.csv")
HEATMAP = pd.read_csv(PROC_DIR / "heatmap_hour_month.csv")
STL_DF = pd.read_csv(PROC_DIR / "stl_decomposition.csv", parse_dates=["date"])
CCF_DF = pd.read_csv(PROC_DIR / "ccf_meteorology_mp25.csv")
WIND_ROSE = pd.read_csv(PROC_DIR / "rosa_vientos_frecuencias.csv")
CLUSTERS = pd.read_csv(PROC_DIR / "pca_clusters_daily.csv", parse_dates=["date"])
STATIONS = pd.read_csv(PBI_DIR / "dim_estacion.csv")
with open(PROC_DIR / "analysis_results_summary.json", "r", encoding="utf-8") as fh:
    SUMMARY = json.load(fh)

STATION_LABELS = dict(zip(STATIONS["station_id"], STATIONS["station_name"] + " (" + STATIONS["city"] + ")"))
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
GEC_ORDER = [
    "Bueno (<=50)",
    "Regular (50-79)",
    "Alerta (80-109)",
    "Preemergencia (110-169)",
    "Emergencia (>=170)",
]
GEC_COLORS = {
    "Bueno (<=50)": "#2A9D8F",
    "Regular (50-79)": "#E9C46A",
    "Alerta (80-109)": "#F4A261",
    "Preemergencia (110-169)": "#E76F51",
    "Emergencia (>=170)": "#9B2226",
}

app = Dash(__name__, title="MP2,5 y Clima — Region de Aysen (SINCA 2013-2026)")


def kpi_card(title: str, value: str, subtitle: str, accent: str = "#0F4C81") -> html.Div:
    return html.Div(
        style={
            "background": "#FFFFFF",
            "borderRadius": "8px",
            "padding": "14px 16px",
            "borderLeft": f"4px solid {accent}",
            "boxShadow": "0 1px 3px rgba(15,23,42,0.08)",
            "flex": "1",
            "minWidth": "190px",
        },
        children=[
            html.Div(title, style={"fontSize": "12px", "color": "#475569", "fontWeight": "600", "textTransform": "uppercase"}),
            html.Div(value, style={"fontSize": "24px", "color": "#0F172A", "fontWeight": "700", "margin": "4px 0"}),
            html.Div(subtitle, style={"fontSize": "12px", "color": "#64748B"}),
        ],
    )


app.layout = html.Div(
    style={
        "fontFamily": "'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
        "backgroundColor": "#F8FAFC",
        "minHeight": "100vh",
        "padding": "18px 24px",
        "color": "#0F172A",
    },
    children=[
        # Encabezado
        html.Div(
            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "flexWrap": "wrap", "marginBottom": "14px"},
            children=[
                html.Div(
                    children=[
                        html.H2(
                            "Episodios de MP2,5 y Clima en la Region de Aysen (2013-2026)",
                            style={"margin": "0", "color": "#0F172A", "fontSize": "22px"},
                        ),
                        html.Div(
                            "Datos horarios SINCA (MMA) | Norma DS N° 12/2011 (50 ug/m3, >=18 h validas) | Prototipo Python (previo a Power BI)",
                            style={"fontSize": "13px", "color": "#475569", "marginTop": "2px"},
                        ),
                    ]
                ),
                html.Div(
                    "Corte de datos: 23 oct 2026 (2026 = ano incompleto)",
                    style={
                        "background": "#FEF3C7",
                        "color": "#92400E",
                        "padding": "6px 12px",
                        "borderRadius": "6px",
                        "fontSize": "12px",
                        "fontWeight": "600",
                    },
                ),
            ],
        ),
        # Barra de filtros
        html.Div(
            style={
                "display": "flex",
                "gap": "16px",
                "flexWrap": "wrap",
                "background": "#FFFFFF",
                "padding": "14px 16px",
                "borderRadius": "8px",
                "boxShadow": "0 1px 3px rgba(15,23,42,0.06)",
                "marginBottom": "14px",
            },
            children=[
                html.Div(
                    style={"minWidth": "240px", "flex": "1"},
                    children=[
                        html.Label("Estacion principal", style={"fontSize": "12px", "fontWeight": "600", "color": "#334155"}),
                        dcc.Dropdown(
                            id="station-dd",
                            options=[{"label": v, "value": k} for k, v in STATION_LABELS.items()],
                            value="CoyhaiqueII",
                            clearable=False,
                        ),
                    ],
                ),
                html.Div(
                    style={"minWidth": "260px", "flex": "1"},
                    children=[
                        html.Label("Ventana de comparacion anual (manejo 2026)", style={"fontSize": "12px", "fontWeight": "600", "color": "#334155"}),
                        dcc.RadioItems(
                            id="window-mode",
                            options=[
                                {"label": " YTD comparable (Ene-23 Oct)", "value": "ytd"},
                                {"label": " Invierno (Abr-Sep)", "value": "winter"},
                                {"label": " Ano completo (excl. 2026)", "value": "complete"},
                            ],
                            value="ytd",
                            inline=True,
                            style={"marginTop": "6px", "fontSize": "13px", "display": "flex", "gap": "12px"},
                        ),
                    ],
                ),
                html.Div(
                    style={"minWidth": "280px", "flex": "1.2"},
                    children=[
                        html.Label("Rango de anos", style={"fontSize": "12px", "fontWeight": "600", "color": "#334155"}),
                        dcc.RangeSlider(
                            id="year-slider",
                            min=2014,
                            max=2026,
                            step=1,
                            value=[2014, 2026],
                            marks={y: str(y) for y in range(2014, 2027, 2)},
                        ),
                    ],
                ),
            ],
        ),
        # KPIs dinamicos
        html.Div(id="kpi-row", style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "14px"}),
        # Pestanas
        dcc.Tabs(
            id="main-tabs",
            value="tab-stl",
            children=[
                dcc.Tab(label="1. Evolucion, Episodios y STL", value="tab-stl"),
                dcc.Tab(label="2. Ciclo Diario y Estacional", value="tab-heatmap"),
                dcc.Tab(label="3. Mapa y Comparacion Regional", value="tab-map"),
                dcc.Tab(label="4. Meteorologia, CCF y Rosa de Vientos", value="tab-met"),
                dcc.Tab(label="5. PCA y Regimenes (Clustering)", value="tab-pca"),
            ],
        ),
        html.Div(id="tab-content", style={"marginTop": "14px"}),
    ],
)


@app.callback(
    Output("kpi-row", "children"),
    Input("station-dd", "value"),
    Input("window-mode", "value"),
    Input("year-slider", "value"),
)
def update_kpis(station_id: str, window_mode: str, year_range: list[int]):
    df = DAILY[(DAILY["station_id"] == station_id) & (DAILY["year"].between(year_range[0], year_range[1]))].copy()
    if window_mode == "ytd":
        df = df[df["is_ytd_window"]]
        w_lbl = "Ventana Ene-23 Oct"
    elif window_mode == "winter":
        df = df[df["is_winter_season"]]
        w_lbl = "Temporada Abr-Sep"
    else:
        df = df[df["year"] < 2026]
        w_lbl = "Anos completos (sin 2026)"

    valid = df[df["mp25_valid_day"]]
    mean_mp25 = valid["mp25_24h"].mean() if len(valid) else np.nan
    days_over = int(valid["over_norm_50"].sum()) if len(valid) else 0
    max_mp25 = valid["mp25_24h"].max() if len(valid) else np.nan
    comp_pct = 100.0 * len(valid) / len(df) if len(df) else 0.0
    prelim_pct = 100.0 * (valid["mp25_day_quality"] != "validado").mean() if len(valid) else 0.0

    return [
        kpi_card("MP2,5 Promedio 24h", f"{mean_mp25:.1f} ug/m3" if pd.notna(mean_mp25) else "N/D", w_lbl, "#0F4C81"),
        kpi_card("Dias Sobre Norma (>50)", f"{days_over:,}", f"{100*days_over/max(len(valid),1):.1f}% de dias validos", "#C1121F"),
        kpi_card("Maximo Diario 24h", f"{max_mp25:.0f} ug/m3" if pd.notna(max_mp25) else "N/D", f"Umbral emergencia: 170 ug/m3", "#E76F51"),
        kpi_card("Calidad y Completitud", f"{comp_pct:.1f}%", f"Preliminar/no val.: {prelim_pct:.1f}%", "#2A9D8F"),
    ]


@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "value"),
    Input("station-dd", "value"),
    Input("window-mode", "value"),
    Input("year-slider", "value"),
)
def render_tab(tab: str, station_id: str, window_mode: str, year_range: list[int]):
    y0, y1 = year_range
    card_style = {"background": "#FFFFFF", "padding": "14px", "borderRadius": "8px", "boxShadow": "0 1px 3px rgba(15,23,42,0.08)"}

    if tab == "tab-stl":
        # Serie mensual + tendencia STL
        stl_s = STL_DF[(STL_DF["station_id"] == station_id) & (STL_DF["date"].dt.year.between(y0, y1))]
        fig_stl = go.Figure()
        fig_stl.add_trace(go.Scatter(x=stl_s["date"], y=stl_s["observed_mp25"], mode="lines+markers", name="Promedio mensual", line={"color": "#94A3B8", "width": 1.5}, marker={"size": 4}))
        fig_stl.add_trace(go.Scatter(x=stl_s["date"], y=stl_s["trend"], mode="lines", name="Tendencia STL (robusta)", line={"color": "#0F4C81", "width": 3}))
        fig_stl.add_hline(y=50, line_dash="dash", line_color="#C1121F", annotation_text="Norma diaria DS 12 (50 ug/m3)")
        fig_stl.update_layout(title=f"Serie mensual y tendencia STL — {STATION_LABELS[station_id]}", yaxis_title="MP2,5 (ug/m3)", template="plotly_white", height=360, margin={"l": 50, "r": 20, "t": 45, "b": 40})

        # Barras apiladas anuales por categoria GEC (>50)
        d = DAILY[(DAILY["station_id"] == station_id) & (DAILY["year"].between(y0, y1)) & (DAILY["mp25_valid_day"])].copy()
        if window_mode == "ytd":
            d = d[d["is_ytd_window"]]
        elif window_mode == "winter":
            d = d[d["is_winter_season"]]
        else:
            d = d[d["year"] < 2026]
        d_over = d[d["over_norm_50"] == 1]
        gec_counts = d_over.groupby(["year", "gec_category"]).size().reset_index(name="days")
        fig_bar = px.bar(
            gec_counts,
            x="year",
            y="days",
            color="gec_category",
            category_orders={"gec_category": GEC_ORDER[1:]},
            color_discrete_map=GEC_COLORS,
            title=f"Dias sobre la norma (>50 ug/m3) por categoria GEC — {STATION_LABELS[station_id]}",
            labels={"year": "Ano", "days": "Dias sobre 50 ug/m3", "gec_category": "Categoria DS 12"},
        )
        fig_bar.update_layout(template="plotly_white", height=360, margin={"l": 50, "r": 20, "t": 45, "b": 40})
        return html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"},
            children=[html.Div(dcc.Graph(figure=fig_stl), style=card_style), html.Div(dcc.Graph(figure=fig_bar), style=card_style)],
        )

    if tab == "tab-heatmap":
        hm = HEATMAP[HEATMAP["station_id"] == station_id]
        piv = hm.pivot(index="hour", columns="month", values="mp25_mean").reindex(index=range(24), columns=range(1, 13))
        fig_hm = go.Figure(
            data=go.Heatmap(
                z=piv.values,
                x=MESES,
                y=[f"{h:02d}:00" for h in range(24)],
                colorscale="YlOrRd",
                colorbar={"title": "MP2,5 (ug/m3)"},
            )
        )
        fig_hm.update_layout(
            title=f"Ciclo diario y estacional (Hora x Mes) — {STATION_LABELS[station_id]}",
            xaxis_title="Mes",
            yaxis_title="Hora del dia",
            template="plotly_white",
            height=450,
            margin={"l": 60, "r": 20, "t": 45, "b": 45},
        )
        # Perfil horario invierno vs resto del ano
        hm_w = hm[hm["month"].between(4, 9)].groupby("hour")["mp25_mean"].mean()
        hm_s = hm[~hm["month"].between(4, 9)].groupby("hour")["mp25_mean"].mean()
        fig_diurnal = go.Figure()
        fig_diurnal.add_trace(go.Scatter(x=hm_w.index, y=hm_w.values, mode="lines+markers", name="Invierno (Abr-Sep)", line={"color": "#C1121F", "width": 2.5}))
        fig_diurnal.add_trace(go.Scatter(x=hm_s.index, y=hm_s.values, mode="lines+markers", name="Resto del ano (Oct-Mar)", line={"color": "#2A9D8F", "width": 2.5}))
        fig_diurnal.add_hline(y=50, line_dash="dash", line_color="#475569")
        fig_diurnal.update_layout(
            title="Perfil horario promedio: temporada fria vs. resto del ano",
            xaxis_title="Hora del dia",
            yaxis_title="MP2,5 promedio horario (ug/m3)",
            template="plotly_white",
            height=450,
            margin={"l": 55, "r": 20, "t": 45, "b": 45},
        )
        return html.Div(
            style={"display": "grid", "gridTemplateColumns": "1.2fr 1fr", "gap": "14px"},
            children=[html.Div(dcc.Graph(figure=fig_hm), style=card_style), html.Div(dcc.Graph(figure=fig_diurnal), style=card_style)],
        )

    if tab == "tab-map":
        sub = DAILY[(DAILY["year"].between(max(y0, 2022), y1)) & (DAILY["mp25_valid_day"])]
        if window_mode == "ytd":
            sub = sub[sub["is_ytd_window"]]
        elif window_mode == "winter":
            sub = sub[sub["is_winter_season"]]
        else:
            sub = sub[sub["year"] < 2026]
        agg = sub.groupby("station_id", as_index=False).agg(
            mp25_mean=("mp25_24h", "mean"),
            days_over_50=("over_norm_50", "sum"),
            valid_days=("mp25_valid_day", "sum"),
        )
        agg["tasa_episodios_pct"] = (100.0 * agg["days_over_50"] / agg["valid_days"]).round(1)
        m_df = STATIONS.merge(agg, on="station_id", how="left")
        fig_map = px.scatter_map(
            m_df,
            lat="lat",
            lon="lon",
            size="tasa_episodios_pct",
            color="mp25_mean",
            hover_name="station_name",
            hover_data={"city": True, "mp25_mean": ":.1f", "tasa_episodios_pct": ":.1f", "lat": False, "lon": False},
            color_continuous_scale="YlOrRd",
            size_max=34,
            zoom=6.2,
            center={"lat": -46.15, "lon": -72.35},
            title="Mapa regional de estaciones SINCA (tamano = % dias >50, color = MP2,5 medio)",
        )
        fig_map.update_layout(height=450, margin={"l": 10, "r": 10, "t": 45, "b": 10})

        # Comparacion multi-estacion anual (invierno Abr-Sep)
        y_sub = YEARLY[(YEARLY["year"].between(y0, y1)) & (YEARLY["is_complete_winter"])]
        fig_comp = px.line(
            y_sub,
            x="year",
            y="days_over_50_winter",
            color="station_id",
            markers=True,
            title="Dias sobre norma en temporada invernal (Abr-Sep) por estacion",
            labels={"year": "Ano", "days_over_50_winter": "Dias >50 ug/m3 (Abr-Sep)", "station_id": "Estacion"},
        )
        fig_comp.update_layout(template="plotly_white", height=450, margin={"l": 50, "r": 20, "t": 45, "b": 40})
        return html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "14px"},
            children=[html.Div(dcc.Graph(figure=fig_map), style=card_style), html.Div(dcc.Graph(figure=fig_comp), style=card_style)],
        )

    if tab == "tab-met":
        # CCF en Coyhaique II
        var_names = {"temp": "Temperatura", "velviento": "Velocidad viento", "humedad": "Humedad relativa", "presion": "Presion atm."}
        ccf_plot = CCF_DF.copy()
        ccf_plot["Variable"] = ccf_plot["variable"].map(var_names)
        fig_ccf = px.line(
            ccf_plot,
            x="lag_days",
            y="spearman_rho",
            color="Variable",
            markers=True,
            title="Correlacion cruzada (Spearman CCF) entre clima(t-k) y MP2,5(t) — Coyhaique II",
            labels={"lag_days": "Rezago k (dias; k>0: clima antecede a MP2,5)", "spearman_rho": "Rho de Spearman"},
        )
        fig_ccf.add_hline(y=0, line_color="#64748B", line_width=1)
        fig_ccf.add_vline(x=0, line_dash="dot", line_color="#64748B")
        fig_ccf.update_layout(template="plotly_white", height=420, margin={"l": 50, "r": 20, "t": 45, "b": 45})

        # Rosa de vientos climatologica (si aplica a la estacion)
        wr_sid = station_id if station_id in WIND_ROSE["station_id"].unique() else "CoyhaiqueII"
        wr = WIND_ROSE[WIND_ROSE["station_id"] == wr_sid]
        fig_wr = go.Figure(
            go.Barpolar(
                r=wr["freq_pct"],
                theta=wr["angle_center_deg"],
                width=[14.5] * len(wr),
                marker_color=wr["freq_pct"],
                marker_colorscale="Blues",
            )
        )
        note_wr = (
            f"Rosa de vientos climatologica ({wr_sid})"
            if station_id == wr_sid
            else f"Cochrane no posee rosa de vientos en SINCA (se muestra {wr_sid})"
        )
        fig_wr.update_layout(
            title=note_wr,
            polar={"angularaxis": {"direction": "clockwise", "rotation": 90}, "radialaxis": {"ticksuffix": "%"}},
            template="plotly_white",
            height=420,
            margin={"l": 30, "r": 30, "t": 55, "b": 30},
        )
        banner = html.Div(
            "Nota metodologica (verificacion de datos): SINCA publica la direccion del viento solo como tabla historica agregada de frecuencias por 24 sectores de 15° (no existe direccion horaria). Por ello, la rosa muestra el regimen climatologico predominante y la relacion con episodios se analiza mediante velocidad del viento horaria/diaria.",
            style={"background": "#EFF6FF", "color": "#1E3A8A", "padding": "10px 14px", "borderRadius": "6px", "fontSize": "13px", "marginBottom": "12px"},
        )
        return html.Div(
            children=[
                banner,
                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1.2fr 1fr", "gap": "14px"},
                    children=[html.Div(dcc.Graph(figure=fig_ccf), style=card_style), html.Div(dcc.Graph(figure=fig_wr), style=card_style)],
                ),
            ]
        )

    # tab-pca
    fig_pca = px.scatter(
        CLUSTERS,
        x="PC1",
        y="PC2",
        color="cluster_name",
        hover_data={"date": True, "mp25_24h": ":.1f", "temp": ":.1f", "velviento": ":.2f", "humedad": ":.1f", "presion": ":.1f"},
        opacity=0.65,
        title="Proyeccion PCA (PC1 vs PC2) y clusters de regimenes climatico-contaminantes — Coyhaique II",
        color_discrete_sequence=["#2A9D8F", "#E9C46A", "#C1121F", "#0F4C81"],
    )
    fig_pca.update_layout(template="plotly_white", height=440, margin={"l": 50, "r": 20, "t": 45, "b": 45})

    prof_df = pd.DataFrame(SUMMARY["pca_clustering"]["cluster_profiles"])[
        ["cluster_name", "n_days", "mp25_median", "episode_rate_pct", "share_of_all_episodes_pct", "temp_mean", "velviento_mean", "humedad_mean", "presion_mean"]
    ]
    prof_df.columns = ["Regimen", "Dias", "MP2,5 med.", "Tasa >50 (%)", "% total epis.", "Temp (C)", "Viento (m/s)", "HR (%)", "Presion (hPa)"]
    table = dash_table.DataTable(
        data=prof_df.to_dict("records"),
        columns=[{"name": c, "id": c} for c in prof_df.columns],
        style_cell={"textAlign": "center", "padding": "8px", "fontSize": "13px"},
        style_header={"backgroundColor": "#0F4C81", "color": "white", "fontWeight": "600"},
    )
    return html.Div(
        style={"display": "grid", "gridTemplateColumns": "1.25fr 1fr", "gap": "14px", "alignItems": "start"},
        children=[
            html.Div(dcc.Graph(figure=fig_pca), style=card_style),
            html.Div(
                style=card_style,
                children=[
                    html.H4("Perfiles de regimenes diarios (Coyhaique II)", style={"marginTop": "0"}),
                    table,
                ],
            ),
        ],
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
