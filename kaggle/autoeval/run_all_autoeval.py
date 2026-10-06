#!/usr/bin/env python3
"""Orchestrateur global des 3 niveaux d'Auto-Évaluation sur nos données."""

import subprocess
import sys
import time
from pathlib import Path

DIR = Path(__file__).resolve().parent

SCRIPTS = [
    ("Niveau 1 : Statique & Syntaxe AST (940 décisions réelles)", DIR / "eval_level1_static.py"),
    ("Niveau 2 : Rejeu de Correction & Résilience (Recovery)", DIR / "eval_level2_recovery.py"),
    ("Niveau 3 : Bac à Sable & Dépendances Sandbox (129 tâches)", DIR / "eval_level3_sandbox_audit.py"),
]


def main():
    print("\n" + "█" * 78)
    print("🏆 BANC D'AUTO-ÉVALUATION INTÉGRAL SUR NOS DONNÉES (NIVEAUX 1, 2 & 3)")
    print("█" * 78 + "\n")

    t_start = time.time()
    results = []

    for name, script in SCRIPTS:
        t0 = time.time()
        res = subprocess.run([sys.executable, str(script)], capture_output=False)
        dt = time.time() - t0
        passed = (res.returncode == 0)
        results.append((name, passed, dt))
        print("\n")

    print("█" * 78)
    print("📋 SYNTHÈSE GLOBALE DE LA SUITE DE TESTS D'AUTO-ÉVALUATION :")
    print("█" * 78)
    all_ok = True
    for name, passed, dt in results:
        status_str = "✅ PASS" if passed else "❌ FAIL"
        if not passed:
            all_ok = False
        print(f" • {status_str} | {name:<60} ({dt:.2f}s)")

    total_time = time.time() - t_start
    print("-" * 78)
    print(f"⏱️ Temps total de certification : {total_time:.2f} secondes.")
    if all_ok:
        print("🎉 CERTIFICATION TOTALE : Tous les tests d'auto-évaluation sur nos données sont au vert !")
    else:
        print("⚠️ Certains tests nécessitent une investigation.")
    print("█" * 78 + "\n")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
