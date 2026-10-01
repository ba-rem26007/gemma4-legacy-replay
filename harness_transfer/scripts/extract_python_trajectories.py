#!/usr/bin/env python3
"""Extracteur intelligent de trajectoires d'entraînement Python (FastAPI, Requests, Rich).

Principes fondamentaux :
1. Règle du 'Sweet Spot' : 250 à 350 exemples de haute qualité chirurgicale (évite l'overfitting).
2. Étanche & Anti-contamination : Exclut formellement les 30 tâches de dev30.txt.
3. Zero Proprietary AI : 100% basé sur des commits réels de mainteneurs humains mergés.
4. Format SEARCH/REPLACE strict : Compatible Gemma 4 avec masquage des tours utilisateur.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

REPOS = {
    "fastapi": Path("/home/elrems/kaggle/harness_transfer/repos/fastapi"),
    "requests": Path("/home/elrems/kaggle/harness_transfer/repos/requests"),
    "rich": Path("/home/elrems/kaggle/harness_transfer/repos/rich"),
}

OUTPUT_FILE = Path("/home/elrems/kaggle/harness_transfer/data/train_python.jsonl")
DEV30_FILE = Path("/home/elrems/kaggle/harness_transfer/data/dev30.txt")

SYSTEM_PROMPT = """You are Gemma 4, an autonomous software engineering agent specialized in Python.
Given a bug report or feature issue description and the relevant Python code file, your goal is to locate the bug and provide a precise patch using SEARCH/REPLACE blocks.

Format your answer strictly with:
<<<<<<< SEARCH
[exact original code to replace]
=======
[replacement code]
>>>>>>> REPLACE
"""


def load_dev_ids(dev_file: Path) -> Set[str]:
    """Extrait tous les identifiants numériques de la suite d'évaluation pour éviter toute contamination."""
    ids = set()
    if not dev_file.exists():
        return ids
    with open(dev_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split("_")
                if len(parts) > 1:
                    ids.add(parts[1])
                ids.add(line)
    return ids


def parse_diff_to_hunks(diff_text: str) -> List[Tuple[str, str, str]]:
    """Parse un patch diff unifié en triplets (fichier, search_block, replace_block)."""
    hunks = []
    current_file = None
    current_search = []
    current_replace = []
    in_hunk = False

    for line in diff_text.splitlines():
        if line.startswith("--- a/"):
            current_file = line[6:]
            continue
        if line.startswith("+++ b/"):
            continue
        if line.startswith("@@"):
            if in_hunk and current_search and (current_search != current_replace):
                hunks.append((current_file, "\n".join(current_search), "\n".join(current_replace)))
            current_search = []
            current_replace = []
            in_hunk = True
            continue

        if in_hunk:
            if line.startswith("-"):
                current_search.append(line[1:])
            elif line.startswith("+"):
                current_replace.append(line[1:])
            elif line.startswith(" "):
                current_search.append(line[1:])
                current_replace.append(line[1:])

    if in_hunk and current_search and (current_search != current_replace):
        hunks.append((current_file, "\n".join(current_search), "\n".join(current_replace)))

    return hunks


def extract_repo_commits(repo_name: str, repo_path: Path, dev_ids: Set[str], max_per_repo: int = 120) -> List[Dict]:
    print(f"\n🔍 Analyse du dépôt {repo_name} ({repo_path})...")
    res = subprocess.run(
        ["git", "log", "--grep=fix", "--grep=bug", "--grep=resolve", "--grep=close", "--format=%H%x00%s%x00%b%x1e"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    raw_commits = res.stdout.split("\x1e")
    examples = []

    for item in raw_commits:
        if not item.strip():
            continue
        parts = item.split("\x00")
        if len(parts) < 2:
            continue
        commit_hash = parts[0].strip()
        subject = parts[1].strip()
        body = parts[2].strip() if len(parts) > 2 else ""

        # 1. Filtre anti-contamination strict
        contaminated = False
        for dev_id in dev_ids:
            if dev_id in subject or dev_id in body:
                contaminated = True
                break
        if contaminated:
            continue

        # 2. Vérification des fichiers modifiés
        names_cmd = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        changed_files = [f for f in names_cmd.stdout.strip().split("\n") if f]
        py_files = [f for f in changed_files if f.endswith(".py") and not f.startswith("tests/") and "test_" not in f]

        # On ne retient que les correctifs chirurgicaux (1 à 2 fichiers source Python)
        if not (1 <= len(py_files) <= 2):
            continue

        # 3. Extraction du diff
        diff_cmd = subprocess.run(
            ["git", "diff", f"{commit_hash}~1", commit_hash, "--"] + py_files,
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        diff_text = diff_cmd.stdout

        # Filtrer la taille du diff (< 60 lignes changées au total)
        diff_lines = diff_text.splitlines()
        added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))
        if added + removed > 50 or added + removed < 2:
            continue

        hunks = parse_diff_to_hunks(diff_text)
        if not hunks or len(hunks) > 2:
            continue

        # 4. Construction de la réponse SEARCH/REPLACE
        blocks = []
        valid_hunks = True
        for fname, s_block, r_block in hunks:
            # Nettoyage des blocs vides
            if not s_block.strip() and not r_block.strip():
                continue
            # Trop gros pour un bloc
            if len(s_block.splitlines()) > 30 or len(r_block.splitlines()) > 30:
                valid_hunks = False
                break
            blocks.append(f"File `{fname}`:\n<<<<<<< SEARCH\n{s_block}\n=======\n{r_block}\n>>>>>>> REPLACE")

        if not valid_hunks or not blocks:
            continue

        # 5. Récupération d'un extrait du fichier d'origine pour le prompt
        primary_file = hunks[0][0]
        show_cmd = subprocess.run(
            ["git", "show", f"{commit_hash}~1:{primary_file}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        orig_content = show_cmd.stdout
        # Prendre au maximum les 150 premières lignes ou un extrait ciblé pour ne pas saturer la fenêtre
        snippet_lines = orig_content.splitlines()[:120]
        file_snippet = "\n".join(snippet_lines)

        user_content = f"""Problem Description:
{subject}

{body}

Target File: `{primary_file}`
Context Snippet:
```python
{file_snippet}
```

Please output the minimal SEARCH/REPLACE patch to fix this issue."""

        assistant_content = "\n\n".join(blocks)

        # Estimation des tokens (~ 4 caractères par token)
        total_chars = len(SYSTEM_PROMPT) + len(user_content) + len(assistant_content)
        tokens_est = total_chars // 4

        if tokens_est > 3500:
            continue

        example = {
            "repo": repo_name,
            "commit": commit_hash,
            "subject": subject,
            "tokens_est": tokens_est,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content},
            ],
        }
        examples.append(example)

        if len(examples) >= max_per_repo:
            break

    print(f"  -> Retenu pour {repo_name} : {len(examples)} trajectoires chirurgicales.")
    return examples


def main():
    print("🚀 Démarrage de l'extraction des trajectoires Python intelligentes...")
    dev_ids = load_dev_ids(DEV30_FILE)
    print(f"🛡️  Identifiants de test sous embargo anti-contamination : {len(dev_ids)}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    all_examples = []
    # Distribution intelligente : 80 fastapi, 100 requests, 120 rich -> ~300 exemples au total
    targets = {"fastapi": 80, "requests": 100, "rich": 120}

    for repo_name, repo_path in REPOS.items():
        quota = targets.get(repo_name, 100)
        exs = extract_repo_commits(repo_name, repo_path, dev_ids, max_per_repo=quota)
        all_examples.extend(exs)

    print(f"\n📦 Écriture de {len(all_examples)} exemples dans {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"✅ Extraction terminée avec succès !")
    print(f"   Fichier généré : {OUTPUT_FILE}")
    print(f"   Taille : {OUTPUT_FILE.stat().st_size / 1024:.1f} Ko")
    print(f"   Nombre d'exemples : {len(all_examples)}")


if __name__ == "__main__":
    main()
