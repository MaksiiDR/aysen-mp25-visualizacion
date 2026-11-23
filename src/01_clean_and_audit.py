"""
01_clean_and_audit.py
---------------------
Limpieza, auditoria de calidad de datos, manejo explicito de datos faltantes y
ano incompleto (2026), verificacion de rosa de vientos y exportacion de modelo
estrella para Power BI a partir de los 25 archivos CSV horarios de SINCA.

Norma de referencia:
- DS N° 12/2011 (Ministerio del Medio Ambiente): limite diario de MP2,5 = 50 ug/m3
  como promedio de 24 h, exigiendo >= 18 horas validas (75% del dia).
- Categorias de Gestion de Episodios Criticos (GEC, DS 12 / PDA Coyhaique):
  Bueno: <= 50 | Alerta: > 50 a <= 80 | Preemergencia: > 80 a <= 110 |
  Emergencia: > 110 (nota: DS 12 define Regular 50-79, Alerta 80-109,
  Preemergencia 110-169, Emergencia >= 170; usamos la escala oficial DS 12).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR.parent / "datos"
OUT_PROC = BASE_DIR / "data_processed"
OUT_PBI = BASE_DIR / "powerbi" / "data"

OUT_PROC.mkdir(parents=True, exist_ok=True)
OUT_PBI.mkdir(parents=True, exist_ok=True)

# Coordenadas oficiales aproximadas de las estaciones SINCA en la Region de Aysen
STATIONS_META = [
    {
        "station_id": "CoyhaiqueII",
        "station_name": "Coyhaique II",
        "city": "Coyhaique",
        "lat": -45.5796,
        "lon": -72.0611,
        "has_wind_rose": True,
        "has_met_hourly": True,
        "role": "Estacion principal (contaminantes + meteorologia completa)",
    },
    {
        "station_id": "Coyhaique",
        "station_name": "Coyhaique",
        "city": "Coyhaique",
        "lat": -45.5712,
        "lon": -72.0685,
        "has_wind_rose": True,
        "has_met_hourly": True,
        "role": "Estacion historica urbana (MP2,5, MP10 y meteorologia)",
    },
    {
        "station_id": "Vialidad",
        "station_name": "Vialidad",
        "city": "Puerto Aysen",
        "lat": -45.4054,
        "lon": -72.6977,
        "has_wind_rose": True,
        "has_met_hourly": True,
        "role": "Estacion costera-valle (MP2,5 y meteorologia parcial)",
    },
    {
        "station_id": "Cochrane",
        "station_name": "Cochrane",
        "city": "Cochrane",
        "lat": -47.2539,
        "lon": -72.5731,
        "has_wind_rose": False,
        "has_met_hourly": False,
        "role": "Estacion austral (solo MP2,5)",
    },
]

# Archivos horarios a ingerir: (station_id, variable, filename, is_pollutant)
HOURLY_FILES = [
    ("CoyhaiqueII", "mp25", "CoyhaiqueII_MP25_horario.csv", True),
    ("CoyhaiqueII", "mp10", "CoyhaiqueII_MP10_horario.csv", True),
    ("CoyhaiqueII", "co", "CoyhaiqueII_CO_horario.csv", True),
    ("CoyhaiqueII", "so2", "CoyhaiqueII_SO2_horario.csv", True),
    ("CoyhaiqueII", "o3", "CoyhaiqueII_O3_horario.csv", True),
    ("CoyhaiqueII", "no2", "CoyhaiqueII_NO2_horario.csv", True),
    ("CoyhaiqueII", "no", "CoyhaiqueII_NO_horario.csv", True),
    ("CoyhaiqueII", "nox", "CoyhaiqueII_NOx_horario.csv", True),
    ("CoyhaiqueII", "temp", "CoyhaiqueII_temperatura_horario.csv", False),
    ("CoyhaiqueII", "humedad", "CoyhaiqueII_humedad_horario.csv", False),
    ("CoyhaiqueII", "presion", "CoyhaiqueII_presion_horario.csv", False),
    ("CoyhaiqueII", "velviento", "CoyhaiqueII_velviento_horario.csv", False),
    ("Coyhaique", "mp25", "Coyhaique_MP25_horario.csv", True),
    ("Coyhaique", "mp10", "Coyhaique_MP10_horario.csv", True),
    ("Coyhaique", "temp", "Coyhaique_temperatura_horario.csv", False),
    ("Coyhaique", "humedad", "Coyhaique_humedad_horario.csv", False),
    ("Coyhaique", "velviento", "Coyhaique_velviento_horario.csv", False),
    ("Vialidad", "mp25", "Vialidad_MP25_horario.csv", True),
    ("Vialidad", "temp", "Vialidad_temperatura_horario.csv", False),
    ("Vialidad", "humedad", "Vialidad_humedad_horario.csv", False),
    ("Vialidad", "velviento", "Vialidad_velviento_horario.csv", False),
    ("Cochrane", "mp25", "Cochrane_MP25_horario.csv", True),
]

WIND_ROSE_FILES = [
    ("CoyhaiqueII", "CoyhaiqueII_rosa_vientos_frecuencias.csv"),
    ("Coyhaique", "Coyhaique_rosa_vientos_frecuencias.csv"),
    ("Vialidad", "Vialidad_rosa_vientos_frecuencias.csv"),
]

# Limites fisicos razonables para descartar errores instrumentales extremos
PHYSICAL_BOUNDS = {
    "mp25": (0.0, 2000.0),
    "mp10": (0.0, 3000.0),
    "co": (0.0, 100.0),
    "so2": (0.0, 1000.0),
    "o3": (0.0, 400.0),
    "no2": (0.0, 500.0),
    "no": (0.0, 1000.0),
    "nox": (0.0, 1500.0),
    "temp": (-35.0, 45.0),
    "humedad": (0.0, 100.0),
    "presion": (850.0, 1080.0),
    "velviento": (0.0, 60.0),
}


def parse_sinca_hourly(path: Path, is_pollutant: bool, var_name: str) -> tuple[pd.DataFrame, dict]:
    """Lee un CSV horario de SINCA respetando separador ';', decimal ',' y estado de validacion."""
    raw = pd.read_csv(
        path,
        sep=";",
        dtype=str,
        encoding="utf-8",
        encoding_errors="replace",
        engine="python",
    )
    date_col = raw.columns[0]
    hour_col = raw.columns[1]

    d_str = raw[date_col].astype(str).str.strip().str.zfill(6)
    h_str = raw[hour_col].astype(str).str.strip().str.zfill(4)
    dt = pd.to_datetime(d_str + h_str, format="%y%m%d%H%M", errors="coerce")

    def to_num(series: pd.Series) -> pd.Series:
        return pd.to_numeric(series.astype(str).str.strip().str.replace(",", ".", regex=False), errors="coerce")

    if is_pollutant:
        v_val = to_num(raw.iloc[:, 2])
        v_pre = to_num(raw.iloc[:, 3])
        v_nov = to_num(raw.iloc[:, 4])
        # Prioridad oficial SINCA: validado > preliminar > no validado
        val = v_val.combine_first(v_pre).combine_first(v_nov)
        status = np.where(
            v_val.notna(),
            "validado",
            np.where(v_pre.notna(), "preliminar", np.where(v_nov.notna(), "no_validado", "faltante")),
        )
    else:
        val = to_num(raw.iloc[:, 2])
        status = np.where(val.notna(), "observado", "faltante")

    lo, hi = PHYSICAL_BOUNDS[var_name]
    out_of_bounds = val.notna() & ((val < lo) | (val > hi))
    n_oob = int(out_of_bounds.sum())
    if n_oob > 0:
        val = val.mask(out_of_bounds)
        status = np.where(out_of_bounds, "descartado_fisico", status)

    df = pd.DataFrame({"datetime": dt, "value": val, "status": status}).dropna(subset=["datetime"])
    df = df.drop_duplicates(subset=["datetime"], keep="first").sort_values("datetime").reset_index(drop=True)

    audit = {
        "file": path.name,
        "variable": var_name,
        "n_rows": int(len(df)),
        "start_date": df["datetime"].min().strftime("%Y-%m-%d"),
        "end_date": df["datetime"].max().strftime("%Y-%m-%d"),
        "n_valid_any": int(df["value"].notna().sum()),
        "completeness_pct": round(100.0 * df["value"].notna().mean(), 2),
        "n_validado": int((df["status"] == "validado").sum()),
        "n_preliminar": int((df["status"] == "preliminar").sum()),
        "n_no_validado": int((df["status"] == "no_validado").sum()),
        "n_out_of_bounds": n_oob,
    }
    return df, audit


def parse_wind_rose(station_id: str, path: Path) -> pd.DataFrame:
    """Parsea la tabla estatica de frecuencias por sector de 15 grados de SINCA."""
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        _ = fh.readline()
        for line in fh:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^(\d+,\d)-(\d+,\d)(\d+,\d)%$", line)
            if not m:
                raise ValueError(f"Formato inesperado en {path.name}: {line!r}")
            ang_start = float(m.group(1).replace(",", "."))
            ang_end = float(m.group(2).replace(",", "."))
            freq_pct = float(m.group(3).replace(",", "."))
            center = 0.0 if ang_start > ang_end else (ang_start + ang_end) / 2.0
            rows.append(
                {
                    "station_id": station_id,
                    "sector_label": f"{ang_start:.1f}-{ang_end:.1f}",
                    "angle_start_deg": ang_start,
                    "angle_end_deg": ang_end,
                    "angle_center_deg": center,
                    "freq_pct": freq_pct,
                }
            )
    df = pd.DataFrame(rows)
    total = df["freq_pct"].sum()
    assert 99.0 <= total <= 101.0, f"Suma rosa de vientos fuera de rango ({total:.2f}%) en {station_id}"
    return df


def classify_gec_ds12(mp25_24h: float) -> str:
    """Clasifica concentracion diaria de MP2,5 segun rangos oficiales DS N° 12/2011 (Chile)."""
    if pd.isna(mp25_24h):
        return "Sin dato (<18h)"
    if mp25_24h <= 50.0:
        return "Bueno (<=50)"
    if mp25_24h < 80.0:
        return "Regular (50-79)"
    if mp25_24h < 110.0:
        return "Alerta (80-109)"
    if mp25_24h < 170.0:
        return "Preemergencia (110-169)"
    return "Emergencia (>=170)"


def main() -> None:
    print("1. Ingiriendo y auditando los 22 archivos horarios y 3 rosas de viento...")
    audit_records = []
    hourly_by_station: dict[str, pd.DataFrame] = {}

    for station_id, var_name, fname, is_pollutant in HOURLY_FILES:
        path = RAW_DIR / fname
        assert path.exists(), f"Archivo no encontrado: {path}"
        df_var, audit = parse_sinca_hourly(path, is_pollutant, var_name)
        audit["station_id"] = station_id
        audit_records.append(audit)

        rename_cols = {"value": var_name}
        if var_name == "mp25":
            rename_cols["status"] = "mp25_status"
            sub = df_var[["datetime", "value", "status"]].rename(columns=rename_cols)
        else:
            sub = df_var[["datetime", "value"]].rename(columns=rename_cols)

        if station_id not in hourly_by_station:
            hourly_by_station[station_id] = sub
        else:
            hourly_by_station[station_id] = hourly_by_station[station_id].merge(
                sub, on="datetime", how="outer"
            )

    audit_df = pd.DataFrame(audit_records)
    audit_df.to_csv(OUT_PROC / "audit_series_sin_ca.csv", index=False)

    # Parsear rosas de viento (verificacion feedback profesor #3)
    wind_roses = [parse_wind_rose(sid, RAW_DIR / fname) for sid, fname in WIND_ROSE_FILES]
    wind_rose_df = pd.concat(wind_roses, ignore_index=True)
    wind_rose_df.to_csv(OUT_PROC / "rosa_vientos_frecuencias.csv", index=False)
    wind_rose_df.to_csv(OUT_PBI / "fact_rosa_vientos.csv", index=False)

    # Consolidar tablas horarias y diarias por estacion
    all_hourly_mp25_parts = []
    all_daily_parts = []
    yearly_completeness_parts = []

    # Ventana YTD comparable para manejar el ano incompleto 2026 (hasta 23 de octubre)
    # Permite comparar 2026 en igualdad de condiciones contra el mismo periodo ene 1 - oct 23 de anos previos
    YTD_CUTOFF_MONTH = 10
    YTD_CUTOFF_DAY = 23

    for station_id, df in hourly_by_station.items():
        df = df.sort_values("datetime").reset_index(drop=True)
        df["station_id"] = station_id
        df["date"] = df["datetime"].dt.normalize()
        df["year"] = df["datetime"].dt.year
        df["month"] = df["datetime"].dt.month
        df["day"] = df["datetime"].dt.day
        df["hour"] = df["datetime"].dt.hour
        df["is_winter_season"] = df["month"].between(4, 9)
        df["is_ytd_window"] = (df["month"] < YTD_CUTOFF_MONTH) | (
            (df["month"] == YTD_CUTOFF_MONTH) & (df["day"] <= YTD_CUTOFF_DAY)
        )

        # Guardar serie horaria completa de Coyhaique II (para dashboard y analisis horario)
        if station_id == "CoyhaiqueII":
            df.to_csv(OUT_PROC / "coyhaiqueII_hourly.csv.gz", index=False, compression="gzip")

        # Guardar subconjunto horario compacto de MP2,5 y meteo basica de todas las estaciones
        keep_cols = [c for c in ["datetime", "date", "year", "month", "hour", "station_id", "mp25", "mp25_status", "temp", "humedad", "velviento", "presion"] if c in df.columns]
        all_hourly_mp25_parts.append(df[keep_cols])

        # Agregacion diaria segun regla oficial DS 12 (>= 18 horas validas = 75%)
        agg_dict = {"mp25": ["mean", "max", "count"]}
        for col in ["mp10", "co", "so2", "o3", "temp", "humedad", "presion", "velviento"]:
            if col in df.columns:
                agg_dict[col] = ["mean", "min", "max", "count"] if col in ["temp", "velviento"] else ["mean", "count"]

        daily = df.groupby("date").agg(agg_dict)
        daily.columns = [f"{a}_{b}" for a, b in daily.columns]
        daily = daily.reset_index()

        # Aplicar umbral >= 18 h validas para promedio diario valido de MP2,5 y resto de variables
        daily["mp25_valid_day"] = daily["mp25_count"] >= 18
        daily["mp25_24h"] = np.where(daily["mp25_valid_day"], daily["mp25_mean"], np.nan)
        daily["over_norm_50"] = np.where(daily["mp25_valid_day"], (daily["mp25_24h"] > 50.0).astype(float), np.nan)
        daily["gec_category"] = daily["mp25_24h"].apply(classify_gec_ds12)

        for col in ["mp10", "co", "so2", "o3", "temp", "humedad", "presion", "velviento"]:
            cnt_col = f"{col}_count"
            mean_col = f"{col}_mean"
            if mean_col in daily.columns:
                daily[col] = np.where(daily[cnt_col] >= 18, daily[mean_col], np.nan)
        if "temp_min" in daily.columns:
            daily["temp_min_24h"] = np.where(daily["temp_count"] >= 18, daily["temp_min"], np.nan)
        if "velviento_min" in daily.columns:
            daily["velviento_max_24h"] = np.where(daily["velviento_count"] >= 18, daily["velviento_max"], np.nan)

        # Etiqueta de calidad dominante diaria para MP2,5 (validado vs preliminar/no_validado)
        day_status = (
            df[df["mp25"].notna()]
            .groupby("date")["mp25_status"]
            .agg(lambda s: "preliminar_o_noval" if (s != "validado").any() else "validado")
            .rename("mp25_day_quality")
        )
        daily = daily.merge(day_status, on="date", how="left")
        daily["mp25_day_quality"] = daily["mp25_day_quality"].fillna("sin_dato")

        daily["station_id"] = station_id
        daily["year"] = daily["date"].dt.year
        daily["month"] = daily["date"].dt.month
        daily["day"] = daily["date"].dt.day
        daily["is_winter_season"] = daily["month"].between(4, 9)
        daily["is_ytd_window"] = (daily["month"] < YTD_CUTOFF_MONTH) | (
            (daily["month"] == YTD_CUTOFF_MONTH) & (daily["day"] <= YTD_CUTOFF_DAY)
        )

        # Seleccionar columnas limpias
        clean_cols = [
            "date", "station_id", "year", "month", "day",
            "is_winter_season", "is_ytd_window",
            "mp25_count", "mp25_valid_day", "mp25_24h", "mp25_max",
            "over_norm_50", "gec_category", "mp25_day_quality",
        ]
        for extra in ["mp10", "co", "so2", "o3", "temp", "temp_min_24h", "humedad", "presion", "velviento", "velviento_max_24h"]:
            if extra in daily.columns:
                clean_cols.append(extra)
        daily_clean = daily[clean_cols].copy()
        all_daily_parts.append(daily_clean)

        # Auditoria anual de completitud y ano completo vs parcial (respuesta directa a feedback #2)
        for yr, grp in daily_clean.groupby("year"):
            expected_days = 366 if pd.Timestamp(year=yr, month=1, day=1).is_leap_year else 365
            valid_days = int(grp["mp25_valid_day"].sum())
            winter_grp = grp[grp["is_winter_season"]]
            winter_valid = int(winter_grp["mp25_valid_day"].sum())
            ytd_grp = grp[grp["is_ytd_window"]]
            ytd_valid = int(ytd_grp["mp25_valid_day"].sum())
            expected_ytd = 297 if pd.Timestamp(year=yr, month=1, day=1).is_leap_year else 296

            is_complete_calendar = (valid_days / expected_days) >= 0.75 and yr < 2026
            is_complete_winter = (winter_valid / 183.0) >= 0.75
            is_complete_ytd = (ytd_valid / expected_ytd) >= 0.75

            yearly_completeness_parts.append(
                {
                    "station_id": station_id,
                    "year": int(yr),
                    "expected_days": expected_days,
                    "valid_days_mp25": valid_days,
                    "completeness_year_pct": round(100.0 * valid_days / expected_days, 1),
                    "valid_days_winter": winter_valid,
                    "completeness_winter_pct": round(100.0 * winter_valid / 183.0, 1),
                    "valid_days_ytd": ytd_valid,
                    "completeness_ytd_pct": round(100.0 * ytd_valid / expected_ytd, 1),
                    "is_complete_year": bool(is_complete_calendar),
                    "is_complete_winter": bool(is_complete_winter),
                    "is_complete_ytd": bool(is_complete_ytd),
                    "mean_mp25_all": round(float(grp["mp25_24h"].mean()), 2) if valid_days > 0 else np.nan,
                    "mean_mp25_winter": round(float(winter_grp["mp25_24h"].mean()), 2) if winter_valid > 0 else np.nan,
                    "mean_mp25_ytd": round(float(ytd_grp["mp25_24h"].mean()), 2) if ytd_valid > 0 else np.nan,
                    "days_over_50_all": int(grp["over_norm_50"].sum()) if valid_days > 0 else 0,
                    "days_over_50_winter": int(winter_grp["over_norm_50"].sum()) if winter_valid > 0 else 0,
                    "days_over_50_ytd": int(ytd_grp["over_norm_50"].sum()) if ytd_valid > 0 else 0,
                    "pct_days_prelim_or_noval": round(
                        100.0 * (grp.loc[grp["mp25_valid_day"], "mp25_day_quality"] != "validado").mean(), 1
                    )
                    if valid_days > 0
                    else np.nan,
                }
            )

    hourly_all = pd.concat(all_hourly_mp25_parts, ignore_index=True)
    daily_all = pd.concat(all_daily_parts, ignore_index=True)
    yearly_df = pd.DataFrame(yearly_completeness_parts).sort_values(["station_id", "year"]).reset_index(drop=True)

    # Agregar perfil horario x mes por estacion (para heatmaps rapidos en Power BI y Dash)
    heatmap_df = (
        hourly_all.dropna(subset=["mp25"])
        .groupby(["station_id", "month", "hour"], as_index=False)
        .agg(
            mp25_mean=("mp25", "mean"),
            mp25_median=("mp25", "median"),
            mp25_p90=("mp25", lambda s: np.percentile(s, 90)),
            n_obs=("mp25", "count"),
        )
    )
    heatmap_df["mp25_mean"] = heatmap_df["mp25_mean"].round(2)
    heatmap_df["mp25_median"] = heatmap_df["mp25_median"].round(2)
    heatmap_df["mp25_p90"] = heatmap_df["mp25_p90"].round(2)

    # Agregar serie mensual con regla >= 75% de dias validos del mes
    daily_all["year_month"] = daily_all["date"].dt.to_period("M").dt.to_timestamp()
    monthly_df = (
        daily_all.groupby(["station_id", "year_month", "year", "month"], as_index=False)
        .agg(
            valid_days=("mp25_valid_day", "sum"),
            mp25_mean=("mp25_24h", "mean"),
            mp25_p90=("mp25_24h", lambda s: np.nanpercentile(s.dropna(), 90) if s.notna().any() else np.nan),
            days_over_50=("over_norm_50", "sum"),
            temp_mean=("temp", "mean"),
            velviento_mean=("velviento", "mean"),
            humedad_mean=("humedad", "mean"),
            presion_mean=("presion", "mean"),
        )
    )
    monthly_df["days_in_month"] = monthly_df["year_month"].dt.days_in_month
    monthly_df["month_valid"] = (monthly_df["valid_days"] / monthly_df["days_in_month"]) >= 0.75
    monthly_df["mp25_mean_valid"] = np.where(monthly_df["month_valid"], monthly_df["mp25_mean"], np.nan)

    # Guardar archivos procesados
    hourly_all.to_csv(OUT_PROC / "all_stations_hourly.csv.gz", index=False, compression="gzip")
    daily_all.to_csv(OUT_PROC / "all_stations_daily.csv", index=False)
    yearly_df.to_csv(OUT_PROC / "yearly_summary_completeness.csv", index=False)
    monthly_df.to_csv(OUT_PROC / "monthly_summary.csv", index=False)
    heatmap_df.to_csv(OUT_PROC / "heatmap_hour_month.csv", index=False)

    # Exportar modelo estrella para Power BI
    dim_estacion = pd.DataFrame(STATIONS_META)
    dim_estacion.to_csv(OUT_PBI / "dim_estacion.csv", index=False)

    all_dates = pd.date_range(daily_all["date"].min(), daily_all["date"].max(), freq="D")
    meses_es = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
    }
    dim_fecha = pd.DataFrame({"date": all_dates})
    dim_fecha["year"] = dim_fecha["date"].dt.year
    dim_fecha["month"] = dim_fecha["date"].dt.month
    dim_fecha["month_name"] = dim_fecha["month"].map(meses_es)
    dim_fecha["quarter"] = "T" + dim_fecha["date"].dt.quarter.astype(str)
    dim_fecha["day_of_week"] = dim_fecha["date"].dt.dayofweek + 1
    dim_fecha["is_weekend"] = dim_fecha["date"].dt.dayofweek >= 5
    dim_fecha["is_winter_season"] = dim_fecha["month"].between(4, 9)
    dim_fecha["is_ytd_comparable"] = (dim_fecha["month"] < YTD_CUTOFF_MONTH) | (
        (dim_fecha["month"] == YTD_CUTOFF_MONTH) & (dim_fecha["date"].dt.day <= YTD_CUTOFF_DAY)
    )
    dim_fecha["year_status"] = np.where(dim_fecha["year"] == 2026, "Incompleto (YTD oct)", "Completo")
    dim_fecha.to_csv(OUT_PBI / "dim_fecha.csv", index=False)

    daily_all.to_csv(OUT_PBI / "fact_calidad_aire_diaria.csv", index=False)
    heatmap_df.to_csv(OUT_PBI / "fact_ciclo_horario_mensual.csv", index=False)
    yearly_df.to_csv(OUT_PBI / "fact_resumen_anual_completitud.csv", index=False)

    # Self-checks basicos (ponytail: toda logica no trivial lleva verificacion)
    assert len(audit_df) == 22, "Deben auditarse exactamente 22 series horarias"
    assert set(wind_rose_df["station_id"].unique()) == {"CoyhaiqueII", "Coyhaique", "Vialidad"}
    assert (daily_all.loc[~daily_all["mp25_valid_day"], "mp25_24h"].isna()).all(), "Dias con <18h deben ser NaN"
    assert not yearly_df.loc[yearly_df["year"] == 2026, "is_complete_year"].any(), "2026 debe marcarse como ano incompleto"

    summary = {
        "total_csv_files": 25,
        "hourly_files": 22,
        "wind_rose_files": 3,
        "ytd_cutoff": "2026-10-23",
        "total_hourly_rows": int(len(hourly_all)),
        "total_daily_rows": int(len(daily_all)),
        "stations": list(hourly_by_station.keys()),
    }
    with open(OUT_PROC / "audit_overview.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)

    print("\n=== RESUMEN DE AUDITORIA DE SERIES ===")
    print(audit_df[["station_id", "variable", "start_date", "end_date", "n_rows", "completeness_pct", "n_preliminar", "n_no_validado"]].to_string(index=False))
    print("\n=== RESUMEN ANUAL Y COMPLETITUD (MP2,5) ===")
    print(yearly_df[["station_id", "year", "completeness_year_pct", "completeness_winter_pct", "is_complete_year", "mean_mp25_winter", "days_over_50_all", "days_over_50_ytd", "pct_days_prelim_or_noval"]].to_string(index=False))
    print("\n=== ROSAS DE VIENTO (TOP 3 SECTORES POR ESTACION) ===")
    for sid, g in wind_rose_df.groupby("station_id"):
        top3 = g.nlargest(3, "freq_pct")[["sector_label", "freq_pct"]].to_dict("records")
        print(f"  {sid:12s}: sum={g['freq_pct'].sum():.1f}% | top3={top3}")
    print("\nOK: Limpieza, auditoria y exportacion Power BI completadas con exito.")


if __name__ == "__main__":
    main()
