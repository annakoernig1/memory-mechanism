"""Layer 4 – fünfstufiges Retrieval (Kap. 4.3.1.4):
1 Permanent Context (Typ1/5) · 2 State Injection (Typ2) · 3 Semantic Retrieval (Typ3/4)
4 Relevance Filtering (Domäne/Aktualität/Decay) · 5 Context Assembly."""
from __future__ import annotations
from config import MemoryConfig
from src.llm import LLMClient
from src.models import MemoryType, Domain
from src.decay import current_weight, _days_since


class RetrievalLayer:
    def __init__(self, cfg, llm, fact_store, vector_store):
        self.cfg, self.llm = cfg, llm
        self.facts, self.vectors = fact_store, vector_store

    def build_context(self, query: str, query_domain: Domain | None = None) -> str:
        # 1 Permanent
        permanent = self.facts.all_of_types([MemoryType.STABLE_FACT, MemoryType.GOAL])
        # 2 State (nur innerhalb Aktualitätsfenster)
        states = [s for s in self.facts.all_of_types([MemoryType.DYNAMIC_STATE])
                  if _days_since(s.updated_at) <= self.cfg.state_recency_days]
        # 3 Semantic
        sem = self.vectors.query(query, self.cfg.top_k)
        # 4 Relevance Filtering
        filtered = []
        for hit in sem:
            meta = hit["metadata"]
            if self.cfg.enable_segmentation and query_domain:   # ABLATION H7
                if meta["domain"] == Domain.PERSONAL.value and query_domain != Domain.PERSONAL:
                    continue
            if meta.get("decay_weight", 1.0) < self.cfg.decay_retrieval_threshold:
                continue
            filtered.append(hit)
        # 5 Assembly
        return self._assemble(permanent, states, filtered)

    def _assemble(self, permanent, states, semantic) -> str:
        parts = []
        if permanent:
            parts.append("# Stabile Fakten & Ziele\n" +
                         "\n".join(f"- {p.content}" for p in permanent))
        if states:
            parts.append("# Aktueller Zustand\n" +
                         "\n".join(f"- {s.content}" for s in states))
        if semantic:
            label = "Präferenzen & Episoden"
            lines = []
            for h in semantic:
                tag = ""
                if self.cfg.enable_sycophancy_guard and \
                   h["metadata"]["type"] == MemoryType.PREFERENCE.value:
                    tag = " (Nutzerpräferenz, keine fachliche Vorgabe)"
                lines.append(f"- {h['document']}{tag}")
            parts.append(f"# {label}\n" + "\n".join(lines))
        # TODO(Phase 3b): Token-Budget cfg.context_token_budget durchsetzen.
        return "\n\n".join(parts)
