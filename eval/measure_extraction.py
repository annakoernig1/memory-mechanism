from dotenv import load_dotenv
load_dotenv()
 
from collections import defaultdict
from config import MemoryConfig
from src.llm import LLMClient
from src.extraction import extract
from eval.extraction_testset import TESTSET
 
TYPEN = ["STABLE_FACT", "DYNAMIC_STATE", "PREFERENCE", "EPISODE", "GOAL"]
 
cfg = MemoryConfig(); cfg.llm_provider = "anthropic"
llm = LLMClient(cfg)
 
# tp/fp/fn je Typ zählen (satzweise auf Typ-Ebene)
tp = defaultdict(int); fp = defaultdict(int); fn = defaultdict(int)
exakt = 0
 
for text, erwartet in TESTSET:
    erkannt = {k.type.value for k in extract(f"User: {text}", cfg, llm)}
    if erkannt == erwartet:
        exakt += 1
    for typ in TYPEN:
        if typ in erkannt and typ in erwartet: tp[typ] += 1
        elif typ in erkannt and typ not in erwartet: fp[typ] += 1
        elif typ not in erkannt and typ in erwartet: fn[typ] += 1
 
def prf(t):
    p = tp[t] / (tp[t] + fp[t]) if (tp[t] + fp[t]) else 0.0
    r = tp[t] / (tp[t] + fn[t]) if (tp[t] + fn[t]) else 0.0
    f = 2*p*r / (p + r) if (p + r) else 0.0
    return p, r, f
 
print(f"{'Typ':<15} {'TP':>3} {'FP':>3} {'FN':>3} {'Prec':>6} {'Recall':>7} {'F1':>6}")
print("-" * 52)
for t in TYPEN:
    p, r, f = prf(t)
    print(f"{t:<15} {tp[t]:>3} {fp[t]:>3} {fn[t]:>3} {p:>6.0%} {r:>7.0%} {f:>6.2f}")
print("-" * 52)
print(f"Exakte Satz-Übereinstimmung: {exakt}/{len(TESTSET)} = {exakt/len(TESTSET):.0%}")