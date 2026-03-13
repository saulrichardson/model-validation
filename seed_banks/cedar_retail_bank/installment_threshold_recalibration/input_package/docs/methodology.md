# Methodology: Installment Threshold Recalibration

## Overview

This document outlines the model methodology for the Cedar Retail Bank Point-of-Sale Installment Lending scorecard, supporting the full revalidation necessitated by the recent material change in risk threshold policy as part of the candidate (2025.2) release.

## Model Versions

- Champion: v2024.4
- Candidate: v2025.2

## Sample

- Population: Point-of-sale installment applicants (Jan–Apr 2024)
- Development sample size: 1,600 loans
- Randomization Seed: 77

## Model Formulation

Logistic regression with the following features:

| Variable           | Champion Coefficient | Candidate Coefficient |
|--------------------|---------------------|----------------------|
| bureau_headroom    | 1.22                | 1.20                 |
| dti_ratio          | 1.26                | 1.31                 |
| utilization_rate   | 0.70                | 0.73                 |
| delinquency_12m    | 0.49                | 0.52                 |
| inquiries_6m       | 0.15                | 0.14                 |
| thin_file_flag     | 0.29                | 0.51                 |
| short_tenure       | 0.17                | 0.20                 |
| low_cash_buffer    | —                   | 0.54                 |

Intercepts:
- Champion: -2.38
- Candidate: -2.21

## Threshold Policy

The recalibration sets a new application approval probability threshold. All applicants scoring above threshold are approved, below are declined.

- Old threshold (documented): 0.40
- Implemented threshold: 0.39
- Evaluated Range: 0.35, 0.37, 0.39, 0.41, 0.43

**Note:** Documentation references the previously used 0.40 threshold; however, the candidate package implements 0.39 as the cutoff, matching the revised business targets. 

## Reason-Code Treatment

Applicants receive reason codes at decline, corresponding to their most adverse model drivers (see reason code table under 'Change Request'). The mapping does not account for new feature _low_cash_buffer_, which, while included in the candidate, is not presently mapped for reason code generation.

## Validation Approach

- Out-of-time back-testing of champion vs candidate
- Stability analysis for new and existing features
- Operating point sensitivity reviewed for booking vs loss forecasting

## Limitations

- The candidate model introduces a new feature (low_cash_buffer) without a mapped output reason code, to be addressed in future refresh cycles.
- Some operational and governance documentation references stale threshold policy.
