# Model Validation

Codex-first model validation workbench for local bank-style workflows.

This repo is the main product repo. The parent repo owns:

- the TypeScript Codex SDK orchestration layer in `scripts/codex/`
- reusable workflow instructions in `skills/`
- bank-style seed bundles in `seed_banks/`
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
- `seed_banks/`
  Canonical bank-style seed bundles, each with `seed.json`, `seed_spec.json`, `input_package/`, and `expected_outputs/`.
- `.workbench/`
  Local case storage, generated outputs, and run traces. Ignored by git.

## Quick Start

1. Install Python dependencies with `poetry install`.
2. Install the Codex runner dependencies with `npm --prefix scripts/codex install`.
3. Copy `codex.config.example.toml` to `codex.config.toml` if you want custom SDK thread settings.
4. Add `OPENAI_API_KEY` to the repo-root `.env`.
5. Start the gateway utility if you want rich authored seed docs:
   `cd agent-gateway && OPENAI_KEY=$OPENAI_API_KEY poetry run python -m gateway --host 127.0.0.1 --port 8000`
6. Regenerate bank seed bundles with `poetry run python scripts/generate_seed_banks.py --authoring-mode gateway`.
7. Smoke-test the runtime with `poetry run workbench-seed preflight`.

## Useful Commands

- `poetry run workbench-seed list-seeds`
- `poetry run workbench-seed run --seed-id atlas_installment_refresh_2025_q1 --stop-after playbook`
- `poetry run workbench-seed run --seed-id cedar_installment_threshold_recalibration`
- `poetry run workbench-seed run --seed-id meridian_heloc_readiness_pack_q1`
- `poetry run workbench-seed run --seed-id oakline_vendor_readiness_packet`
- `poetry run workbench-seed summarize --case-id <case_id>`

## Notes

- The workbench is optimized for local inspection, not deployment polish.
- Codex is the planner and executor.
- The gateway is a utility sidecar for fixed-prompt large-document analysis.
