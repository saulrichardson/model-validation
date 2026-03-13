"""CLI bridge between the TypeScript Codex runner and Python workbench tools/state."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .case_ops import (
    execution_skill_id,
    mark_case_completed,
    mark_case_failed,
    playbook_catalog_payload,
    prepare_case,
    stage_complete,
    stage_failed,
    stage_start,
)
from .discovery import inventory_case
from .schemas import (
    AgentStage,
    CaseRecord,
    DiscoveryStageOutput,
    EvidenceLedgerEntry,
    ExecutionStageOutput,
    PlaybookStageOutput,
    ReportStageOutput,
    ToolCallRecord,
    utc_now,
)
from .settings import Settings, get_settings
from .sidecar import GatewaySidecarService
from .skills import SkillRegistry
from .storage import CaseRepository
from .tools import ToolEvidenceDraft, ToolInvocationResult, WorkbenchToolbox


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="workbench-bridge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_prepare = subparsers.add_parser("prepare-case")
    parser_prepare.add_argument("--case-id", required=True)

    parser_read = subparsers.add_parser("read-case")
    parser_read.add_argument("--case-id", required=True)

    parser_context = subparsers.add_parser("runner-context")
    parser_context.add_argument("--case-id", required=True)

    parser_stage_start = subparsers.add_parser("stage-start")
    parser_stage_start.add_argument("--case-id", required=True)
    parser_stage_start.add_argument(
        "--stage",
        required=True,
        choices=[stage.value for stage in AgentStage if stage != AgentStage.SIDECAR],
    )
    parser_stage_start.add_argument("--agent-name", required=True)
    parser_stage_start.add_argument("--skill-id", required=True)
    parser_stage_start.add_argument("--model", required=True)
    parser_stage_start.add_argument("--message", required=True)

    parser_stage_complete = subparsers.add_parser("stage-complete")
    parser_stage_complete.add_argument("--case-id", required=True)
    parser_stage_complete.add_argument(
        "--stage",
        required=True,
        choices=[stage.value for stage in AgentStage if stage != AgentStage.SIDECAR],
    )
    parser_stage_complete.add_argument("--summary-file", required=True)
    parser_stage_complete.add_argument("--trace-file", required=True)
    parser_stage_complete.add_argument("--response-file", required=True)
    parser_stage_complete.add_argument("--usage-file", required=True)
    parser_stage_complete.add_argument("--events-file", required=True)
    parser_stage_complete.add_argument("--response-id", required=True)

    parser_stage_failed = subparsers.add_parser("stage-failed")
    parser_stage_failed.add_argument("--case-id", required=True)
    parser_stage_failed.add_argument(
        "--stage",
        required=True,
        choices=[stage.value for stage in AgentStage if stage != AgentStage.SIDECAR],
    )
    parser_stage_failed.add_argument("--message", required=True)
    parser_stage_failed.add_argument("--trace-file", required=True)

    parser_tool = subparsers.add_parser("tool")
    parser_tool.add_argument("--case-id", required=True)
    parser_tool.add_argument(
        "--stage",
        required=True,
        choices=[stage.value for stage in AgentStage if stage != AgentStage.SIDECAR],
    )
    parser_tool.add_argument("--tool-name", required=True)
    parser_tool.add_argument("--args-json", required=True)

    parser_complete = subparsers.add_parser("mark-completed")
    parser_complete.add_argument("--case-id", required=True)

    parser_failed = subparsers.add_parser("mark-failed")
    parser_failed.add_argument("--case-id", required=True)
    parser_failed.add_argument("--message", required=True)

    return parser


def repository(settings: Settings) -> CaseRepository:
    repo = CaseRepository(settings.workbench_storage_dir)
    repo.initialize()
    return repo


def skills(settings: Settings) -> SkillRegistry:
    registry = SkillRegistry(settings.workbench_skill_dir)
    registry.load()
    return registry


def load_case(repo: CaseRepository, case_id: str) -> CaseRecord:
    return repo.get_case(case_id)


def runner_context(case_id: str) -> dict[str, object]:
    settings = get_settings()
    repo = repository(settings)
    case = load_case(repo, case_id)
    skill_registry = skills(settings)
    case_dir = repo.create_case_dir(case_id)
    return {
        "case": case.model_dump(mode="json"),
        "repo_root": str(Path(__file__).resolve().parents[3]),
        "case_dir": str(case_dir),
        "outputs_dir": str(case_dir / "outputs"),
        "skills": skill_registry.list_ids(),
        "playbook_catalog": playbook_catalog_payload(skill_registry),
        "execution_skill_id": execution_skill_id(case),
    }


def stage_model(
    stage: AgentStage,
) -> type[DiscoveryStageOutput | PlaybookStageOutput | ExecutionStageOutput | ReportStageOutput]:
    if stage == AgentStage.DISCOVERY:
        return DiscoveryStageOutput
    if stage == AgentStage.PLAYBOOK:
        return PlaybookStageOutput
    if stage == AgentStage.EXECUTION:
        return ExecutionStageOutput
    if stage == AgentStage.REPORT:
        return ReportStageOutput
    raise ValueError(f"Unsupported stage: {stage.value}")


def parse_stage_output(
    stage: AgentStage, path: Path
) -> DiscoveryStageOutput | PlaybookStageOutput | ExecutionStageOutput | ReportStageOutput:
    model = stage_model(stage)
    return model.model_validate_json(path.read_text(encoding="utf-8"))


def usage_payload(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


async def run_tool_command(
    *, case_id: str, stage: AgentStage, tool_name: str, args_json: str
) -> dict[str, object]:
    settings = get_settings()
    repo = repository(settings)
    case = load_case(repo, case_id)
    inventory = inventory_case(case)
    repo.save_case(case)

    gateway = GatewaySidecarService(settings=settings)
    toolbox = WorkbenchToolbox(
        inventory=inventory,
        repo=repo,
        settings=settings,
        gateway=gateway,
    )
    tool = toolbox.get_tool(stage, tool_name)
    call_id = f"call_{uuid.uuid4().hex[:12]}"
    tool_call_id = f"tool_{uuid.uuid4().hex[:12]}"
    started_at = utc_now()

    try:
        parsed_args = tool.input_model.model_validate_json(args_json)
        result = tool.handler(parsed_args)
        if hasattr(result, "__await__"):
            result = await result  # type: ignore[assignment]
        if not isinstance(result, ToolInvocationResult):
            raise TypeError(f"Tool '{tool_name}' returned unexpected payload type.")

        evidence_entries = materialize_evidence(
            case=case,
            stage=stage,
            tool_name=tool_name,
            drafts=result.evidence,
        )
        case.tool_calls.append(
            ToolCallRecord(
                tool_call_id=tool_call_id,
                call_id=call_id,
                stage=stage,
                tool_name=tool_name,
                transport=tool.transport,
                arguments=parsed_args.model_dump(mode="json"),
                output_summary=result.summary,
                output_path=result.output_path,
                evidence_ids=[entry.evidence_id for entry in evidence_entries],
                status="completed",
                started_at=started_at,
                completed_at=utc_now(),
            )
        )
        if result.output_path:
            case.outputs[f"tool_{tool_call_id}"] = result.output_path

        outputs = result.payload.get("outputs")
        if isinstance(outputs, dict):
            for key, value in outputs.items():
                if isinstance(value, str) and value:
                    case.outputs[key] = value
        repo.save_case(case)

        payload = dict(result.payload)
        payload["summary"] = result.summary
        payload["tool_call_id"] = tool_call_id
        payload["evidence_entries"] = [
            {
                "evidence_id": entry.evidence_id,
                "title": entry.title,
                "relative_path": entry.relative_path,
                "summary": entry.summary,
            }
            for entry in evidence_entries
        ]
        return payload
    except Exception as exc:  # noqa: BLE001
        case.tool_calls.append(
            ToolCallRecord(
                tool_call_id=tool_call_id,
                call_id=call_id,
                stage=stage,
                tool_name=tool_name,
                transport=tool.transport,
                arguments=safe_json_loads(args_json),
                status="failed",
                started_at=started_at,
                completed_at=utc_now(),
                error_message=str(exc),
            )
        )
        repo.save_case(case)
        raise
    finally:
        await gateway.shutdown()


def safe_json_loads(payload: str) -> dict[str, Any]:
    try:
        loaded = json.loads(payload)
    except json.JSONDecodeError:
        return {"raw": payload}
    if isinstance(loaded, dict):
        return loaded
    return {"value": loaded}


def materialize_evidence(
    *,
    case: CaseRecord,
    stage: AgentStage,
    tool_name: str,
    drafts: list[ToolEvidenceDraft],
) -> list[EvidenceLedgerEntry]:
    entries: list[EvidenceLedgerEntry] = []
    for draft in drafts:
        existing = next(
            (
                item
                for item in case.evidence_ledger
                if (draft.output_path and item.output_path == draft.output_path)
                or (draft.relative_path and item.relative_path == draft.relative_path)
            ),
            None,
        )
        if existing is not None:
            entries.append(existing)
            continue
        entry = EvidenceLedgerEntry(
            evidence_id=f"ev_{len(case.evidence_ledger) + 1:03d}",
            source_type=draft.source_type,
            title=draft.title,
            summary=draft.summary,
            relative_path=draft.relative_path,
            output_path=draft.output_path,
            stage=stage,
            tool_name=tool_name,
        )
        case.evidence_ledger.append(entry)
        entries.append(entry)
    return entries


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    settings = get_settings()
    repo = repository(settings)

    try:
        if args.command == "prepare-case":
            print(json.dumps(prepare_case(load_case(repo, args.case_id), repo), indent=2))
            return 0

        if args.command == "read-case":
            print(load_case(repo, args.case_id).model_dump_json(indent=2))
            return 0

        if args.command == "runner-context":
            print(json.dumps(runner_context(args.case_id), indent=2))
            return 0

        if args.command == "stage-start":
            stage_start(
                load_case(repo, args.case_id),
                repo,
                stage=AgentStage(args.stage),
                agent_name=args.agent_name,
                skill_id=args.skill_id,
                model=args.model,
                message=args.message,
            )
            return 0

        if args.command == "stage-complete":
            stage_complete(
                load_case(repo, args.case_id),
                repo,
                stage=AgentStage(args.stage),
                stage_output=parse_stage_output(AgentStage(args.stage), Path(args.summary_file)),
                summary_file=args.summary_file,
                trace_file=args.trace_file,
                response_file=args.response_file,
                events_file=args.events_file,
                usage_file=args.usage_file,
                usage=usage_payload(Path(args.usage_file)),
                response_id=args.response_id,
            )
            return 0

        if args.command == "stage-failed":
            stage_failed(
                load_case(repo, args.case_id),
                repo,
                stage=AgentStage(args.stage),
                message=args.message,
                trace_file=args.trace_file,
            )
            return 0

        if args.command == "mark-completed":
            mark_case_completed(load_case(repo, args.case_id), repo)
            return 0

        if args.command == "mark-failed":
            mark_case_failed(load_case(repo, args.case_id), repo, args.message)
            return 0

        if args.command == "tool":
            print(
                json.dumps(
                    asyncio.run(
                        run_tool_command(
                            case_id=args.case_id,
                            stage=AgentStage(args.stage),
                            tool_name=args.tool_name,
                            args_json=args.args_json,
                        )
                    ),
                    indent=2,
                )
            )
            return 0

        raise ValueError(f"Unknown command: {args.command}")
    except (KeyError, ValidationError, FileNotFoundError, ValueError, RuntimeError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
