#!/usr/bin/env python3
"""Réévalue les patchs déjà produits (aucun appel LLM) : utile quand l'évaluateur change.

Usage : PSB=n python3 bench/reeval.py runs/<run_A> [runs/<run_B> …]
Écrit <run>/<pr>/result_reeval.json et affiche le tableau.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval import evaluate

for run in sys.argv[1:]:
    for d in sorted(Path(run).iterdir()):
        p = d / "patch.diff"
        if not d.is_dir() or not p.exists():
            continue
        r = evaluate(int(d.name), str(p)) if p.read_text().strip() else {"pr": int(d.name), "applied": False, "fixed": False, "regression": None}
        (d / "result_reeval.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
        print(run, json.dumps({k: r.get(k) for k in ("pr", "applied", "fixed", "regression")}), flush=True)
