"""Intercoder-Reliabilität (Kap. 6): Cohens Kappa (je Typ + gesamt) und
Krippendorffs Alpha über binäre (Aussage x Typ)-Entscheidungen.
Mehrfachkodierung ist zulässig -> jede Aussage ist eine MENGE von Typen.
SET 1 (Pilot) fließt NICHT in Kappa ein; er dient der Regelpräzisierung (v1.1).
SET 2 (Haupt) ist die Grundlage für Kappa und Alpha."""
from __future__ import annotations
from sklearn.metrics import cohen_kappa_score
 
TYPEN = ["SF", "DS", "PR", "EP", "GO"]   # STABLE_FACT, DYNAMIC_STATE, PREFERENCE, EPISODE, GOAL
 
# ============================================================
# SET 2 – HAUPTKODIERUNG  (je Aussage eine Menge von Typen; set() = keine)
# ============================================================
coder_A_haupt = [
    {"SF"},{"SF"},{"SF"},{"DS"},{"DS"},{"DS"},{"PR"},{"PR"},{"PR"},{"EP"},
    {"EP"},{"EP"},{"GO"},{"GO"},{"GO"},set(),set(),set(),{"SF","DS"},{"PR","DS"},
]
coder_B_haupt = [
    {"SF"},{"SF"},{"SF"},{"DS"},{"DS"},{"DS"},{"PR"},{"PR"},{"PR"},{"EP"},
    {"EP"},{"EP"},{"GO"},{"GO"},{"GO"},set(),set(),set(),{"SF","DS"},{"PR","DS"},
]
 
# ============================================================
# SET 1 – PILOT  (nur zur Dokumentation der Divergenzen -> Manual v1.1)
# ============================================================
coder_A_pilot = [
    {"SF"},{"DS"},{"PR"},{"EP"},{"GO"},set(),set(),{"DS"},{"PR"},
]
coder_B_pilot = [
    {"SF","DS"},{"DS","EP"},{"PR"},{"EP"},{"GO"},{"PR"},{"GO"},{"EP"},{"PR"},
]
 
# ---------- Hilfsfunktionen ----------
def binaer(coder_sets):
    """(Aussage x Typ) -> flache 0/1-Liste, Reihenfolge stabil."""
    return [1 if t in s else 0 for s in coder_sets for t in TYPEN]
 
def krippendorff_alpha_nominal(units):
    """units: Liste von Werte-Listen je Einheit (hier je Einheit 2 Werte: A,B)."""
    from collections import defaultdict
    o = defaultdict(float); werte = set()
    for u in units:
        r = [x for x in u if x is not None]; m = len(r)
        if m < 2: continue
        for i in range(m):
            for j in range(m):
                if i != j: o[(r[i], r[j])] += 1.0/(m-1)
        werte.update(r)
    werte = sorted(werte)
    n_c = {c: sum(o[(c,k)] for k in werte) for c in werte}
    n = sum(n_c.values())
    if n <= 1: return float("nan")
    A = sum(o[(c,k)] for c in werte for k in werte if c != k)
    B = sum(n_c[c]*n_c[k] for c in werte for k in werte if c != k)
    if B == 0: return 1.0
    return 1 - (n-1)*A/B
 
# ---------- Auswertung SET 2 (Haupt) ----------
a_all = binaer(coder_A_haupt)
b_all = binaer(coder_B_haupt)
 
print("="*64)
print("SET 2 – HAUPTKODIERUNG  (n =", len(coder_A_haupt), "Aussagen)")
print("="*64)
print(f"\nCohens Kappa (gesamt, ueber alle Typ-Entscheidungen): {cohen_kappa_score(a_all, b_all):.3f}")
 
# Krippendorffs Alpha gesamt (Einheiten = jede (Aussage x Typ)-Entscheidung)
units_all = [[a, b] for a, b in zip(a_all, b_all)]
print(f"Krippendorffs Alpha (gesamt, nominal):               {krippendorff_alpha_nominal(units_all):.3f}")
 
print("\nJe Informationstyp:")
for t in TYPEN:
    ai = [1 if t in s else 0 for s in coder_A_haupt]
    bi = [1 if t in s else 0 for s in coder_B_haupt]
    try:
        k = cohen_kappa_score(ai, bi)
        k = f"{k:.3f}"
    except Exception:
        k = "n.def."
    al = krippendorff_alpha_nominal([[a, b] for a, b in zip(ai, bi)])
    print(f"  {t:<4} Kappa={k:<7} Alpha={al:.3f}")
 
# ---------- SET 1 (Pilot): Divergenzen dokumentieren ----------
print("\n" + "="*64)
print("SET 1 – PILOT: Divergenzen (Grundlage fuer Manual v1.1)")
print("="*64)
div = 0
for i,(a,b) in enumerate(zip(coder_A_pilot, coder_B_pilot), 1):
    mark = "" if a==b else "   <-- DIVERGENZ"
    if a!=b: div += 1
    A = "{"+", ".join(sorted(a))+"}" if a else "(keine)"
    B = "{"+", ".join(sorted(b))+"}" if b else "(keine)"
    print(f"  P{i}: Person1={A:<14} Person2={B:<14}{mark}")
print(f"\n  Divergenzen im Pilot: {div}/{len(coder_A_pilot)}")