"""Adapter-Schnittstelle zwischen dem Mechanismus und dem LongMemEval-Harness (Kap. 6).
Früh definieren, damit die Evaluation in Phase 4 nur noch 'angesteckt' werden muss.
TODO(Phase 4): LongMemEval-S laden, Sitzungen sequentiell einspielen (Memory-Aufbau),
dann Frage stellen und Antwort zur LLM-as-Judge-Bewertung zurückgeben."""
from __future__ import annotations
from config import MemoryConfig
from src.orchestrator import MemoryMechanism
from src.models import Domain


def run_question(sessions: list[str], question: str, cfg: MemoryConfig) -> str:
    mech = MemoryMechanism(cfg)
    for i, turn in enumerate(sessions):              # Memory-Aufbau über Sitzungen
        mech.respond(turn, domain=None, session_id=f"s{i}")
    return mech.respond(question, domain=None, session_id="q")
