# Prior Review Note / Follow-up Tracker - Q1 2026 CECL Full Review

## 1. Context
This memo summarizes items carried forward into the Q1 2026 full review cycle and documents status, evidence reviewed, and follow-up actions.

## 2. Items from last cycle (status)
### 2.1 Forecast horizon and reversion alignment (Carry-forward)
- **Topic:** Consistency between documented macro horizon/reversion and the reserve engine implementation.
- **Prior expectation:** Implement **4 quarters** forecast and **4 quarters** linear reversion as documented.
- **Current-cycle observation:** Variance testing indicates the engine output reflects a different horizon/reversion behavior than documentation.
- **Status:** **Open**
- **Action:** Finance and Model Owner to provide parameter configuration evidence (run logs / config files) and reconcile documentation to implementation or implement remediation.
- **Target date:** Prior to Q2 2026 governance cycle.

### 2.2 Scenario ordering reasonableness - Residential Mortgage (New in Q1 2026)
- **Topic:** Under Severe, Residential Mortgage results appear directionally inconsistent versus Adverse.
- **Driver hypothesis:** Severe macro path includes faster post-2026Q4 house price recovery combined with a Severe mortgage overlay that provides relief.
- **Status:** **Open**
- **Action:** Model Owner to provide a driver decomposition showing (i) macro contribution by variable, (ii) overlay contribution, and (iii) any interaction effects from collateral assumptions.
- **Target date:** Next ALCO/ACL governance readout.

### 2.3 Overlay transparency and magnitude communication (Carry-forward)
- **Topic:** Overlay narrative framing vs. realized overlay contribution to total ACL.
- **Observation:** Overlays are described as "modest," but bps schedules indicate meaningful segment add-ons under stress scenarios.
- **Status:** **Open**
- **Action:** Enhance overlay memo to include exposure-weighted impact and reconcile to documented cap language where exceptions occur.
- **Target date:** Q2 2026 close package.

## 3. Evidence reviewed in Q1 2026
- Scenario decks (Baseline/Adverse/Severe) for 2026Q1-2027Q4
- Segment macro sensitivity matrix and base anchors (intercepts, LGD bases)
- Overlay schedule by segment and scenario
- Directionality checks by scenario for segment outputs (summary-level)

## 4. Summary of required remediation deliverables
1. **Horizon/reversion reconciliation memo** (documentation vs. implementation; include evidence and approval path).
2. **Residential Mortgage severe-vs-adverse explanation** supported by decomposition exhibits.
3. **Overlay impact disclosure** (bps, dollar impact, and exposure-weighted totals) and formal exception documentation where applicable.
