from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def validate_required_columns(df: pd.DataFrame, required: List[str], dataset_name: str) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{dataset_name} is missing required columns: {missing}")


def load_clean_data(path: Path, required: List[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_required_columns(df, required, "clean_data")
    df["close_time"] = pd.to_datetime(df["close_time"], errors="coerce")
    df["close_date"] = df["close_time"].dt.floor("D")
    if "quality_flag" in df.columns:
        df = df[df["quality_flag"].isin(["OK", "WARN"])].copy()
    return df


def load_selected_traders(path: Path, required: List[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_required_columns(df, required, "selected_traders")
    return df


def load_weights(path: Path, required: List[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    validate_required_columns(df, required, "portfolio_weights")
    return df


def apply_weights(clean_df: pd.DataFrame, selected_df: pd.DataFrame, weights_df: pd.DataFrame) -> pd.DataFrame:
    active_traders = set(selected_df["trader_id"].astype(str))
    weighted = clean_df[clean_df["trader_id"].astype(str).isin(active_traders)].copy()
    weight_map = dict(zip(weights_df["trader_id"].astype(str), weights_df["target_weight_pct"].astype(float) / 100.0))
    weighted["weight"] = weighted["trader_id"].astype(str).map(weight_map)
    if weighted["weight"].isna().any():
        raise ValueError("Some selected traders do not have portfolio weights.")
    weighted["weighted_pnl"] = weighted["pnl_net"].astype(float) * weighted["weight"].astype(float)
    weighted = weighted.sort_values("close_time").reset_index(drop=True)
    return weighted


def build_portfolio_curves(weighted_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    trade_curve = weighted_df[["trader_id", "close_time", "close_date", "weight", "pnl_net", "weighted_pnl"]].copy()
    trade_curve["equity"] = trade_curve["weighted_pnl"].cumsum()
    trade_curve["drawdown"] = trade_curve["equity"] - trade_curve["equity"].cummax()

    daily_curve = (
        weighted_df.groupby("close_date", as_index=False)
        .agg(weighted_pnl=("weighted_pnl", "sum"))
        .sort_values("close_date")
    )
    daily_curve["equity"] = daily_curve["weighted_pnl"].cumsum()
    daily_curve["drawdown"] = daily_curve["equity"] - daily_curve["equity"].cummax()
    return {"trade_curve": trade_curve, "daily_curve": daily_curve}


def compute_portfolio_summary(weighted_df: pd.DataFrame, curves: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    return {
        "selected_traders_count": int(weighted_df["trader_id"].nunique()),
        "effective_weight_sum": float(weighted_df[["trader_id", "weight"]].drop_duplicates()["weight"].sum()),
        "number_of_trades": int(len(weighted_df)),
        "number_of_days": int(curves["daily_curve"]["close_date"].nunique()),
        "total_pnl": float(weighted_df["weighted_pnl"].sum()),
        "max_drawdown_trade_level": float(curves["trade_curve"]["drawdown"].min()),
        "max_drawdown_daily_level": float(curves["daily_curve"]["drawdown"].min()),
    }


def compute_correlation(weighted_df: pd.DataFrame) -> pd.DataFrame:
    daily_pivot = (
        weighted_df.groupby(["close_date", "trader_id"], as_index=False)["weighted_pnl"].sum()
        .pivot(index="close_date", columns="trader_id", values="weighted_pnl")
        .fillna(0.0)
    )
    if daily_pivot.shape[1] < 2:
        return pd.DataFrame()
    return daily_pivot.corr()


def save_outputs(output_dir: Path, curves: Dict[str, pd.DataFrame], summary: Dict[str, Any], corr_df: pd.DataFrame) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    curves["trade_curve"].to_csv(output_dir / "portfolio_trade_curve.csv", index=False)
    curves["daily_curve"].to_csv(output_dir / "portfolio_daily_curve.csv", index=False)
    with (output_dir / "portfolio_summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    if not corr_df.empty:
        corr_df.to_csv(output_dir / "portfolio_correlation.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest a weighted portfolio of selected traders.")
    parser.add_argument("--config", required=True, help="Path to config_case.json")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    output_dir = Path(config["output_paths"]["monitoring_dir"])

    try:
        clean_df = load_clean_data(Path(config["input_paths"]["clean_data_csv"]), config["required_columns"]["clean_data"])
        selected_df = load_selected_traders(Path(config["input_paths"]["selected_traders_csv"]), config["required_columns"]["selected_traders"])
        weights_df = load_weights(Path(config["input_paths"]["portfolio_weights_csv"]), config["required_columns"]["portfolio_weights"])

        weighted_df = apply_weights(clean_df, selected_df, weights_df)
        curves = build_portfolio_curves(weighted_df)
        summary = compute_portfolio_summary(weighted_df, curves)
        corr_df = compute_correlation(weighted_df)

        save_outputs(output_dir, curves, summary, corr_df)
        print(f"Portfolio backtest written to {output_dir}")
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"portfolio_engine.py failed: {exc}") from exc


if __name__ == "__main__":
    main()
