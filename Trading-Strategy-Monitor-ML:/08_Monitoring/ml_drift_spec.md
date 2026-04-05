# ML Drift Specification

## Objective
Define a simple ML / anomaly detection module to detect operational drift — as a complement to the main quantitative analysis, not a replacement for it.

## Chosen approach
Unsupervised model, reproducible with `pandas` + `numpy` only.

## Weekly feature set
- `expectancy`
- `win_rate`
- `pnl_std`
- `trades`
- `hold_min_median`
- `buy_share`
- `volume_mean`

## Historical baseline used
- Frequency: weekly
- Valid observations: 310
- Robust center: historical median of each feature
- Robust scale: historical MAD of each feature

## Computed signals

### 1. Robust score
Average of absolute robust z-scores per week.
- threshold_warning: 8.44
- threshold_critical: 11.02

### 2. Regularized Mahalanobis distance
Multivariate distance against the baseline cloud.
- threshold_warning: 3.87
- threshold_critical: 5.15

### 3. PSI (Population Stability Index)
Distribution comparison: baseline vs recent window.
- threshold_warning: 0.20
- threshold_critical: 0.35

## Classification logic
- **GREEN**: no score exceeds the warning threshold
- **YELLOW**: at least one score exceeds the warning threshold
- **RED**: at least one score exceeds the critical threshold

## Recommended windows
- Baseline fit: full available history up to the previous cutoff
- Operational scoring: last 4 closed weeks
- Refit: monthly or when a new baseline is approved

## Integration rule
ML drift signal is one input to the composite traffic light engine.
It does not override the statistical rules or hard limit breaches.
