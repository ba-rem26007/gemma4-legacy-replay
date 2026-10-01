#!/usr/bin/env python3
"""Évaluateur hermétique local / Colab pour les tâches SWE-bench Python (FastAPI).

Reproduit le protocole d'évaluation officiel :
1. Extraction de la tâche depuis tasks.jsonl (instance_id, base_commit, test_patch).
2. Préparation du dépôt à base_commit dans un espace de travail isolé.
3. Exécution de l'agent -> génération de agent_patch.
4. Application de agent_patch + test_patch.
5. Lancement de pytest : si exit_code == 0 -> RESOLVED (1.0), sinon FAILED (0.0).
6. Calcul du score agrégé Pass@1.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

FASTAPI_REPO_URL = "https://github.com/fastapi/fastapi.git"


def load_task(tasks_file: Path, instance_id: str) -> Optional[Dict[str, Any]]:
    if not tasks_file.exists():
        raise FileNotFoundError(f"tasks.jsonl introuvable à {tasks_file}")
    with open(tasks_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                t = json.loads(line)
                if t.get("instance_id") == instance_id:
                    return t
    return None


def setup_workspace(workspace_dir: Path, base_commit: str) -> None:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    git_dir = workspace_dir / ".git"
    if not git_dir.exists():
        print(f"📦 Clonage de FastAPI dans {workspace_dir}...")
        subprocess.run(["git", "clone", FASTAPI_REPO_URL, str(workspace_dir)], check=True)
    
    print(f"🔄 Restauration au commit de base : {base_commit}")
    subprocess.run(["git", "clean", "-fdx"], cwd=str(workspace_dir), check=True)
    subprocess.run(["git", "checkout", "-f", base_commit], cwd=str(workspace_dir), check=True)


def apply_patch(workspace_dir: Path, patch_text: str) -> bool:
    if not patch_text.strip():
        return True
    if not patch_text.endswith("\n"):
        patch_text += "\n"
    try:
        p = subprocess.run(
            ["git", "apply", "--recount", "-v"],
            input=patch_text,
            text=True,
            cwd=str(workspace_dir),
            capture_output=True,
            check=False,
        )
        return p.returncode == 0
    except Exception as e:
        print(f"Erreur d'application de patch : {e}")
        return False


def run_oracle_tests(workspace_dir: Path) -> bool:
    """Exécute les tests pytest et retourne True si tous passent."""
    try:
        cmd = ["python3", "-m", "pytest", "-q", "--tb=short"]
        p = subprocess.run(cmd, cwd=str(workspace_dir), capture_output=True, text=True, timeout=120)
        return p.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏱️ Timeout des tests unitaires (> 120s)")
        return False


def evaluate_task(task: Dict[str, Any], workspace_dir: Path, agent_patch: Optional[str] = None) -> Dict[str, Any]:
    instance_id = task["instance_id"]
    base_commit = task["base_commit"]
    test_patch = task["test_patch"]

    setup_workspace(workspace_dir, base_commit)

    patch_applied = True
    if agent_patch:
        patch_applied = apply_patch(workspace_dir, agent_patch)
        if not patch_applied:
            print(f"❌ Impossible d'appliquer l'agent_patch sur {instance_id}")
            return {"instance_id": instance_id, "resolved": False, "patch_applied": False, "reason": "patch_apply_failed"}

    # Application du test_patch officiel hermétique
    test_applied = apply_patch(workspace_dir, test_patch)
    if not test_applied:
        print(f"⚠️ Échec d'application du test_patch sur {instance_id}")
        return {"instance_id": instance_id, "resolved": False, "patch_applied": patch_applied, "reason": "test_patch_failed"}

    # Lancement du verdict
    tests_pass = run_oracle_tests(workspace_dir)
    print(f"🏁 Résultat {instance_id} : {'RESOLVED (PASS)' if tests_pass else 'UNRESOLVED (FAIL)'}")

    return {
        "instance_id": instance_id,
        "resolved": tests_pass,
        "patch_applied": patch_applied,
    }


def main():
    parser = argparse.ArgumentParser(description="Évaluateur de tâches Python local/Colab")
    parser.add_argument("--tasks", type=Path, default=Path("/tmp/kaggle_data/tasks.jsonl"), help="Chemin vers tasks.jsonl")
    parser.add_argument("--instance-id", type=str, required=True, help="ID de la tâche à tester (ex: fastapi_14419)")
    parser.add_argument("--workspace", type=Path, default=Path("/tmp/eval_fastapi"), help="Espace de travail")
    parser.add_argument("--agent-patch", type=Path, default=None, help="Patch produit par l'agent (.patch)")
    args = parser.parse_args()

    task = load_task(args.tasks, args.instance_id)
    if not task:
        print(f"❌ Tâche '{args.instance_id}' introuvable dans {args.tasks}")
        sys.exit(1)

    agent_patch_text = args.agent_patch.read_text(encoding="utf-8") if args.agent_patch else None
    result = evaluate_task(task, args.workspace, agent_patch_text)
    print("\n" + json.dumps(result, indent=2))
    sys.exit(0 if result["resolved"] else 1)


if __name__ == "__main__":
    main()
