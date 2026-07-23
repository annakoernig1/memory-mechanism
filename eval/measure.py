"""Ergänzende Messung für NFA-01 (Latenz) und NFA-02 (Tokenverbrauch).
Zwei sauber getrennte Größen:
  (1) Read-Path-Retrieval-Latenz: NUR build_context() — lokal, ohne LLM, ohne Netz.
      Das ist die Größe, auf die sich NFA-01 (< 500 ms) bezieht.
  (2) Tokenverbrauch: input/output je API-Aufruf, getrennt nach Read-Path
      (Antwortgenerierung) und Write-Path (Extraktion), aus msg.usage.
 
Kleine, illustrative Stichprobe. Aufruf:  python -m eval.measure
Kopiere die Datei nach eval/measure.py."""
from dotenv import load_dotenv
load_dotenv()
import os, time, json, statistics, tempfile, shutil
from config import MemoryConfig
from src.orchestrator import MemoryMechanism
from src.models import ExtractionCandidate, MemoryType, Domain
from src.extraction import _SYSTEM as EXTRACTION_SYSTEM
 
# --- Einige realistische Test-Seeds, damit der Speicher nicht leer ist ---
SEEDS = [
    ("Nutzer trainiert für einen Triathlon im September.", MemoryType.GOAL, Domain.TRAINING),
    ("Nutzer bevorzugt Intervalltraining am Morgen.", MemoryType.PREFERENCE, Domain.TRAINING),
    ("Nutzer hatte letzte Woche eine Erkältung.", MemoryType.DYNAMIC_STATE, Domain.HEALTH),
    ("Nutzer ist 34 Jahre alt und läuft seit 5 Jahren.", MemoryType.STABLE_FACT, Domain.PERSONAL),
    ("Nutzer lief den letzten 10-km-Lauf in 48 Minuten.", MemoryType.EPISODE, Domain.TRAINING),
]
QUERIES = [
    "Wie soll ich diese Woche mein Lauftraining gestalten?",
    "Worauf soll ich bei der Wettkampfvorbereitung achten?",
    "Wie kann ich meine 10-km-Zeit verbessern?",
    "Was ist bei Training nach einer Erkältung zu beachten?",
    "Wie strukturiere ich meine Trainingswoche sinnvoll?",
]
N_WIEDERHOLUNGEN = 20   # für die Latenz-Statistik (lokal, günstig)
 
# Realistische Dialogausschnitte für die Write-Path-Messung (echte Extraktion).
# So enthält der Write-Path-Output tatsächlich extrahierte Einträge statt einer Leerantwort.
WRITE_DIALOGE = [
    ("User: Ich bin 34 und trainiere für meinen ersten Triathlon im September. "
     "Morgens laufe ich am liebsten, abends fühle ich mich schlapp.\n"
     "Assistant: Super, dann legen wir den Fokus auf morgendliche Läufe und einen "
     "strukturierten Aufbau bis September."),
    ("User: Letzte Woche hatte ich eine Erkältung und musste pausieren. Jetzt bin ich "
     "wieder fit und will durchstarten, am liebsten jeden Tag hart.\n"
     "Assistant: Nach einer Erkältung steigern wir behutsam; komplette Ruhetage bleiben wichtig."),
    ("User: Meinen letzten 10-km-Lauf bin ich in 48 Minuten gelaufen. Mein Ziel sind "
     "unter 45 Minuten bis zum Herbst.\n"
     "Assistant: 48 Minuten sind eine gute Basis; mit Intervalltraining ist Sub-45 realistisch."),
    ("User: Ich mag kein Schwimmen im Freiwasser, im Becken ist es okay. Radfahren liebe ich.\n"
     "Assistant: Dann planen wir Beckentraining für die Technik und nutzen deine Stärke auf dem Rad."),
    ("User: Ich wohne in München und arbeite Vollzeit, unter der Woche habe ich nur abends Zeit.\n"
     "Assistant: Wir legen die langen Einheiten aufs Wochenende und halten die Woche kurz und intensiv."),
]
 
 
def _fresh_mech():
    wd = tempfile.mkdtemp(prefix="measure_")
    cfg = MemoryConfig(); cfg.llm_provider = "anthropic"
    cfg.sqlite_path = os.path.join(wd, "m.sqlite3")
    cfg.chroma_path = os.path.join(wd, "chroma")
    mech = MemoryMechanism(cfg)
    for content, typ, dom in SEEDS:
        mech.mgmt.integrate(ExtractionCandidate(content=content, type=typ,
                            domain=dom, confidence=0.9), session_id="seed")
    return mech, wd, cfg
 
 
def messung_latenz(mech):
    """Reine Retrieval-Latenz von build_context() — lokal, ohne LLM."""
    zeiten = []
    for _ in range(N_WIEDERHOLUNGEN):
        for q in QUERIES:
            t0 = time.perf_counter()
            mech.retr.build_context(q, Domain.TRAINING)
            zeiten.append((time.perf_counter() - t0) * 1000.0)  # ms
    return zeiten
 
 
def messung_token(cfg, mech):
    """Tokenverbrauch je API-Aufruf, getrennt Read-Path (Antwort) und Write-Path (Extraktion)."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
 
    def call(system, user):
        msg = client.messages.create(
            model=cfg.llm_model, max_tokens=4096,
            system=[{"type": "text", "text": system}],
            messages=[{"role": "user", "content": user}],
        )
        return msg.usage.input_tokens, msg.usage.output_tokens
 
    read_in, read_out, write_in, write_out = [], [], [], []
    # Read-Path: Antwortgenerierung mit zusammengebautem Kontext
    for q in QUERIES:
        context = mech.retr.build_context(q, Domain.TRAINING)
        system = ("Du bist ein KI-Coach. Nutze den folgenden gespeicherten Kontext, "
                  "wenn er relevant ist:\n\n" + context)
        i, o = call(system, q)
        read_in.append(i); read_out.append(o)
    # Write-Path: echte Extraktion an realistischen Dialogausschnitten
    for convo in WRITE_DIALOGE:
        i2, o2 = call(EXTRACTION_SYSTEM, convo)
        write_in.append(i2); write_out.append(o2)
    return read_in, read_out, write_in, write_out
 
 
def stat(xs):
    return {"median": round(statistics.median(xs), 1),
            "mittel": round(statistics.mean(xs), 1),
            "min": round(min(xs), 1), "max": round(max(xs), 1),
            "stdabw": round(statistics.pstdev(xs), 1) if len(xs) > 1 else 0.0}
 
 
def main():
    mech, wd, cfg = _fresh_mech()
    try:
        print("== (1) Read-Path-Retrieval-Latenz (nur build_context, lokal) ==")
        lat = messung_latenz(mech)
        s = stat(lat)
        print(f"   n={len(lat)} Messungen  |  Median {s['median']} ms  "
              f"(Mittel {s['mittel']}, min {s['min']}, max {s['max']}, SD {s['stdabw']})")
        print(f"   NFA-01 (< 500 ms) erfüllt: {'JA' if s['median'] < 500 else 'NEIN'}")
 
        print("\n== (2) Tokenverbrauch je Anfrage (aus msg.usage) ==")
        ri, ro, wi, wo = messung_token(cfg, mech)
        print(f"   Read-Path  Input:  {stat(ri)}")
        print(f"   Read-Path  Output: {stat(ro)}")
        print(f"   Write-Path Input:  {stat(wi)}")
        print(f"   Write-Path Output: {stat(wo)}")
        gesamt_in = statistics.mean(ri) + statistics.mean(wi)
        gesamt_out = statistics.mean(ro) + statistics.mean(wo)
        print(f"   Ø gesamt/Anfrage:  ~{round(gesamt_in)} Input + ~{round(gesamt_out)} Output Token")
 
        out = {"latenz_ms": s, "n_latenz": len(lat),
               "token": {"read_in": stat(ri), "read_out": stat(ro),
                         "write_in": stat(wi), "write_out": stat(wo)}}
        json.dump(out, open("eval/results_measure.json", "w"), ensure_ascii=False, indent=2)
        print("\nGespeichert: eval/results_measure.json")
    finally:
        try:
            from chromadb.api.shared_system_client import SharedSystemClient
            SharedSystemClient.clear_system_cache()
        except Exception:
            pass
        shutil.rmtree(wd, ignore_errors=True)
 
 
if __name__ == "__main__":
    main()