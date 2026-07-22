from dotenv import load_dotenv; load_dotenv()
from config import MemoryConfig
from src.orchestrator import MemoryMechanism
from src.decay import current_weight
from src.models import MemoryItem, MemoryType, Domain
from datetime import datetime, timezone, timedelta
import os, shutil
 
for p in ("memory.sqlite3",):
    if os.path.exists(p): os.remove(p)
if os.path.isdir(".chroma"): shutil.rmtree(".chroma")
 
cfg = MemoryConfig()
 
# Kontrollrechnung: ein Eintrag, dessen letzter Zugriff 30 Tage zurückliegt
alt = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
probe = MemoryItem(content="Test", type=MemoryType.PREFERENCE,
                   domain=Domain.GENERAL, confidence=0.9, last_accessed=alt)
print("Erwartetes Gewicht nach 30 Tagen:", round(current_weight(probe, cfg), 3))
 
# End-to-End: frisch gespeichert -> nahe 1.0 (Delta t ~ 0)
m = MemoryMechanism(cfg)
m.respond("Ich schwimme am liebsten im Freiwasser.", session_id="t1")
hits = m.vectors.query("Schwimmen", top_k=3)
for h in hits:
    print(h["metadata"]["type"], "decay_weight =", round(h["metadata"]["decay_weight"], 3))
 