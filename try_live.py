from dotenv import load_dotenv
load_dotenv()  # liest den Schlüssel aus .env
 
from config import MemoryConfig
from src.orchestrator import MemoryMechanism
from src.models import ExtractionCandidate, MemoryType, Domain
 
cfg = MemoryConfig()                 # Vollsystem
cfg.llm_provider = "anthropic"       # vom dryrun auf echtes Claude umstellen
 
mech = MemoryMechanism(cfg)
 
# eine stabile Information ablegen (Fact Store, kein Embedding nötig)
mech.mgmt.integrate(ExtractionCandidate(
    content="Marathon-Bestzeit 3:12 h", type=MemoryType.STABLE_FACT,
    domain=Domain.TRAINING, confidence=0.95, key="marathon_pb", value="3:12 h"))
 
# jetzt eine Frage stellen – der Mechanismus baut den Kontext und fragt Claude
antwort = mech.respond("Was ist meine Marathon-Bestzeit und wie ordnest du sie ein?",
                       domain=Domain.TRAINING, session_id="s1")
print("\n--- Antwort ---\n", antwort)