Black-box behavioral review skill for opaque vendor or runtime-only packages.

Goal:
- Execute what can be executed without pretending conceptual visibility exists.
- Emphasize runtime behavior, output distributions, segment observations, and reason-code coverage boundaries.

Focus areas:
- Smoke-test runtime execution.
- Profile score and decision distributions.
- Review segment behavior and reason-code outputs.
- State conceptual-review limitations explicitly.

Execution posture:
- Do not overclaim conceptual soundness from runtime behavior alone.
- Treat missing documentation as a coverage boundary, not as an invitation to speculate.
- If a gateway sidecar benchmark materially improves the review, use it as auxiliary evidence rather than as the primary workflow.
