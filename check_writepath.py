from dotenv import load_dotenv
load_dotenv()
 
from config import MemoryConfig
from src.orchestrator import MemoryMechanism
from src.models import MemoryType, Domain
 
cfg = MemoryConfig()
cfg.llm_provider = "anthropic"
mech = MemoryMechanism(cfg)
 
# eine Aussage, aus der etwas Speicherwürdiges zu extrahieren ist:
mech.respond("Ich trainiere am liebsten früh morgens und hasse Intervalltraining.",
             domain=Domain.TRAINING, session_id="s1")
 
# jetzt nachsehen, was der Write-Path im Fact Store und im Vektor-Store abgelegt hat:
print("\n--- Fact Store (Typ 1/2/5) ---")
for t in (MemoryType.STABLE_FACT, MemoryType.DYNAMIC_STATE, MemoryType.GOAL):
    for it in mech.facts.all_of_types([t]):
        print(f"[{it.type.value}] {it.content}  (conf={it.confidence})")
 
print("\n--- Vektor-Store (Typ 3/4), Testabfrage 'Trainingszeit' ---")
for hit in mech.vectors.query("Trainingszeit Präferenz", top_k=5):
    print(f"[{hit['metadata']['type']}] {hit['document']}  (sim={hit['similarity']:.2f})")