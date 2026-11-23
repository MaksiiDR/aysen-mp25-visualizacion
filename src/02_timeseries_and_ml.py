"""
02_timeseries_and_ml.py
-----------------------
Analisis de series de tiempo (STL, Mann-Kendall / Sen, ACF / PACF, CCF),
correlaciones meteorologicas, PCA + comparacion objetiva de clustering
(K-Means, GMM, Ward) y validacion explicativa con particion temporal
(TimeSeriesSplit + GridSearchCV) sobre los datos limpios de SINCA.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pymannkendall as mk
from scipy import stats
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    adjusted_rand_score,
    average_precision_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import acf, ccf, pacf

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parent.parent
PROC_DIR = BASE_DIR / "data_processed"
PBI_DIR = BASE_DIR / "powerbi" / "data"


def run_stl_decomposition(monthly_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Ejecuta descomposicion STL robusta en series mensuales de MP2,5 por estacion."""
    stl_parts = []
    stl_meta = {}

    for sid, grp in monthly_df.groupby("station_id"):
        g = grp.sort_values("year_month").copy()
        idx = pd.date_range(g["year_month"].min(), g["year_month"].max(), freq="MS")
        s = g.set_index("year_month")["mp25_mean_valid"].reindex(idx)

        # Recortar extremos NaN y verificar longitud minima (>= 24 meses = 2 ciclos anuales)
        first_valid = s.first_valid_index()
        last_valid = s.last_valid_index()
        s = s.loc[first_valid:last_valid]
        if len(s) < 24:
            continue

        # Solo interpolar huecos cortos (<= 2 meses consecutivos) para STL; documentar cuantos
        n_missing_before = int(s.isna().sum())
        is_interp = s.isna()
        s_filled = s.interpolate(method="linear", limit=2)
        # Si queda algun hueco largo (>2 meses), usar promedio climatologico del mismo mes solo para STL y marcarlo
        if s_filled.isna().any():
            month_means = s_filled.groupby(s_filled.index.month).transform("mean")
            s_filled = s_filled.fillna(month_means)

        # Comparar hiperparametros STL: robust=True (period=12, seasonal=13 vs 7)
        res = STL(s_filled, period=12, seasonal=13, robust=True).fit()
        res_nonrob = STL(s_filled, period=12, seasonal=13, robust=False).fit()

        # Fuerza estacional y de tendencia (Wang et al. 2006)
        var_resid = float(np.var(res.resid))
        var_tr_res = float(np.var(res.trend + res.resid))
        var_se_res = float(np.var(res.seasonal + res.resid))
        trend_strength = max(0.0, 1.0 - var_resid / var_tr_res) if var_tr_res > 0 else 0.0
        seasonal_strength = max(0.0, 1.0 - var_resid / var_se_res) if var_se_res > 0 else 0.0

        stl_meta[sid] = {
            "n_months": int(len(s)),
            "start": first_valid.strftime("%Y-%m"),
            "end": last_valid.strftime("%Y-%m"),
            "n_missing_interpolated_for_stl": n_missing_before,
            "trend_strength": round(trend_strength, 3),
            "seasonal_strength": round(seasonal_strength, 3),
            "trend_start_ugm3": round(float(res.trend.iloc[0]), 2),
            "trend_end_ugm3": round(float(res.trend.iloc[-1]), 2),
            "resid_mad_robust": round(float(np.median(np.abs(res.resid))), 2),
            "resid_mad_nonrobust": round(float(np.median(np.abs(res_nonrob.resid))), 2),
        }

        part = pd.DataFrame(
            {
                "date": s.index,
                "station_id": sid,
                "observed_mp25": s.values,
                "stl_input_mp25": s_filled.values,
                "was_interpolated": is_interp.values,
                "trend": res.trend.values,
                "seasonal": res.seasonal.values,
                "resid": res.resid.values,
            }
        )
        stl_parts.append(part)

    stl_df = pd.concat(stl_parts, ignore_index=True)
    return stl_df, stl_meta


def run_trend_tests(yearly_df: pd.DataFrame) -> dict:
    """Ejecuta test no parametrico de Mann-Kendall y pendiente de Sen (anos completos e invierno con 2026)."""
    results = {}
    for sid, grp in yearly_df.groupby("station_id"):
        g = grp.sort_values("year")
        comp = g[g["is_complete_year"]]
        wint = g[g["is_complete_winter"]]
        ytd = g[g["is_complete_ytd"]]

        station_res = {}
        for label, sub, col_mean, col_days in [
            ("complete_years", comp, "mean_mp25_all", "days_over_50_all"),
            ("winter_incl_2026", wint, "mean_mp25_winter", "days_over_50_winter"),
            ("ytd_incl_2026", ytd, "mean_mp25_ytd", "days_over_50_ytd"),
        ]:
            if len(sub) >= 4:
                mk_mean = mk.original_test(sub[col_mean].dropna().values)
                mk_days = mk.original_test(sub[col_days].dropna().values)
                station_res[label] = {
                    "years": [int(sub["year"].min()), int(sub["year"].max())],
                    "n_years": int(len(sub)),
                    "mp25_mean_trend": mk_mean.trend,
                    "mp25_mean_p": round(float(mk_mean.p), 4),
                    "mp25_mean_sen_slope": round(float(mk_mean.slope), 3),
                    "days_over_50_trend": mk_days.trend,
                    "days_over_50_p": round(float(mk_days.p), 4),
                    "days_over_50_sen_slope": round(float(mk_days.slope), 3),
                }
        results[sid] = station_res
    return results


def run_temporal_and_met_correlations(daily_df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Calcula ACF/PACF, correlacion cruzada (CCF) y pruebas Mann-Whitney en Coyhaique II."""
    c2 = daily_df[daily_df["station_id"] == "CoyhaiqueII"].sort_values("date").copy()
    c2_idx = c2.set_index("date").asfreq("D")

    # ACF y PACF sobre serie diaria (solo interpolacion corta <= 2 dias para lags; se reporta n valido)
    s_mp25 = c2_idx["mp25_24h"].interpolate(limit=2).dropna()
    acf_vals = acf(s_mp25, nlags=14, fft=True)
    pacf_vals = pacf(s_mp25, nlags=14, method="ywm")

    # CCF (lags -7 a +7) entre MP2,5 y cada variable meteorologica en temporada invernal y anual
    met_vars = ["temp", "velviento", "humedad", "presion"]
    ccf_rows = []
    for var in met_vars:
        pair = c2_idx[["mp25_24h", var]].dropna()
        # Correlacion de Spearman contemporanea (lag 0)
        rho_all, p_all = stats.spearmanr(pair["mp25_24h"], pair[var])
        pair_w = c2_idx.loc[(c2_idx.index.month >= 4) & (c2_idx.index.month <= 9), ["mp25_24h", var]].dropna()
        rho_w, p_w = stats.spearmanr(pair_w["mp25_24h"], pair_w[var])

        # CCF para lags k = -7..+7: corr(var[t-k], mp25[t]) -> k > 0 significa clima antecede a MP2,5
        for lag in range(-7, 8):
            shifted = c2_idx[var].shift(lag)
            valid_pair = pd.concat([c2_idx["mp25_24h"], shifted], axis=1).dropna()
            r_pearson = float(valid_pair.iloc[:, 0].corr(valid_pair.iloc[:, 1], method="pearson"))
            r_spearman = float(valid_pair.iloc[:, 0].corr(valid_pair.iloc[:, 1], method="spearman"))
            ccf_rows.append(
                {
                    "variable": var,
                    "lag_days": lag,
                    "pearson_r": round(r_pearson, 4),
                    "spearman_rho": round(r_spearman, 4),
                    "n_pairs": int(len(valid_pair)),
                    "spearman_lag0_all": round(float(rho_all), 4),
                    "spearman_lag0_winter": round(float(rho_w), 4),
                }
            )
    ccf_df = pd.DataFrame(ccf_rows)

    # Comparacion de distribuciones meteorologicas: dias episodio (>50) vs normales (<=50)
    ep_tests = {}
    valid_c2 = c2[c2["mp25_valid_day"]].copy()
    for var in ["temp", "temp_min_24h", "velviento", "humedad", "presion", "mp10", "co", "so2", "o3"]:
        if var not in valid_c2.columns:
            continue
        g1 = valid_c2.loc[valid_c2["over_norm_50"] == 1, var].dropna()
        g0 = valid_c2.loc[valid_c2["over_norm_50"] == 0, var].dropna()
        u_stat, p_val = stats.mannwhitneyu(g1, g0, alternative="two-sided")
        ep_tests[var] = {
            "episode_median": round(float(g1.median()), 2),
            "episode_mean": round(float(g1.mean()), 2),
            "episode_iqr": [round(float(g1.quantile(0.25)), 2), round(float(g1.quantile(0.75)), 2)],
            "normal_median": round(float(g0.median()), 2),
            "normal_mean": round(float(g0.mean()), 2),
            "normal_iqr": [round(float(g0.quantile(0.25)), 2), round(float(g0.quantile(0.75)), 2)],
            "mannwhitney_p": float(f"{p_val:.3e}"),
            "n_ep": int(len(g1)),
            "n_norm": int(len(g0)),
        }

    # Correlacion espacial entre estaciones (MP2,5 diario)
    piv = daily_df.pivot(index="date", columns="station_id", values="mp25_24h")
    inter_station_corr = {}
    stations = list(piv.columns)
    for i in range(len(stations)):
        for j in range(i + 1, len(stations)):
            s1, s2 = stations[i], stations[j]
            sub = piv[[s1, s2]].dropna()
            r, p = stats.spearmanr(sub[s1], sub[s2])
            inter_station_corr[f"{s1}_vs_{s2}"] = {
                "spearman_rho": round(float(r), 4),
                "p_value": float(f"{p:.3e}"),
                "n_days": int(len(sub)),
            }

    return (
        {
            "acf_lags_0_14": [round(float(x), 4) for x in acf_vals],
            "pacf_lags_0_14": [round(float(x), 4) for x in pacf_vals],
            "episode_vs_normal_tests": ep_tests,
            "inter_station_spearman": inter_station_corr,
        },
        ccf_df,
    )


def run_pca_and_clustering(daily_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Ejecuta PCA y comparacion objetiva de K-Means, GMM y Ward en Coyhaique II."""
    c2 = daily_df[daily_df["station_id"] == "CoyhaiqueII"].sort_values("date").copy()

    # Variables multivariadas con alta completitud (>91% en Coyhaique II desde ago-2015)
    # Transformacion log1p para contaminantes asimetricos (MP2,5, CO)
    features_raw = ["mp25_24h", "co", "temp", "humedad", "velviento", "presion"]
    df_ml = c2[["date", "station_id", "year", "month", "is_winter_season", "over_norm_50", "gec_category", "mp10", "so2", "o3"] + features_raw].dropna(subset=features_raw).copy()

    X_df = pd.DataFrame(index=df_ml.index)
    X_df["log_mp25"] = np.log1p(df_ml["mp25_24h"])
    X_df["log_co"] = np.log1p(df_ml["co"])
    X_df["temp"] = df_ml["temp"]
    X_df["humedad"] = df_ml["humedad"]
    X_df["velviento"] = df_ml["velviento"]
    X_df["presion"] = df_ml["presion"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_df.values)

    # PCA completo
    pca = PCA(random_state=42)
    X_pca = pca.fit_transform(X_scaled)
    evr = pca.explained_variance_ratio_
    cum_evr = np.cumsum(evr)

    loadings = pd.DataFrame(
        pca.components_[:3].T,
        index=X_df.columns,
        columns=["PC1", "PC2", "PC3"],
    ).round(4)

    # Comparar K-Means, GMM y Ward para k = 2..6
    eval_rows = []
    models_labels: dict[tuple[str, int], np.ndarray] = {}

    for k in range(2, 7):
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        lbl_km = km.fit_predict(X_scaled)
        models_labels[("K-Means", k)] = lbl_km

        gmm = GaussianMixture(n_components=k, covariance_type="full", n_init=5, random_state=42)
        lbl_gmm = gmm.fit_predict(X_scaled)
        models_labels[("GMM", k)] = lbl_gmm

        ward = AgglomerativeClustering(n_clusters=k, linkage="ward")
        lbl_ward = ward.fit_predict(X_scaled)
        models_labels[("Ward", k)] = lbl_ward

        for name, labels in [("K-Means", lbl_km), ("GMM", lbl_gmm), ("Ward", lbl_ward)]:
            sil = float(silhouette_score(X_scaled, labels))
            db = float(davies_bouldin_score(X_scaled, labels))
            ch = float(calinski_harabasz_score(X_scaled, labels))

            # Estabilidad temporal (ARI entre ajuste en todo el periodo vs mitad 2015-2020 y 2021-2026)
            mid = len(X_scaled) // 2
            if name == "K-Means":
                m_first = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X_scaled[:mid])
                ari_stab = float(adjusted_rand_score(labels[mid:], m_first.predict(X_scaled[mid:])))
            elif name == "GMM":
                m_first = GaussianMixture(n_components=k, covariance_type="full", n_init=3, random_state=42).fit(X_scaled[:mid])
                ari_stab = float(adjusted_rand_score(labels[mid:], m_first.predict(X_scaled[mid:])))
            else:
                ari_stab = np.nan

            eval_rows.append(
                {
                    "algorithm": name,
                    "k": k,
                    "silhouette": round(sil, 4),
                    "davies_bouldin": round(db, 4),
                    "calinski_harabasz": round(ch, 1),
                    "temporal_ari": round(ari_stab, 4) if not np.isnan(ari_stab) else None,
                }
            )

    eval_df = pd.DataFrame(eval_rows)

    # Seleccionar el mejor modelo con k >= 3 (k=2 solo separa invierno/verano; k=3 o 4 captura regimen critico)
    cand_k3plus = eval_df[eval_df["k"] >= 3].copy()
    best_row = cand_k3plus.sort_values(["silhouette", "calinski_harabasz"], ascending=[False, False]).iloc[0]
    best_algo = str(best_row["algorithm"])
    best_k = int(best_row["k"])
    raw_labels = models_labels[(best_algo, best_k)]

    # Reordenar etiquetas de cluster de menor a mayor MP2,5 mediano para interpretabilidad
    tmp = pd.DataFrame({"lbl": raw_labels, "mp25": df_ml["mp25_24h"].values})
    order = tmp.groupby("lbl")["mp25"].median().sort_values().index.tolist()
    remap = {old: new for new, old in enumerate(order)}
    ordered_labels = np.array([remap[x] for x in raw_labels])

    if best_k == 3:
        cluster_names = {
            0: "C0: Calido-Ventilado (Limpio)",
            1: "C1: Frio-Transicion (Moderado)",
            2: "C2: Frio-Estancado (Critico)",
        }
    elif best_k == 4:
        cluster_names = {
            0: "C0: Calido-Ventilado (Limpio)",
            1: "C1: Templado-Humedo (Bajo)",
            2: "C2: Frio-Moderado (Transicion)",
            3: "C3: Frio-Estancado (Critico)",
        }
    else:
        cluster_names = {i: f"C{i}" for i in range(best_k)}

    df_ml["PC1"] = np.round(X_pca[:, 0], 4)
    df_ml["PC2"] = np.round(X_pca[:, 1], 4)
    df_ml["PC3"] = np.round(X_pca[:, 2], 4)
    df_ml["cluster_id"] = ordered_labels
    df_ml["cluster_name"] = [cluster_names[i] for i in ordered_labels]

    # Resumen por cluster
    cluster_profiles = []
    for cid, g in df_ml.groupby("cluster_id"):
        cluster_profiles.append(
            {
                "cluster_id": int(cid),
                "cluster_name": cluster_names[int(cid)],
                "n_days": int(len(g)),
                "pct_days": round(100.0 * len(g) / len(df_ml), 1),
                "mp25_median": round(float(g["mp25_24h"].median()), 1),
                "mp25_mean": round(float(g["mp25_24h"].mean()), 1),
                "episode_rate_pct": round(100.0 * float(g["over_norm_50"].mean()), 1),
                "share_of_all_episodes_pct": round(100.0 * float(g["over_norm_50"].sum()) / float(df_ml["over_norm_50"].sum()), 1),
                "temp_mean": round(float(g["temp"].mean()), 1),
                "velviento_mean": round(float(g["velviento"].mean()), 2),
                "humedad_mean": round(float(g["humedad"].mean()), 1),
                "presion_mean": round(float(g["presion"].mean()), 1),
                "co_mean": round(float(g["co"].mean()), 2),
                "winter_share_pct": round(100.0 * float(g["is_winter_season"].mean()), 1),
            }
        )

    pca_summary = {
        "n_complete_days": int(len(df_ml)),
        "date_range": [df_ml["date"].min().strftime("%Y-%m-%d"), df_ml["date"].max().strftime("%Y-%m-%d")],
        "features": list(X_df.columns),
        "explained_variance_ratio": [round(float(x), 4) for x in evr],
        "cumulative_variance_ratio": [round(float(x), 4) for x in cum_evr],
        "loadings": loadings.to_dict(),
        "selected_model": {
            "algorithm": best_algo,
            "k": best_k,
            "silhouette": float(best_row["silhouette"]),
            "davies_bouldin": float(best_row["davies_bouldin"]),
            "calinski_harabasz": float(best_row["calinski_harabasz"]),
            "temporal_ari": best_row["temporal_ari"],
        },
        "cluster_profiles": cluster_profiles,
    }
    return df_ml, eval_df, pca_summary


def run_explanatory_validation(daily_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Validacion explicativa con TimeSeriesSplit y ajuste de hiperparametros (GridSearchCV):
    cuantifica cuanto explican las condiciones meteorologicas (+ persistencia lag-1)
    la ocurrencia de dias sobre la norma (>50 ug/m3) en Coyhaique II.
    """
    c2 = daily_df[daily_df["station_id"] == "CoyhaiqueII"].sort_values("date").copy()
    c2 = c2.set_index("date").asfreq("D").reset_index()

    c2["doy"] = c2["date"].dt.dayofyear
    c2["sin_doy"] = np.sin(2 * np.pi * c2["doy"] / 365.25)
    c2["cos_doy"] = np.cos(2 * np.pi * c2["doy"] / 365.25)
    c2["mp25_lag1"] = c2["mp25_24h"].shift(1)
    c2["over50_lag1"] = c2["over_norm_50"].shift(1)
    c2["temp_lag1"] = c2["temp"].shift(1)
    c2["velviento_lag1"] = c2["velviento"].shift(1)

    met_cols = ["temp", "temp_min_24h", "humedad", "velviento", "presion", "sin_doy", "cos_doy"]
    met_lag_cols = met_cols + ["mp25_lag1", "temp_lag1", "velviento_lag1"]

    df_sup = c2[["date", "over_norm_50", "over50_lag1"] + met_lag_cols].dropna().reset_index(drop=True)
    y = df_sup["over_norm_50"].astype(int).values

    # Split temporal estricto: entrenamiento 2015-2023, prueba fuera de muestra 2024-2026
    train_mask = df_sup["date"] < "2024-01-01"
    test_mask = ~train_mask
    y_train, y_test = y[train_mask], y[test_mask]

    tscv = TimeSeriesSplit(n_splits=5)

    results = []
    # Baseline de persistencia (serie de tiempo ingenua: hoy > 50 si ayer > 50)
    y_pred_pers = df_sup.loc[test_mask, "over50_lag1"].astype(int).values
    y_prob_pers = df_sup.loc[test_mask, "mp25_lag1"].values
    results.append(
        {
            "feature_set": "Solo lag-1 (Persistencia)",
            "model": "Persistencia (t-1)",
            "best_params": "umbral=50 ug/m3",
            "cv_f1": None,
            "test_f1": round(float(f1_score(y_test, y_pred_pers)), 4),
            "test_precision": round(float(precision_score(y_test, y_pred_pers)), 4),
            "test_recall": round(float(recall_score(y_test, y_pred_pers)), 4),
            "test_pr_auc": round(float(average_precision_score(y_test, y_prob_pers)), 4),
            "test_roc_auc": round(float(roc_auc_score(y_test, y_prob_pers)), 4),
        }
    )

    model_specs = [
        (
            "Regresion Logistica",
            Pipeline([("sc", StandardScaler()), ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))]),
            {"clf__C": [0.05, 0.2, 1.0, 5.0]},
        ),
        (
            "Random Forest",
            RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1),
            {"n_estimators": [150, 300], "max_depth": [5, 8, 12], "min_samples_leaf": [5, 15]},
        ),
        (
            "Gradient Boosting",
            GradientBoostingClassifier(random_state=42),
            {"n_estimators": [100, 200], "max_depth": [2, 3], "learning_rate": [0.03, 0.08]},
        ),
    ]

    best_rf_importances = {}
    for fs_name, cols in [("Solo Meteorologia", met_cols), ("Meteorologia + Lag-1", met_lag_cols)]:
        X_tr = df_sup.loc[train_mask, cols].values
        X_te = df_sup.loc[test_mask, cols].values
        for m_name, estimator, grid in model_specs:
            gs = GridSearchCV(estimator, grid, cv=tscv, scoring="f1", n_jobs=-1)
            gs.fit(X_tr, y_train)
            best_est = gs.best_estimator_
            y_pred = best_est.predict(X_te)
            y_prob = best_est.predict_proba(X_te)[:, 1]
            results.append(
                {
                    "feature_set": fs_name,
                    "model": m_name,
                    "best_params": str(gs.best_params_),
                    "cv_f1": round(float(gs.best_score_), 4),
                    "test_f1": round(float(f1_score(y_test, y_pred)), 4),
                    "test_precision": round(float(precision_score(y_test, y_pred)), 4),
                    "test_recall": round(float(recall_score(y_test, y_pred)), 4),
                    "test_pr_auc": round(float(average_precision_score(y_test, y_prob)), 4),
                    "test_roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
                }
            )
            if m_name == "Random Forest":
                best_rf_importances[fs_name] = {
                    c: round(float(imp), 4) for c, imp in zip(cols, best_est.feature_importances_)
                }

    res_df = pd.DataFrame(results)
    meta = {
        "train_period": [df_sup.loc[train_mask, "date"].min().strftime("%Y-%m-%d"), df_sup.loc[train_mask, "date"].max().strftime("%Y-%m-%d")],
        "test_period": [df_sup.loc[test_mask, "date"].min().strftime("%Y-%m-%d"), df_sup.loc[test_mask, "date"].max().strftime("%Y-%m-%d")],
        "n_train": int(train_mask.sum()),
        "n_test": int(test_mask.sum()),
        "positive_rate_train_pct": round(100.0 * float(y_train.mean()), 1),
        "positive_rate_test_pct": round(100.0 * float(y_test.mean()), 1),
        "rf_feature_importances": best_rf_importances,
    }
    return res_df, meta


def main() -> None:
    print("Cargando series procesadas...")
    daily_df = pd.read_csv(PROC_DIR / "all_stations_daily.csv", parse_dates=["date"])
    monthly_df = pd.read_csv(PROC_DIR / "monthly_summary.csv", parse_dates=["year_month"])
    yearly_df = pd.read_csv(PROC_DIR / "yearly_summary_completeness.csv")

    print("1. Ejecutando descomposicion STL mensual...")
    stl_df, stl_meta = run_stl_decomposition(monthly_df)
    stl_df.to_csv(PROC_DIR / "stl_decomposition.csv", index=False)
    stl_df.to_csv(PBI_DIR / "fact_stl_descomposicion.csv", index=False)

    print("2. Ejecutando pruebas de tendencia Mann-Kendall y Sen...")
    trends = run_trend_tests(yearly_df)

    print("3. Calculando ACF/PACF, CCF y pruebas Mann-Whitney...")
    corr_summary, ccf_df = run_temporal_and_met_correlations(daily_df)
    ccf_df.to_csv(PROC_DIR / "ccf_meteorology_mp25.csv", index=False)

    print("4. Ejecutando PCA y comparacion objetiva de clustering (K-Means, GMM, Ward)...")
    clusters_df, cluster_eval_df, pca_summary = run_pca_and_clustering(daily_df)
    clusters_df.to_csv(PROC_DIR / "pca_clusters_daily.csv", index=False)
    clusters_df[["date", "station_id", "PC1", "PC2", "PC3", "cluster_id", "cluster_name", "mp25_24h", "over_norm_50"]].to_csv(
        PBI_DIR / "fact_clusters_pca.csv", index=False
    )
    cluster_eval_df.to_csv(PROC_DIR / "clustering_evaluation.csv", index=False)

    print("5. Ejecutando validacion explicativa con TimeSeriesSplit y GridSearchCV...")
    clf_df, clf_meta = run_explanatory_validation(daily_df)
    clf_df.to_csv(PROC_DIR / "explanatory_models_evaluation.csv", index=False)

    # Consolidar resultados clave en JSON para trazabilidad exacta en paper y slides
    full_results = {
        "stl": stl_meta,
        "mann_kendall_trends": trends,
        "temporal_and_met": corr_summary,
        "pca_clustering": pca_summary,
        "explanatory_validation": clf_meta,
    }
    with open(PROC_DIR / "analysis_results_summary.json", "w", encoding="utf-8") as fh:
        json.dump(full_results, fh, indent=2, ensure_ascii=False)

    # Self-checks
    assert len(stl_df) > 100, "STL debe generar componentes para multiples estaciones"
    assert pca_summary["cumulative_variance_ratio"][1] > 0.50, "PC1+PC2 deben explicar >50% de varianza"
    assert len(cluster_eval_df) == 15, "3 algoritmos x 5 valores de k = 15 evaluaciones"
    assert clf_df["test_roc_auc"].max() > 0.80, "Validacion explicativa debe alcanzar ROC-AUC > 0.80"

    print("\n=== STL STRENGTH ===")
    print(json.dumps(stl_meta, indent=2, ensure_ascii=False))
    print("\n=== TENDENCIAS MANN-KENDALL ===")
    print(json.dumps(trends, indent=2, ensure_ascii=False))
    print("\n=== COMPARACION CLUSTERING (K-MEANS, GMM, WARD) ===")
    print(cluster_eval_df.to_string(index=False))
    print("\n=== PERFILES DE CLUSTER SELECCIONADO ===")
    print(pd.DataFrame(pca_summary["cluster_profiles"]).to_string(index=False))
    print("\n=== VALIDACION EXPLICATIVA (TEST 2024-2026) ===")
    print(clf_df[["feature_set", "model", "cv_f1", "test_f1", "test_precision", "test_recall", "test_pr_auc", "test_roc_auc"]].to_string(index=False))
    print("\nOK: Analisis de series de tiempo, PCA/clustering y validacion completados.")


if __name__ == "__main__":
    main()
