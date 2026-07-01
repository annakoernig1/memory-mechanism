"""Layer 3 – Memory Management (Kap. 4.3.1.3). Operationsauswahl ADD/UPDATE/MERGE/
DELETE/NOOP. Routing: strukturierte Typen -> Fact Store, sonst -> Vektor-Store.
Bei Ablation H6 (enable_llm_op_selection=False) wird immer ADD gewählt;
bei Ablation H5 (enable_dual_store=False) geht alles in den Vektor-Store."""
from __future__ import annotations
from config import MemoryConfig
from src.llm import LLMClient
from src.models import MemoryItem, MemoryType, ExtractionCandidate

_STRUCTURED = {MemoryType.STABLE_FACT, MemoryType.DYNAMIC_STATE, MemoryType.GOAL}


class ManagementLayer:
    def __init__(self, cfg, llm, fact_store, vector_store):
        self.cfg, self.llm = cfg, llm
        self.facts, self.vectors = fact_store, vector_store

    def integrate(self, c: ExtractionCandidate, session_id: str | None = None) -> str:
        if c.confidence < self.cfg.confidence_threshold and not c.is_candidate:
            return "NOOP"
        item = MemoryItem(content=c.content, type=c.type, domain=c.domain,
                          confidence=c.confidence, key=c.key, value=c.value,
                          entities=c.entities, source_session_id=session_id)
        op = "ADD"
        if self.cfg.enable_llm_op_selection:
            op = self._choose_operation(item)   # TODO: LLM-Vergleich mit Nachbarn
        self._apply(op, item)
        return op

    def _choose_operation(self, item: MemoryItem) -> str:
        # TODO(Phase 3b): k ähnlichste bestehende Einträge holen und das LLM
        # ADD/UPDATE/MERGE/NOOP entscheiden lassen. Skeleton: Key-Kollision -> UPDATE.
        if item.key and self.facts.find_by_key(item.key):
            return "UPDATE"
        return "ADD"

    def _apply(self, op: str, item: MemoryItem) -> None:
        use_facts = self.cfg.enable_dual_store and item.type in _STRUCTURED
        if op in ("ADD", "UPDATE", "MERGE"):
            if use_facts:
                if op == "UPDATE" and item.key:
                    old = self.facts.find_by_key(item.key)
                    if old:
                        item.history = old.history + [{"value": old.value,
                                                       "updated_at": old.updated_at}]
                self.facts.upsert(item)
            else:
                self.vectors.add(item)
