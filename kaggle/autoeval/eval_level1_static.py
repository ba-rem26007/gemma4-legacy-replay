#!/usr/bin/env python3
"""Niveau 1 d'Auto-Évaluation : Analyse Statique & Syntaxe Pure.

Évalue directement sur les 940 requêtes/réponses réelles de Gemma 4 31B QAT (runs/leaderboard_local/v4/edits_lent2.jsonl) :
1. Taux de validité JSON des arguments d'outils.
2. Détection du bug des arguments manquants (ex: edit_file sans old_string).
3. Validité syntaxique Python via AST (ast.parse) sur tous les fichiers/scripts générés.
4. Conformité des scripts heredoc et scripts de reproduction (/tmp/repro.py).
"""

import ast
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EDITS_LOG = REPO_ROOT / "runs" / "leaderboard_local" / "v4" / "edits_lent2.jsonl"


def extract_python_scripts(text: str) -> list[str]:
    """Extrait les scripts Python imbriqués dans les heredocs shell ou snippets."""
    scripts = []
    # Pattern heredoc: python3 - <<'EOF' ... EOF
    pattern = r"python3\s+-\s*<<['\"]?(\w+)['\"]?\n(.*?)\n\1"
    for match in re.finditer(pattern, text, re.DOTALL):
        scripts.append(match.group(2))
    return scripts


def test_syntax_ast(code: str) -> tuple[bool, str]:
    """Valide la syntaxe du code via l'arbre syntaxique abstrait."""
    try:
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"SyntaxError L{e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)


def run_level1_evaluation():
    print("=" * 75)
    print("🚀 NIVEAU 1 : AUTO-ÉVALUATION STATIQUE & SYNTAXE SUR DONNÉES RÉELLES (940 APPELS)")
    print("=" * 75)
    t0 = time.time()

    if not EDITS_LOG.exists():
        print(f"❌ Fichier introuvable : {EDITS_LOG}")
        return False

    tool_counts = Counter()
    json_valid = 0
    json_invalid = 0
    
    # Métriques edit_file
    edit_file_total = 0
    edit_file_ok = 0
    edit_file_missing_args = 0
    
    # Métriques code Python généré
    python_scripts_tested = 0
    python_scripts_valid_ast = 0
    ast_errors = []

    with open(EDITS_LOG, "r", encoding="utf-8") as f:
        for line_idx, line in enumerate(f):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                resp = row.get("response", {})
                tool_calls = resp.get("tool_calls", [])
                
                for tc in tool_calls:
                    fn = tc.get("function", {})
                    name = fn.get("name", "unknown")
                    raw_args = fn.get("arguments", "")
                    tool_counts[name] += 1

                    # 1. Validation JSON
                    try:
                        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                        json_valid += 1
                    except Exception as err:
                        json_invalid += 1
                        continue

                    # 2. Analyse edit_file
                    if name == "edit_file":
                        edit_file_total += 1
                        has_path = "filepath" in args or "path" in args
                        has_old = "old_string" in args or "old" in args
                        has_new = "new_string" in args or "new" in args
                        if has_path and has_old and has_new:
                            edit_file_ok += 1
                        else:
                            edit_file_missing_args += 1

                    # 3. Analyse syntaxe Python des write_file / scripts
                    if name == "write_file":
                        content = args.get("content", "")
                        path = args.get("filepath", "")
                        if path.endswith(".py") or "import " in content or "def " in content:
                            python_scripts_tested += 1
                            ok, msg = test_syntax_ast(content)
                            if ok:
                                python_scripts_valid_ast += 1
                            else:
                                ast_errors.append((f"write_file:{path}", line_idx, msg))

                    elif name == "run_command":
                        cmd = args.get("command", "")
                        # Extraire les heredocs python
                        scripts = extract_python_scripts(cmd)
                        for sc in scripts:
                            python_scripts_tested += 1
                            ok, msg = test_syntax_ast(sc)
                            if ok:
                                python_scripts_valid_ast += 1
                            else:
                                ast_errors.append(("heredoc:python3", line_idx, msg))

            except Exception as e:
                pass

    duration = time.time() - t0
    total_calls = json_valid + json_invalid
    pct_json = (json_valid / total_calls * 100) if total_calls else 0
    pct_edit_ok = (edit_file_ok / edit_file_total * 100) if edit_file_total else 0
    pct_ast = (python_scripts_valid_ast / python_scripts_tested * 100) if python_scripts_tested else 0

    print("\n📊 1. RÉPARTITION DES APPELS D'OUTILS SUR LES 940 DÉCISIONS RÉELLES :")
    for tool_name, count in tool_counts.most_common():
        print(f"   • {tool_name:<18} : {count:>4} appels ({count/total_calls*100:>5.1f}%)")

    print("\n📊 2. INTÉGRITÉ JSON & PARSING :")
    print(f"   • JSON valides      : {json_valid}/{total_calls} ({pct_json:.2f}%)")
    print(f"   • JSON corrompus    : {json_invalid}")

    print("\n📊 3. DIAGNOSTIC DE L'OUTIL EDIT_FILE (LE PIÈGE HISTORIQUE) :")
    print(f"   • Total appels edit_file        : {edit_file_total}")
    print(f"   • Appels complets (old+new)     : {edit_file_ok} ({pct_edit_ok:.1f}%)")
    print(f"   • Appels tronqués (perte args)  : {edit_file_missing_args} ({100 - pct_edit_ok:.1f}%)")
    print(f"   👉 Confirmation du diagnostic : edit_file perdait ses arguments dans {100-pct_edit_ok:.1f}% des cas, d'où la bascule sur script Python dans la V5/V6 !")

    print("\n📊 4. VALIDITÉ SYNTAXIQUE AST DU CODE PYTHON GÉNÉRÉ :")
    print(f"   • Scripts Python audités        : {python_scripts_tested}")
    print(f"   • Syntaxe AST 100% conforme     : {python_scripts_valid_ast}/{python_scripts_tested} ({pct_ast:.2f}%)")
    print(f"   • Erreurs de syntaxe bloquantes : {len(ast_errors)}")

    if ast_errors:
        print("\n⚠️ Exemples d'erreurs de syntaxe détectées dans les logs passés :")
        for origin, idx, err in ast_errors[:3]:
            print(f"   [{origin} #L{idx}] {err}")

    print("\n⏱️ Performance de l'auto-évaluation Niveau 1 :")
    print(f"   • {total_calls} appels analysés en {duration:.2f}s ({duration*1000/total_calls:.2f} ms/décision)")

    print("=" * 75)
    return pct_json > 98.0 and pct_ast > 85.0


if __name__ == "__main__":
    success = run_level1_evaluation()
    sys.exit(0 if success else 1)
