from dotenv import load_dotenv
load_dotenv()
 
from config import MemoryConfig
from src.llm import LLMClient
from src.extraction import extract
from eval.extraction_testset import TESTSET
 
cfg = MemoryConfig(); cfg.llm_provider = "anthropic"
llm = LLMClient(cfg)
 
treffer = 0
gesamt = len(TESTSET)
print(f"{'Eingabe':<48} {'erwartet':<16} {'erkannt':<16} ok")
print("-" * 90)
for text, erwartet in TESTSET:
    kandidaten = extract(f"User: {text}", cfg, llm)
    erkannt = {k.type.value for k in kandidaten}
    ok = (erkannt == erwartet)
    treffer += ok
    print(f"{text[:46]:<48} {str(sorted(erwartet)):<16} {str(sorted(erkannt)):<16} {'✓' if ok else '✗'}")
 
print("-" * 90)
print(f"Exakte Übereinstimmung: {treffer}/{gesamt} = {treffer/gesamt:.0%}")