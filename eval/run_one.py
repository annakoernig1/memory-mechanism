from dotenv import load_dotenv
load_dotenv()
import json
from config import MemoryConfig
from eval.adapter import run_question
 
data = json.load(open("data/longmemeval_oracle.json"))
item = data[0]                      # erste Frage (temporal-reasoning)
 
cfg = MemoryConfig()
cfg.llm_provider = "anthropic"
 
print(f"Frage:   {item['question']}")
print(f"Gold:    {item['answer']}")
print(f"Typ:     {item['question_type']}")
print(f"Sitzungen: {len(item['haystack_sessions'])}\n... Mechanismus läuft ...\n")
 
result = run_question(item, cfg)
print("Hypothese:", result["hypothesis"])