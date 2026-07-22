"""Adapter zwischen dem Mechanismus und dem LongMemEval-Datensatz (Kap. 6).
Drei getrennte Phasen:
  1. ingest_session  – reiner Write-Path (Gedächtnisaufbau, keine Antwortgenerierung)
  2. answer_question – reiner Read-Path (Antwort ohne erneutes Schreiben)
  3. run_question    – verarbeitet eine komplette LongMemEval-Frage
Einheitsdomäne (Option 1): alle Benchmark-Daten laufen unter einer neutralen Domäne,
damit LongMemEval die Gedächtnisfähigkeiten (F3) misst; die Domänensegmentierung (F4)
wird separat in der Risiko-Probe getestet."""
from __future__ import annotations
from config import MemoryConfig
from src.orchestrator import MemoryMechanism
from src.models import Domain
from src.extraction import extract
 
# Einheitsdomäne für den Benchmark
BENCH_DOMAIN = Domain.GENERAL
 
def ingest_session(mech: MemoryMechanism, session: list[dict], session_id: str) -> None:
    """Spielt eine Sitzung ein: nur Write-Path, keine Antwortgenerierung.
    Jede User-Nachricht (mit der folgenden Assistant-Antwort als Kontext) wird
    zur Extraktion gegeben."""
    for i, msg in enumerate(session):
        if msg["role"] != "user":
            continue
        assistant = ""
        if i + 1 < len(session) and session[i + 1]["role"] == "assistant":
            assistant = session[i + 1]["content"]
        convo = f"User: {msg['content']}\nAssistant: {assistant}"
        for cand in extract(convo, mech.cfg, mech.llm):
            cand.domain = BENCH_DOMAIN          # Einheitsdomäne erzwingen
            mech.mgmt.integrate(cand, session_id=session_id)
 
 
def answer_question(mech: MemoryMechanism, question: str,
                    full_history: str | None = None) -> str:
    """Read-Path. Bei full_history wird die gesamte Historie ungefiltert genutzt
    (Baseline Full-Context); bei mode 'none' bleibt der Kontext leer."""
    mode = mech.cfg.retrieval_mode
    if mode == "none":
        context = ""
    elif mode == "full_context":
        context = full_history or ""
    else:
        context = mech.retr.build_context(question, query_domain=None)
    system = ("Du bist ein hilfreicher Assistent. Nutze den folgenden gespeicherten "
              "Kontext, wenn er relevant ist. Wenn die Information fehlt, sage das ehrlich:\n\n"
              + context)
    return mech.llm.complete(system, question)
 
 
def _history_text(item: dict) -> str:
    """Baut die gesamte Sitzungshistorie als Fließtext (für Full-Context)."""
    teile = []
    for i, session in enumerate(item["haystack_sessions"]):
        teile.append(f"# Sitzung {i+1}")
        for msg in session:
            teile.append(f"{msg['role'].capitalize()}: {msg['content']}")
    return "\n".join(teile)
 
 
def run_question(item: dict, cfg: MemoryConfig) -> dict:
    """Verarbeitet eine LongMemEval-Frage mit frischem, isoliertem Gedächtnis.
    Write-Path nur im Modus 'memory'; Baselines 'none'/'full_context' überspringen ihn."""
    import os, copy, shutil, tempfile
 
    workdir = tempfile.mkdtemp(prefix="lme_")
    q_cfg = copy.copy(cfg)
    q_cfg.sqlite_path = os.path.join(workdir, "memory.sqlite3")
    q_cfg.chroma_path = os.path.join(workdir, "chroma")
 
    try:
        mech = MemoryMechanism(q_cfg)
        full_history = None
        if q_cfg.retrieval_mode == "memory":
            for i, session in enumerate(item["haystack_sessions"]):
                ingest_session(mech, session, session_id=f"{item['question_id']}_s{i}")
        elif q_cfg.retrieval_mode == "full_context":
            full_history = _history_text(item)
        # 'none' braucht weder Ingest noch Historie
        hypothesis = answer_question(mech, item["question"], full_history=full_history)
    finally:
        try:
            from chromadb.api.shared_system_client import SharedSystemClient
            SharedSystemClient.clear_system_cache()
        except Exception:
            pass
        shutil.rmtree(workdir, ignore_errors=True)
 
    return {
        "question_id": item["question_id"],
        "question_type": item["question_type"],
        "question": item["question"],
        "gold": item["answer"],
        "hypothesis": hypothesis,
        "config_fingerprint": q_cfg.fingerprint(),   # Reproduzierbarkeit
    }
