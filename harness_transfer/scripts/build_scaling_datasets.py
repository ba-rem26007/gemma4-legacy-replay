#!/usr/bin/env python3
"""Générateur de corpus gradués (1 Mo, 2 Mo, 3 Mo, 4 Mo) pour l'étude d'ablation /loop.

Objectif : Évaluer les lois d'échelle (Scaling Laws) du fine-tuning LoRA Gemma 4 sur Python.
Dépôts cibles : FastAPI, Requests, Rich, Flask, Click (2 643 commits de bugfix).
Contraintes :
1. Anti-contamination absolue avec dev30.txt.
2. Zéro IA propriétaire : 100% commits de mainteneurs humains mergés.
3. Gradualité stricte : train_1mb ⊂ train_2mb ⊂ train_3mb ⊂ train_4mb.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Tuple

REPOS = {
    "fastapi": Path("/home/elrems/kaggle/harness_transfer/repos/fastapi"),
    "requests": Path("/home/elrems/kaggle/harness_transfer/repos/requests"),
    "rich": Path("/home/elrems/kaggle/harness_transfer/repos/rich"),
    "flask": Path("/home/elrems/kaggle/harness_transfer/repos/flask"),
    "click": Path("/home/elrems/kaggle/harness_transfer/repos/click"),
    "jinja": Path("/home/elrems/kaggle/harness_transfer/repos/jinja"),
    "urllib3": Path("/home/elrems/kaggle/harness_transfer/repos/urllib3"),
    "werkzeug": Path("/home/elrems/kaggle/harness_transfer/repos/werkzeug"),
}

DATA_DIR = Path("/home/elrems/kaggle/harness_transfer/data")
DEV30_FILE = DATA_DIR / "dev30.txt"

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


def extract_candidates(repo_name: str, repo_path: Path, dev_ids: Set[str], max_count: int = 250) -> List[Dict]:
    print(f"📦 Extraction depuis {repo_name}...")
    res = subprocess.run(
        ["git", "log", "--grep=fix", "--grep=bug", "--grep=resolve", "--grep=close", "--format=%H%x00%s%x00%b%x1e"],
        cwd=repo_path, capture_output=True, text=True, check=True
    )

    commits = res.stdout.split("\x1e")
    examples = []

    for item in commits:
        if not item.strip():
            continue
        parts = item.split("\x00")
        if len(parts) < 2:
            continue
        commit_hash = parts[0].strip()
        subject = parts[1].strip()
        body = parts[2].strip() if len(parts) > 2 else ""

        # Anti-contamination
        if any(dev_id in subject or dev_id in body for dev_id in dev_ids):
            continue

        # Diff inspection
        names_cmd = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
            cwd=repo_path, capture_output=True, text=True
        )
        changed_files = [f for f in names_cmd.stdout.strip().split("\n") if f]
        py_files = [f for f in changed_files if f.endswith(".py") and not f.startswith("tests/") and "test_" not in f]

        if not (1 <= len(py_files) <= 2):
            continue

        diff_cmd = subprocess.run(
            ["git", "diff", f"{commit_hash}~1", commit_hash, "--"] + py_files,
            cwd=repo_path, capture_output=True, text=True
        )
        diff_text = diff_cmd.stdout
        diff_lines = diff_text.splitlines()
        added = sum(1 for l in diff_lines if l.startswith("+") and not l.startswith("+++"))
        removed = sum(1 for l in diff_lines if l.startswith("-") and not l.startswith("---"))
        if added + removed > 55 or added + removed < 2:
            continue

        hunks = parse_diff_to_hunks(diff_text)
        if not hunks or len(hunks) > 2:
            continue

        blocks = []
        valid_hunks = True
        for fname, s_block, r_block in hunks:
            if not s_block.strip() and not r_block.strip():
                continue
            if len(s_block.splitlines()) > 35 or len(r_block.splitlines()) > 35:
                valid_hunks = False
                break
            blocks.append(f"File `{fname}`:\n<<<<<<< SEARCH\n{s_block}\n=======\n{r_block}\n>>>>>>> REPLACE")

        if not valid_hunks or not blocks:
            continue

        primary_file = hunks[0][0]
        show_cmd = subprocess.run(
            ["git", "show", f"{commit_hash}~1:{primary_file}"],
            cwd=repo_path, capture_output=True, text=True
        )
        snippet_lines = show_cmd.stdout.splitlines()[:120]
        file_snippet = "\n".join(snippet_lines)

        user_content = f"""Problem Description:\n{subject}\n\n{body}\n\nTarget File: `{primary_file}`\nContext Snippet:\n```python\n{file_snippet}\n```\n\nPlease output the minimal SEARCH/REPLACE patch to fix this issue."""
        assistant_content = "\n\n".join(blocks)

        total_chars = len(SYSTEM_PROMPT) + len(user_content) + len(assistant_content)
        tokens_est = total_chars // 4

        if tokens_est > 3500:
            continue

        examples.append({
            "repo": repo_name,
            "commit": commit_hash,
            "subject": subject,
            "tokens_est": tokens_est,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
                {"role": "assistant", "content": assistant_content}
            ]
        })

        if len(examples) >= max_count:
            break

    print(f"  -> Retenu pour {repo_name} : {len(examples)} trajectoires.")
    return examples


def main():
    print("🚀 Construction des corpus gradués 1 Mo à 8 Mo (Lois d'échelle & Overfitting)...")
    dev_ids = load_dev_ids(DEV30_FILE)
    print(f"🛡️  Embargo anti-contamination : {len(dev_ids)} identifiants protégés.")

    all_candidates = []
    quotas = {
        "fastapi": 120,
        "requests": 380,
        "rich": 450,
        "flask": 450,
        "click": 250,
        "jinja": 200,
        "urllib3": 350,
        "werkzeug": 350,
    }

    for name, path in REPOS.items():
        exs = extract_candidates(name, path, dev_ids, max_count=quotas.get(name, 200))
        all_candidates.extend(exs)

    print(f"\nTotal global extrait : {len(all_candidates)} exemples.")

    # Découpage progressif imbriqué (train_1mb ⊂ ... ⊂ train_8mb)
    targets = [
        ("train_1mb.jsonl", 190),   # ~1.0 Mo
        ("train_2mb.jsonl", 380),   # ~2.0 Mo
        ("train_3mb.jsonl", 570),   # ~3.0 Mo
        ("train_4mb.jsonl", 742),   # ~4.0 Mo
        ("train_6mb.jsonl", min(1150, len(all_candidates))),  # ~6.0 Mo
        ("train_8mb.jsonl", min(1550, len(all_candidates))),  # ~8.0 Mo
    ]

    for filename, count in targets:
        subset = all_candidates[:count]
        out_path = DATA_DIR / filename
        with open(out_path, "w", encoding="utf-8") as f:
            for ex in subset:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
        size_kb = out_path.stat().st_size / 1024
        print(f"✅ {filename:16} : {len(subset):4} exemples | {size_kb:.1f} Ko ({size_kb/1024:.2f} Mo)")


if __name__ == "__main__":
    main()

