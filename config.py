"""Zentrale Konfiguration. Die Feature-Flags sind das Herzstück der Ablationsstudie
(H4–H7 aus Kapitel 6.1): Jede Gestaltungsentscheidung lässt sich einzeln abschalten,
ohne den Code zu ändern. So teilen alle Varianten dieselbe Codebasis, dieselben Daten
und dasselbe Modell und unterscheiden sich nur in der untersuchten Komponente.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import json


@dataclass
class MemoryConfig:
    # ---- Modell / Reproduzierbarkeit (Kap. 6.1.6) ----
    llm_provider: str = "anthropic"           # "anthropic" | "openai" | "dryrun"
    llm_model: str = "claude-sonnet-5" 
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.0                  # deterministisch für Reproduzierbarkeit
    seed: int = 42

    # ---- Speicherpfade ----
    chroma_path: str = ".chroma"
    sqlite_path: str = "memory.sqlite3"

    # ---- Retrieval-Parameter (Kap. 4.3.1.4) ----
    top_k: int = 10
    state_recency_days: int = 14              # Aktualitätsfenster für Typ-2-Zustände
    decay_retrieval_threshold: float = 0.2    # < 0.2 => "dormant", nicht abgerufen
    decay_delete_threshold: float = 0.05      # < 0.05 => Löschvorschlag
    context_token_budget: int = 2000

    # ---- Extraktion (Kap. 4.3.1.1) ----
    confidence_threshold: float = 0.6         # >= 0.6 wird gespeichert
    candidate_band: tuple = (0.4, 0.6)        # Graubereich -> als Kandidat markiert

    # ---- typspezifische Decay-Raten lambda (Kap. 4.3.1.3) ----
    decay_lambda: dict = field(default_factory=lambda: {
        "STABLE_FACT": 0.001,
        "DYNAMIC_STATE": 0.05,
        "PREFERENCE": 0.005,
        "EPISODE": 0.03,
        "GOAL": 0.0,           # kein Decay bis Zieldatum; danach uniform_lambda
    })
    uniform_lambda: float = 0.02              # für Ablation "ohne typspezifischen Decay"

    # ===================================================================
    # FEATURE-FLAGS = ABLATIONSSCHALTER  (Vollsystem = alle True)
    # ===================================================================
    enable_segmentation: bool = True      # H7/H8: Domänensegmentierung gegen Leakage
    enable_typed_decay: bool = True       # H4: typspezifischer vs. uniformer Decay
    enable_dual_store: bool = True        # H5: Fact Store + Vektor-Store vs. nur Vektor
    enable_llm_op_selection: bool = True  # H6: CRUD+M-Auswahl vs. nur ADD
    enable_sycophancy_guard: bool = True  # F4: defensive Präferenz-Kennzeichnung

    @classmethod
    def vollsystem(cls) -> "MemoryConfig":
        return cls()

    @classmethod
    def ablation(cls, **flags) -> "MemoryConfig":
        """z.B. MemoryConfig.ablation(enable_segmentation=False) für H7."""
        c = cls()
        for k, v in flags.items():
            setattr(c, k, v)
        return c

    def fingerprint(self) -> str:
        """Eindeutige Signatur der Konfiguration – in jedes Eval-Log schreiben."""
        return json.dumps(asdict(self), sort_keys=True, default=str)
