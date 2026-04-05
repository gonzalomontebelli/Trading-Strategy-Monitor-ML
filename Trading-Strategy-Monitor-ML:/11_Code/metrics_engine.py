from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_required_columns(df: pd.DataFrame, required: List[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def load_clean_data(path: Path, required: List[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_required_columns(df, required)
    df["open_time"] = pd.to_datetime(df["open_time"], errors="coerce")
    df["close_time"] = pd.to_datetime(df["close_time"], errors="coerce")
    df["holding_minutes"] = (df["close_time"] - df["open_time"]).dt.total_seconds() / 60.0
    df["close_date"] = df["close_time"].dt.floor("D")
    df["buy_flag"] = (df["side"].astype(str).str.upper() == "BUY").astype(int)
    accepted_flags = {"OK", "WARN"}
    if "quality_flag" in df.columns:
        df = df[df["quality_flag"].isin(accepted_flags)].copy()
    return df


def compute_trade_level_metrics(group: pd.DataFrame) -> Dict[str, Any]:
    pnl = group["pnl_net"].astype(float)
    trade_std = float(pnl.std(ddof=1)) if len(pnl) > 1 else np.nan
    equity = pnl.cumsum()
    drawdown = equity - equity.cummax()
    wins = pnl[pnl > 0]
    losses = pnl[pnl < 0]

    return {
        "trader_id": str(group["trader_id"].iloc[0]),
        "n_trades": int(len(group)),
        "n_active_days": int(group["close_date"].nunique()),
        "date_start": str(group["close_time"].min()),
        "date_end": str(group["close_time"].max()),
        "win_rate": float((pnl > 0).mean()),
        "expectancy": float(pnl.mean()),
        "trade_std": trade_std,
        "e_sd": float(pnl.mean() / trade_std) if trade_std and not np.isnan(trade_std) else np.nan,
        "sqn": float((pnl.mean() / trade_std) * math.sqrt(len(pnl))) if trade_std and not np.isnan(trade_std) else np.nan,
        "profit_factor": float(wins.sum() / abs(losses.sum())) if len(losses) > 0 else np.nan,
        "avg_win": float(wins.mean()) if len(wins) > 0 else np.nan,
        "avg_loss_abs": float(abs(losses.mean())) if len(losses) > 0 else np.nan,
        "max_single_win": float(pnl.max()),
        "max_single_loss": float(pnl.min()),
        "max_drawdown_abs_closed_pnl": float(drawdown.min()),
        "holding_min_mean": float(group["holding_minutes"].mean()),
        "holding_min_median": float(group["holding_minutes"].median()),
        "buy_share": float(group["buy_flag"].mean()),
        "volume_mean": float(group["volume"].mean()),
    }


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


def save_outputs(output_dir: Path, trader_metrics: pd.DataFrame, daily_df: pd.DataFrame, weekly_df: pd.DataFrame, monthly_df: pd.DataFrame, quarterly_df: pd.DataFrame) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    trader_metrics.to_csv(output_dir / "trader_metrics_baseline.csv", index=False)
    daily_df.to_csv(output_dir / "daily_metrics.csv", index=False)
    weekly_df.to_csv(output_dir / "weekly_metrics.csv", index=False)
    monthly_df.to_csv(output_dir / "monthly_metrics.csv", index=False)
    quarterly_df.to_csv(output_dir / "quarterly_metrics.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute trade, daily and period metrics for monitoring.")
    parser.add_argument("--config", required=True, help="Path to config_case.json")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    output_dir = Path(config["output_paths"]["monitoring_dir"])

    try:
        df = load_clean_data(Path(config["input_paths"]["clean_data_csv"]), config["required_columns"]["clean_data"])

        trader_metrics = pd.DataFrame(
            [compute_trade_level_metrics(group.sort_values("close_time")) for _, group in df.groupby("trader_id", sort=False)]
        )

        daily_df = (
            df.groupby(["trader_id", "close_date"], as_index=False)
            .agg(
                pnl_net=("pnl_net", "sum"),
                trades=("pnl_net", "count"),
                win_rate=("pnl_net", lambda s: float((s > 0).mean())),
                expectancy=("pnl_net", "mean"),
                volume_sum=("volume", "sum"),
                hold_min_median=("holding_minutes", "median"),
            )
        )

        weekly_df = compute_period_metrics(df, config["monitoring_cadence"]["weekly"])
        monthly_df = compute_period_metrics(df, config["monitoring_cadence"]["monthly"])
        quarterly_df = compute_period_metrics(df, config["monitoring_cadence"]["quarterly"])

        save_outputs(output_dir, trader_metrics, daily_df, weekly_df, monthly_df, quarterly_df)
        print(f"Metrics written to {output_dir}")
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"metrics_engine.py failed: {exc}") from exc


if __name__ == "__main__":
    main()
