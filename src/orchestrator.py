"""Verdrahtet Write-Path (asynchron, nach der Antwort) und Read-Path (vor der Antwort).
Die LLM-Aufrufe für Extraktion/Management liegen bewusst NACH der Nutzerantwort,
damit NFA-01 (<500 ms) nur das Read-Path-Retrieval betrifft."""
from __future__ import annotations
from config import MemoryConfig
from src.llm import LLMClient
from src.storage.fact_store import FactStore
from src.storage.vector_store import VectorStore
from src.extraction import extract
from src.management import ManagementLayer
from src.retrieval import RetrievalLayer
from src.models import Domain


class MemoryMechanism:
    def __init__(self, cfg: MemoryConfig):
        self.cfg = cfg
        self.llm = LLMClient(cfg)
        self.facts = FactStore(cfg.sqlite_path)
        self.vectors = VectorStore(cfg.chroma_path, self.llm.embed)
        self.mgmt = ManagementLayer(cfg, self.llm, self.facts, self.vectors)
        self.retr = RetrievalLayer(cfg, self.llm, self.facts, self.vectors)

    def respond(self, user_msg: str, domain: Domain | None = None,
                session_id: str | None = None) -> str:
        # READ PATH ---------------------------------------------------
        context = self.retr.build_context(user_msg, domain)
        system = ("Du bist ein KI-Coach. Nutze den folgenden gespeicherten Kontext, "
                  "wenn er relevant ist:\n\n" + context)
        answer = self.llm.complete(system, user_msg)
        # WRITE PATH (asynchron im Echtbetrieb; hier sequentiell) ------
        convo = f"User: {user_msg}\nAssistant: {answer}"
        for cand in extract(convo, self.cfg, self.llm):
            self.mgmt.integrate(cand, session_id=session_id)
        return answer
