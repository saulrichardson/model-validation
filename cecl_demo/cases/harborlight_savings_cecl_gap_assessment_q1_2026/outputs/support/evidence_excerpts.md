# Evidence Excerpts: Q1 2026 CECL Readiness Gap Assessment

The excerpts below are short raw snippets from uploaded materials or generated review artifacts.

## [BANK INPUT] `docs/methodology.md`
Documented forecast, reversion, segmentation, and missing-runtime boundary used in the gap assessment.

```text
# CECL Methodology

The documented CECL process for Harborlight Savings describes a 8-quarter reasonable-and-supportable period with 4 reversion quarters. Documentation states the reserve process covers the following segments:

- Residential Mortgage
- HELOC
- CRE Investor
- CRE Owner Occupied
- Commercial and Industrial
```

## [BANK INPUT] `docs/scenario_assumptions.md`
Numeric scenario horizon and narrative-alignment discussion showing the mismatch between documented and provided scenario depth.

```text
# Scenario Assumptions

Severe is described as a uniformly harsher path than adverse across the full review horizon. Management expects house prices and unemployment to remain materially worse under severe in every quarter reviewed by governance.
```

## [BANK INPUT] `docs/overlay_memo.md`
Overlay cap language and segment overlay values that Codex challenged against the provided reserve bridge.

```text
# Overlay Memo

Qualitative overlay is described as modest and capped at 6.0 bps, pending additional governance evidence.
```

## [BANK INPUT] `outputs/provided_overlay_bridge.csv + outputs/provided_segment_reserves.csv`
Bank-supplied output snapshots used for the documentation-led reconciliation work.

```text
[provided_overlay_bridge.csv]
segment_id,documented_cap_bps,provided_overlay_bps
residential_mortgage,6.0,12.0
heloc,6.0,16.0
cre_investor,6.0,18.0
commercial_and_industrial,6.0,14.0

[provided_segment_reserves.csv]
segment_id,scenario_name,reserve_amount
residential_mortgage,baseline,8420000.0
residential_mortgage,adverse,11300000.0
residential_mortgage,severe,10980000.0
heloc,baseline,5180000.0
heloc,adverse,6450000.0
heloc,severe,6430000.0
cre_investor,baseline,11900000.0
cre_investor,adverse,17120000.0
cre_investor,severe,17880000.0
commercial_and_industrial,baseline,12920000.0
commercial_and_industrial,adverse,17310000.0
commercial_and_industrial,severe,17720000.0
```

## [CODEX OUTPUT] `outputs/support/coverage_statement.md`
Codex-generated coverage boundary showing which procedures were supported and which were blocked.

```text
# Coverage Statement

The package contains useful CECL documentation and output snapshots, but it does not contain the implementation artifacts needed for execution-based validation.

## Supported Work
- Discovery and evidence sufficiency review
- Scenario-definition consistency review
- Provided-output reconciliation
- Overlay documentation review

## Blocked Work
- Baseline reproduction
- Scenario reruns against a reserve engine
- Sensitivity testing on implementation assumptions
- Model-code review
```

## [CODEX OUTPUT] `outputs/support/findings_register.json`
Codex-generated findings register capturing the primary documentation and evidence gaps.

```text
{
  "findings": [
    {
      "severity": "high",
      "title": "Execution-based review is blocked by missing reserve engine and lineage evidence",
      "summary": "The package includes prior outputs and narrative materials, but no reserve engine, reproducibility script, or lineaged runbook sufficient for execution-based review.",
      "evidence": [
        "docs/evidence_request_log.md",
        "docs/gap_tracker.md",
        "outputs/provided_reserve_summary.csv"
      ]
    },
    {
      "severity": "high",
      "title": "Scenario narrative is not fully aligned to the supplied scenario tables",
      "summary": "The severe scenario narrative describes a uniformly harsher path, but the supplied numeric scenarios show 4 quarter(s) where severe house-price growth is less severe than adverse.",
      "evidence": [
        "docs/scenario_assumptions.md",
        "scenarios/adverse.csv",
        "scenarios/severe.csv"
      ]
    },
    {
      "severity": "medium",
      "title": "Documented segment structure does not reconcile to the provided reserve outputs",
      "summary": "Documentation describes 5 segments, while the provided reserve outputs reconcile to 4 output segments.",
      "evidence": [
        "docs/methodology.md",
        "docs/model_overview.md",
        "outputs/provided_segment_reserves.csv"
      ]
    },
    {
      "severity": "medium",
      "title": "Overlay documentation understates the magnitude implied by the provided reserve bridge",
      "summary": "The overlay memo frames qualitative adjustment as capped at 6.0 bps, but the provided bridge shows up to 18.0 bps.",
      "evidence": [
        "docs/overlay_memo.md",
        "outputs/provided_overlay_bridge.csv"
      ]
    }
  ]
}
```
