from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def main(base_path: str = ".") -> None:
    base = Path(base_path)

    canonical_map_path = base / "canonical_map.json"
    detected_columns_path = base / "detected_columns.csv"
    field_mapping_path = base / "field_mapping.csv"

    with canonical_map_path.open("r", encoding="utf-8") as f:
        canonical_map = json.load(f)

    detected = pd.read_csv(detected_columns_path)
    field_mapping = pd.read_csv(field_mapping_path)

    detected_columns = detected["column_name"].tolist()
    canonical_minimum = canonical_map["canonical_schema_minimum"]
    field_mapping_minimum = field_mapping.loc[
        field_mapping["mapping_scope"] == "canonical_minimum", "canonical_field"
    ].tolist()

    required_sources = []
    missing_source_columns = []

    for field in canonical_minimum:
        spec = canonical_map["field_map"][field]
        source_column = spec.get("source_column")
        if source_column is None:
            continue
        required_sources.append(source_column)
        if source_column not in detected_columns:
            missing_source_columns.append(source_column)

    field_mapping_fields = set(field_mapping["canonical_field"].tolist())
    canonical_map_fields = set(canonical_map["field_map"].keys()) | set(
        canonical_map["support_field_map"].keys()
    )

    missing_in_field_mapping = sorted(canonical_map_fields - field_mapping_fields)
    extra_in_field_mapping = sorted(field_mapping_fields - canonical_map_fields)

    print("canon_min_match:", canonical_minimum == field_mapping_minimum)
    print("missing_source_columns:", missing_source_columns)
    print("missing_in_field_mapping:", missing_in_field_mapping)
    print("extra_in_field_mapping:", extra_in_field_mapping)
    print("required_sources:", required_sources)


if __name__ == "__main__":
    main()
