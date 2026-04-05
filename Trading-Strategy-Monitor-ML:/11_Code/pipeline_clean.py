from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file with basic error handling."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(f"Could not load config JSON: {path}") from exc


def validate_required_columns(df: pd.DataFrame, required: List[str], dataset_name: str) -> None:
    """Fail fast when an input dataset does not respect the expected contract."""
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"{dataset_name} is missing required columns: {missing}")


def coerce_datetime_columns(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Parse datetime fields and collect warnings for rows that fail conversion."""
    warnings: List[str] = []
    out = df.copy()
    for column in columns:
        if column not in out.columns:
            continue
        parsed = pd.to_datetime(out[column], errors="coerce")
        failed = int(parsed.isna().sum() - out[column].isna().sum())
        if failed > 0:
            warnings.append(f"{column}: {failed} rows failed datetime parsing")
        out[column] = parsed
    return out, warnings


def coerce_numeric_columns(df: pd.DataFrame, columns: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    """Parse numeric fields and collect warnings for rows that fail conversion."""
    warnings: List[str] = []
    out = df.copy()
    for column in columns:
        if column not in out.columns:
            continue
        parsed = pd.to_numeric(out[column], errors="coerce")
        failed = int(parsed.isna().sum() - out[column].isna().sum())
        if failed > 0:
            warnings.append(f"{column}: {failed} rows failed numeric parsing")
        out[column] = parsed
    return out, warnings


def assign_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply lightweight row-level validation on a canonical clean dataset.

    This function does not invent data. It only tags rows based on observable issues:
    - missing critical fields
    - close_time before open_time
    - non-positive volume
    """
    out = df.copy()
    existing_quality = out["quality_flag"].astype(str) if "quality_flag" in out.columns else pd.Series("OK", index=out.index)
    quality_notes = pd.Series("", index=out.index, dtype="object")

    critical_fields = ["trader_id", "symbol", "side", "open_time", "close_time", "volume", "entry_price", "exit_price", "pnl_net", "trade_id"]
    missing_mask = out[critical_fields].isna().any(axis=1)
    quality_notes.loc[missing_mask] = quality_notes.loc[missing_mask] + "|missing_critical_field"

    time_mask = out["close_time"] < out["open_time"]
    quality_notes.loc[time_mask] = quality_notes.loc[time_mask] + "|close_before_open"

    volume_mask = out["volume"] <= 0
    quality_notes.loc[volume_mask] = quality_notes.loc[volume_mask] + "|non_positive_volume"

    computed_flag = pd.Series("OK", index=out.index, dtype="object")
    computed_flag.loc[missing_mask | time_mask | volume_mask] = "ERROR"

    if "quality_flag" in out.columns:
        # Keep the worst flag between upstream and current validation.
        computed_flag = np.where((existing_quality == "ERROR") | (computed_flag == "ERROR"), "ERROR", existing_quality)
        computed_flag = pd.Series(computed_flag, index=out.index, dtype="object")

    out["quality_flag"] = computed_flag
    notes = quality_notes.str.strip("|")
    out["validation_notes"] = notes.mask(notes.eq(""), np.nan)
    return out


def build_quality_log(df: pd.DataFrame, conversion_warnings: List[str]) -> pd.DataFrame:
    """Generate a compact quality log that keeps traceability."""
    rows = []
    for warning in conversion_warnings:
        rows.append({"event_type": "conversion_warning", "detail": warning})
    if "validation_notes" in df.columns:
        flagged = df["validation_notes"].dropna()
        for note, count in flagged.value_counts().items():
            rows.append({"event_type": "row_validation", "detail": f"{note} | count={int(count)}"})
    if not rows:
        rows.append({"event_type": "info", "detail": "No additional validation warnings generated."})
    return pd.DataFrame(rows)


def save_outputs(df: pd.DataFrame, quality_log: pd.DataFrame, output_dir: Path) -> None:
    """Persist clean dataset and quality log to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_dir / "clean_data_validated.csv", index=False)
    quality_log.to_csv(output_dir / "clean_data_quality_log.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and re-export a canonical clean dataset.")
    parser.add_argument("--config", required=True, help="Path to config_case.json")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = load_json(config_path)

    input_path = Path(config["input_paths"]["clean_data_csv"])
    output_dir = Path(config["output_paths"]["monitoring_dir"])

    try:
        df = pd.read_csv(input_path)
        validate_required_columns(df, config["required_columns"]["clean_data"], "clean_data")
        df, dt_warnings = coerce_datetime_columns(df, ["open_time", "close_time"])
        df, num_warnings = coerce_numeric_columns(df, ["volume", "entry_price", "exit_price", "pnl_net", "trade_id"])
        validated = assign_quality_flags(df)
        quality_log = build_quality_log(validated, dt_warnings + num_warnings)
        save_outputs(validated, quality_log, output_dir)
        print(f"Validation completed. Files written to {output_dir}")
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"pipeline_clean.py failed: {exc}") from exc


if __name__ == "__main__":
    main()
