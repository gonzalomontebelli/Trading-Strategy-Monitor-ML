from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


def clean_money(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype(str)
        .str.replace("\xa0", "", regex=False)
        .str.replace(",", "", regex=False),
        errors="coerce",
    )


def extract_num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.extract(r"([0-9]*\.?[0-9]+)")[0], errors="coerce")


def main() -> None:
    # Paths relative to project root — adjust as needed
    root = Path(".")
    audit_dir = root / "02_Audit"
    audit_dir.mkdir(parents=True, exist_ok=True)

    csv_path = next((root / "01_Raw").glob("*.csv"), None)
    config_path = audit_dir / "config_block_phase0.json"
    if csv_path is None:
        raise FileNotFoundError("Expected a .csv file in 01_Raw/. Check the folder.")

    df = pd.read_csv(csv_path)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    entry = pd.to_datetime(df["Entry time (UTC+1)"], format="%d/%m/%Y %H:%M:%S.%f", errors="coerce")
    close = pd.to_datetime(df["Closing time (UTC+1)"], format="%d/%m/%Y %H:%M:%S.%f", errors="coerce")
    entry_price = pd.to_numeric(df["Entry price"], errors="coerce")
    close_price = pd.to_numeric(df["Closing price"], errors="coerce")
    net = clean_money(df["Net $"])
    gross = clean_money(df["Gross $"])
    balance = clean_money(df["Balance $"])
    pips = pd.to_numeric(df["Pips"], errors="coerce")
    commission = pd.to_numeric(df["Broker commission"], errors="coerce")
    swaps = pd.to_numeric(df["Swaps"], errors="coerce")
    ids = pd.to_numeric(df["ID"], errors="coerce")
    qty_num = extract_num(df["Quantity"])
    vol_num = extract_num(df["Volume"])

    critical_fields = set(
        config["critical_fields_detected"].get("pnl_fields", [])
        + config["critical_fields_detected"].get("time_fields", [])
        + config["critical_fields_detected"].get("size_fields", [])
        + config["critical_fields_detected"].get("instrument_field", [])
        + config["critical_fields_detected"].get("trade_identifier_field", [])
    )

    groups = {
        "Label": "identificación",
        "Symbol": "identificación",
        "Type": "identificación",
        "ID": "identificación",
        "Entry time (UTC+1)": "ejecución",
        "Closing time (UTC+1)": "ejecución",
        "Entry price": "ejecución",
        "Closing price": "ejecución",
        "Quantity": "riesgo",
        "Volume": "riesgo",
        "Broker commission": "riesgo",
        "Swaps": "riesgo",
        "Net $": "resultado",
        "Pips": "resultado",
        "Gross $": "resultado",
        "Balance $": "resultado",
    }

    notes = {
        "Quantity": "Columna de tamaño en texto; solapada con Volume.",
        "Volume": "Columna de tamaño en texto; solapada con Quantity.",
        "Net $": "Equivale a Gross $ en este export porque Broker commission y Swaps son 0.",
        "Gross $": "Equivale a Net $ en este export porque Broker commission y Swaps son 0.",
        "Balance $": "Texto con separador NBSP; requiere limpieza antes de casteo numérico.",
        "Entry time (UTC+1)": "Formato validado DD/MM/YYYY HH:MM:SS.mmm; semántica UTC+1 abierta.",
        "Closing time (UTC+1)": "Formato validado DD/MM/YYYY HH:MM:SS.mmm; semántica UTC+1 abierta.",
        "Broker commission": "Todos los valores observados son 0.",
        "Swaps": "Todos los valores observados son 0.",
        "ID": "Único por fila, pero no secuencial continuo.",
    }

    null_counts = {c: int(df[c].isna().sum()) for c in df.columns}
    blank_counts = {c: int((df[c].astype(str).str.strip() == "").sum()) for c in df.columns}

    parser_status = {}
    parse_success_rate = {}
    for c in df.columns:
        if c in ["Entry time (UTC+1)", "Closing time (UTC+1)"]:
            parsed = entry if "Entry" in c else close
            parser_status[c] = "OK" if parsed.notna().all() else "ERROR"
            parse_success_rate[c] = float(parsed.notna().mean())
        elif c in ["Entry price", "Closing price", "Broker commission", "Swaps", "Pips", "ID"]:
            parsed = {
                "Entry price": entry_price,
                "Closing price": close_price,
                "Broker commission": commission,
                "Swaps": swaps,
                "Pips": pips,
                "ID": ids,
            }[c]
            parser_status[c] = "OK" if parsed.notna().all() else "ERROR"
            parse_success_rate[c] = float(parsed.notna().mean())
        elif c in ["Net $", "Gross $", "Balance $"]:
            parsed = {"Net $": net, "Gross $": gross, "Balance $": balance}[c]
            parser_status[c] = "OK" if parsed.notna().all() else "WARN"
            parse_success_rate[c] = float(parsed.notna().mean())
        elif c in ["Quantity", "Volume"]:
            parsed = {"Quantity": qty_num, "Volume": vol_num}[c]
            parser_status[c] = "OK" if parsed.notna().all() else "WARN"
            parse_success_rate[c] = float(parsed.notna().mean())
        else:
            parser_status[c] = "N/A"
            parse_success_rate[c] = np.nan

    detected_columns = pd.DataFrame({
        "column_order": range(1, len(df.columns) + 1),
        "column_name": df.columns,
        "raw_dtype": [str(df[c].dtype) for c in df.columns],
        "semantic_group": [groups[c] for c in df.columns],
        "critical_field": [c in critical_fields for c in df.columns],
        "null_count": [null_counts[c] for c in df.columns],
        "blank_string_count": [blank_counts[c] for c in df.columns],
        "unique_values": [int(df[c].nunique(dropna=False)) for c in df.columns],
        "parser_status": [parser_status[c] for c in df.columns],
        "parse_success_rate": [parse_success_rate[c] for c in df.columns],
        "notes": [notes.get(c, "") for c in df.columns],
    })

    detected_columns.to_csv(audit_dir / "detected_columns.csv", index=False, encoding="utf-8")


if __name__ == "__main__":
    main()
