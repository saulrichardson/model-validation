# Harborlight Savings - CECL Model Overview (Q1 2026)

**Case slug:** `harborlight_savings_cecl_gap_assessment_q1_2026`  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment  
**Product context:** Consumer and real-estate portfolio reserve process

## 1. Model purpose
The CECL reserve framework estimates lifetime expected credit losses for the consumer and real-estate portfolios and produces allowance outputs by reporting segment for financial reporting.

## 2. Model type and high-level approach
Per the model card summary provided for review, the framework is described as a scenario-conditioned expected loss approach, producing reserve outputs by segment and aggregating to portfolio totals. The model card references a macroeconomic scenario pathway and an explicit reversion to a long-run anchor.

## 3. Forecast and reversion horizon (model card)
**R&S forecast horizon (model card): 6 quarters**  
**Reversion horizon (model card): 2 quarters**

Note: The model card horizon differs from the methodology narrative in the CECL process documentation. The discrepancy is not resolved in the materials provided and is treated as an open gap pending governance evidence of the approved horizon.

## 4. Segmentation and outputs
### 4.1 Output segments observed in reserve outputs
- `residential_mortgage`
- `heloc`
- `cre_investor`
- `commercial_and_industrial`

### 4.2 Documented segments referenced in process documentation
- Residential Mortgage
- HELOC
- CRE Investor
- CRE Owner Occupied
- Commercial and Industrial

Observation (structural): the documented segment set includes **CRE Owner Occupied**, while the supplied output segments do **not** include a corresponding output segment. No mapping table or aggregation logic was provided showing where CRE Owner Occupied is reported.

## 5. Scenario set
The model card references three macroeconomic scenarios:
- Baseline
- Adverse
- Severe

Macro drivers present in supplied paths:
- Unemployment rate
- GDP growth
- House price growth
- CRE price growth
- Prime rate

The supplied scenario paths include 6 quarters (2026Q1-2027Q2). The model card does not clarify whether additional quarters are sourced, repeated, or derived to meet the stated horizon.

## 6. Overlays
Reserve outputs are adjusted via management overlays by output segment. Overlays provided for Q1 2026 readiness review (bps):
- `residential_mortgage`: 12.0
- `heloc`: 16.0
- `cre_investor`: 18.0
- `commercial_and_industrial`: 14.0

Documentation reviewed references a portfolio overlay cap of **6.0 bps**; no approved exception memo was included to explain the difference.

## 7. Implementation and reproducibility (limitations)
A reserve engine implementation, configuration details, input file lineage, and reproducible run package were not included. As a result:
- The review cannot validate calculation correctness, runtime controls, or repeatability.
- The review is limited to consistency and completeness of the documentation package and governance artifacts.
