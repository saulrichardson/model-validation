"""Evidence reference helpers shared across workbench modules."""

from __future__ import annotations

from .schemas import CaseRecord, EvidenceRef


def evidence_refs_from_ids(case: CaseRecord, evidence_ids: list[str]) -> list[EvidenceRef]:
    refs: list[EvidenceRef] = []
    for evidence_id in evidence_ids:
        entry = next((item for item in case.evidence_ledger if item.evidence_id == evidence_id), None)
        if entry is None:
            refs.append(EvidenceRef(evidence_id=evidence_id, detail="Referenced evidence id."))
            continue
        refs.append(
            EvidenceRef(
                evidence_id=evidence_id,
                detail=entry.summary,
                title=entry.title,
                relative_path=entry.relative_path or entry.output_path,
            )
        )
    return refs
