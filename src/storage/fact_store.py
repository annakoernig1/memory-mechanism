"""Fact Store (SQLite) für strukturierte Typen 1/2/5 – deterministischer Key-Zugriff,
Versionierung über das history-Feld (Kap. 4.3.1.2)."""
from __future__ import annotations
import sqlite3, json
from src.models import MemoryItem, MemoryType, Domain


class FactStore:
    def __init__(self, path: str):
        self.con = sqlite3.connect(path)
        self.con.execute("""CREATE TABLE IF NOT EXISTS facts(
            id TEXT PRIMARY KEY, key TEXT, value TEXT, content TEXT, type TEXT,
            domain TEXT, confidence REAL, created_at TEXT, updated_at TEXT,
            last_accessed TEXT, access_count INTEGER, decay_weight REAL,
            source_session_id TEXT, history TEXT, goal_due TEXT)""")
        self.con.commit()

    def upsert(self, it: MemoryItem) -> None:
        self.con.execute("INSERT OR REPLACE INTO facts VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            it.id, it.key, it.value, it.content, it.type.value, it.domain.value,
            it.confidence, it.created_at, it.updated_at, it.last_accessed,
            it.access_count, it.decay_weight, it.source_session_id,
            json.dumps(it.history), it.goal_due))
        self.con.commit()

    def find_by_key(self, key: str) -> MemoryItem | None:
        row = self.con.execute("SELECT * FROM facts WHERE key=?", (key,)).fetchone()
        return self._row_to_item(row) if row else None

    def all_of_types(self, types: list[MemoryType]) -> list[MemoryItem]:
        q = ",".join("?" for _ in types)
        rows = self.con.execute(
            f"SELECT * FROM facts WHERE type IN ({q})", [t.value for t in types]).fetchall()
        return [self._row_to_item(r) for r in rows]

    def _row_to_item(self, r) -> MemoryItem:
        return MemoryItem(
            id=r[0], key=r[1], value=r[2], content=(r[3] or ""), type=MemoryType(r[4]),
            domain=Domain(r[5]), confidence=r[6], created_at=r[7], updated_at=r[8],
            last_accessed=r[9], access_count=r[10], decay_weight=r[11],
            source_session_id=r[12], history=json.loads(r[13] or "[]"), goal_due=r[14])
