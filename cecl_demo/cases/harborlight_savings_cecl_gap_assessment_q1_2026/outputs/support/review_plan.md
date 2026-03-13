# Review Plan: Q1 2026 CECL Readiness Gap Assessment

The review plan below is the work Codex would perform against the discovered package.

## Evidence sufficiency
The first job is to determine whether the package supports a review memo or only a gap assessment.

- Evidence: docs/evidence_request_log.md, docs/gap_tracker.md, outputs/provided_reserve_summary.csv
- Planned checks: runtime blocker assessment, lineage assessment, coverage statement

## Scenario consistency
If scenario narratives do not match the numeric scenario tables, management cannot rely on directional reserve conclusions.

- Evidence: docs/scenario_assumptions.md, scenarios/adverse.csv, scenarios/severe.csv
- Planned checks: narrative versus table comparison, severity ordering review

## Output reconciliation
Even without code, prior reserve outputs can be checked for segment reconciliation and overlay magnitude claims.

- Evidence: outputs/provided_segment_reserves.csv, outputs/provided_overlay_bridge.csv, docs/overlay_memo.md
- Planned checks: segment taxonomy comparison, overlay magnitude comparison
