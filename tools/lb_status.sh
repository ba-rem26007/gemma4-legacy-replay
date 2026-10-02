#!/usr/bin/env bash
# Avancement d'un passage d'éval locale Leaderboard sur la VM Colab : par bras, tâches finies / résolues / patchs vides.
# Usage : tools/lb_status.sh <session_colab> <tag>
S=$1; TAG=$2
printf 'import json,glob,collections\nc=collections.defaultdict(lambda:[0,0,0,0.0])\nfor f in glob.glob("/content/lb/runs/%s/*/results_*.jsonl"):\n    for l in open(f):\n        r=json.loads(l); k=c[r["arm"]]; k[0]+=1; k[1]+=bool(r.get("resolved")); k[2]+=r.get("patch_chars",0)==0; k[3]+=r.get("wall_s",0)\nfor a,(n,ok,vide,t) in sorted(c.items()): print(f"{a}: {n} finies, {ok} résolues, {vide} patchs vides, {t/max(n,1)/60:.1f} min/tâche")\nprint("FINI" if "PASSAGE TERMINÉ" in open("/content/lb/run_%s.log").read() else "en cours")\n' "$TAG" "$TAG" > "${TMPDIR:-/tmp}/lbst_$$.py"
for i in 1 2 3; do out=$(timeout 120 "$HOME/.local/bin/colab4" exec -s "$S" -f "${TMPDIR:-/tmp}/lbst_$$.py" 2>&1) && { echo "$out"; break; }; sleep 10; done
rm -f "${TMPDIR:-/tmp}/lbst_$$.py"
