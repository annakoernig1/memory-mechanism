from dotenv import load_dotenv
load_dotenv()
 
from config import MemoryConfig
from src.llm import LLMClient
from src.extraction import extract
 
cfg = MemoryConfig()
cfg.llm_provider = "anthropic"
llm = LLMClient(cfg)
 
konversation = ("User: Ich hab chronisch Probleme mit der Achillessehne, deshalb keine "
                "Sprints. Aber diese Woche fühl ich mich richtig stark. Nächstes Jahr "
                "will ich die Challenge Roth finishen.\n"
                "Assistant: Notiert, wir planen entsprechend.")
 
kandidaten = extract(konversation, cfg, llm)
print("Anzahl extrahierter Kandidaten:", len(kandidaten))
for k in kandidaten:
    print(f"- [{k.type.value}] {k.content}  conf={k.confidence} domain={k.domain.value}")

from src.extraction import _SYSTEM
roh = llm.complete(_SYSTEM, konversation, json_mode = True)
print("\n--- ROHANTWORT DES MODELLS ---\n", repr(roh))