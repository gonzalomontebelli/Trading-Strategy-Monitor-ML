from __future__ import annotations

from math import sqrt
from pathlib import Path
import argparse

import numpy as np
import pandas as pd


def compute_phase5(clean_path: str, log_path: str, output_dir: str) -> None:
    clean = pd.read_csv(clean_path)
    log = pd.read_csv(log_path)

    for col in ["open_time", "close_time"]:
        clean[col] = pd.to_datetime(clean[col], errors="coerce")

    eligible = clean.loc[clean["quality_flag"].fillna("") != "ERROR"].copy()
    eligible = eligible.sort_values(["trader_id", "close_time", "trade_id"]).reset_index(drop=True)

    input_counts = clean.groupby("trader_id").size().rename("records_input_total")
    excluded_counts = clean.loc[clean["quality_flag"].fillna("") == "ERROR"].groupby("trader_id").size().rename("records_excluded_error")

    rows: list[dict[str, object]] = []
    for trader_id, df in eligible.groupby("trader_id", sort=False):
        pnl = df["pnl_net"].astype(float)
        n = len(df)
        wins = pnl > 0
        losses = pnl < 0

        pnl_mean = pnl.mean()
        pnl_sd = pnl.std(ddof=1) if n > 1 else np.nan
        e_sd = pnl_mean / pnl_sd if pd.notna(pnl_sd) and pnl_sd != 0 else np.nan
        pl_sd = pnl.sum() / pnl_sd if pd.notna(pnl_sd) and pnl_sd != 0 else np.nan
        sqn_approx_pnl = sqrt(n) * e_sd if pd.notna(e_sd) else np.nan

        seq = df.sort_values(["close_time", "trade_id"]).copy()
        equity = seq["balance_after_trade"].astype(float)
        running_peak = equity.cummax()
        dd_abs_series = equity - running_peak
        max_drawdown_abs_approx = float(-dd_abs_series.min()) if len(dd_abs_series) else np.nan
        dd_pct_series = dd_abs_series / running_peak.replace(0, np.nan)
        max_drawdown_pct_approx_pct = float(-dd_pct_series.min() * 100.0) if len(dd_pct_series) else np.nan

        hold_min = (df["close_time"] - df["open_time"]).dt.total_seconds() / 60.0

        rows.append(
            {
                "trader_id": trader_id,
                "records_input_total": int(input_counts.get(trader_id, n)),
                "records_excluded_error": int(excluded_counts.get(trader_id, 0)),
                "analysis_rows_used": int(n),
                "symbols_count": int(df["symbol"].nunique()),
                "symbols_list": "|".join(sorted(df["symbol"].dropna().astype(str).unique())),
                "date_from": df["close_time"].min().isoformat(sep=" ", timespec="milliseconds"),
                "date_to": df["close_time"].max().isoformat(sep=" ", timespec="milliseconds"),
                "n_trades": int(n),
                "winning_trades": int(wins.sum()),
                "losing_trades": int(losses.sum()),
                "breakeven_trades": int((pnl == 0).sum()),
                "total_pnl_net": float(pnl.sum()),
                "expectancy_e": float(pnl_mean),
                "pnl_sd": float(pnl_sd) if pd.notna(pnl_sd) else np.nan,
                "e_sd": float(e_sd) if pd.notna(e_sd) else np.nan,
                "pl_sd": float(pl_sd) if pd.notna(pl_sd) else np.nan,
                "sqn_approx_pnl": float(sqn_approx_pnl) if pd.notna(sqn_approx_pnl) else np.nan,
                "pct_winners_pct": float(wins.mean() * 100.0),
                "avg_win": float(pnl[wins].mean()) if wins.any() else np.nan,
                "avg_loss_abs_proxy_risk": float((-pnl[losses]).mean()) if losses.any() else np.nan,
                "profit_factor": float(pnl[wins].sum() / (-pnl[losses].sum())) if losses.any() and (-pnl[losses].sum()) != 0 else np.nan,
                "max_drawdown_abs_approx": max_drawdown_abs_approx,
                "max_drawdown_pct_approx_pct": max_drawdown_pct_approx_pct,
                "avg_volume": float(df["volume"].mean()),
                "avg_holding_minutes": float(hold_min.mean()),
                "median_holding_minutes": float(hold_min.median()),
                "buy_share_pct": float((df["side"].astype(str).str.upper() == "BUY").mean() * 100.0),
                "sell_share_pct": float((df["side"].astype(str).str.upper() == "SELL").mean() * 100.0),
                "quality_flag_profile": "|".join(sorted(df["quality_flag"].dropna().astype(str).unique())),
                "quality_warning_profile": "|".join(sorted(df["quality_warning_codes"].dropna().astype(str).unique())),
            }
        )

    metrics = pd.DataFrame(rows)

    ranking = metrics.sort_values(
        by=["e_sd", "sqn_approx_pnl", "pl_sd", "pct_winners_pct", "max_drawdown_pct_approx_pct", "avg_loss_abs_proxy_risk"],
        ascending=[False, False, False, False, True, True],
    ).reset_index(drop=True)
    ranking.insert(0, "rank_quantitativo", range(1, len(ranking) + 1))

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(out / "trader_metrics.csv", index=False)
    ranking.to_csv(out / "ranking_cuantitativo.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 5 quantitative analysis for trader copy-trading cases.")
    parser.add_argument("--clean", required=True, help="Path to clean_data.csv")
    parser.add_argument("--log", required=True, help="Path to data_quality_log.csv")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()

    try:
        compute_phase5(clean_path=args.clean, log_path=args.log, output_dir=args.out)
        print("Phase 5 completed.")
    except Exception as exc:
        raise SystemExit(f"Phase 5 failed: {exc}")
