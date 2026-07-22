"""Führt EINE benannte Konfiguration über die feste, geschichtete Stichprobe aus.
Aufruf z. B.:  python -m eval.run_config vollsystem 2
Erstes Argument: Konfigurationsname; zweites (optional): Fragen pro Typ."""
from dotenv import load_dotenv
load_dotenv()
import json, time, os, sys, random, collections
from config import MemoryConfig
from eval.adapter import run_question
 
DATASET = "data/longmemeval_s.json"
SEED = 42
 
# ---- verfügbare Konfigurationen (Name -> MemoryConfig) ----
def make_configs():
    return {
        "vollsystem":  MemoryConfig.vollsystem(),
        "no_memory":   MemoryConfig.ablation(retrieval_mode="none"),
        "full_context":MemoryConfig.ablation(retrieval_mode="full_context"),
        "rag_naiv":    MemoryConfig.ablation(enable_dual_store=False,
                                             enable_typed_decay=False,
                                             enable_segmentation=False,
                                             enable_llm_op_selection=False),
        "abl_h4_decay":     MemoryConfig.ablation(enable_typed_decay=False),
        "abl_h5_dualstore": MemoryConfig.ablation(enable_dual_store=False),
        "abl_h6_opsel":     MemoryConfig.ablation(enable_llm_op_selection=False),
        "abl_h7_segment":   MemoryConfig.ablation(enable_segmentation=False),
    }
 
def stratified_sample(data, per_type, seed=SEED):
    by_type = collections.defaultdict(list)
    for q in data:
        by_type[q["question_type"]].append(q)
    rng = random.Random(seed)
    sample = []
    for qtype in sorted(by_type):
        pool = by_type[qtype][:]      # Kopie
        rng.shuffle(pool)
        sample.extend(pool[:per_type])
    return sample
 
def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "vollsystem"
    per_type = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    configs = make_configs()
    if name not in configs:
        print(f"Unbekannte Konfiguration '{name}'. Verfügbar: {', '.join(configs)}")
        sys.exit(1)
    cfg = configs[name]
    cfg.llm_provider = "anthropic"
 
    data = json.load(open(DATASET))
    sample = stratified_sample(data, per_type)
    out = f"eval/results_s_{name}.json"
 
    results, done = [], set()
    if os.path.exists(out):
        results = json.load(open(out))
        done = {r["question_id"] for r in results}
 
    print(f"Konfiguration: {name}  |  {len(sample)} Fragen "
          f"({per_type}/Typ, Seed={SEED})  |  bereits erledigt: {len(done)}\n")
 
    for idx, item in enumerate(sample, 1):
        if item["question_id"] in done:
            continue
        t0 = time.time()
        res = run_question(item, cfg)
        res["seconds"] = round(time.time() - t0, 1)
        res["config_name"] = name
        results.append(res)
        json.dump(results, open(out, "w"), ensure_ascii=False, indent=2)
        print(f"[{idx}/{len(sample)}] {res['question_type']:<26} ({res['seconds']}s)")
 
    print(f"\nGespeichert: {out}")
 
if __name__ == "__main__":
    main()