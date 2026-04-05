from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


EPS = 1e-9


@dataclass
class MonitorConfig:
    required_columns: List[str]
    optional_columns: List[str]
    baseline: Dict[str, int]
    ml: Dict[str, float]
    traffic_light: Dict[str, float]
    weights: Dict[str, float]
    hard_breaches: Dict[str, float]

    @staticmethod
    def load(path: str | Path) -> "MonitorConfig":
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return MonitorConfig(**raw)


def load_trades(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Formato no soportado: {path.suffix}")


def validate_columns(df: pd.DataFrame, required_columns: List[str]) -> None:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")


def prepare_trade_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "quality_flag" in df.columns:
        df = df[df["quality_flag"].fillna("OK") != "ERROR"].copy()

    df["close_time"] = pd.to_datetime(df["close_time"], errors="coerce")
    df = df.dropna(subset=["trader_id", "close_time", "pnl_net"]).copy()
    df = df.sort_values(["trader_id", "close_time"]).reset_index(drop=True)

    df["is_win"] = (df["pnl_net"] > 0).astype(int)
    df["is_loss"] = (df["pnl_net"] < 0).astype(int)
    df["abs_pnl"] = df["pnl_net"].abs()

    if "symbol" in df.columns:
        df["symbol"] = df["symbol"].astype(str).fillna("UNKNOWN")

    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    if "holding_minutes" in df.columns:
        df["holding_minutes"] = pd.to_numeric(df["holding_minutes"], errors="coerce")

    if "risk_pct" in df.columns:
        df["risk_pct"] = pd.to_numeric(df["risk_pct"], errors="coerce")

    if "slippage" in df.columns:
        df["slippage"] = pd.to_numeric(df["slippage"], errors="coerce")

    return df


def max_consecutive_losses(values: pd.Series) -> int:
    streak = 0
    best = 0
    for x in values.fillna(0).tolist():
        if x < 0:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    return best


def profit_factor(pnl: pd.Series) -> float:
    gross_profit = pnl[pnl > 0].sum()
    gross_loss = abs(pnl[pnl < 0].sum())
    if gross_loss <= EPS:
        return np.inf if gross_profit > 0 else 1.0
    return float(gross_profit / gross_loss)


def expectancy_from_series(pnl: pd.Series) -> float:
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]
    win_rate = len(wins) / max(len(pnl), 1)
    avg_win = wins.mean() if len(wins) else 0.0
    avg_loss = losses.mean() if len(losses) else 0.0
    return float((win_rate * avg_win) + ((1 - win_rate) * avg_loss))


def symbol_concentration(group: pd.DataFrame) -> float:
    if "symbol" not in group.columns or group["symbol"].isna().all():
        return np.nan
    freq = group["symbol"].value_counts(normalize=True)
    return float(freq.iloc[0]) if not freq.empty else np.nan


def volume_cv(group: pd.DataFrame) -> float:
    if "volume" not in group.columns:
        return np.nan
    series = pd.to_numeric(group["volume"], errors="coerce").dropna()
    if len(series) < 2 or abs(series.mean()) <= EPS:
        return np.nan
    return float(series.std(ddof=0) / abs(series.mean()))


def aggregate_by_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    period:
        - 'W' for weekly
        - 'M' for monthly
    """
    if period == "W":
        period_key = df["close_time"].dt.to_period("W").astype(str)
    elif period == "M":
        period_key = df["close_time"].dt.to_period("M").astype(str)
    else:
        raise ValueError("period debe ser 'W' o 'M'")

    tmp = df.copy()
    tmp["period_key"] = period_key

    rows = []
    for (trader_id, pkey), group in tmp.groupby(["trader_id", "period_key"], sort=True):
        pnl = group["pnl_net"].astype(float)

        row = {
            "trader_id": trader_id,
            "period_key": pkey,
            "n_trades": int(len(group)),
            "pnl_sum": float(pnl.sum()),
            "pnl_mean": float(pnl.mean()),
            "pnl_std": float(pnl.std(ddof=0)) if len(group) > 1 else 0.0,
            "win_rate": float((pnl > 0).mean()),
            "avg_win": float(pnl[pnl > 0].mean()) if (pnl > 0).any() else 0.0,
            "avg_loss": float(pnl[pnl < 0].mean()) if (pnl < 0).any() else 0.0,
            "expectancy": expectancy_from_series(pnl),
            "profit_factor": profit_factor(pnl),
            "max_consec_losses": max_consecutive_losses(pnl),
            "symbol_concentration": symbol_concentration(group),
            "size_instability": volume_cv(group),
        }

        if "holding_minutes" in group.columns:
            row["avg_holding_minutes"] = float(pd.to_numeric(group["holding_minutes"], errors="coerce").mean())
        else:
            row["avg_holding_minutes"] = np.nan

        if "risk_pct" in group.columns:
            row["avg_risk_pct"] = float(pd.to_numeric(group["risk_pct"], errors="coerce").mean())
        else:
            row["avg_risk_pct"] = np.nan

        if "slippage" in group.columns:
            row["avg_slippage"] = float(pd.to_numeric(group["slippage"], errors="coerce").mean())
        else:
            row["avg_slippage"] = np.nan

        rows.append(row)

    out = pd.DataFrame(rows)
    return out.sort_values(["trader_id", "period_key"]).reset_index(drop=True)


def robust_baseline_stats(df: pd.DataFrame, feature_cols: List[str]) -> Dict[str, Dict[str, float]]:
    stats: Dict[str, Dict[str, float]] = {}
    for col in feature_cols:
        series = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        median = float(series.median()) if not series.empty else np.nan
        mad = float((series - series.median()).abs().median()) if not series.empty else np.nan
        p05 = float(series.quantile(0.05)) if not series.empty else np.nan
        p95 = float(series.quantile(0.95)) if not series.empty else np.nan
        stats[col] = {"median": median, "mad": mad, "p05": p05, "p95": p95}
    return stats


def robust_z(value: float, median: float, mad: float) -> float:
    if pd.isna(value) or pd.isna(median):
        return 0.0
    scaled_mad = 1.4826 * (mad if not pd.isna(mad) and mad > EPS else EPS)
    return float(abs(value - median) / scaled_mad)


def build_training_window(df: pd.DataFrame, min_periods: int, exclude_recent: int) -> pd.DataFrame:
    if len(df) <= exclude_recent:
        return pd.DataFrame(columns=df.columns)
    train = df.iloc[: max(len(df) - exclude_recent, 0)].copy()
    if len(train) < min_periods:
        return pd.DataFrame(columns=df.columns)
    return train


def fit_isolation_forest(train_df: pd.DataFrame, feature_cols: List[str], cfg: MonitorConfig) -> Tuple[StandardScaler, IsolationForest] | Tuple[None, None]:
    X = train_df[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if len(X) < 5:
        return None, None

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        contamination=float(cfg.ml["contamination"]),
        random_state=int(cfg.ml["random_state"]),
        n_estimators=int(cfg.ml["n_estimators"]),
    )
    model.fit(X_scaled)
    return scaler, model


def anomaly_to_unit_interval(raw_decision_score: float) -> float:
    """
    IsolationForest decision_function:
    higher = more normal
    lower = more anomalous
    Convertimos a escala intuitiva 0..1 donde 1 = muy anómalo
    """
    score = 1.0 / (1.0 + np.exp(4.0 * raw_decision_score))
    return float(np.clip(score, 0.0, 1.0))


def compute_severity(current_row: pd.Series, baseline_stats: Dict[str, Dict[str, float]], cfg: MonitorConfig) -> Tuple[float, Dict[str, float], List[str]]:
    weights = cfg.weights
    hard_cfg = cfg.hard_breaches

    metric_details: Dict[str, float] = {}
    hard_breaches: List[str] = []
    severity = 0.0

    def add_weighted_signal(name: str, condition: bool, magnitude: float, weight_key: str) -> None:
        nonlocal severity
        metric_details[name] = float(magnitude)
        if condition:
            severity += float(weights[weight_key]) * min(1.0, magnitude / 3.0)

    # Expectancy
    exp_stats = baseline_stats.get("expectancy", {})
    exp_z = robust_z(current_row.get("expectancy", np.nan), exp_stats.get("median", np.nan), exp_stats.get("mad", np.nan))
    add_weighted_signal(
        "expectancy_drop",
        bool(current_row.get("expectancy", 0.0) < exp_stats.get("median", np.inf)),
        exp_z,
        "expectancy_drop",
    )
    if current_row.get("expectancy", 0.0) < hard_cfg["expectancy_red_below"] and exp_z >= hard_cfg["max_robust_z_red"]:
        hard_breaches.append("expectancy_negativa_con_caida_fuerte")

    # Profit factor
    pf_stats = baseline_stats.get("profit_factor", {})
    pf_z = robust_z(current_row.get("profit_factor", np.nan), pf_stats.get("median", np.nan), pf_stats.get("mad", np.nan))
    add_weighted_signal(
        "profit_factor_drop",
        bool(current_row.get("profit_factor", np.inf) < pf_stats.get("median", -np.inf)),
        pf_z,
        "profit_factor_drop",
    )
    if current_row.get("profit_factor", np.inf) < hard_cfg["profit_factor_red_below"] and pf_z >= 2.0:
        hard_breaches.append("profit_factor_debil")

    # Win rate
    wr_stats = baseline_stats.get("win_rate", {})
    wr_z = robust_z(current_row.get("win_rate", np.nan), wr_stats.get("median", np.nan), wr_stats.get("mad", np.nan))
    add_weighted_signal(
        "win_rate_drop",
        bool(current_row.get("win_rate", 1.0) < wr_stats.get("median", -np.inf)),
        wr_z,
        "win_rate_drop",
    )

    # Volatility up
    vol_stats = baseline_stats.get("pnl_std", {})
    vol_z = robust_z(current_row.get("pnl_std", np.nan), vol_stats.get("median", np.nan), vol_stats.get("mad", np.nan))
    add_weighted_signal(
        "pnl_volatility_up",
        bool(current_row.get("pnl_std", 0.0) > vol_stats.get("median", np.inf)),
        vol_z,
        "pnl_volatility_up",
    )

    # Trade count down
    n_stats = baseline_stats.get("n_trades", {})
    n_z = robust_z(current_row.get("n_trades", np.nan), n_stats.get("median", np.nan), n_stats.get("mad", np.nan))
    add_weighted_signal(
        "trade_count_drop",
        bool(current_row.get("n_trades", np.inf) < n_stats.get("median", -np.inf)),
        n_z,
        "trade_count_drop",
    )

    # Consecutive losses up
    cl_stats = baseline_stats.get("max_consec_losses", {})
    cl_z = robust_z(current_row.get("max_consec_losses", np.nan), cl_stats.get("median", np.nan), cl_stats.get("mad", np.nan))
    add_weighted_signal(
        "max_consec_losses_up",
        bool(current_row.get("max_consec_losses", 0.0) > cl_stats.get("median", np.inf)),
        cl_z,
        "max_consec_losses_up",
    )

    # Symbol concentration up
    sc_stats = baseline_stats.get("symbol_concentration", {})
    sc_z = robust_z(current_row.get("symbol_concentration", np.nan), sc_stats.get("median", np.nan), sc_stats.get("mad", np.nan))
    add_weighted_signal(
        "symbol_concentration_up",
        bool(current_row.get("symbol_concentration", 0.0) > sc_stats.get("median", np.inf)),
        sc_z,
        "symbol_concentration_up",
    )

    # Size instability up
    si_stats = baseline_stats.get("size_instability", {})
    si_z = robust_z(current_row.get("size_instability", np.nan), si_stats.get("median", np.nan), si_stats.get("mad", np.nan))
    add_weighted_signal(
        "size_instability_up",
        bool(current_row.get("size_instability", 0.0) > si_stats.get("median", np.inf)),
        si_z,
        "size_instability_up",
    )

    severity = float(np.clip(severity, 0.0, 100.0))
    return severity, metric_details, hard_breaches


def assign_traffic_light(severity: float, anomaly_score: float, hard_breaches: List[str], cfg: MonitorConfig) -> str:
    traffic = cfg.traffic_light

    if hard_breaches and anomaly_score >= traffic["yellow_anomaly_min"]:
        return "RED"

    if severity >= traffic["red_severity_min"] or anomaly_score >= traffic["red_anomaly_min"]:
        return "RED"

    if severity >= traffic["yellow_severity_min"] or anomaly_score >= traffic["yellow_anomaly_min"]:
        return "YELLOW"

    return "GREEN"


def explain_alert(light: str, trader_id: str, period_key: str, severity: float, anomaly_score: float, hard_breaches: List[str], metric_details: Dict[str, float]) -> str:
    top_metrics = sorted(metric_details.items(), key=lambda x: x[1], reverse=True)[:3]
    top_str = ", ".join([f"{k}={v:.2f}" for k, v in top_metrics if v > 0])

    if light == "GREEN":
        return (
            f"Trader {trader_id} en VERDE para {period_key}. "
            f"Score={severity:.1f}, anomaly={anomaly_score:.2f}. "
            f"Sin deterioro relevante. Seguir copiando."
        )

    if light == "YELLOW":
        return (
            f"Trader {trader_id} en AMARILLO para {period_key}. "
            f"Score={severity:.1f}, anomaly={anomaly_score:.2f}. "
            f"Desvíos a vigilar: {top_str}. Mantener tamaño y monitorear el próximo periodo."
        )

    return (
        f"Trader {trader_id} en ROJO para {period_key}. "
        f"Score={severity:.1f}, anomaly={anomaly_score:.2f}. "
        f"Hard breaches: {hard_breaches if hard_breaches else 'ninguno explícito'}, "
        f"desvíos clave: {top_str}. Pausar copy y revisar."
    )


def score_periods(features_df: pd.DataFrame, horizon_name: str, cfg: MonitorConfig) -> pd.DataFrame:
    if features_df.empty:
        return features_df.copy()

    feature_cols = [
        "n_trades",
        "pnl_sum",
        "pnl_mean",
        "pnl_std",
        "win_rate",
        "expectancy",
        "profit_factor",
        "max_consec_losses",
        "symbol_concentration",
        "size_instability",
    ]
    feature_cols = [c for c in feature_cols if c in features_df.columns]

    all_rows = []
    for trader_id, trader_df in features_df.groupby("trader_id", sort=False):
        trader_df = trader_df.sort_values("period_key").reset_index(drop=True)

        min_periods = cfg.baseline["weekly_min_periods"] if horizon_name == "weekly" else cfg.baseline["monthly_min_periods"]
        exclude_recent = cfg.baseline["exclude_most_recent_periods"]

        train_df = build_training_window(trader_df, min_periods=min_periods, exclude_recent=exclude_recent)
        baseline_stats = robust_baseline_stats(train_df, feature_cols) if not train_df.empty else {}

        scaler, model = fit_isolation_forest(train_df, feature_cols, cfg) if not train_df.empty else (None, None)

        for idx, row in trader_df.iterrows():
            row = row.copy()

            if train_df.empty:
                anomaly_score = np.nan
                severity = np.nan
                hard_breaches = ["baseline_insuficiente"]
                metric_details = {}
                light = "GREEN"
                message = (
                    f"Trader {trader_id} sin baseline suficiente en {row['period_key']}. "
                    f"No se activa semáforo duro todavía."
                )
            else:
                X = row[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_frame().T
                anomaly_score = np.nan
                if scaler is not None and model is not None:
                    x_scaled = scaler.transform(X)
                    raw_decision = float(model.decision_function(x_scaled)[0])
                    anomaly_score = anomaly_to_unit_interval(raw_decision)

                severity, metric_details, hard_breaches = compute_severity(row, baseline_stats, cfg)
                light = assign_traffic_light(
                    severity=float(severity),
                    anomaly_score=float(0.0 if pd.isna(anomaly_score) else anomaly_score),
                    hard_breaches=hard_breaches,
                    cfg=cfg,
                )
                message = explain_alert(
                    light=light,
                    trader_id=str(trader_id),
                    period_key=str(row["period_key"]),
                    severity=float(severity),
                    anomaly_score=float(0.0 if pd.isna(anomaly_score) else anomaly_score),
                    hard_breaches=hard_breaches,
                    metric_details=metric_details,
                )

            out = row.to_dict()
            out["horizon"] = horizon_name
            out["severity_score"] = severity
            out["anomaly_score"] = anomaly_score
            out["traffic_light"] = light
            out["hard_breaches"] = "|".join(hard_breaches) if isinstance(hard_breaches, list) else str(hard_breaches)
            out["alert_message"] = message
            all_rows.append(out)

    return pd.DataFrame(all_rows)


def latest_status(weekly_alerts: pd.DataFrame, monthly_alerts: pd.DataFrame) -> pd.DataFrame:
    def latest(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
        cols = ["trader_id", "period_key", "traffic_light", "severity_score", "anomaly_score", "alert_message"]
        out = df.sort_values(["trader_id", "period_key"]).groupby("trader_id").tail(1)[cols].copy()
        return out.rename(columns={c: f"{prefix}_{c}" for c in cols if c != "trader_id"})

    w = latest(weekly_alerts, "weekly")
    m = latest(monthly_alerts, "monthly")
    out = w.merge(m, on="trader_id", how="outer")

    def final_light(row: pd.Series) -> str:
        wl = row.get("weekly_traffic_light")
        ml = row.get("monthly_traffic_light")
        order = {"GREEN": 0, "YELLOW": 1, "RED": 2}
        candidates = [x for x in [wl, ml] if x in order]
        if not candidates:
            return "GREEN"
        return sorted(candidates, key=lambda x: order[x])[-1]

    out["final_traffic_light"] = out.apply(final_light, axis=1)
    return out.sort_values("trader_id").reset_index(drop=True)


def save_outputs(
    weekly_features: pd.DataFrame,
    monthly_features: pd.DataFrame,
    weekly_alerts: pd.DataFrame,
    monthly_alerts: pd.DataFrame,
    latest_df: pd.DataFrame,
    outdir: str | Path,
) -> None:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    weekly_features.to_csv(outdir / "weekly_features.csv", index=False)
    monthly_features.to_csv(outdir / "monthly_features.csv", index=False)
    weekly_alerts.to_csv(outdir / "weekly_alerts.csv", index=False)
    monthly_alerts.to_csv(outdir / "monthly_alerts.csv", index=False)
    latest_df.to_csv(outdir / "trader_status_latest.csv", index=False)

    messages = {
        "weekly": weekly_alerts[["trader_id", "period_key", "traffic_light", "alert_message"]].to_dict(orient="records"),
        "monthly": monthly_alerts[["trader_id", "period_key", "traffic_light", "alert_message"]].to_dict(orient="records"),
    }
    with open(outdir / "alert_messages.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)


def run_pipeline(input_path: str | Path, config_path: str | Path, outdir: str | Path) -> None:
    cfg = MonitorConfig.load(config_path)
    df = load_trades(input_path)
    validate_columns(df, cfg.required_columns)

    prepared = prepare_trade_data(df)

    weekly_features = aggregate_by_period(prepared, period="W")
    monthly_features = aggregate_by_period(prepared, period="M")

    weekly_alerts = score_periods(weekly_features, horizon_name="weekly", cfg=cfg)
    monthly_alerts = score_periods(monthly_features, horizon_name="monthly", cfg=cfg)

    latest_df = latest_status(weekly_alerts, monthly_alerts)

    save_outputs(
        weekly_features=weekly_features,
        monthly_features=monthly_features,
        weekly_alerts=weekly_alerts,
        monthly_alerts=monthly_alerts,
        latest_df=latest_df,
        outdir=outdir,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Monitoreo ML de traders con semáforo semanal y mensual.")
    parser.add_argument("--input", required=True, help="Ruta al CSV/XLSX de trades canónicos.")
    parser.add_argument("--config", required=True, help="Ruta al JSON de configuración.")
    parser.add_argument("--outdir", required=True, help="Carpeta de salida.")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()
    run_pipeline(input_path=args.input, config_path=args.config, outdir=args.outdir)


if __name__ == "__main__":
    main()
