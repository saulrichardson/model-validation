# Oakline Auto Finance — Acquisition Model Methodology Summary

**Model Family:** Indirect Auto Finance Acquisition  
**Vendor:** [Redacted]  
**Sample Size:** 420 loan applications  

## Purpose
This model estimates the likelihood of successful repayment for indirect auto finance applicants, supporting loan acquisition decisions. It is designed for use by Oakline's retail indirect channel, ranking incoming credit applications prior to manual review.

## Data & Features
The scorecard utilizes 11 features, including applicant bureau attributes, vehicle information, and certain dealer-level variables. Vendor did not supply feature derivation code or transformation details.

## Model Approach
Vendor states a binomial logistic regression was fitted to predict 18-month account performance. No details were provided on variable selection, data partitioning, or regularization. No uplift or challenger analysis was included. Methodological limitations and assumptions are not specified.

## Deployment & Use
- The model is accessible only to Oakline via vendor API endpoint.  
- No details on pre/post processing or error handling are provided.  
- No challenger or champion framework was documented.

## Known Gaps
- No model equation, scoring logic, or underlying weights released.  
- No supporting assets, sample code, or data dictionary included.

Refer to the "Evidence Request Log" for further open items.
