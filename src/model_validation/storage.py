"""Local persistence for workbench cases."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .schemas import CaseRecord, utc_now


class CaseRepository:
    def __init__(self, storage_dir: Path) -> None:
        self._storage_dir = storage_dir
        self._db_path = storage_dir / "workbench.sqlite3"
        self._case_root = storage_dir / "cases"

    @property
    def case_root(self) -> Path:
        return self._case_root

    def initialize(self) -> None:
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._case_root.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    case_name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    payload TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def list_cases(self) -> list[CaseRecord]:
        with self._connect() as conn:
            rows = conn.execute("SELECT payload FROM cases ORDER BY updated_at DESC").fetchall()
        return [CaseRecord.model_validate_json(row[0]) for row in rows]

    def get_case(self, case_id: str) -> CaseRecord:
        with self._connect() as conn:
            row = conn.execute("SELECT payload FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        if row is None:
            raise KeyError(f"Case not found: {case_id}")
        return CaseRecord.model_validate_json(row[0])

    def save_case(self, case: CaseRecord) -> CaseRecord:
        case.updated_at = utc_now()
        payload = case.model_dump_json()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO cases(case_id, case_name, source, status, updated_at, payload)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(case_id) DO UPDATE SET
                    case_name = excluded.case_name,
                    source = excluded.source,
                    status = excluded.status,
                    updated_at = excluded.updated_at,
                    payload = excluded.payload
                """,
                (
                    case.case_id,
                    case.name,
                    case.source.value,
                    case.status.value,
                    case.updated_at.isoformat(),
                    payload,
                ),
            )
            conn.commit()
        return case

    def create_case_dir(self, case_id: str) -> Path:
        case_dir = self._case_root / case_id
        (case_dir / "input").mkdir(parents=True, exist_ok=True)
        (case_dir / "outputs").mkdir(parents=True, exist_ok=True)
        return case_dir

    def output_path(self, case_id: str, filename: str) -> Path:
        case_dir = self.create_case_dir(case_id)
        output_path = case_dir / "outputs" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        return output_path

    def dump_output_json(self, case_id: str, filename: str, payload: object) -> str:
        output_path = self.output_path(case_id, filename)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(output_path)

    def dump_output_text(self, case_id: str, filename: str, content: str) -> str:
        output_path = self.output_path(case_id, filename)
        output_path.write_text(content, encoding="utf-8")
        return str(output_path)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._db_path)
        try:
            yield conn
        finally:
            conn.close()
