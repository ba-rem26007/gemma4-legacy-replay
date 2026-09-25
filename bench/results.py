#!/usr/bin/env python3
"""Agrège les runs d'évaluation TEST → docs/RESULTATS.md (verdicts réévalués si disponibles).

Un bug est « résolu » si l'oracle passe ET qu'aucune régression n'est détectée (anti-régression avant l'oracle).
Usage : python3 bench/results.py
"""
import csv, json, random, statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "runs"
# essais par condition (essai 1 = run interrompu puis repris → union de deux dossiers)
TRIALS = {
    "A": [["20260925-092935-A", "20260925-101441-A"], ["20260925-114612-A"], ["20260925-142912-A"], ["20260925-165642-A"]],
    "R": [["20260925-092934-R", "20260925-101441-R"], ["20260925-114712-R"], ["20260925-143833-R"], ["20260925-171642-R"]],
}
LABEL = {"A": "A · ticket seul", "R": "R · ticket + 2 corrections TRAIN similaires"}


def load(dirs, bugs):
    out = {}
    for d in dirs:
        for pr in bugs:
            base = RUNS / d / pr
            r0 = base / "result.json"
            if not r0.exists():
                continue
            r = json.loads(r0.read_text())
            rv = base / "result_reeval.json"
            if rv.exists():
                v = json.loads(rv.read_text())
                r.update({k: v.get(k) for k in ("applied", "fixed", "regression")})
                r["reeval"] = True
            out[pr] = r
    return out


def main():
    bugs = [r["pr"] for r in csv.DictReader(open(ROOT / "data" / "bugs_test.csv")) if r["statut"] == "valide"]
    title = {r["pr"]: r["titre_ticket"] for r in csv.DictReader(open(ROOT / "data" / "bugs_test.csv"))}
    data = {c: [load(t, bugs) for t in TRIALS[c]] for c in TRIALS}
    solved = lambda r: bool(r and r.get("fixed") and not r.get("regression"))

    lines = ["# Résultats — vivier TEST 9.1.x (33 bugs, oracles cachés)", "",
             "Gemma 4 31B (API Google AI Studio), déroulé fixe, **1 tentative par bug** (pas de retour de test), température 0,2.",
             "« Résolu » = l'oracle passe **et** aucune régression (accueil FO + login BO) sur la base remise à zéro.",
             "Verdicts **réévalués** sans rappeler le modèle (`bench/reeval.py`) sur instances neuves quand disponibles.",
             "L'essai 1 a tourné sur un environnement partiellement défectueux : sa génération est valable, son verdict l'est après réévaluation.", ""]
    lines += ["## Taux de résolution par essai", "", "| Condition | Essai 1 | Essai 2 | Essai 3 | Essai 4 | Moyenne | Écart-type | Résolu ≥ 1 fois (pass@4) | Bon fichier (moy.) | Régressions |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    per_bug = {}
    for c in TRIALS:
        counts, locs, regs, reev, n_eval = [], [], 0, 0, []
        for t in data[c]:
            counts.append(sum(solved(t.get(b)) for b in bugs))
            locs.append(sum(bool(t.get(b, {}).get("loc_hit")) for b in bugs))
            regs += sum(bool(t.get(b, {}).get("regression")) for b in bugs)
            reev += sum(bool(t.get(b, {}).get("reeval")) for b in bugs)
            n_eval.append(sum(b in t for b in bugs))
        ever = sum(any(solved(t.get(b)) for t in data[c]) for b in bugs)
        for b in bugs:
            per_bug.setdefault(b, {})[c] = sum(solved(t.get(b)) for t in data[c])
        cells = [f"{k}/{n}" for k, n in zip(counts, n_eval)]
        lines.append(f"| {LABEL[c]} | {' | '.join(cells)} | {statistics.mean(counts):.1f} ({statistics.mean(counts) / len(bugs):.0%}) | "
                     f"{statistics.pstdev(counts):.1f} | {ever}/{len(bugs)} | {statistics.mean(locs):.1f} | {regs} |")
    # écart R − A apparié par bug (bootstrap)
    diffs = [(per_bug[b]["R"] - per_bug[b]["A"]) / 4 for b in bugs]
    random.seed(0)
    boots = sorted(statistics.mean(random.choices(diffs, k=len(diffs))) for _ in range(5000))
    lo, hi = boots[125], boots[4875]
    lines += ["", "## R contre A (apparié par bug)", "",
              f"Écart moyen du taux de résolution R − A : **{statistics.mean(diffs):+.1%}** "
              f"(IC 95 % bootstrap : {lo:+.1%} à {hi:+.1%}).",
              "Si l'intervalle contient 0, l'injection de corrections similaires n'a pas d'effet démontré.", ""]
    never = [b for b in bugs if per_bug[b]["A"] == 0 and per_bug[b]["R"] == 0]
    always = [b for b in bugs if per_bug[b]["A"] == 4 and per_bug[b]["R"] == 4]
    lines += [f"- Bugs jamais résolus (0/8) : **{len(never)}**", f"- Bugs toujours résolus (8/8) : **{len(always)}**", "",
              "## Détail par bug (nombre d'essais résolus sur 4)", "", "| Bug | Ticket | A | R |", "|---|---|---|---|"]
    for b in sorted(bugs, key=lambda b: -(per_bug[b]["A"] + per_bug[b]["R"])):
        lines.append(f"| [#{b}](https://github.com/PrestaShop/PrestaShop/pull/{b}) | {title[b][:70]} | {per_bug[b]['A']} | {per_bug[b]['R']} |")
    (ROOT / "docs" / "RESULTATS.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:20]))


if __name__ == "__main__":
    main()
