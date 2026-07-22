"""Geschichteter Probelauf über longmemeval_s: pro Fragetyp k Fragen,
reproduzierbar (fester Seed). Speichert nach JEDER Frage, damit ein
Abbruch nichts kostet und ein Neustart dort fortsetzt, wo er aufhörte."""
from dotenv import load_dotenv
load_dotenv()
import json, time, os, random, collections
from config import MemoryConfig
from eval.adapter import run_question
 
DATASET = "data/longmemeval_s.json"
OUT     = "eval/results_s.json"
PER_TYPE = 1        # Fragen pro Fragetyp  (Probelauf: 1  ->  großer Lauf: höher setzen)
SEED     = 42       # feste Auswahl -> reproduzierbar
 
# ---- geschichtete Stichprobe ziehen ----
data = json.load(open(DATASET))
by_type = collections.defaultdict(list)
for q in data:
    by_type[q["question_type"]].append(q)
 
rng = random.Random(SEED)
sample = []
for qtype in sorted(by_type):
    pool = by_type[qtype]
    rng.shuffle(pool)
    sample.extend(pool[:PER_TYPE])
print(f"Stichprobe: {len(sample)} Fragen über {len(by_type)} Typen "
      f"({PER_TYPE} je Typ), Seed={SEED}\n")
 
# ---- bereits erledigte Fragen überspringen (Fortsetzbarkeit) ----
results, done = [], set()
if os.path.exists(OUT):
    results = json.load(open(OUT))
    done = {r["question_id"] for r in results}
    print(f"{len(done)} Fragen bereits vorhanden – werden übersprungen.\n")
 
cfg = MemoryConfig(); cfg.llm_provider = "anthropic"
 
for idx, item in enumerate(sample, 1):
    if item["question_id"] in done:
        continue
    t0 = time.time()
    res = run_question(item, cfg)
    res["seconds"] = round(time.time() - t0, 1)
    results.append(res)
    json.dump(results, open(OUT, "w"), ensure_ascii=False, indent=2)   # nach JEDER Frage
    print(f"[{idx}/{len(sample)}] {res['question_type']:<26} "
          f"({res['seconds']}s, {res['seconds']/60:.1f} min)")
 
print(f"\nGespeichert: {OUT}")
print("\n" + "=" * 80)
for r in results:
    print(f"\nTyp:   {r['question_type']}")
    print(f"Frage: {r['question']}")
    print(f"Gold:  {r['gold']}")
    print(f"Hypo:  {r['hypothesis'][:300]}")