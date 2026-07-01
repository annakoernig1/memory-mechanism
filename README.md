# Persistenter Memory-Mechanismus — Prototyp

Proof-of-Concept zur Masterarbeit. Vier-Schichten-Architektur (Kap. 4.3),
dualer Speicher (ChromaDB + SQLite), fünfstufiges Retrieval, typspezifischer Decay.

## Setup
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # API-Schlüssel eintragen
pytest -q                       # walking skeleton läuft im dryrun (ohne Schlüssel)
```

## Reproduzierbarkeit (Kap. 6.1.6)
`config.MemoryConfig.llm_model` mit EXAKTEM Versions-Snapshot füllen, dann
`pip freeze > requirements.lock`. `cfg.fingerprint()` in jedes Eval-Log schreiben.

## Ablationen (Kap. 6.1.4) — kein Codeumbau nötig
| Hypothese | Aufruf |
|---|---|
| Vollsystem | `MemoryConfig.vollsystem()` |
| H4 ohne typspez. Decay | `MemoryConfig.ablation(enable_typed_decay=False)` |
| H5 ohne dualen Store | `MemoryConfig.ablation(enable_dual_store=False)` |
| H6 nur ADD | `MemoryConfig.ablation(enable_llm_op_selection=False)` |
| H7 ohne Segmentierung | `MemoryConfig.ablation(enable_segmentation=False)` |

## Build-Reihenfolge
- **3a** Fundament: `config`, `models`, `storage/*`, `decay` → `pytest` grün (walking skeleton).
- **3b** Vertiefung: `extraction` (Few-Shot, Validierung), `management._choose_operation`
  (LLM-Vergleich, UPDATE/MERGE), Decay-Job, Token-Budget in `retrieval`.
- **3c** Integration: `app.py` (Streamlit-Demo), Demonstrationsszenario.
- **4** Evaluation: `eval/adapter.py` an LongMemEval-Harness anschließen.
