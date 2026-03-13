# Documentation Cross-Check

## Methodology versus implementation
The written methodology and model overview describe a different forecast and reversion treatment than the reserve engine actually uses.

- Evidence: docs/methodology.md, docs/model_overview.md, model/cecl_engine.py
- Documented forecast quarters: 4
- Implemented forecast quarters: 6
- Documented reversion quarters: 4
- Implemented reversion quarters: 2

## Overlay posture
The overlay memo understates the magnitude of the overlay table used in the actual scenario runs.

- Evidence: docs/overlay_memo.md, data/overlay_schedule.csv, outputs/support/sensitivity_results.csv
- Documented overlay cap: 5.0 bps
- Actual overlay cap in schedule: 9.0 bps

## Scenario reasonableness
Overall reserve monotonicity is intact, but one segment behaves oddly under the severe scenario.

- Evidence: outputs/support/segment_reserve_comparison.csv, docs/scenario_assumptions.md, docs/overlay_memo.md
- Overall reserve ordering: baseline 4876841.47, adverse 7132021.97, severe 8287703.47
- Anomaly segment: residential_mortgage
- Adverse versus severe segment delta: -109988.30
