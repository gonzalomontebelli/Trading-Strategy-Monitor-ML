from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd


FEATURE_COLUMNS = ["expectancy", "win_rate", "pnl_std", "trades", "hold_min_median", "buy_share", "volume_mean"]


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_clean_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = ["trader_id", "close_time", "open_time", "side", "volume", "pnl_net", "quality_flag"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"clean_data is missing required columns: {missing}")

    df["close_time"] = pd.to_datetime(df["close_time"], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], errors="coerce")
    df["holding_minutes"] = (df["close_time"] - df["open_time"]).dt.total_seconds() / 60.0
    df["buy_flag"] = (df["side"].astype(str).str.upper() == "BUY").astype(int)
    df = df[df["quality_flag"].isin(["OK", "WARN"])].copy()
    return df


def compute_period_metrics(df: pd.DataFrame, freq: str) -> pd.DataFrame:
    grouped = df.set_index("close_time").groupby(["trader_id", pd.Grouper(freq=freq)])
    out = grouped.agg(
        pnl_net=("pnl_net", "sum"),
        trades=("pnl_net", "count"),
        win_rate=("pnl_net", lambda s: float((s > 0).mean())),
        expectancy=("pnl_net", "mean"),
        pnl_std=("pnl_net", lambda s: float(s.std(ddof=1)) if len(s) > 1 else np.nan),
        volume_mean=("volume", "mean"),
        hold_min_median=("holding_minutes", "median"),
        buy_share=("buy_flag", "mean"),
    ).reset_index()
    out["e_sd"] = out["expectancy"] / out["pnl_std"]
    return out


def count_threshold_breaches(row: pd.Series, thresholds: Dict[str, Any]) -> Tuple[int, int, List[str], List[str]]:
    warning_hits: List[str] = []
    critical_hits: List[str] = []

    lower_metrics = ["trades", "pnl_net", "win_rate", "expectancy", "e_sd", "buy_share"]
    upper_metrics = ["pnl_std", "hold_min_median", "volume_mean"]

    for metric in lower_metrics:
        if metric not in row or metric not in thresholds["warning"]:
            continue
        value = row[metric]
        if pd.isna(value):
            continue
        warning_limit = thresholds["warning"][metric + "_min"] if metric != "buy_share" else thresholds["warning"]["buy_share_min"]
        critical_limit = thresholds["critical"][metric + "_min"] if metric != "buy_share" else thresholds["critical"]["buy_share_min"]
        if value <= warning_limit:
            warning_hits.append(metric)
        if value <= critical_limit:
            critical_hits.append(metric)

    for metric in upper_metrics:
        if metric not in row:
            continue
        value = row[metric]
        if pd.isna(value):
            continue
        if value >= thresholds["warning"][metric + "_max"]:
            warning_hits.append(metric)
        if value >= thresholds["critical"][metric + "_max"]:
            critical_hits.append(metric)

    if "buy_share" in row and not pd.isna(row["buy_share"]):
        value = row["buy_share"]
        if value >= thresholds["warning"]["buy_share_max"]:
            warning_hits.append("buy_share_high")
        if value >= thresholds["critical"]["buy_share_max"]:
            critical_hits.append("buy_share_high")

    return len(set(warning_hits)), len(set(critical_hits)), sorted(set(warning_hits)), sorted(set(critical_hits))


def add_consecutive_negative_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values(["trader_id", "close_time"]).copy()
    out["negative_period"] = (out["pnl_net"] <= 0).astype(int)
    out["consecutive_negative"] = (
        out.groupby("trader_id")["negative_period"]
        .transform(lambda s: s.groupby((s != s.shift()).cumsum()).cumsum())
    )
    out.loc[out["negative_period"] == 0, "consecutive_negative"] = 0
    return out


def fit_simple_drift_model(history_df: pd.DataFrame) -> Dict[str, Any]:
    data = history_df[FEATURE_COLUMNS].dropna().copy()
    center = data.median()
    mad = (data - center).abs().median().replace(0, np.nan)

    z = ((data - center) / mad).abs()
    robust_score = z.mean(axis=1)

    x = ((data - center) / mad).fillna(0.0).to_numpy(dtype=float)
    cov = np.cov(x.T)
    cov = cov + np.eye(cov.shape[0]) * 1e-6
    inv_cov = np.linalg.inv(cov)

    mahal = []
    for row in x:
        mahal.append(float(np.sqrt(row @ inv_cov @ row.T)))
    mahal_series = pd.Series(mahal, index=data.index)

    return {
        "center": center.to_dict(),
        "mad": mad.to_dict(),
        "inv_cov": inv_cov.tolist(),
        "robust_score_warning": float(robust_score.quantile(0.90)),
        "robust_score_critical": float(robust_score.quantile(0.95)),
        "mahal_warning": float(mahal_series.quantile(0.90)),
        "mahal_critical": float(mahal_series.quantile(0.95)),
    }


def compute_psi(reference: Iterable[float], recent: Iterable[float], buckets: int = 10) -> float:
    ref = pd.Series(reference).dropna().astype(float)
    cur = pd.Series(recent).dropna().astype(float)
    if ref.empty or cur.empty:
        return 0.0

    quantiles = np.unique(np.quantile(ref, q=np.linspace(0, 1, buckets + 1)))
    if len(quantiles) < 3:
        return 0.0

    ref_bins = pd.cut(ref, bins=quantiles, include_lowest=True)
    cur_bins = pd.cut(cur, bins=quantiles, include_lowest=True)

    ref_dist = ref_bins.value_counts(normalize=True).sort_index()
    cur_dist = cur_bins.value_counts(normalize=True).sort_index()

    all_idx = ref_dist.index.union(cur_dist.index)
    ref_dist = ref_dist.reindex(all_idx, fill_value=1e-6).clip(lower=1e-6)
    cur_dist = cur_dist.reindex(all_idx, fill_value=1e-6).clip(lower=1e-6)

    ratio = (cur_dist / ref_dist).replace([np.inf, -np.inf], 1.0).clip(lower=1e-6)
    psi = ((cur_dist - ref_dist) * np.log(ratio)).sum()
    return float(psi)


def score_recent_period(row: pd.Series, drift_model: Dict[str, Any]) -> Tuple[float, float]:
    center = pd.Series(drift_model["center"])
    mad = pd.Series(drift_model["mad"]).replace(0, np.nan)
    vector = row[FEATURE_COLUMNS].astype(float)
    robust_z = ((vector - center) / mad).abs()
    robust_score = float(robust_z.mean())

    x = ((vector - center) / mad).fillna(0.0).to_numpy(dtype=float)
    inv_cov = np.array(drift_model["inv_cov"], dtype=float)
    mahal = float(np.sqrt(x @ inv_cov @ x.T))
    return robust_score, mahal


def classify_status(warning_breaches: int, critical_breaches: int, consecutive_negative: int, robust_score: float, mahal: float, thresholds: Dict[str, Any], psi: float) -> str:
    ml_red = (
        robust_score >= thresholds["ml_drift_thresholds"]["robust_score_critical"]
        or mahal >= thresholds["ml_drift_thresholds"]["mahalanobis_critical"]
        or psi >= thresholds["ml_drift_thresholds"]["psi_critical"]
    )
    ml_yellow = (
        robust_score >= thresholds["ml_drift_thresholds"]["robust_score_warning"]
        or mahal >= thresholds["ml_drift_thresholds"]["mahalanobis_warning"]
        or psi >= thresholds["ml_drift_thresholds"]["psi_warning"]
    )

    if critical_breaches >= 3 or consecutive_negative >= 3 or ml_red:
        return "RED"
    if warning_breaches >= 2 or consecutive_negative >= 2 or ml_yellow:
        return "YELLOW"
    return "GREEN"


def build_monitor_report(period_df: pd.DataFrame, thresholds: Dict[str, Any], period_name: str) -> pd.DataFrame:
    period_df = add_consecutive_negative_flags(period_df)
    report_rows: List[Dict[str, Any]] = []

    for trader_id, trader_periods in period_df.groupby("trader_id"):
        history = trader_periods.sort_values("close_time").reset_index(drop=True)
        drift_model = fit_simple_drift_model(history)
        for idx, row in history.iterrows():
            rule_block = thresholds["alert_rules"][period_name]
            warning_breaches, critical_breaches, warning_metrics, critical_metrics = count_threshold_breaches(row, rule_block)

            recent_window = history.loc[max(0, idx - 3): idx, "expectancy"]
            ref_window = history.loc[: max(0, idx - 4), "expectancy"]
            psi = compute_psi(ref_window, recent_window)

            robust_score, mahal = score_recent_period(row, drift_model)
            status = classify_status(
                warning_breaches=warning_breaches,
                critical_breaches=critical_breaches,
                consecutive_negative=int(row["consecutive_negative"]),
                robust_score=robust_score,
                mahal=mahal,
                thresholds=thresholds,
                psi=psi,
            )

            report_rows.append(
                {
                    "trader_id": trader_id,
                    "period_start": row["close_time"],
                    "pnl_net": row["pnl_net"],
                    "trades": row["trades"],
                    "win_rate": row["win_rate"],
                    "expectancy": row["expectancy"],
                    "pnl_std": row["pnl_std"],
                    "e_sd": row["e_sd"],
                    "hold_min_median": row["hold_min_median"],
                    "buy_share": row["buy_share"],
                    "volume_mean": row["volume_mean"],
                    "warning_breaches": warning_breaches,
                    "critical_breaches": critical_breaches,
                    "warning_metrics": "|".join(warning_metrics) if warning_metrics else np.nan,
                    "critical_metrics": "|".join(critical_metrics) if critical_metrics else np.nan,
                    "consecutive_negative": int(row["consecutive_negative"]),
                    "robust_score": robust_score,
                    "mahalanobis": mahal,
                    "psi_expectancy": psi,
                    "status": status,
                }
            )

    return pd.DataFrame(report_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate monitoring alerts and simple ML drift signals.")
    parser.add_argument("--config", required=True, help="Path to config_case.json")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    thresholds = load_json(Path(config["monitoring_thresholds_path"]))
    output_dir = Path(config["output_paths"]["monitoring_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        df = load_clean_data(Path(config["input_paths"]["clean_data_csv"]))
        weekly = compute_period_metrics(df, config["monitoring_cadence"]["weekly"])
        monthly = compute_period_metrics(df, config["monitoring_cadence"]["monthly"])
        quarterly = compute_period_metrics(df, config["monitoring_cadence"]["quarterly"])

        weekly_report = build_monitor_report(weekly, thresholds, "weekly")
        monthly_report = build_monitor_report(monthly, thresholds, "monthly")
        quarterly_report = build_monitor_report(quarterly, thresholds, "quarterly")

        weekly_report.to_csv(output_dir / "weekly_monitor_report.csv", index=False)
        monthly_report.to_csv(output_dir / "monthly_monitor_report.csv", index=False)
        quarterly_report.to_csv(output_dir / "quarterly_monitor_report.csv", index=False)
        print(f"Monitoring reports written to {output_dir}")
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"monitoring_engine.py failed: {exc}") from exc


if __name__ == "__main__":
    main()
