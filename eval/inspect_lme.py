import json, os
path = "data/longmemeval_oracle.json"
data = json.load(open(path))
print("Anzahl Fragen:", len(data))
bsp = data[0]
print("\nSchlüssel je Frage:", list(bsp.keys()))
print("\nFrage:", bsp.get("question"))
print("Antwort (gold):", bsp.get("answer"))
print("Frage-Typ:", bsp.get("question_type"))
sessions = bsp.get("haystack_sessions") or bsp.get("sessions")
print("\nAnzahl Sitzungen:", len(sessions))
print("Erste Sitzung (Auszug):", json.dumps(sessions[0][:2], ensure_ascii=False, indent=2)[:600])