"""Lädt longmemeval_s (das eigentliche Benchmark-Set) von Hugging Face."""
from huggingface_hub import hf_hub_download
import shutil, os
 
src = hf_hub_download(repo_id="xiaowu0162/longmemeval-cleaned",
                      filename="longmemeval_s_cleaned.json", repo_type="dataset")
os.makedirs("data", exist_ok=True)
shutil.copy(src, "data/longmemeval_s.json")
print("Gespeichert: data/longmemeval_s.json")