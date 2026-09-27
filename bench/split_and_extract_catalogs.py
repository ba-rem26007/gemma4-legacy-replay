#!/usr/bin/env python3
"""Segmentation et extraction modulaire des bugs et évolutions PrestaShop par branche.

Génère une arborescence légère dans bench/catalogs/<branche>/ :
  - bugs.jsonl
  - improvements.jsonl
  - features.jsonl
et un index récapitulatif dans bench/catalogs/INDEX.md.
"""

import argparse
import collections
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = "PrestaShop/PrestaShop"
BRANCHES = ["8.0.x", "8.1.x", "8.2.x", "9.0.x", "9.1.x", "9.2.x", "develop", "1.7.8.x"]
CATALOGS_DIR = HERE / "catalogs"
DIFFS_DIR = HERE / "diffs"
SECURITY = re.compile(r"secur|xss|csrf|injection|sqli|vulnerab|exploit|cve|rce|privilege|forbid|sanitiz|htmlentit|strip_tags|permission|access right|escap", re.I)
NON_UI = re.compile(r"^(tests?/|\.github/|composer\.|package|\.docker|docker|install-dev/)", re.I)


def run_gh(*args):
    """Exécute une commande GitHub CLI."""
    res = subprocess.run(["gh", *args], capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return res.stdout


def linked_issues(body):
    """Extrait les numéros d'issues liés dans la description de la PR."""
    rows = [l for l in (body or "").splitlines() if re.match(r"\|\s*(Fixed|How to test|Issue)", l, re.I)]
    nums = re.findall(r"(?:#|issues/)(\d{4,6})", " ".join(rows))
    return list(dict.fromkeys(int(n) for n in nums))


def dispatch_existing_bugs():
    """Segmente les bugs existants de catalog.jsonl par branche."""
    cat_path = HERE / "catalog.jsonl"
    if not cat_path.exists():
        print("catalog.jsonl introuvable, étape ignorée.")
        return collections.defaultdict(int)

    counts = collections.defaultdict(int)
    print(f"Segmentation des bugs existants depuis {cat_path.name}...")
    with open(cat_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            branch = item.get("branch", "unknown")
            target_branch = branch if branch in BRANCHES else "autres"
            b_dir = CATALOGS_DIR / target_branch
            b_dir.mkdir(parents=True, exist_ok=True)
            with open(b_dir / "bugs.jsonl", "a", encoding="utf-8") as out_f:
                out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
            counts[target_branch] += 1

    return counts


def fetch_prs_for_branch(branch, label, max_limit=100):
    """Récupère les PRs mergées pour une branche et un label donnés."""
    raw = run_gh("pr", "list", "-R", REPO, "--state", "merged",
                 "--base", branch, "--label", label, "--limit", str(max_limit),
                 "--json", "number,title,body,additions,deletions,changedFiles,files,labels,mergeCommit,url,baseRefName")
    if not raw:
        return []
    try:
        return json.loads(raw)
    except Exception:
        return []


def process_and_save_prs(branch, pr_type, prs):
    """Filtre, enrichit et enregistre les PRs dans le sous-catalogue approprié."""
    b_dir = CATALOGS_DIR / branch
    b_dir.mkdir(parents=True, exist_ok=True)
    out_file = b_dir / f"{pr_type}.jsonl"

    # Vérifier les PRs déjà enregistrées pour éviter les doublons
    existing_prs = set()
    if out_file.exists():
        with open(out_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    existing_prs.add(json.loads(line).get("pr"))

    saved_count = 0
    with open(out_file, "a", encoding="utf-8") as f_out:
        for pr in prs:
            pr_num = pr["number"]
            if pr_num in existing_prs:
                continue

            size = pr.get("additions", 0) + pr.get("deletions", 0)
            files = [file_obj["path"] for file_obj in pr.get("files", [])]
            label_names = [l["name"] for l in pr.get("labels", [])]

            # Filtres d'hygiène et de sécurité
            if SECURITY.search(pr.get("title", "") + " " + " ".join(label_names)):
                continue

            # Recherche des issues liées
            issues = linked_issues(pr.get("body", ""))
            issue_title = ""
            issue_body = ""
            issue_num = issues[0] if issues else 0

            if issue_num:
                raw_issue = run_gh("issue", "view", str(issue_num), "-R", REPO, "--json", "title,body")
                if raw_issue:
                    try:
                        iss_data = json.loads(raw_issue)
                        issue_title = iss_data.get("title", "")
                        issue_body = iss_data.get("body", "")
                    except Exception:
                        pass

            # Récupération du merge commit et du commit de base (avant)
            mc = (pr.get("mergeCommit") or {}).get("oid")
            if not mc:
                raw_sha = run_gh("api", f"repos/{REPO}/pulls/{pr_num}", "--jq", ".merge_commit_sha")
                mc = raw_sha.strip() if raw_sha else None

            parents = []
            if mc and mc != "null":
                raw_parents = run_gh("api", f"repos/{REPO}/commits/{mc}", "--jq", "[.parents[].sha]")
                if raw_parents:
                    try:
                        parents = json.loads(raw_parents)
                    except Exception:
                        pass

            base_commit = parents[0] if parents else ""

            # Sauvegarde du diff officiel si absent
            diff_file = DIFFS_DIR / f"{pr_num}.diff"
            if not diff_file.exists():
                diff_content = run_gh("pr", "diff", str(pr_num), "-R", REPO)
                if diff_content:
                    DIFFS_DIR.mkdir(parents=True, exist_ok=True)
                    diff_file.write_text(diff_content, encoding="utf-8")

            record = {
                "pr": pr_num,
                "type": pr_type,
                "branch": branch,
                "title": pr.get("title", ""),
                "url": pr.get("url", ""),
                "issue": issue_num,
                "issue_title": issue_title,
                "issue_body": issue_body,
                "base_commit": base_commit,
                "merge_commit": mc,
                "files": files,
                "lines": size,
                "labels": label_names
            }
            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            existing_prs.add(pr_num)
            saved_count += 1

    return saved_count


def generate_index_markdown():
    """Génère l'index global récapitulatif dans bench/catalogs/INDEX.md."""
    index_md = ["# Index des Catalogues PrestaShop (Bugs & Évolutions)\n"]
    index_md.append("Sous-catalogues légers par branche dans `bench/catalogs/<branche>/`.\n")
    index_md.append("| Branche | Bugs (`bugs.jsonl`) | Évolutions (`improvements.jsonl`) | Features (`features.jsonl`) | Total |")
    index_md.append("|---|:---:|:---:|:---:|:---:|")

    total_all = 0
    all_branches = sorted(list(p.name for p in CATALOGS_DIR.iterdir() if p.is_dir()))

    for b in all_branches:
        b_dir = CATALOGS_DIR / b
        nb_bugs = sum(1 for _ in open(b_dir / "bugs.jsonl")) if (b_dir / "bugs.jsonl").exists() else 0
        nb_imp = sum(1 for _ in open(b_dir / "improvements.jsonl")) if (b_dir / "improvements.jsonl").exists() else 0
        nb_feat = sum(1 for _ in open(b_dir / "features.jsonl")) if (b_dir / "features.jsonl").exists() else 0
        tot = nb_bugs + nb_imp + nb_feat
        total_all += tot
        index_md.append(f"| **{b}** | {nb_bugs} | {nb_imp} | {nb_feat} | **{tot}** |")

    index_md.append(f"\n**Total général consolidé : {total_all} tickets / PRs.**\n")
    (CATALOGS_DIR / "INDEX.md").write_text("\n".join(index_md), encoding="utf-8")
    print(f"Index mis à jour dans {CATALOGS_DIR / 'INDEX.md'} (Total: {total_all})")


def main():
    parser = argparse.ArgumentParser(description="Extraction et segmentation des sous-catalogues PrestaShop")
    parser.add_argument("--fetch-remote", action="store_true", help="Interroge GitHub pour extraire improvements et features")
    parser.add_argument("--limit-per-type", type=int, default=100, help="Nombre max de PRs par type/branche")
    args = parser.parse_args()

    CATALOGS_DIR.mkdir(parents=True, exist_ok=True)
    DIFFS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Segmentation des bugs existants
    dispatch_existing_bugs()

    # 2. Extraction des évolutions depuis GitHub si demandée
    if args.fetch_remote:
        print("\n--- Extraction GitHub des Évolutions (Improvements & Features) ---")
        for branch in BRANCHES:
            print(f"\n[Branche {branch}]")
            for label, pr_type in [("Improvement", "improvements"), ("Feature", "features")]:
                print(f"  Fetching {label}...")
                prs = fetch_prs_for_branch(branch, label, args.limit_per_type)
                saved = process_and_save_prs(branch, pr_type, prs)
                print(f"  -> {saved} nouvelles PRs enregistrées dans catalogs/{branch}/{pr_type}.jsonl")

    # 3. Génération de l'index
    generate_index_markdown()


if __name__ == "__main__":
    main()
