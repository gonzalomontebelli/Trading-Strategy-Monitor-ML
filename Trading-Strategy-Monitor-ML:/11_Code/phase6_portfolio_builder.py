from __future__ import annotations

from pathlib import Path
import pandas as pd


def load_inputs(base_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    ranking = pd.read_csv(base_path / "ranking_cuantitativo.csv")
    metrics = pd.read_csv(base_path / "trader_metrics.csv")
    return ranking, metrics


def build_selected_traders(case_id: str, ranking: pd.DataFrame, metrics: pd.DataFrame) -> pd.DataFrame:
    r = ranking.iloc[0]
    m = metrics.iloc[0]
    return pd.DataFrame([{
        "case_id": case_id,
        "trader_id": m["trader_id"],
        "selection_status": "SELECTED_WITH_RESERVATIONS",
        "copy_decision": "COPIAR_CON_RESERVAS",
        "portfolio_role": "CORE_SINGLE_MANAGER",
        "universe_context": "single_trader_universe",
        "selection_rank": int(r["rank_quantitativo"]),
        "inclusion_reason": "Único trader elegible del universo actual; métricas positivas y consistencia defendible, pero sin comparables internos.",
        "primary_risk": "concentracion_total_en_un_solo_trader_y_un_solo_simbolo",
        "quality_flag_profile": m["quality_flag_profile"],
        "quality_warning_profile": m["quality_warning_profile"],
    }])


def build_portfolio_weights(case_id: str, metrics: pd.DataFrame) -> pd.DataFrame:
    m = metrics.iloc[0]
    return pd.DataFrame([{
        "case_id": case_id,
        "trader_id": m["trader_id"],
        "target_weight_pct": 100.0,
        "weight_basis": "single_trader_universe_only",
        "portfolio_type": "single_manager_pilot_portfolio",
        "implementation_note": "El 100% corresponde a la composición interna de la cartera; la activación en capital real debe ser escalonada por validación operativa.",
    }])


def main() -> None:
    # Paths relative to project root — adjust as needed
    base_path = Path(".")
    case_id = "2026-04_Quantum_US30_SingleTrader"
    portfolio_dir = base_path / "07_Portfolio"
    portfolio_dir.mkdir(parents=True, exist_ok=True)

    ranking, metrics = load_inputs(base_path / "06_Analysis")
    selected_traders = build_selected_traders(case_id, ranking, metrics)
    portfolio_weights = build_portfolio_weights(case_id, metrics)

    selected_traders.to_csv(portfolio_dir / "selected_traders.csv", index=False)
    portfolio_weights.to_csv(portfolio_dir / "portfolio_weights.csv", index=False)


if __name__ == "__main__":
    main()
