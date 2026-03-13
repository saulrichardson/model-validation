"""Artifact inventory helpers for uploaded model-validation cases."""

from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

from .schemas import ArtifactKind, ArtifactRecord, CaseRecord, DataProfile

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".sql",
    ".csv",
    ".tsv",
}


@dataclass
class InventoryContext:
    case: CaseRecord
    artifact_index: dict[str, ArtifactRecord]
    text_lookup: dict[str, str] = field(default_factory=dict)
    dataset_profiles: dict[str, DataProfile] = field(default_factory=dict)

    def find_by_tag(self, tag: str) -> list[ArtifactRecord]:
        return [artifact for artifact in self.artifact_index.values() if tag in artifact.tags]

    def find_first(self, *tags: str) -> ArtifactRecord | None:
        for artifact in self.artifact_index.values():
            if all(tag in artifact.tags for tag in tags):
                return artifact
        return None

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        artifact = self.artifact_index.get(artifact_id)
        if artifact is None:
            raise KeyError(f"Unknown artifact id: {artifact_id}")
        return artifact


def inventory_case(case: CaseRecord) -> InventoryContext:
    root_dir = Path(case.root_dir)
    artifacts: list[ArtifactRecord] = []
    artifact_index: dict[str, ArtifactRecord] = {}
    text_lookup: dict[str, str] = {}
    dataset_profiles: dict[str, DataProfile] = {}

    for file_path in sorted(path for path in root_dir.rglob("*") if path.is_file()):
        relative_path = str(file_path.relative_to(root_dir))
        artifact_id = f"art_{len(artifacts) + 1:03d}"
        kind = classify_artifact(file_path)
        excerpt = extract_excerpt(file_path, kind)
        tags = infer_tags(relative_path, kind, excerpt)
        artifact = ArtifactRecord(
            artifact_id=artifact_id,
            relative_path=relative_path,
            absolute_path=str(file_path),
            kind=kind,
            size_bytes=file_path.stat().st_size,
            mime_type=mimetypes.guess_type(file_path.name)[0],
            tags=tags,
            excerpt=excerpt,
        )
        artifacts.append(artifact)
        artifact_index[artifact_id] = artifact

        if excerpt:
            text_lookup[artifact_id] = excerpt

        if kind == ArtifactKind.DATASET:
            profile = maybe_profile_dataset(file_path)
            if profile is not None:
                dataset_profiles[artifact_id] = profile

    case.artifacts = artifacts
    return InventoryContext(
        case=case,
        artifact_index=artifact_index,
        text_lookup=text_lookup,
        dataset_profiles=dataset_profiles,
    )


def classify_artifact(path: Path) -> ArtifactKind:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if name == "dockerfile":
        return ArtifactKind.CONTAINER
    if suffix in {".py", ".r", ".sh"}:
        return ArtifactKind.CODE
    if suffix == ".ipynb":
        return ArtifactKind.NOTEBOOK
    if suffix in {".md", ".txt", ".pdf"}:
        return ArtifactKind.DOCUMENT
    if suffix in {".csv", ".tsv", ".xlsx", ".parquet"}:
        return ArtifactKind.DATASET
    if suffix in {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}:
        lowered = str(path).lower()
        if "metric" in lowered or "distribution" in lowered or "summary" in lowered:
            return ArtifactKind.METRICS
        return ArtifactKind.CONFIG
    if suffix in {".onnx", ".pkl", ".joblib"}:
        return ArtifactKind.MODEL
    if suffix == ".bin":
        return ArtifactKind.BINARY
    if suffix in {".zip", ".tar", ".gz"}:
        return ArtifactKind.ARCHIVE
    return ArtifactKind.UNKNOWN


def extract_excerpt(path: Path, kind: ArtifactKind, *, limit: int = 1400) -> str | None:
    try:
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(str(path))
            if not reader.pages:
                return None
            return (reader.pages[0].extract_text() or "").strip()[:limit] or None
        if path.suffix.lower() == ".ipynb":
            payload = json.loads(path.read_text(encoding="utf-8"))
            chunks: list[str] = []
            for cell in payload.get("cells", [])[:4]:
                source = "".join(cell.get("source", []))
                if source:
                    chunks.append(source.strip())
            return "\n\n".join(chunks)[:limit] or None
        if path.suffix.lower() in TEXT_EXTENSIONS or kind in {
            ArtifactKind.CODE,
            ArtifactKind.DOCUMENT,
            ArtifactKind.METRICS,
            ArtifactKind.CONFIG,
        }:
            return path.read_text(encoding="utf-8", errors="ignore")[:limit].strip() or None
    except Exception:  # noqa: BLE001
        return None
    return None


def infer_tags(relative_path: str, kind: ArtifactKind, excerpt: str | None) -> list[str]:
    lowered = relative_path.lower()
    excerpt_lower = (excerpt or "").lower()
    tags: set[str] = set()
    if kind == ArtifactKind.CODE:
        tags.add("code")
    if kind == ArtifactKind.DATASET:
        tags.add("dataset")
    if kind == ArtifactKind.DOCUMENT:
        tags.add("document")
    if kind == ArtifactKind.METRICS:
        tags.add("metrics")
    if "baseline" in lowered:
        tags.add("baseline")
    if "candidate" in lowered or "challenger" in lowered:
        tags.add("candidate")
    if "method" in lowered or "model card" in excerpt_lower or "methodology" in lowered:
        tags.add("methodology")
    if "prior_validation" in lowered or "prior validation" in excerpt_lower:
        tags.add("prior_validation")
    if "change_request" in lowered or "change request" in excerpt_lower:
        tags.add("change_request")
    if (
        "reason_code" in lowered
        or "reason_table" in lowered
        or "adverse-action" in excerpt_lower
        or "adverse action" in excerpt_lower
    ):
        tags.add("reason_codes")
    if "feature_dictionary" in lowered or "feature_name" in excerpt_lower:
        tags.add("feature_dictionary")
    if (
        "score_batch" in lowered
        or "run_smoke" in lowered
        or "harness" in lowered
        or "revalidation" in lowered
        or "compare_models" in lowered
        or "replay" in lowered
    ):
        tags.add("runtime_harness")
    if (
        "requirements" in lowered
        or lowered.endswith("pyproject.toml")
        or "environment" in lowered
        or "runtime_dependencies" in lowered
    ):
        tags.add("dependency_spec")
    if "monitor" in lowered:
        tags.add("monitoring")
    if "development" in lowered or "calibration" in lowered or "training" in lowered:
        tags.add("development_evidence")
    if "dockerfile" in lowered:
        tags.add("container_spec")
    if "distribution" in lowered:
        tags.add("production_distribution")
    if "summary" in lowered:
        tags.add("summary")
    if "target_default" in excerpt_lower:
        tags.add("target_labels")
    if "score" in lowered or "decision" in excerpt_lower or "pd_estimate" in excerpt_lower:
        tags.add("scoring")
    return sorted(tags)


def maybe_profile_dataset(path: Path) -> DataProfile | None:
    try:
        separator = "\t" if path.suffix.lower() == ".tsv" else ","
        frame = pd.read_csv(path, sep=separator)
    except Exception:  # noqa: BLE001
        return None

    numeric_columns = list(frame.select_dtypes(include=["number"]).columns)
    categorical_columns = [column for column in frame.columns if column not in numeric_columns]
    missing_by_column = {
        column: round(float(frame[column].isna().mean()), 4)
        for column in frame.columns
        if float(frame[column].isna().mean()) > 0
    }
    highlights: list[str] = []
    if missing_by_column:
        highest_missing = sorted(missing_by_column.items(), key=lambda item: item[1], reverse=True)[
            0
        ]
        highlights.append(
            f"Highest missingness is {highest_missing[0]} at {highest_missing[1]:.1%}."
        )
    if "target_default" in frame.columns:
        highlights.append(f"Target default rate is {float(frame['target_default'].mean()):.1%}.")

    return DataProfile(
        row_count=int(len(frame)),
        column_count=int(len(frame.columns)),
        target_column="target_default" if "target_default" in frame.columns else None,
        numeric_columns=numeric_columns[:12],
        categorical_columns=categorical_columns[:12],
        missing_rate_by_column=missing_by_column,
        highlights=highlights,
    )


def capability_hints(context: InventoryContext) -> list[str]:
    artifacts = list(context.artifact_index.values())
    tags = {tag for artifact in artifacts for tag in artifact.tags}
    hints: set[str] = set()
    if any(artifact.kind == ArtifactKind.DATASET for artifact in artifacts):
        hints.add("sample_data")
    if any(profile.target_column for profile in context.dataset_profiles.values()):
        hints.add("target_labels")
    if any(
        "code" in artifact.tags and "baseline" in artifact.tags for artifact in artifacts
    ) and any("code" in artifact.tags and "candidate" in artifact.tags for artifact in artifacts):
        hints.add("baseline_candidate_pair")
        hints.add("runnable_model")
    elif any("code" in artifact.tags for artifact in artifacts):
        hints.add("runnable_model")
    if "runtime_harness" in tags:
        hints.add("runtime_harness")
    if "container_spec" in tags or any(
        artifact.kind == ArtifactKind.CONTAINER for artifact in artifacts
    ):
        hints.add("container_spec")
    if "methodology" in tags:
        hints.add("methodology_doc")
        hints.add("documentation_pack")
    if "prior_validation" in tags:
        hints.add("prior_validation")
    if "change_request" in tags:
        hints.add("change_request")
    if "reason_codes" in tags:
        hints.add("reason_code_mapping")
    if "feature_dictionary" in tags:
        hints.add("feature_dictionary")
    if "dependency_spec" in tags:
        hints.add("dependency_environment_spec")
    if "monitoring" in tags:
        hints.add("monitoring_evidence")
    if "development_evidence" in tags:
        hints.add("development_provenance")
    if "production_distribution" in tags:
        hints.add("production_distribution")
    if any(artifact.kind == ArtifactKind.METRICS for artifact in artifacts):
        hints.add("comparable_metrics")
    return sorted(hints)


def summarize_inventory(context: InventoryContext) -> dict[str, object]:
    largest_profile = primary_data_profile(context)
    return {
        "artifact_count": len(context.artifact_index),
        "artifact_types": sorted({artifact.kind.value for artifact in context.artifact_index.values()}),
        "capability_hints": capability_hints(context),
        "largest_dataset_profile": largest_profile.model_dump(mode="json") if largest_profile else None,
    }


def primary_data_profile(context: InventoryContext) -> DataProfile | None:
    if not context.dataset_profiles:
        return None
    _, profile = max(
        context.dataset_profiles.items(),
        key=lambda item: item[1].row_count or 0,
    )
    return profile
