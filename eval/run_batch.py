from dotenv import load_dotenv
load_dotenv()
import json, time, os
from config import MemoryConfig
from eval.adapter import run_question
 
N = 10                                   # Anzahl Fragen für diesen Durchlauf
DATASET = "data/longmemeval_oracle.json"
OUT = "eval/results_oracle.json"
 
data = json.load(open(DATASET))[:N]
cfg = MemoryConfig(); cfg.llm_provider = "anthropic"
 
results = []
for idx, item in enumerate(data, 1):
    t0 = time.time()
    res = run_question(item, cfg)
    res["seconds"] = round(time.time() - t0, 1)
    results.append(res)
    print(f"[{idx}/{len(data)}] {res['question_type']:<22} ({res['seconds']}s)")
 
json.dump(results, open(OUT, "w"), ensure_ascii=False, indent=2)
print(f"\nGespeichert: {OUT}")
 
# kompakte Übersicht für die manuelle Sichtung
print("\n" + "=" * 80)
for r in results:
    print(f"\nTyp:   {r['question_type']}")
    print(f"Frage: {r['question']}")
    print(f"Gold:  {r['gold']}")
    print(f"Hypo:  {r['hypothesis'][:300]}")