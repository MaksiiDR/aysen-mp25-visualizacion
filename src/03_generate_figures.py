"""
03_generate_figures.py
----------------------
Genera:
1) Las 3 figuras en alta resolucion (300 dpi, estilo IEEE, sin titulos internos,
   fuente serif acorde al documento, ejes con unidades) para el paper en
   `informe/figures/` (junto a 1 tabla = maximo 4 tablas/figuras).
2) Graficos individuales limpios (sans-serif, alta legibilidad) para la
   presentacion final de 8 minutos en `presentacion/figures/`.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data_processed"
FIG_PAPER = BASE_DIR / "informe" / "figures"
FIG_SLIDE = BASE_DIR / "presentacion" / "figures"
FIG_PAPER.mkdir(parents=True, exist_ok=True)
FIG_SLIDE.mkdir(parents=True, exist_ok=True)

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
GEC_COLS = [
    ("Regular (50-79)", "#E9C46A", "Regular (50–79)"),
    ("Alerta (80-109)", "#F4A261", "Alerta (80–109)"),
    ("Preemergencia (110-169)", "#E76F51", "Preemerg. (110–169)"),
    ("Emergencia (>=170)", "#9B2226", "Emerg. (>=170)"),
]


def set_ieee_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif"],
            "font.size": 8.0,
            "axes.titlesize": 8.5,
            "axes.labelsize": 8.0,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 7.0,
            "axes.linewidth": 0.7,
            "grid.linewidth": 0.4,
            "grid.alpha": 0.3,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def set_slide_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Arial"],
            "font.size": 11.0,
            "axes.titlesize": 12.5,
            "axes.labelsize": 11.0,
            "xtick.labelsize": 10.0,
            "ytick.labelsize": 10.0,
            "legend.fontsize": 9.8,
            "axes.linewidth": 0.9,
            "grid.linewidth": 0.5,
            "grid.alpha": 0.3,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def make_fig1_paper(daily: pd.DataFrame, stl: pd.DataFrame, heatmap: pd.DataFrame) -> None:
    """Fig. 1 (IEEE 2-col): (a) Tendencia STL regional, (b) Dias >50 GEC Coyhaique II, (c) Heatmap Hora x Mes."""
    set_ieee_style()
    fig = plt.figure(figsize=(7.16, 4.75))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.05, 1.0], width_ratios=[1.12, 1.0], hspace=0.38, wspace=0.28)

    # (a) Tendencia STL mensual regional + corte 2026
    ax_a = fig.add_subplot(gs[0, 0])
    palette = {"CoyhaiqueII": "#0F4C81", "Vialidad": "#2A9D8F", "Cochrane": "#C1121F"}
    labels = {"CoyhaiqueII": "Coyhaique II", "Vialidad": "Vialidad (Pto. Aysén)", "Cochrane": "Cochrane"}
    for sid in ["CoyhaiqueII", "Vialidad", "Cochrane"]:
        sub = stl[stl["station_id"] == sid].sort_values("date")
        if sid == "CoyhaiqueII":
            ax_a.plot(sub["date"], sub["observed_mp25"], color="#CBD5E1", lw=0.65, zorder=1, label="Mensual (Coyhaique II)")
        ax_a.plot(sub["date"], sub["trend"], color=palette[sid], lw=1.7, zorder=3, label=f"Tend. STL {labels[sid]}")

    ax_a.axhline(50, color="#64748B", ls="--", lw=0.8, zorder=2)
    ax_a.text(pd.Timestamp("2018-02-01"), 54, "Norma 24h (50 µg/m³)", fontsize=6.4, color="#475569")
    ax_a.axvspan(pd.Timestamp("2026-01-01"), pd.Timestamp("2026-10-23"), color="#FEF3C7", alpha=0.75, zorder=0)
    ax_a.text(pd.Timestamp("2026-05-15"), 102, "2026*\nYTD", fontsize=6.0, color="#92400E", ha="center", fontweight="bold")
    ax_a.set_ylabel("MP2,5 (µg/m³)")
    ax_a.set_xlabel("Año")
    ax_a.set_ylim(0, 215)
    ax_a.xaxis.set_major_locator(mdates.YearLocator(2))
    ax_a.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax_a.grid(True, axis="y")
    ax_a.legend(loc="upper right", frameon=True, framealpha=0.92, edgecolor="#E2E8F0", ncol=2, borderpad=0.3, handlelength=1.2, columnspacing=0.6, fontsize=6.2)
    ax_a.text(-0.14, 1.04, "(a)", transform=ax_a.transAxes, fontweight="bold", fontsize=8.5)

    # (b) Dias sobre norma por categoria GEC en Coyhaique II (2014-2026 YTD)
    ax_b = fig.add_subplot(gs[0, 1])
    c2 = daily[(daily["station_id"] == "CoyhaiqueII") & (daily["year"] >= 2014) & (daily["mp25_valid_day"]) & (daily["over_norm_50"] == 1)]
    years = list(range(2014, 2027))
    bottoms = np.zeros(len(years))
    x = np.arange(len(years))
    for cat_key, color, cat_lbl in GEC_COLS:
        vals = [int(((c2["year"] == y) & (c2["gec_category"] == cat_key)).sum()) for y in years]
        bars = ax_b.bar(x, vals, bottom=bottoms, color=color, width=0.72, label=cat_lbl, edgecolor="white", linewidth=0.3)
        # Sombrear barra 2026* para indicar ano incompleto YTD
        bars[-1].set_hatch("///")
        bars[-1].set_edgecolor("#1E293B")
        bottoms += np.array(vals)
    for xi, tot in zip(x, bottoms):
        ax_b.text(xi, tot + 2.5, f"{int(tot)}", ha="center", va="bottom", fontsize=6.2, color="#1E293B")
    ax_b.set_xticks(x)
    ax_b.set_xticklabels([str(y)[2:] + ("*" if y == 2026 else "") for y in years])
    ax_b.set_xlabel("Año (*2026: ene–23 oct, 100% invierno)")
    ax_b.set_ylabel("Días > 50 µg/m³")
    ax_b.set_ylim(0, 208)
    ax_b.grid(True, axis="y")
    ax_b.legend(loc="upper right", frameon=True, framealpha=0.92, edgecolor="#E2E8F0", ncol=2, borderpad=0.3, columnspacing=0.6, handletextpad=0.4, fontsize=6.3)
    ax_b.text(-0.14, 1.04, "(b)", transform=ax_b.transAxes, fontweight="bold", fontsize=8.5)

    # (c) Heatmap Hora x Mes (Coyhaique II)
    ax_c = fig.add_subplot(gs[1, :])
    hm = heatmap[heatmap["station_id"] == "CoyhaiqueII"]
    piv = hm.pivot(index="hour", columns="month", values="mp25_mean").reindex(index=range(24), columns=range(1, 13))
    im = ax_c.imshow(piv.values.T, aspect="auto", cmap="YlOrRd", origin="upper", vmin=0, vmax=175)
    ax_c.set_xticks(range(0, 24, 2))
    ax_c.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)])
    ax_c.set_yticks(range(12))
    ax_c.set_yticklabels(MESES)
    ax_c.set_xlabel("Hora del día (UTC-3 / hora local SINCA)")
    ax_c.set_ylabel("Mes")
    ax_c.spines["top"].set_visible(True)
    ax_c.spines["right"].set_visible(True)
    cbar = fig.colorbar(im, ax=ax_c, pad=0.015, fraction=0.025)
    cbar.set_label("MP2,5 promedio horario (µg/m³)", fontsize=7.5)
    cbar.ax.tick_params(labelsize=6.8)
    ax_c.text(-0.06, 1.04, "(c)", transform=ax_c.transAxes, fontweight="bold", fontsize=8.5)

    fig.savefig(FIG_PAPER / "fig1_temporal_patterns.png", bbox_inches="tight")
    plt.close(fig)


def make_fig2_paper(daily: pd.DataFrame, ccf_df: pd.DataFrame, wind_rose: pd.DataFrame, summary: dict) -> None:
    """Fig. 2 (IEEE 2-col): (a) CCF clima vs MP2,5, (b) Clima en episodios vs normales, (c) Rosa de vientos climatologica."""
    set_ieee_style()
    fig = plt.figure(figsize=(7.16, 2.85))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1.2, 1.05, 1.0], wspace=0.34)

    # (a) CCF Spearman lags -5..+5
    ax_a = fig.add_subplot(gs[0, 0])
    var_cfg = [
        ("temp", "Temperatura", "#C1121F", "o"),
        ("velviento", "Vel. viento", "#0F4C81", "s"),
        ("humedad", "Humedad rel.", "#2A9D8F", "^"),
        ("presion", "Presión atm.", "#D97706", "D"),
    ]
    sub_ccf = ccf_df[ccf_df["lag_days"].between(-5, 5)]
    for v, lbl, col, mk_sym in var_cfg:
        s = sub_ccf[sub_ccf["variable"] == v].sort_values("lag_days")
        ax_a.plot(s["lag_days"], s["spearman_rho"], color=col, marker=mk_sym, ms=3.2, lw=1.2, label=lbl)
    ax_a.axhline(0, color="#64748B", lw=0.7)
    ax_a.axvline(0, color="#94A3B8", ls=":", lw=0.8)
    acf1 = summary["temporal_and_met"]["acf_lags_0_14"][1]
    ax_a.text(0.03, 0.37, f"Persistencia MP2,5:\nACF(1d) = {acf1:.2f}", transform=ax_a.transAxes, fontsize=6.3, bbox={"boxstyle": "round,pad=0.25", "facecolor": "#F8FAFC", "edgecolor": "#CBD5E1"})
    ax_a.set_xlabel("Rezago k (días; k>0: clima antecede)")
    ax_a.set_ylabel("Correlación Spearman (ρ)")
    ax_a.set_ylim(-0.88, 0.78)
    ax_a.set_xticks([-5, -3, -1, 0, 1, 3, 5])
    ax_a.grid(True)
    ax_a.legend(loc="center right", bbox_to_anchor=(0.99, 0.62), frameon=True, framealpha=0.92, edgecolor="#E2E8F0", borderpad=0.25, handlelength=1.3, fontsize=6.2)
    ax_a.text(-0.18, 1.04, "(a)", transform=ax_a.transAxes, fontweight="bold", fontsize=8.5)

    # (b) Boxplots comparativos (Temperatura y Velocidad del viento: Normal vs Episodio >50)
    ax_b = fig.add_subplot(gs[0, 1])
    c2 = daily[(daily["station_id"] == "CoyhaiqueII") & (daily["mp25_valid_day"])].dropna(subset=["temp", "velviento"])
    ep = c2[c2["over_norm_50"] == 1]
    no = c2[c2["over_norm_50"] == 0]

    # Eje izquierdo: Temperatura (°C), Eje derecho: Velocidad del viento (m/s)
    bp_t = ax_b.boxplot(
        [no["temp"].values, ep["temp"].values],
        positions=[0.8, 1.5],
        widths=0.45,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#0F172A", "linewidth": 1.2},
        boxprops={"linewidth": 0.7},
    )
    bp_t["boxes"][0].set_facecolor("#93C5FD")
    bp_t["boxes"][1].set_facecolor("#F87171")

    ax_b2 = ax_b.twinx()
    ax_b2.spines["top"].set_visible(False)
    bp_v = ax_b2.boxplot(
        [no["velviento"].values, ep["velviento"].values],
        positions=[2.6, 3.3],
        widths=0.45,
        patch_artist=True,
        showfliers=False,
        medianprops={"color": "#0F172A", "linewidth": 1.2},
        boxprops={"linewidth": 0.7},
    )
    bp_v["boxes"][0].set_facecolor("#6EE7B7")
    bp_v["boxes"][1].set_facecolor("#FBBF24")

    ax_b.set_xticks([0.8, 1.5, 2.6, 3.3])
    ax_b.set_xticklabels(["≤50", ">50", "≤50", ">50"])
    ax_b.set_ylabel("Temperatura diaria (°C)", color="#1E3A8A")
    ax_b2.set_ylabel("Vel. viento diaria (m/s)", color="#065F46")
    ax_b.set_xlabel("Condición diaria MP2,5 (µg/m³)")
    ax_b.set_xlim(0.25, 3.85)
    ax_b.set_ylim(-6.0, 26.5)
    ax_b2.set_ylim(-0.3, 8.9)
    ax_b.grid(True, axis="y")
    ax_b.text(1.15, 23.0, "Temp.\n(p<0,001)", ha="center", fontsize=6.4, color="#1E3A8A", fontweight="bold")
    ax_b.text(2.95, 23.0, "Viento\n(p<0,001)", ha="center", fontsize=6.4, color="#065F46", fontweight="bold")
    ax_b.text(-0.20, 1.04, "(b)", transform=ax_b.transAxes, fontweight="bold", fontsize=8.5)

    # (c) Rosa de vientos climatologica (Coyhaique II vs Vialidad)
    ax_c = fig.add_subplot(gs[0, 2], projection="polar")
    ax_c.set_theta_zero_location("N")
    ax_c.set_theta_direction(-1)
    wr_c2 = wind_rose[wind_rose["station_id"] == "CoyhaiqueII"].sort_values("angle_center_deg")
    wr_vi = wind_rose[wind_rose["station_id"] == "Vialidad"].sort_values("angle_center_deg")

    theta_c2 = np.deg2rad(wr_c2["angle_center_deg"].values)
    theta_vi = np.deg2rad(wr_vi["angle_center_deg"].values)
    width = np.deg2rad(14.0)
    ax_c.bar(theta_c2, wr_c2["freq_pct"].values, width=width, color="#0F4C81", alpha=0.68, edgecolor="white", lw=0.4, label="Coyhaique II")
    ax_c.plot(np.append(theta_vi, theta_vi[0]), np.append(wr_vi["freq_pct"].values, wr_vi["freq_pct"].values[0]), color="#D97706", lw=1.35, label="Vialidad")
    ax_c.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax_c.set_xticklabels(["N", "NE", "E", "SE", "S", "SO", "O", "NO"], fontsize=6.8)
    ax_c.set_rgrids([5, 10, 15], labels=["5%", "10%", "15%"], angle=45, fontsize=6.2)
    ax_c.legend(loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False, fontsize=6.6, handlelength=1.2)
    ax_c.text(-0.18, 1.08, "(c)", transform=ax_c.transAxes, fontweight="bold", fontsize=8.5)

    fig.savefig(FIG_PAPER / "fig2_meteorology_wind.png", bbox_inches="tight")
    plt.close(fig)


def make_fig3_paper(clusters_df: pd.DataFrame, summary: dict) -> None:
    """Fig. 3 (IEEE 2-col): (a) Biplot PCA + clusters optimos, (b) Perfil de episodios y clima por cluster."""
    set_ieee_style()
    fig = plt.figure(figsize=(7.16, 2.85))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.25, 1.0], wspace=0.30)

    evr = summary["pca_clustering"]["explained_variance_ratio"]
    loadings = summary["pca_clustering"]["loadings"]
    profiles = pd.DataFrame(summary["pca_clustering"]["cluster_profiles"])
    k_sel = summary["pca_clustering"]["selected_model"]["k"]

    cluster_colors = ["#2A9D8F", "#E9C46A", "#C1121F", "#0F4C81"][:k_sel]
    spanish_names = {
        0: "C0: Cálido-Ventilado",
        1: "C1: Frío-Transición",
        2: "C2: Frío-Estancado",
    }
    short_names = [spanish_names.get(int(r["cluster_id"]), r["cluster_name"]) for _, r in profiles.iterrows()]

    # (a) Biplot PCA
    ax_a = fig.add_subplot(gs[0, 0])
    for idx, cid in enumerate(sorted(clusters_df["cluster_id"].unique())):
        sub = clusters_df[clusters_df["cluster_id"] == cid]
        ax_a.scatter(sub["PC1"], sub["PC2"], s=6, alpha=0.42, color=cluster_colors[idx], label=short_names[idx], rasterized=True, edgecolors="none")

    # Vectores de carga (loadings) escalados con offsets limpios sin solapamiento
    var_labels = {
        "log_mp25": ("log(MP2,5)", (0.25, -0.45)),
        "log_co": ("log(CO)", (0.25, 0.35)),
        "temp": ("Temp.", (-0.25, 0.25)),
        "humedad": ("Humedad", (0.15, -0.35)),
        "velviento": ("Viento", (-0.20, -0.42)),
        "presion": ("Presión", (0.20, 0.15)),
    }
    scale = 3.6
    for feat, (lbl, (dx, dy)) in var_labels.items():
        lx = loadings["PC1"][feat] * scale
        ly = loadings["PC2"][feat] * scale
        ax_a.annotate(
            "",
            xy=(lx, ly),
            xytext=(0, 0),
            arrowprops={"arrowstyle": "->", "color": "#0F172A", "lw": 1.15},
        )
        ha = "left" if lx + dx >= 0 else "right"
        ax_a.text(
            lx + dx,
            ly + dy,
            lbl,
            fontsize=6.6,
            fontweight="bold",
            color="#0F172A",
            ha=ha,
            va="center",
            bbox={"boxstyle": "round,pad=0.12", "facecolor": "white", "alpha": 0.78, "edgecolor": "none"},
        )

    ax_a.axhline(0, color="#94A3B8", lw=0.5, ls="--")
    ax_a.axvline(0, color="#94A3B8", lw=0.5, ls="--")
    ax_a.set_xlabel(f"PC1 ({100*evr[0]:.1f}% varianza explicada)")
    ax_a.set_ylabel(f"PC2 ({100*evr[1]:.1f}% varianza explicada)")
    ax_a.legend(loc="upper left", frameon=True, framealpha=0.9, edgecolor="#E2E8F0", markerscale=2.0, fontsize=6.4, borderpad=0.25)
    ax_a.grid(True)
    ax_a.text(-0.14, 1.04, "(a)", transform=ax_a.transAxes, fontweight="bold", fontsize=8.5)

    # (b) Tasa de episodios (>50) y perfil climatico por cluster
    ax_b = fig.add_subplot(gs[0, 1])
    y_pos = np.arange(len(profiles))
    bars = ax_b.barh(y_pos, profiles["episode_rate_pct"].values, color=cluster_colors, height=0.55, edgecolor="#1E293B", lw=0.5)
    for yi, (_, row) in enumerate(profiles.iterrows()):
        info = f" {row['episode_rate_pct']:.1f}% | Med: {row['mp25_median']:.0f} µg/m³\n T={row['temp_mean']:.1f}°C, V={row['velviento_mean']:.1f} m/s"
        x_txt = row["episode_rate_pct"] + 1.5
        if row["episode_rate_pct"] > 58:
            ax_b.text(row["episode_rate_pct"] - 2.0, yi, f"{row['episode_rate_pct']:.1f}%\nMed: {row['mp25_median']:.0f} µg/m³", va="center", ha="right", fontsize=6.4, color="white", fontweight="bold")
            ax_b.text(row["episode_rate_pct"] + 1.5, yi, f"T={row['temp_mean']:.1f}°C\nV={row['velviento_mean']:.1f} m/s", va="center", ha="left", fontsize=6.3, color="#1E293B")
        else:
            ax_b.text(x_txt, yi, info, va="center", ha="left", fontsize=6.3, color="#1E293B")

    ax_b.set_yticks(y_pos)
    ax_b.set_yticklabels([f"C{r['cluster_id']}\n(n={r['n_days']})" for _, r in profiles.iterrows()])
    ax_b.set_xlabel("Tasa de días sobre norma > 50 µg/m³ (%)")
    ax_b.set_xlim(0, 118)
    ax_b.grid(True, axis="x")
    ax_b.text(-0.18, 1.04, "(b)", transform=ax_b.transAxes, fontweight="bold", fontsize=8.5)

    fig.savefig(FIG_PAPER / "fig3_pca_clusters.png", bbox_inches="tight")
    plt.close(fig)


def make_slide_figures(
    daily: pd.DataFrame,
    yearly: pd.DataFrame,
    stl: pd.DataFrame,
    heatmap: pd.DataFrame,
    ccf_df: pd.DataFrame,
    wind_rose: pd.DataFrame,
    clusters_df: pd.DataFrame,
    clf_df: pd.DataFrame,
    summary: dict,
) -> None:
    """Genera graficos limpios y grandes para la presentacion de 8 minutos."""
    set_slide_style()

    # Slide 1: Auditoria de completitud y cobertura (manejo de faltantes y 2026)
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    piv = yearly[yearly["year"] >= 2014].pivot(index="station_id", columns="year", values="completeness_year_pct").reindex(["CoyhaiqueII", "Coyhaique", "Vialidad", "Cochrane"])
    data = piv.values
    im = ax.imshow(np.nan_to_num(data, nan=-10), cmap="YlGnBu", vmin=0, vmax=100, aspect="auto")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            if np.isnan(val):
                ax.text(j, i, "—", ha="center", va="center", color="#94A3B8", fontsize=10)
            else:
                txt_col = "white" if val >= 65 else "#0F172A"
                ax.text(j, i, f"{val:.0f}%", ha="center", va="center", color=txt_col, fontsize=9.5, fontweight="bold")
    ax.set_xticks(range(len(piv.columns)))
    ax.set_xticklabels([f"{y}*" if y == 2026 else str(y) for y in piv.columns])
    ax.set_yticks(range(4))
    ax.set_yticklabels(["Coyhaique II", "Coyhaique", "Vialidad (Aysén)", "Cochrane"])
    ax.set_xlabel("Año (*2026: corte 23 oct — 100% cobertura invernal Abr–Sep)")
    cbar = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.03)
    cbar.set_label("Completitud anual de MP2,5 (%)")
    fig.savefig(FIG_SLIDE / "slide_completeness_audit.png", bbox_inches="tight")
    plt.close(fig)

    # Slide 2: Tendencia STL regional + Dias >50 en invierno
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.2))
    palette = {"CoyhaiqueII": "#0F4C81", "Vialidad": "#2A9D8F", "Cochrane": "#C1121F"}
    names = {"CoyhaiqueII": "Coyhaique II", "Vialidad": "Vialidad (Pto. Aysén)", "Cochrane": "Cochrane"}
    for sid in ["CoyhaiqueII", "Vialidad", "Cochrane"]:
        sub = stl[stl["station_id"] == sid].sort_values("date")
        ax1.plot(sub["date"], sub["trend"], color=palette[sid], lw=2.6, label=names[sid])
    ax1.axhline(50, color="#64748B", ls="--", lw=1.2)
    ax1.axvspan(pd.Timestamp("2026-01-01"), pd.Timestamp("2026-10-23"), color="#FEF3C7", alpha=0.65)
    ax1.set_ylabel("Tendencia STL MP2,5 (µg/m³)")
    ax1.set_xlabel("Año (sombreado: 2026 YTD)")
    ax1.set_ylim(0, 72)
    ax1.grid(True, axis="y")
    ax1.legend(frameon=True, facecolor="white")

    # Barras apiladas GEC Coyhaique II
    c2 = daily[(daily["station_id"] == "CoyhaiqueII") & (daily["year"] >= 2014) & (daily["mp25_valid_day"]) & (daily["over_norm_50"] == 1)]
    years = list(range(2014, 2027))
    x = np.arange(len(years))
    bottoms = np.zeros(len(years))
    for cat_key, color, cat_lbl in GEC_COLS:
        vals = [int(((c2["year"] == y) & (c2["gec_category"] == cat_key)).sum()) for y in years]
        bars = ax2.bar(x, vals, bottom=bottoms, color=color, width=0.72, label=cat_lbl)
        bars[-1].set_hatch("///")
        bars[-1].set_edgecolor("#1E293B")
        bottoms += np.array(vals)
    for xi, tot in zip(x, bottoms):
        ax2.text(xi, tot + 3, f"{int(tot)}", ha="center", fontsize=8.5, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(y)[2:] + ("*" if y == 2026 else "") for y in years])
    ax2.set_ylabel("Días > 50 µg/m³ (Coyhaique II)")
    ax2.set_xlabel("Año (*2026 YTD ene–23 oct)")
    ax2.set_ylim(0, 178)
    ax2.grid(True, axis="y")
    ax2.legend(ncol=2, fontsize=8.5, frameon=True, facecolor="white")
    fig.tight_layout()
    fig.savefig(FIG_SLIDE / "slide_trends_and_gec.png", bbox_inches="tight")
    plt.close(fig)

    # Slide 3: Heatmap + Ciclo horario invierno vs verano
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.3), gridspec_kw={"width_ratios": [1.35, 1]})
    hm = heatmap[heatmap["station_id"] == "CoyhaiqueII"]
    piv = hm.pivot(index="hour", columns="month", values="mp25_mean").reindex(index=range(24), columns=range(1, 13))
    im = ax1.imshow(piv.values.T, aspect="auto", cmap="YlOrRd", vmin=0, vmax=175)
    ax1.set_xticks(range(0, 24, 3))
    ax1.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 3)])
    ax1.set_yticks(range(12))
    ax1.set_yticklabels(MESES)
    ax1.set_xlabel("Hora del día")
    ax1.set_ylabel("Mes")
    cbar = fig.colorbar(im, ax=ax1, pad=0.02, fraction=0.04)
    cbar.set_label("MP2,5 (µg/m³)")

    hw = hm[hm["month"].between(4, 9)].groupby("hour")["mp25_mean"].mean()
    hs = hm[~hm["month"].between(4, 9)].groupby("hour")["mp25_mean"].mean()
    ax2.plot(hw.index, hw.values, color="#C1121F", lw=2.8, marker="o", ms=4, label="Invierno (Abr–Sep)")
    ax2.plot(hs.index, hs.values, color="#2A9D8F", lw=2.5, marker="s", ms=4, label="Resto del año")
    ax2.axhline(50, color="#475569", ls="--", lw=1.1, label="Norma 50 µg/m³")
    ax2.set_xlabel("Hora del día")
    ax2.set_ylabel("MP2,5 promedio horario (µg/m³)")
    ax2.set_xticks(range(0, 24, 4))
    ax2.grid(True)
    ax2.legend(frameon=True, facecolor="white")
    fig.tight_layout()
    fig.savefig(FIG_SLIDE / "slide_diurnal_heatmap.png", bbox_inches="tight")
    plt.close(fig)

    # Slide 4: CCF + Rosa de vientos climatologica (proporcion mas ancha y eje Y completo)
    fig = plt.figure(figsize=(11.5, 3.85))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.38, 1.0], wspace=0.24)
    ax1 = fig.add_subplot(gs[0, 0])
    for v, lbl, col, mk_sym in [
        ("temp", "Temperatura", "#C1121F", "o"),
        ("velviento", "Velocidad viento", "#0F4C81", "s"),
        ("humedad", "Humedad relativa", "#2A9D8F", "^"),
        ("presion", "Presión atmosférica", "#D97706", "D"),
    ]:
        s = ccf_df[(ccf_df["variable"] == v) & (ccf_df["lag_days"].between(-5, 5))].sort_values("lag_days")
        ax1.plot(s["lag_days"], s["spearman_rho"], color=col, marker=mk_sym, lw=2.2, ms=5.2, label=lbl)
    ax1.axhline(0, color="#64748B", lw=1.0)
    ax1.axvline(0, color="#94A3B8", ls=":", lw=1.0)
    ax1.set_xlabel("Rezago k (días; k>0: clima antecede a MP2,5)")
    ax1.set_ylabel("Correlación Spearman (ρ)")
    ax1.set_ylim(-0.88, 0.78)
    ax1.grid(True)
    ax1.legend(loc="center right", bbox_to_anchor=(0.99, 0.56), frameon=True, facecolor="white", fontsize=9.0)

    ax2 = fig.add_subplot(gs[0, 1], projection="polar")
    ax2.set_theta_zero_location("N")
    ax2.set_theta_direction(-1)
    wr_c2 = wind_rose[wind_rose["station_id"] == "CoyhaiqueII"].sort_values("angle_center_deg")
    wr_vi = wind_rose[wind_rose["station_id"] == "Vialidad"].sort_values("angle_center_deg")
    th = np.deg2rad(wr_c2["angle_center_deg"].values)
    ax2.bar(th, wr_c2["freq_pct"].values, width=np.deg2rad(14.0), color="#0F4C81", alpha=0.72, edgecolor="white", label="Coyhaique II")
    ax2.plot(np.append(th, th[0]), np.append(wr_vi["freq_pct"].values, wr_vi["freq_pct"].values[0]), color="#D97706", lw=2.2, label="Vialidad")
    ax2.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
    ax2.set_xticklabels(["N", "NE", "E", "SE", "S", "SO", "O", "NO"])
    ax2.set_rgrids([5, 10, 15], labels=["5%", "10%", "15%"], angle=45)
    ax2.legend(loc="upper right", bbox_to_anchor=(1.32, 1.08), ncol=1, frameon=True, facecolor="white", fontsize=9.0)
    fig.savefig(FIG_SLIDE / "slide_met_ccf_wind.png", bbox_inches="tight")
    plt.close(fig)

    # Slide 5: PCA & Clusters + Validacion explicativa
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.05), gridspec_kw={"width_ratios": [1.15, 1.0]})
    evr = summary["pca_clustering"]["explained_variance_ratio"]
    profiles = pd.DataFrame(summary["pca_clustering"]["cluster_profiles"])
    k_sel = summary["pca_clustering"]["selected_model"]["k"]
    ccols = ["#2A9D8F", "#E9C46A", "#C1121F", "#0F4C81"][:k_sel]
    es_labels = {0: "C0: Cálido-Ventilado (Limpio)", 1: "C1: Frío-Transición (Moderado)", 2: "C2: Frío-Estancado (Crítico)"}
    for idx, cid in enumerate(sorted(clusters_df["cluster_id"].unique())):
        sub = clusters_df[clusters_df["cluster_id"] == cid]
        lbl = es_labels.get(int(cid), profiles.loc[profiles["cluster_id"] == cid, "cluster_name"].values[0])
        ax1.scatter(sub["PC1"], sub["PC2"], s=14, alpha=0.45, color=ccols[idx], label=lbl, edgecolors="none")
    ax1.set_xlabel(f"PC1 ({100*evr[0]:.1f}% varianza)")
    ax1.set_ylabel(f"PC2 ({100*evr[1]:.1f}% varianza)")
    ax1.grid(True)
    ax1.legend(loc="upper left", fontsize=8.5, markerscale=1.8, frameon=True, facecolor="white")

    # Comparacion F1 y PR-AUC de modelos explicativos (test 2024-2026)
    plot_clf = clf_df[clf_df["feature_set"].isin(["Solo lag-1 (Persistencia)", "Solo Meteorologia", "Meteorologia + Lag-1"])].copy()
    plot_clf["short"] = plot_clf.apply(
        lambda r: "Persistencia\n(lag-1)" if "Persistencia" in r["model"] else f"{r['model'].replace('Regresion Logistica', 'LogReg').replace('Gradient Boosting', 'GradBoost')}\n({'Met' if r['feature_set']=='Solo Meteorologia' else 'Met+Lag1'})",
        axis=1,
    )
    y_i = np.arange(len(plot_clf))
    ax2.barh(y_i - 0.18, plot_clf["test_f1"].values, height=0.34, color="#0F4C81", label="F1-score (test 2024–26)")
    ax2.barh(y_i + 0.18, plot_clf["test_pr_auc"].values, height=0.34, color="#E76F51", label="PR-AUC (test 2024–26)")
    ax2.set_yticks(y_i)
    ax2.set_yticklabels(plot_clf["short"].values, fontsize=8.8)
    ax2.set_xlim(0, 1.05)
    ax2.set_xlabel("Desempeño fuera de muestra (2024–2026)")
    ax2.grid(True, axis="x")
    ax2.legend(loc="lower right", fontsize=8.5, frameon=True, facecolor="white")
    fig.tight_layout()
    fig.savefig(FIG_SLIDE / "slide_pca_and_models.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    daily = pd.read_csv(PROC_DIR / "all_stations_daily.csv", parse_dates=["date"])
    yearly = pd.read_csv(PROC_DIR / "yearly_summary_completeness.csv")
    stl = pd.read_csv(PROC_DIR / "stl_decomposition.csv", parse_dates=["date"])
    heatmap = pd.read_csv(PROC_DIR / "heatmap_hour_month.csv")
    ccf_df = pd.read_csv(PROC_DIR / "ccf_meteorology_mp25.csv")
    wind_rose = pd.read_csv(PROC_DIR / "rosa_vientos_frecuencias.csv")
    clusters_df = pd.read_csv(PROC_DIR / "pca_clusters_daily.csv", parse_dates=["date"])
    clf_df = pd.read_csv(PROC_DIR / "explanatory_models_evaluation.csv")
    with open(PROC_DIR / "analysis_results_summary.json", "r", encoding="utf-8") as fh:
        summary = json.load(fh)

    make_fig1_paper(daily, stl, heatmap)
    make_fig2_paper(daily, ccf_df, wind_rose, summary)
    make_fig3_paper(clusters_df, summary)
    make_slide_figures(daily, yearly, stl, heatmap, ccf_df, wind_rose, clusters_df, clf_df, summary)

    for p in [
        FIG_PAPER / "fig1_temporal_patterns.png",
        FIG_PAPER / "fig2_meteorology_wind.png",
        FIG_PAPER / "fig3_pca_clusters.png",
    ]:
        assert p.exists() and p.stat().st_size > 20000, f"Figura faltante o vacia: {p}"
    print("OK: 3 figuras IEEE (300 dpi) y 5 graficos de presentacion generados.")


if __name__ == "__main__":
    main()
