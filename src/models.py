"""Datenmodell: die fünf Informationstypen (Kap. 4.2.1) und das Memory-Item."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import uuid


class MemoryType(str, Enum):
    STABLE_FACT = "STABLE_FACT"      # Typ 1
    DYNAMIC_STATE = "DYNAMIC_STATE"  # Typ 2
    PREFERENCE = "PREFERENCE"        # Typ 3
    EPISODE = "EPISODE"              # Typ 4
    GOAL = "GOAL"                    # Typ 5


class Domain(str, Enum):
    TRAINING = "TRAINING"
    HEALTH = "HEALTH"
    NUTRITION = "NUTRITION"
    PERSONAL = "PERSONAL"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryItem:
    content: str
    type: MemoryType
    domain: Domain
    confidence: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    key: str | None = None                 # für strukturierte Fakten (Typ 1/2/5)
    value: str | None = None
    entities: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    last_accessed: str = field(default_factory=_now)
    access_count: int = 0
    decay_weight: float = 1.0
    source_session_id: str | None = None
    history: list[dict] = field(default_factory=list)  # Versionierung (FA-06)
    goal_due: str | None = None            # nur Typ 5

    def to_metadata(self) -> dict:
        """flache Metadaten für ChromaDB (nur primitive Typen erlaubt)."""
        return {
            "id": self.id, "type": self.type.value, "domain": self.domain.value,
            "confidence": self.confidence, "created_at": self.created_at,
            "updated_at": self.updated_at, "last_accessed": self.last_accessed,
            "access_count": self.access_count, "decay_weight": self.decay_weight,
            "source_session_id": self.source_session_id or "",
        }


@dataclass
class ExtractionCandidate:
    content: str
    type: MemoryType
    domain: Domain
    confidence: float
    key: str | None = None
    value: str | None = None
    entities: list[str] = field(default_factory=list)
    is_candidate: bool = False   # True wenn confidence im Graubereich (0.4–0.6)
