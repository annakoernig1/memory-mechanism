"""Typspezifischer Decay (Kap. 4.3.1.3).
decay_weight(t) = base * exp(-lambda * Δt_tage), Δt seit letztem Zugriff.
Bei Zugriff wird last_accessed zurückgesetzt -> Gewicht erholt sich (keine
Doppelzählung von access_boost; vgl. Präzisierung im konsolidierten Stand).
Ergebnis auf [0, base] geklippt."""
from __future__ import annotations
import math
from datetime import datetime, timezone
from config import MemoryConfig
from src.models import MemoryItem, MemoryType


def _days_since(iso: str) -> float:
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0)


def lambda_for(item: MemoryItem, cfg: MemoryConfig) -> float:
    if not cfg.enable_typed_decay:            # ABLATION H4
        return cfg.uniform_lambda
    if item.type == MemoryType.GOAL:
        # kein Decay bis Zieldatum; danach moderates Vergessen
        if item.goal_due and _days_since(item.goal_due) <= 0:
            return 0.0
        return 0.1 if item.goal_due else cfg.decay_lambda["GOAL"]
    return cfg.decay_lambda[item.type.value]


def current_weight(item: MemoryItem, cfg: MemoryConfig, base: float = 1.0) -> float:
    lam = lambda_for(item, cfg)
    w = base * math.exp(-lam * _days_since(item.last_accessed))
    return max(0.0, min(base, w))
