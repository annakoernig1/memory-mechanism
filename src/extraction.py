"""Layer 1 – Memory Extraction (Kap. 4.3.1.1).
LLM extrahiert speicherwürdige Infos als JSON. Schwelle: conf>=0.6 wird gespeichert,
0.4–0.6 als Kandidat markiert.
TODO(Phase 3b): Few-Shot-Beispiele je Typ in den Prompt aufnehmen und Extraktion
gegen ein handgelabeltes Set validieren (Precision/Recall statt blindem Vertrauen
auf die selbstberichtete confidence – vgl. kritische Anmerkung Kap. 4)."""
from __future__ import annotations
import json
from config import MemoryConfig
from src.llm import LLMClient
from src.models import ExtractionCandidate, MemoryType, Domain

_SYSTEM = """Du extrahierst speicherwürdige, nutzerbezogene Informationen aus einer
Konversation. Gib NUR JSON zurück: {"memories":[{"content","type","domain",
"confidence","key","value","entities"}]}. type ∈ STABLE_FACT|DYNAMIC_STATE|
PREFERENCE|EPISODE|GOAL. domain ∈ TRAINING|HEALTH|NUTRITION|PERSONAL.
confidence ∈ [0,1]. Keine Spekulation."""


def extract(conversation: str, cfg: MemoryConfig, llm: LLMClient) -> list[ExtractionCandidate]:
    raw = llm.complete(_SYSTEM, conversation, json_mode=True)
    try:
        data = json.loads(raw).get("memories", [])
    except json.JSONDecodeError:
        return []
    lo, hi = cfg.candidate_band
    out = []
    for m in data:
        conf = float(m.get("confidence", 0))
        if conf < lo:
            continue
        out.append(ExtractionCandidate(
            content=m["content"], type=MemoryType(m["type"]),
            domain=Domain(m.get("domain", "PERSONAL")), confidence=conf,
            key=m.get("key"), value=m.get("value"),
            entities=m.get("entities", []), is_candidate=(conf < hi)))
    return out
