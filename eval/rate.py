"""Manuelle Bewertung der Hypothesen gegen die Gold-Antworten.
Urteile: [k]orrekt / [t]eilweise / [f]alsch / [s]kip.
Fortschritt wird laufend gespeichert; erneutes Starten setzt fort."""
import json, os
import sys

RESULTS = sys.argv[1] if len(sys.argv) > 1 else "eval/results_oracle.json"
RATINGS = sys.argv[2] if len(sys.argv) > 2 else "eval/ratings_oracle.json"
print(f"Bewerte: {RESULTS}  ->  {RATINGS}")
 
results = json.load(open(RESULTS))
ratings = {}
if os.path.exists(RATINGS):
    ratings = json.load(open(RATINGS))
 
MAP = {"k": "korrekt", "t": "teilweise", "f": "falsch"}
 
for idx, r in enumerate(results, 1):
    qid = r["question_id"]
    if qid in ratings:                      # bereits bewertet -> überspringen
        continue
    print("\n" + "=" * 78)
    print(f"[{idx}/{len(results)}]  Typ: {r['question_type']}")
    print(f"\nFrage:  {r['question']}")
    print(f"\nGold:   {r['gold']}")
    print(f"\nHypo:   {r['hypothesis']}")
    print("-" * 78)
    while True:
        a = input("Urteil  [k]orrekt / [t]eilweise / [f]alsch / [s]kip / [q]uit: ").strip().lower()
        if a in ("k", "t", "f"):
            note = input("Notiz (optional, Enter zum Überspringen): ").strip()
            ratings[qid] = {"urteil": MAP[a], "notiz": note,
                            "question_type": r["question_type"]}
            json.dump(ratings, open(RATINGS, "w"), ensure_ascii=False, indent=2)
            break
        if a == "s":
            break
        if a == "q":
            print("\nGespeichert. Fortsetzen durch erneutes Starten.")
            raise SystemExit
        print("Bitte k, t, f, s oder q eingeben.")
 
# Zusammenfassung
print("\n" + "=" * 78)
print("ZWISCHENSTAND")
from collections import Counter
c = Counter(v["urteil"] for v in ratings.values())
for k in ("korrekt", "teilweise", "falsch"):
    print(f"  {k:<10}: {c.get(k, 0)}")
print(f"  bewertet  : {len(ratings)}/{len(results)}")