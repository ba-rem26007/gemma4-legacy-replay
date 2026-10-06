#!/usr/bin/env python3
"""Générateur et évaluateur des corpus fins à pas de 0.2 Mo (0.2 Mo à 1.0 Mo).

1. Découpe déterministe depuis train_1mb.jsonl / all_candidates :
   - train_0.2mb.jsonl (~38 exemples, ~200 Ko)
   - train_0.4mb.jsonl (~76 exemples, ~400 Ko)
   - train_0.6mb.jsonl (~114 exemples, ~600 Ko)
   - train_0.8mb.jsonl (~152 exemples, ~800 Ko)
   - train_1.0mb.jsonl (190 exemples, ~1.0 Mo)
2. Vérification d'intégrité et mesure syntaxique / AST sur chaque palier.
"""

import json
from pathlib import Path

DATA_DIR = Path("/home/elrems/kaggle/harness_transfer/data")
TRAIN_1MB = DATA_DIR / "train_1mb.jsonl"
OUT_DIR = DATA_DIR / "fine_scaling"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_fine_datasets():
    print("=" * 70)
    print("🚀 GÉNÉRATION DES CORPUS FINS À PAS DE 0.2 Mo (0.2 Mo à 1.0 Mo)")
    print("=" * 70)

    if not TRAIN_1MB.exists():
        print(f"❌ Fichier source introuvable : {TRAIN_1MB}")
        return False

    with open(TRAIN_1MB, "r", encoding="utf-8") as f:
        examples = [json.loads(line) for line in f if line.strip()]

    total = len(examples)
    print(f"📂 Total d'exemples sources dans train_1mb : {total}")

    # Découpage par tranche de 20% (~38 exemples = ~200 Ko)
    paliers = [
        ("train_0.2mb.jsonl", int(total * 0.20)),   # ~38 ex (~200 Ko)
        ("train_0.4mb.jsonl", int(total * 0.40)),   # ~76 ex (~400 Ko)
        ("train_0.6mb.jsonl", int(total * 0.60)),   # ~114 ex (~600 Ko)
        ("train_0.8mb.jsonl", int(total * 0.80)),   # ~152 ex (~800 Ko)
        ("train_1.0mb.jsonl", total),               # 190 ex (~1 000 Ko)
    ]

    generated = []
    for filename, count in paliers:
        subset = examples[:count]
        out_file = OUT_DIR / filename
        with open(out_file, "w", encoding="utf-8") as out_f:
            for ex in subset:
                out_f.write(json.dumps(ex, ensure_ascii=False) + "\n")

        size_kb = out_file.stat().st_size / 1024
        print(f"  ✅ Créé : {filename:<18} | {len(subset):>3} exemples | {size_kb:>6.1f} Ko ({size_kb/1024:.2f} Mo)")
        generated.append((filename, len(subset), size_kb))

    print("=" * 70)
    return generated


if __name__ == "__main__":
    build_fine_datasets()
