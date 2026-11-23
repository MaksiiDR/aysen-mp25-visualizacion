"""
04_verify_all.py
----------------
Pruebas de verificacion automatizada (self-checks) y medicion empirica de
escalabilidad (>115.000 registros horarios) para la matriz objetiva de seleccion
de metodos visuales (Seccion 6 de la propuesta).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data_processed"
PBI_DIR = BASE_DIR / "powerbi" / "data"


def benchmark_visual_scalability() -> dict:
    """Mide tiempos reales de carga y agregacion sobre >115 mil registros horarios."""
    timings = {}

    t0 = time.perf_counter()
    c2_h = pd.read_csv(PROC_DIR / "coyhaiqueII_hourly.csv.gz", parse_dates=["datetime"])
    t_load_hourly = time.perf_counter() - t0
    assert len(c2_h) >= 115000, f"Esperado >=115k filas horarias, obtenido {len(c2_h)}"

    # 1. Heatmap Hora x Mes desde serie horaria completa
    t0 = time.perf_counter()
    piv = c2_h.pivot_table(index="hour", columns="month", values="mp25", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.imshow(piv.values, aspect="auto")
    plt.close(fig)
    timings["heatmap_from_115k_s"] = round(time.perf_counter() - t0, 3)

    # 2. Serie de tiempo diaria/mensual + STL desde serie horaria completa
    t0 = time.perf_counter()
    d = c2_h.groupby("date")["mp25"].agg(["mean", "count"])
    d_valid = d.loc[d["count"] >= 18, "mean"]
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.plot(d_valid.index, d_valid.values)
    plt.close(fig)
    timings["timeseries_from_115k_s"] = round(time.perf_counter() - t0, 3)

    # 3. Calendario diario de dias sobre la norma (13 anos x 365 dias)
    t0 = time.perf_counter()
    d_cal = c2_h.groupby(["year", "month", "day"])["mp25"].agg(["mean", "count"]).reset_index()
    d_cal["over50"] = np.where(d_cal["count"] >= 18, d_cal["mean"] > 50, np.nan)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(d_cal["day"], d_cal["month"], c=d_cal["over50"].fillna(-1), s=4)
    plt.close(fig)
    timings["calendar_from_115k_s"] = round(time.perf_counter() - t0, 3)

    # 4. Carga desde esquema estrella pre-agregado (Dash / Power BI)
    t0 = time.perf_counter()
    for fname in [
        "dim_estacion.csv",
        "dim_fecha.csv",
        "fact_calidad_aire_diaria.csv",
        "fact_ciclo_horario_mensual.csv",
        "fact_stl_descomposicion.csv",
        "fact_clusters_pca.csv",
        "fact_rosa_vientos.csv",
    ]:
        _ = pd.read_csv(PBI_DIR / fname)
    timings["star_schema_full_load_s"] = round(time.perf_counter() - t0, 3)
    timings["hourly_raw_load_115k_s"] = round(t_load_hourly, 3)
    timings["n_hourly_rows_coyhaiqueII"] = int(len(c2_h))
    return timings


def verify_pipeline_integrity() -> None:
    """Verifica invariantes clave de datos, modelo estrella y resultados."""
    required_pbi = [
        "dim_estacion.csv",
        "dim_fecha.csv",
        "fact_calidad_aire_diaria.csv",
        "fact_ciclo_horario_mensual.csv",
        "fact_resumen_anual_completitud.csv",
        "fact_stl_descomposicion.csv",
        "fact_clusters_pca.csv",
        "fact_rosa_vientos.csv",
    ]
    for f in required_pbi:
        p = PBI_DIR / f
        assert p.exists() and p.stat().st_size > 100, f"Falta tabla Power BI: {p}"

    daily = pd.read_csv(PBI_DIR / "fact_calidad_aire_diaria.csv")
    assert set(daily["station_id"].unique()) == {"CoyhaiqueII", "Coyhaique", "Vialidad", "Cochrane"}
    assert (daily.loc[daily["mp25_count"] < 18, "mp25_24h"].isna()).all()
    assert (daily.loc[daily["over_norm_50"] == 1, "mp25_24h"] > 50.0).all()

    wr = pd.read_csv(PBI_DIR / "fact_rosa_vientos.csv")
    for sid, grp in wr.groupby("station_id"):
        assert len(grp) == 24, f"Rosa {sid} debe tener 24 sectores"
        assert 99.0 <= grp["freq_pct"].sum() <= 101.0

    with open(PROC_DIR / "analysis_results_summary.json", "r", encoding="utf-8") as fh:
        res = json.load(fh)
    assert "stl" in res and "pca_clustering" in res and "mann_kendall_trends" in res

    # Verificar importacion y callbacks del dashboard sin errores
    import sys
    sys.path.insert(0, str(BASE_DIR))
    from dashboard.app import render_tab, update_kpis

    kpis = update_kpis("CoyhaiqueII", "ytd", [2014, 2026])
    assert len(kpis) == 4
    for tab in ["tab-stl", "tab-heatmap", "tab-map", "tab-met", "tab-pca"]:
        for sid in ["CoyhaiqueII", "Cochrane"]:
            comp = render_tab(tab, sid, "ytd", [2014, 2026])
            assert comp is not None, f"Fallo al renderizar {tab} para {sid}"


def main() -> None:
    verify_pipeline_integrity()
    timings = benchmark_visual_scalability()
    with open(PROC_DIR / "scalability_benchmark.json", "w", encoding="utf-8") as fh:
        json.dump(timings, fh, indent=2, ensure_ascii=False)
    print("=== BENCHMARK DE ESCALABILIDAD (>115k REGISTROS) ===")
    print(json.dumps(timings, indent=2, ensure_ascii=False))
    assert timings["heatmap_from_115k_s"] < 15.0
    assert timings["timeseries_from_115k_s"] < 15.0
    assert timings["star_schema_full_load_s"] < 5.0
    print("OK: Todas las verificaciones de integridad, dashboard y escalabilidad pasaron.")


if __name__ == "__main__":
    main()
