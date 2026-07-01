"""Walking skeleton: speichern -> abrufen -> injizieren -> antworten.
Läuft ohne API-Schlüssel (dryrun). Erstes Ziel von Phase 3a: dieser Test wird grün."""
import os, tempfile
from config import MemoryConfig
from src.models import ExtractionCandidate, MemoryType, Domain
from src.orchestrator import MemoryMechanism


def _cfg(tmp):
    return MemoryConfig.ablation(llm_provider="dryrun",
                                 sqlite_path=os.path.join(tmp, "m.sqlite3"),
                                 chroma_path=os.path.join(tmp, "chroma"))


def test_end_to_end_dryrun():
    with tempfile.TemporaryDirectory() as tmp:
        mech = MemoryMechanism(_cfg(tmp))
        # eine Information manuell integrieren (Typ 1, strukturiert)
        cand = ExtractionCandidate(content="Marathon-PB 3:12", type=MemoryType.STABLE_FACT,
                                   domain=Domain.TRAINING, confidence=0.9,
                                   key="marathon_pb", value="3:12")
        op = mech.mgmt.integrate(cand, session_id="s1")
        assert op == "ADD"
        # Read-Path: Kontext muss die Information enthalten
        ctx = mech.retr.build_context("Wie soll ich trainieren?", Domain.TRAINING)
        assert "Marathon-PB" in ctx
        # voller Durchlauf
        ans = mech.respond("Plan für morgen?", Domain.TRAINING, "s1")
        assert isinstance(ans, str) and len(ans) > 0


def test_ablation_dual_store_routing():
    with tempfile.TemporaryDirectory() as tmp:
        cfg = _cfg(tmp); cfg.enable_dual_store = False   # H5
        mech = MemoryMechanism(cfg)
        cand = ExtractionCandidate(content="Alter 34", type=MemoryType.STABLE_FACT,
                                   domain=Domain.PERSONAL, confidence=0.95, key="alter")
        mech.mgmt.integrate(cand)
        # ohne dualen Store darf der Fact Store leer bleiben
        assert mech.facts.find_by_key("alter") is None
