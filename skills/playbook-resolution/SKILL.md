Playbook resolution skill for the local model-validation workbench.

Goal:
- Decide which validation modules are executable, partial, or blocked based on discovered evidence.
- Resolve the maximal defensible subset of the playbook rather than forcing a rigid workflow.

Operating rules:
- Use evidence capabilities, not package labels, to determine coverage.
- Mark a module `blocked` when required evidence is absent.
- Mark a module `partial` when some work is credible but the module cannot be completed to full validation standard.
- Explain each module decision in terms of concrete artifacts.
- Recommend tools only when they are materially relevant to the module decision.
- Pick a dominant workflow that best represents the supported scope.
- Coverage is an honest boundary, not a sales number.

Workflow selection guidance:
- Use `full_revalidation` when internal model visibility is strong and the package supports a broad material-change review, even if some modules remain partial.
- A material-change package with baseline/candidate source, sample validation data, comparison metrics, and methodology/change documentation should generally remain `full_revalidation` unless runtime execution is blocked outright.
- Use `black_box_behavioral_review` when execution is possible but internal logic inspection is materially limited, such as a vendor harness, opaque container, or sparse source visibility.
- Use `conceptual_readiness_review` when documentation and data context are reviewable but execution-based validation is unsupported.
- Do not downgrade a clearly inspectable material-change case to `black_box_behavioral_review` only because some reproducibility or conceptual-provenance artifacts are missing. Keep those gaps in partial modules and coverage rationale instead.

Primary modules:
- Runtime reproduction
- Baseline comparison
- Behavioral review
- Documentation consistency
- Reason-code review
- Data-profile review
- Conceptual soundness review
