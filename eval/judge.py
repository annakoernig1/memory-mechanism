"""LLM-as-Judge: bewertet Hypothesen gegen Gold-Antworten und vergleicht
die Urteile mit den manuellen Labels (ratings_oracle.json)."""
from dotenv import load_dotenv
load_dotenv()
import json, os, re
import sys
from config import MemoryConfig
from src.llm import LLMClient

RESULTS = sys.argv[1] if len(sys.argv) > 1 else "eval/results_oracle.json"
RATINGS = sys.argv[2] if len(sys.argv) > 2 else "eval/ratings_oracle.json"
OUT     = sys.argv[3] if len(sys.argv) > 3 else "eval/judge_oracle.json"
 
JUDGE_SYSTEM = (
    "Du bist ein strenger, neutraler Bewerter für ein Frage-Antwort-System. "
    "Dir werden eine Frage, eine Referenzantwort (Gold) und eine zu bewertende "
    "Antwort (Hypothese) vorgelegt. Beurteile ausschließlich die INHALTLICHE "
    "Übereinstimmung mit der Referenzantwort, nicht Formulierung, Länge oder Sprache. "
    "Die Hypothese ist KORREKT, wenn sie die in der Referenzantwort geforderte "
    "Kerninformation sachlich richtig enthält (auch wenn sie zusätzlich erklärt "
    "oder in anderer Sprache formuliert ist). Sie ist FALSCH, wenn die Kerninformation "
    "fehlt, verfehlt oder erfunden ist. "
    "Antworte NUR mit einem JSON-Objekt der Form "
    '{"urteil": "korrekt"|"falsch", "begruendung": "<max. ein Satz>"}. '
    "Kein weiterer Text, keine Codezäune."
)
 
def build_prompt(item):
    return (f"Frage:\n{item['question']}\n\n"
            f"Referenzantwort (Gold):\n{item['gold']}\n\n"
            f"Zu bewertende Antwort (Hypothese):\n{item['hypothesis']}")
 
def parse(txt):
    txt = re.sub(r"^```(?:json)?|```$", "", txt.strip(), flags=re.M).strip()
    m = re.search(r"\{.*\}", txt, flags=re.S)
    return json.loads(m.group(0)) if m else {"urteil": "?", "begruendung": txt[:80]}
 
cfg = MemoryConfig(); cfg.llm_provider = "anthropic"
llm = LLMClient(cfg)
results = json.load(open(RESULTS))
manual  = json.load(open(RATINGS)) if os.path.exists(RATINGS) else {}
 
judged, agree, comparable = [], 0, 0
for r in results:
    raw = llm.complete(JUDGE_SYSTEM, build_prompt(r))
    verdict = parse(raw)
    j = verdict.get("urteil", "?")
    rec = {"question_id": r["question_id"], "judge": j,
           "begruendung": verdict.get("begruendung", "")}
    # Vergleich mit manuellem Label (teilweise -> als korrekt gewertet)
    man = manual.get(r["question_id"], {}).get("urteil")
    if man:
        man_bin = "korrekt" if man in ("korrekt", "teilweise") else "falsch"
        rec["manuell"] = man_bin
        comparable += 1
        if man_bin == j:
            agree += 1
    judged.append(rec)
    print(f"{r['question_id']:<16} Judge={j:<8} Manuell={rec.get('manuell','-')}")
 
json.dump(judged, open(OUT, "w"), ensure_ascii=False, indent=2)
print("\n" + "=" * 60)
if comparable:
    print(f"Übereinstimmung Judge vs. manuell: {agree}/{comparable} "
          f"({100*agree/comparable:.0f}%)")
print(f"Gespeichert: {OUT}")