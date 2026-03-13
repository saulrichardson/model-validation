"""CLI for artifact-first seed orchestration around the Codex SDK workbench."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from .schemas import AgentStage, CaseRecord, SeedBundleDescriptor
from .seed_artifacts import persist_case_seed_summary, persist_sweep_summary
from .service import ValidationWorkbenchService
from .settings import Settings

STAGE_SEQUENCE: list[AgentStage] = [
    AgentStage.DISCOVERY,
    AgentStage.PLAYBOOK,
    AgentStage.EXECUTION,
    AgentStage.REPORT,
]
STAGE_SCRIPT = {
    AgentStage.DISCOVERY: "discover",
    AgentStage.PLAYBOOK: "resolve",
    AgentStage.EXECUTION: "execute",
    AgentStage.REPORT: "report",
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    settings = Settings()
    service = ValidationWorkbenchService(settings)

    if args.command == "list-seeds":
        seed_payload = [seed.model_dump(mode="json") for seed in service.list_seed_bundles()]
        print(json.dumps(seed_payload, indent=2))
        return

    if args.command == "preflight":
        preflight_payload = run_preflight(settings)
        print(json.dumps(preflight_payload, indent=2))
        return

    if args.command == "summarize":
        case = service.get_case(args.case_id)
        paths = persist_case_seed_summary(
            service.repo,
            case,
            stop_after=AgentStage(args.stop_after),
        )
        print(json.dumps({"case_id": case.case_id, "summary_files": paths}, indent=2))
        return

    if args.command == "run":
        preflight = run_preflight(settings)
        case = service.create_case_from_seed(args.seed_id)
        run_case_pipeline(service, case, stop_after=AgentStage(args.stop_after))
        refreshed = service.get_case(case.case_id)
        summary_paths = persist_case_seed_summary(
            service.repo,
            refreshed,
            stop_after=AgentStage(args.stop_after),
            preflight=preflight,
        )
        print(
            json.dumps(
                {
                    "case_id": refreshed.case_id,
                    "status": refreshed.status.value,
                    "summary_files": summary_paths,
                    "final_report": refreshed.final_report.report_type.value
                    if refreshed.final_report
                    else None,
                },
                indent=2,
            )
        )
        return

    if args.command == "sweep":
        preflight = run_preflight(settings)
        seed_ids = args.seed_ids or [seed.seed_id for seed in service.list_seed_bundles()]
        case_summaries: list[dict[str, Any]] = []
        for seed_id in seed_ids:
            case = service.create_case_from_seed(seed_id)
            run_case_pipeline(service, case, stop_after=AgentStage(args.stop_after))
            refreshed = service.get_case(case.case_id)
            persist_case_seed_summary(
                service.repo,
                refreshed,
                stop_after=AgentStage(args.stop_after),
                preflight=preflight,
            )
            case_summaries.append(
                {
                    "case_id": refreshed.case_id,
                    "name": refreshed.name,
                    "status": refreshed.status.value,
                    "coverage": refreshed.coverage.model_dump(mode="json")
                    if refreshed.coverage
                    else None,
                    "final_report": refreshed.final_report.model_dump(mode="json")
                    if refreshed.final_report
                    else None,
                    "summary_file": refreshed.outputs.get("seed_case_summary_json"),
                }
            )
        label = args.label or f"seed_sweep_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
        sweep_paths = persist_sweep_summary(
            settings.workbench_storage_dir,
            label=label,
            case_summaries=case_summaries,
            preflight=preflight,
        )
        print(
            json.dumps(
                {
                    "label": label,
                    "sweep_files": sweep_paths,
                    "cases": case_summaries,
                },
                indent=2,
            )
        )
        return

    if args.command == "verify":
        preflight = run_preflight(settings)
        selected = args.seed_ids or [seed.seed_id for seed in service.list_seed_bundles()]
        descriptors = {seed.seed_id: seed for seed in service.list_seed_bundles()}
        verification_rows: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        for seed_id in selected:
            descriptor = descriptors.get(seed_id)
            if descriptor is None:
                raise KeyError(f"Unknown seed bundle: {seed_id}")
            case = service.create_case_from_seed(seed_id)
            run_case_pipeline(service, case, stop_after=AgentStage(args.stop_after))
            refreshed = service.get_case(case.case_id)
            persist_case_seed_summary(
                service.repo,
                refreshed,
                stop_after=AgentStage(args.stop_after),
                preflight=preflight,
            )
            verification = verify_case_expectations(refreshed, descriptor)
            verification_rows.append(verification)
            if verification["status"] != "passed":
                failures.append(verification)

        label = args.label or f"seed_verify_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
        sweep_paths = persist_sweep_summary(
            settings.workbench_storage_dir,
            label=label,
            case_summaries=verification_rows,
            preflight=preflight,
        )
        payload = {
            "label": label,
            "verification_files": sweep_paths,
            "results": verification_rows,
        }
        print(json.dumps(payload, indent=2))
        if failures:
            raise SystemExit(1)
        return

    raise ValueError(f"Unsupported command: {args.command}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workbench-seed")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-seeds")
    subparsers.add_parser("preflight")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--seed-id", required=True)
    run_parser.add_argument(
        "--stop-after",
        choices=[stage.value for stage in STAGE_SEQUENCE],
        default=AgentStage.REPORT.value,
    )

    sweep_parser = subparsers.add_parser("sweep")
    sweep_parser.add_argument("--seed-ids", nargs="*")
    sweep_parser.add_argument(
        "--stop-after",
        choices=[stage.value for stage in STAGE_SEQUENCE],
        default=AgentStage.REPORT.value,
    )
    sweep_parser.add_argument("--label")

    summarize_parser = subparsers.add_parser("summarize")
    summarize_parser.add_argument("--case-id", required=True)
    summarize_parser.add_argument(
        "--stop-after",
        choices=[stage.value for stage in STAGE_SEQUENCE],
        default=AgentStage.REPORT.value,
    )

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--seed-ids", nargs="*")
    verify_parser.add_argument(
        "--stop-after",
        choices=[stage.value for stage in STAGE_SEQUENCE],
        default=AgentStage.REPORT.value,
    )
    verify_parser.add_argument("--label")

    return parser


def run_case_pipeline(
    service: ValidationWorkbenchService,
    case: CaseRecord,
    *,
    stop_after: AgentStage,
) -> None:
    settings = Settings()
    log_path = service.repo.output_path(case.case_id, "seed/orchestration.log")

    if stop_after == AgentStage.REPORT:
        run_logged_command(
            settings,
            ["run-case", "--", "--case-id", case.case_id],
            log_path=log_path,
        )
    else:
        for stage in STAGE_SEQUENCE:
            run_logged_command(
                settings,
                [STAGE_SCRIPT[stage], "--", "--case-id", case.case_id],
                log_path=log_path,
            )
            if stage == stop_after:
                break

    refreshed = service.get_case(case.case_id)
    refreshed.outputs["seed_orchestration_log"] = str(log_path)
    service.repo.save_case(refreshed)


def run_preflight(settings: Settings) -> dict[str, Any]:
    output = run_logged_command(settings, ["preflight"], log_path=None)
    return extract_json_document(output)


def run_logged_command(
    settings: Settings,
    npm_args: list[str],
    *,
    log_path: Path | None,
) -> str:
    env = os.environ.copy()
    if settings.openai_api_key:
        env.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    env["CODEX_REPO_ROOT"] = str(settings.workbench_codex_package_dir.parent.parent)

    cmd = ["npm", "--prefix", str(settings.workbench_codex_package_dir), "run", *npm_args]
    completed = subprocess.run(
        cmd,
        cwd=settings.workbench_codex_package_dir.parent.parent,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    combined = completed.stdout or ""
    if log_path is not None:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"$ {' '.join(cmd)}\n")
            handle.write(combined)
            if not combined.endswith("\n"):
                handle.write("\n")
    if completed.returncode != 0:
        tail = "\n".join(line for line in combined.splitlines()[-20:] if line.strip())
        raise RuntimeError(tail or f"Command failed: {' '.join(cmd)}")
    return combined


def extract_json_document(output: str) -> dict[str, Any]:
    start = output.find("{")
    end = output.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise RuntimeError(f"Expected JSON output but got:\n{output}")
    return cast(dict[str, Any], json.loads(output[start : end + 1]))


def verify_case_expectations(case: CaseRecord, descriptor: SeedBundleDescriptor) -> dict[str, Any]:
    mismatches: list[str] = []
    actual_workflow = case.coverage.dominant_workflow.value if case.coverage else None
    actual_coverage = case.coverage.coverage_ratio if case.coverage else None
    actual_report = case.final_report.report_type.value if case.final_report else None

    if descriptor.expected_workflow and actual_workflow != descriptor.expected_workflow.value:
        mismatches.append(
            f"expected workflow {descriptor.expected_workflow.value}, got {actual_workflow or 'none'}"
        )
    if (
        descriptor.minimum_coverage_ratio is not None
        and (actual_coverage is None or actual_coverage < descriptor.minimum_coverage_ratio)
    ):
        mismatches.append(
            f"expected coverage >= {descriptor.minimum_coverage_ratio}, got {actual_coverage}"
        )
    if (
        descriptor.expected_report_type is not None
        and actual_report != descriptor.expected_report_type.value
    ):
        mismatches.append(
            f"expected report {descriptor.expected_report_type.value}, got {actual_report or 'none'}"
        )

    return {
        "case_id": case.case_id,
        "name": case.name,
        "seed_id": descriptor.seed_id,
        "status": "passed" if not mismatches else "failed",
        "expected": {
            "workflow": descriptor.expected_workflow.value if descriptor.expected_workflow else None,
            "report_type": (
                descriptor.expected_report_type.value if descriptor.expected_report_type else None
            ),
            "minimum_coverage_ratio": descriptor.minimum_coverage_ratio,
        },
        "actual": {
            "status": case.status.value,
            "workflow": actual_workflow,
            "coverage_ratio": actual_coverage,
            "report_type": actual_report,
            "summary_file": case.outputs.get("seed_case_summary_json"),
        },
        "coverage": case.coverage.model_dump(mode="json") if case.coverage else None,
        "final_report": case.final_report.model_dump(mode="json") if case.final_report else None,
        "mismatches": mismatches,
    }


if __name__ == "__main__":
    main()
