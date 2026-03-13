# Model Validation

Codex-first model validation workbench for local bank-style demo workflows.

This repo is the main product repo. The parent repo owns:

- the TypeScript Codex SDK orchestration layer in `scripts/codex/`
- reusable workflow instructions in `skills/`
- synthetic bank packages in `demo_cases/`
- the Python bridge, tools, storage, and reporting logic in `src/model_validation/`

`agent-gateway/` remains a utility submodule. It is not the workflow engine. Its role is bounded sidecar analysis for cases where Codex wants to hand large document payloads to a fixed-prompt gateway task.

## Demo Workflows

The repo is currently organized around two primary workflows:

1. Material-change revalidation
   Codex inspects a rich internal package, resolves a broad playbook, reruns baseline and candidate models, executes sensitivity and threshold analysis, reviews reason-code behavior, and drafts a revalidation memo.

2. Documentation-led readiness review
   Codex inspects a non-runnable evidence pack, resolves the supported subset of the playbook, benchmarks the documentation pack, identifies consistency and evidence gaps, and drafts a readiness memo.

## Architecture

- `scripts/codex/`
  TypeScript runner using `@openai/codex-sdk` for discovery, playbook resolution, execution, and reporting stages.
- `skills/`
  Repo-local instruction bundles and resource files that guide stage behavior.
- `src/model_validation/`
  Python bridge and deterministic local tools used by Codex during execution.
- `demo_cases/`
  Seeded bank-style artifacts for local demonstrations.
- `.workbench/`
  Local case storage, generated outputs, and demo traces. Ignored by git.

## Quick Start

1. Install Python dependencies with `poetry install`.
2. Install the Codex runner dependencies with `npm --prefix scripts/codex install`.
3. Copy `codex.config.example.toml` to `codex.config.toml` if you want custom SDK thread settings.
4. Add `OPENAI_API_KEY` to the repo-root `.env`.
5. Regenerate demo cases with `poetry run python scripts/generate_demo_cases.py`.
6. Smoke-test the runtime with `poetry run workbench-demo preflight`.

## Useful Commands

- `poetry run workbench-demo list-demos`
- `poetry run workbench-demo run --demo-id material_change_full --stop-after playbook`
- `poetry run workbench-demo run --demo-id material_change_full`
- `poetry run workbench-demo run --demo-id documentation_readiness`
- `poetry run workbench-demo summarize --case-id <case_id>`

## Notes

- The demo is optimized for local inspection, not deployment polish.
- Codex is the planner and executor.
- The gateway is a utility sidecar for fixed-prompt large-document analysis.
