"""Layer 1 – Memory Extraction (Kap. 4.3.1.1).
LLM extrahiert speicherwürdige Infos als JSON. Schwelle: conf>=0.6 wird gespeichert,
0.4–0.6 als Kandidat markiert.
TODO(Phase 3b): Few-Shot-Beispiele je Typ in den Prompt aufnehmen und Extraktion
gegen ein handgelabeltes Set validieren (Precision/Recall statt blindem Vertrauen
auf die selbstberichtete confidence – vgl. kritische Anmerkung Kap. 4)."""
from __future__ import annotations
import json
from config import MemoryConfig
from src.llm import LLMClient
from src.models import ExtractionCandidate, MemoryType, Domain

_SYSTEM = """Du extrahierst speicherwürdige, nutzerbezogene Informationen aus einer
Konversation für das Langzeitgedächtnis eines KI-Coaches. Gib AUSSCHLIESSLICH ein
JSON-Objekt zurück, ohne Codezäune und ohne erklärenden Text:
{"memories":[{"content","type","domain","confidence","key","value","entities"}]}
 
TYPEN (mit Abgrenzung):
- STABLE_FACT: dauerhaft gültige Fakten (Alter, Sportart, chronische Erkrankung, Ausrüstung).
- DYNAMIC_STATE: aktueller, zeitlich begrenzter Zustand (aktuelle Verletzung, Tagesform, Trainingsphase).
- PREFERENCE: stabile Vorliebe/Abneigung (Trainingszeit, Kommunikationsstil, Ernährungspräferenz).
- EPISODE: konkretes vergangenes Ereignis mit Zeitbezug (ein bestimmtes Rennen, eine einzelne Einheit).
- GOAL: zielgerichtete, terminierte Absicht (Wettkampfziel, Zielzeit mit Datum).
 
domain ∈ TRAINING | HEALTH | NUTRITION | PERSONAL. confidence ∈ [0,1].
Nur speichern, was über die aktuelle Sitzung hinaus relevant ist. Keine Spekulation.
Wenn nichts Speicherwürdiges vorliegt: {"memories":[]}.
 
BEISPIELE:
Eingabe: "Ich bin 34 und laufe seit 10 Jahren Triathlon."
Ausgabe: {"memories":[
{"content":"34 Jahre alt","type":"STABLE_FACT","domain":"PERSONAL","confidence":0.98,"key":"alter","value":"34","entities":["Alter"]},
{"content":"Betreibt seit 10 Jahren Triathlon","type":"STABLE_FACT","domain":"TRAINING","confidence":0.95,"key":"sportart","value":"Triathlon","entities":["Triathlon"]}]}
 
Eingabe: "Mein Knie zwickt seit dem Wochenende, ich muss kürzertreten."
Ausgabe: {"memories":[
{"content":"Akute Kniebeschwerden seit dem Wochenende","type":"DYNAMIC_STATE","domain":"HEALTH","confidence":0.9,"key":"knie_status","value":"beschwerden","entities":["Knie"]}]}
 
Eingabe: "Ich will im Oktober meinen ersten Marathon unter 3:30 laufen."
Ausgabe: {"memories":[
{"content":"Zielrennen: erster Marathon im Oktober unter 3:30","type":"GOAL","domain":"TRAINING","confidence":0.95,"key":"ziel_marathon","value":"sub 3:30, Oktober","entities":["Marathon","Oktober"]}]}
 
Eingabe: "Letzten Sonntag hatte ich einen richtig guten langen Lauf, 30 km locker."
Ausgabe: {"memories":[
{"content":"Guter langer Lauf über 30 km am vergangenen Sonntag","type":"EPISODE","domain":"TRAINING","confidence":0.85,"key":null,"value":null,"entities":["langer Lauf","30 km"]}]}
 
Eingabe: "Danke, das hilft mir weiter!"
Ausgabe: {"memories":[]}
"""
 

def _parse_memories(raw: str) -> list:
    import re, json
    text = re.sub(r"```(?:json)?", "", raw).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        print("[extraction] Keine JSON-Struktur in der Antwort gefunden.")
        return []
    try:
        return json.loads(text[start:end + 1]).get("memories", [])
    except json.JSONDecodeError as e:
        print(f"[extraction] JSON-Fehler: {e}\nRohtext war:\n{raw[:500]}")
        return []

def extract(conversation: str, cfg: MemoryConfig, llm: LLMClient) -> list[ExtractionCandidate]:
    raw = llm.complete(_SYSTEM, conversation, json_mode=True)
    data = _parse_memories(raw)
    lo, hi = cfg.candidate_band
    out = []
    for m in data:
        try:
            conf = float(m.get("confidence", 0))
            if conf < lo:
                continue
            out.append(ExtractionCandidate(
                content=m["content"], type=MemoryType(m["type"]),
                domain=Domain(m.get("domain", "PERSONAL")), confidence=conf,
                key=m.get("key"), value=m.get("value"),
                entities=m.get("entities", []), is_candidate=(conf < hi)))
        except (ValueError, KeyError, TypeError) as e:
            print(f"[extraction] Ungültiger Eintrag übersprungen ({type(e).__name__}): "
                  f"{str(m)[:120]}")
            continue
    return out
