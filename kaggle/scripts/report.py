#!/usr/bin/env python3
"""Générateur de rapport métrologique pour les évaluations Gemma 4 (SWE-bench Python).

Lit les traces d'exécution dans un dossier de run (par exemple runs/<date>-<condition>/)
et produit un tableau de synthèse consolidé (CSV et console) :
- Taux de résolution (PASS/FAIL)
- Nombre d'appels d'outils moyen et par tâche
- Durée moyenne d'exécution
- Détection des timeouts et des patchs vides
"""
import argparse
import csv
import json
import sys
from pathlib import Path


def analyze_run(run_dir_str: str, output_csv: str = None):
    run_dir = Path(run_dir_str)
    if not run_dir.exists():
        print(f"❌ Dossier introuvable : {run_dir}")
        sys.exit(1)

    records = []
    
    # Recherche des fichiers de résultats ou métadonnées par tâche
    result_files = sorted(run_dir.glob("**/result.json")) + sorted(run_dir.glob("**/task_result.json"))
    
    if not result_files:
        # Essai de lecture d'un summary.json global
        summary_file = run_dir / "summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                elif isinstance(data, dict) and "tasks" in data:
                    records = data["tasks"]
        else:
            print(f"⚠️ Aucun fichier result.json ou summary.json trouvé dans {run_dir}")

    for rf in result_files:
        try:
            with open(rf) as f:
                records.append(json.load(f))
        except Exception as e:
            print(f"Erreur lecture {rf}: {e}")

    total = len(records)
    if total == 0:
        print("Aucune tâche enregistrée dans ce run.")
        return

    solved = sum(1 for r in records if r.get("resolved") or r.get("fixed") or r.get("score", 0) == 1.0)
    timeouts = sum(1 for r in records if r.get("timeout") or "Timeout" in str(r.get("error", "")))
    empty_patches = sum(1 for r in records if not r.get("patch") and not r.get("submitted_patch"))
    
    total_calls = sum(r.get("tool_calls_used", r.get("turns", 0)) for r in records)
    total_time = sum(r.get("elapsed_seconds", r.get("seconds", 0)) for r in records)

    print("\n" + "="*60)
    print(f"📊 RAPPORT D'ÉVALUATION : {run_dir.name}")
    print("="*60)
    print(f"Tâches totales évaluées : {total}")
    print(f"Résolues (PASS)         : {solved} / {total} ({solved/total*100:.1f}%)")
    print(f"Échecs (FAIL)           : {total - solved} / {total} ({(total-solved)/total*100:.1f}%)")
    print(f"Timeouts                : {timeouts} ({timeouts/total*100:.1f}%)")
    print(f"Patchs vides            : {empty_patches} ({empty_patches/total*100:.1f}%)")
    print(f"Appels d'outils moyens  : {total_calls / total:.1f} par tâche")
    print(f"Temps moyen par tâche   : {total_time / total:.1f} secondes")
    print("="*60 + "\n")

    if output_csv:
        csv_path = Path(output_csv)
        fieldnames = ["task_id", "resolved", "tool_calls", "elapsed_seconds", "timeout", "has_patch"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow({
                    "task_id": r.get("task_id", r.get("pr", "unknown")),
                    "resolved": bool(r.get("resolved") or r.get("fixed") or r.get("score", 0) == 1.0),
                    "tool_calls": r.get("tool_calls_used", r.get("turns", 0)),
                    "elapsed_seconds": r.get("elapsed_seconds", r.get("seconds", 0)),
                    "timeout": bool(r.get("timeout") or "Timeout" in str(r.get("error", ""))),
                    "has_patch": bool(r.get("patch") or r.get("submitted_patch"))
                })
        print(f"📁 Données exportées dans {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générer un rapport d'évaluation Kaggle")
    parser.add_argument("run_dir", help="Chemin du dossier de run à analyser")
    parser.add_argument("--csv", help="Chemin du fichier CSV de sortie", default=None)
    args = parser.parse_args()

    analyze_run(args.run_dir, args.csv)
