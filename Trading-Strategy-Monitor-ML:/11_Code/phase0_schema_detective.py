from __future__ import annotations

import csv
import io
import json
import shutil
from pathlib import Path

import pandas as pd


def clean_money(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.replace("\xa0", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce",
    )


def main() -> None:
    # Paths relative to project root — adjust as needed
    root = Path(".")
    raw_dir = root / "01_Raw"
    audit_dir = root / "02_Audit"

    raw_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    # Update these paths to point to your actual input files in 01_Raw/
    src_csv = next(raw_dir.glob("*.csv"), None)
    src_log = next(raw_dir.glob("*.txt"), None)
    if src_csv is None or src_log is None:
        raise FileNotFoundError("Expected .csv and .txt files in 01_Raw/. Check the folder.")

    shutil.copy2(src_csv, raw_dir / src_csv.name)
    shutil.copy2(src_log, raw_dir / src_log.name)

    df = pd.read_csv(src_csv)
    entry = pd.to_datetime(df["Entry time (UTC+1)"], format="%d/%m/%Y %H:%M:%S.%f", errors="coerce")
    close = pd.to_datetime(df["Closing time (UTC+1)"], format="%d/%m/%Y %H:%M:%S.%f", errors="coerce")

    patterns = {"OPEN_CSV": "[OPEN_CSV]", "CLOSE_CSV": "[CLOSE_CSV]", "DAY_SUMMARY": "[DAY_SUMMARY]"}
    headers: dict[str, str] = {}
    counts = {k: 0 for k in patterns}

    with open(src_log, "r", encoding="utf-8-sig", errors="replace") as f:
        for line in f:
            for key, token in patterns.items():
                if token in line:
                    counts[key] += 1
                    payload = line.split("|")[-1].strip()
                    if "event," in payload and key not in headers:
                        headers[key] = payload
                    break

    config = {
        "case_id": "2026-04_Quantum_US30_SingleTrader",
        "phase": "FASE 0 - SCHEMA DETECTIVE",
        "primary_table": {
            "file_name": src_csv.name,
            "grain": "1 row = 1 closed trade",
            "row_count": int(df.shape[0]),
            "column_count": int(df.shape[1]),
            "time_span": {
                "entry_min": entry.min().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "entry_max": entry.max().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "close_min": close.min().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "close_max": close.max().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            },
        },
        "secondary_embedded_tables": {
            key: {
                "data_rows_detected": counts[key] - 1,
                "columns": next(csv.reader(io.StringIO(header))),
            }
            for key, header in headers.items()
        },
        "critical_fields_detected": {
            "pnl_fields": ["Net $", "Gross $", "Pips", "Balance $"],
            "time_fields": ["Entry time (UTC+1)", "Closing time (UTC+1)"],
            "size_fields": ["Quantity", "Volume"],
            "instrument_field": ["Symbol"],
            "trade_identifier_field": ["ID"],
            "trader_field": [],
        },
    }

    (audit_dir / "config_block_phase0.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
