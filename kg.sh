#!/usr/bin/env bash
# Boucle Kaggle : local -> push notebook (GPU) -> récupération des sorties -> soumission
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] && source .env
: "${COMP:?definis COMP dans .env}"; : "${KAGGLE_USER:?definis KAGGLE_USER dans .env}"
SLUG="${KAGGLE_USER}/${COMP}-nb"

case "${1:-help}" in
  check)    kaggle competitions list -s "$COMP" ;;
  files)    kaggle competitions files "$COMP" ;;
  download) kaggle competitions download "$COMP" -p data && (cd data && unzip -oq "*.zip" && rm -f ./*.zip) ;;
  init)     # génère notebook/kernel-metadata.json
            cat > notebook/kernel-metadata.json <<JSON
{
  "id": "$SLUG",
  "title": "${COMP}-nb",
  "code_file": "main.ipynb",
  "language": "python",
  "kernel_type": "notebook",
  "is_private": true,
  "enable_gpu": true,
  "enable_tpu": false,
  "enable_internet": false,
  "competition_sources": ["$COMP"],
  "dataset_sources": [],
  "kernel_sources": [],
  "model_sources": []
}
JSON
            echo "OK -> notebook/kernel-metadata.json ($SLUG)" ;;
  push)     kaggle kernels push -p notebook ;;
  status)   kaggle kernels status "$SLUG" ;;
  wait)     while :; do s=$(kaggle kernels status "$SLUG" 2>&1); echo "$(date +%T) $s"
              echo "$s" | grep -qiE 'complete|error|cancel' && break; sleep 30; done ;;
  output)   rm -rf output/* && kaggle kernels output "$SLUG" -p output && ls -la output ;;
  submit)   f="${2:-output/submission.csv}"; msg="${3:-$(date +%F_%T)}"
            kaggle competitions submit "$COMP" -f "$f" -m "$msg" ;;
  subs)     kaggle competitions submissions "$COMP" ;;
  lb)       kaggle competitions leaderboard "$COMP" -s | head -20 ;;
  run)      "$0" push && "$0" wait && "$0" output ;;
  *) cat <<H
Usage: ./kg.sh <cmd>
  check      vérifie que le concours existe / accès
  files      liste les fichiers du concours
  download   télécharge + dézippe dans data/
  init       génère notebook/kernel-metadata.json
  push       envoie notebook/ sur Kaggle et lance l'exécution (GPU)
  status     état de l'exécution
  wait       attend la fin de l'exécution
  output     récupère les sorties dans output/
  run        push + wait + output
  submit [fichier] [message]   soumet (défaut: output/submission.csv)
  subs       liste tes soumissions
  lb         top du leaderboard
H
esac
