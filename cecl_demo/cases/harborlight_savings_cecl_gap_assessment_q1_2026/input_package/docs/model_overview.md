# Model Overview (Model Card Summary)

**Bank:** Harborlight Savings  
**Portfolio:** Q1 2026 CECL Readiness Gap Assessment  
**Model/Process:** Consumer and Real-Estate CECL Reserve Estimation Process  
**Intended Use:** Allowance for Credit Losses (ACL) estimation for financial reporting

## 1. Model Purpose and Outputs
The process produces segment-level ACL estimates and reserve bridge reporting suitable for quarterly financial close. Outputs are reported for the following segments (as reflected in provided reserve outputs):
- `residential_mortgage`
- `heloc`
- `cre_investor`
- `commercial_and_industrial`

> Observation: Output segments do not include a distinct `cre_owner_occupied` output.

## 2. Model Type and Core Method
Per the model card, the process is a macro-conditioned loss estimation framework with segment-level reserve outputs. The model card indicates:
- Scenario-conditioned paths drive forward-looking loss estimates.
- Segment-level overlays may be applied post-model to reflect limitations not captured in the quantitative framework.

## 3. Forecast and Reversion (Model Card)
- **Forecast horizon (reasonable & supportable): 6 quarters**.
- **Reversion period: 2 quarters**.

The model card describes linear reversion to a long-run level following the reasonable & supportable period.

## 4. Scenarios and Variables
The model card references baseline, adverse, and severe scenarios and the use of:
- unemployment rate
- GDP growth
- house price growth
- CRE price growth
- prime rate

Provided scenario data includes quarterly values from **2026Q1 to 2027Q2**.

## 5. Overlay Application (As Reflected in Outputs)
Provided overlay bps by output segment:
- `residential_mortgage`: **12.0 bps**
- `heloc`: **16.0 bps**
- `cre_investor`: **18.0 bps**
- `commercial_and_industrial`: **14.0 bps**

> Observation: These overlay magnitudes exceed the 6.0 bps cap referenced in methodology documentation.

## 6. Operational Dependencies (Not Evidenced)
The model card references routine production activities (data refresh, scenario load, execution, QC checks). However, this package does not include:
- reserve engine run logs
- code versioning / release artifacts
- input/output lineage traces
- reproducible run package (inputs, configuration, outputs)

Accordingly, the review is limited to documentation-level design assessment.
