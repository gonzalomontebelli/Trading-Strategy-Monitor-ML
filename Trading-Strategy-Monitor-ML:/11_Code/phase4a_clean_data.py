from __future__ import annotations

import json
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Tuple

import pandas as pd


CASE_ID = "2026-04_Quantum_US30_SingleTrader"


def parse_decimal_text(value: Any) -> Tuple[Decimal | None, str | None]:
    if pd.isna(value):
        return None, "null_value"
    text = str(value).replace("\u00a0", "").replace(" ", "").strip()
    if text == "":
        return None, "empty_string"
    cleaned = re.sub(r"[^0-9,.\-]", "", text)
    if cleaned == "":
        return None, "no_numeric_payload"
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned and "." not in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned), None
    except InvalidOperation:
        return None, f"invalid_decimal:{cleaned}"


def parse_datetime_text(value: Any) -> Tuple[pd.Timestamp | None, str | None]:
    if pd.isna(value):
        return None, "null_value"
    parsed = pd.to_datetime(str(value), format="%d/%m/%Y %H:%M:%S.%f", errors="coerce")
    if pd.isna(parsed):
        return None, "date_parse_failure"
    return parsed, None


def map_side(value: Any) -> Tuple[str | None, str | None]:
    if pd.isna(value):
        return None, "null_value"
    raw = str(value).strip()
    mapping = {"Buy": "BUY", "Sell": "SELL"}
    if raw not in mapping:
        return None, f"side_outside_domain:{raw}"
    return mapping[raw], None


def normalize_symbol(value: Any) -> Tuple[str | None, str | None]:
    if pd.isna(value):
        return None, "null_value"
    symbol = str(value).strip().upper()
    if symbol == "":
        return None, "empty_symbol"
    return symbol, None


if __name__ == "__main__":
    print("Script de referencia de Fase 4A. Los outputs oficiales están en 05_Clean/.")
