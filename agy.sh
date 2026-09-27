#!/usr/bin/env bash
# =============================================================================
# Lanceur Antigravity CLI (agy) sous tmux persistant (gemma4-legacy-replay / kaggle)
# Survit aux coupures réseau / SSH et permet de reprendre la conversation.
#
# Usage :
#   ./agy.sh               Rattache ou lance la session et reprend cette conversation
#   ./agy.sh -c            Reprend la toute dernière conversation (agy --continue)
#   ./agy.sh <id>          Reprend une conversation spécifique par son UUID
#   ./agy.sh -n            Démarre une nouvelle conversation propre
#   ./agy.sh -k            Ferme la session tmux agy-kaggle
#
# Détachement sans couper le processus : Ctrl+b puis d
# =============================================================================

set -euo pipefail

SESSION="agy-kaggle"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONV_ID="40d48b50-e1cf-4827-bbf1-1deb52d1fb69"

AGY="$(command -v agy || echo /home/elrems/.local/bin/agy)"

if [ ! -x "$AGY" ]; then
  echo "Erreur : agy introuvable à l'emplacement $AGY" >&2
  exit 1
fi

FLAGS="--dangerously-skip-permissions"

case "${1:-}" in
  -k|--kill)
    if tmux has-session -t "$SESSION" 2>/dev/null; then
      tmux kill-session -t "$SESSION"
      echo "Session tmux '$SESSION' fermée."
    else
      echo "Aucune session '$SESSION' active."
    fi
    exit 0
    ;;
  -n|--new)
    CMD="$AGY $FLAGS"
    ;;
  -c|--continue)
    CMD="$AGY --continue $FLAGS"
    ;;
  "")
    # Par défaut : reprend la conversation courante, avec fallback sur --continue
    CMD="$AGY --conversation $CONV_ID $FLAGS || $AGY --continue $FLAGS"
    ;;
  *)
    # Si un UUID ou identifiant de conversation est passé en paramètre
    CMD="$AGY --conversation $1 $FLAGS"
    ;;
esac

# Création de la session tmux si elle n'existe pas encore
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Création de la session tmux '$SESSION' dans $DIR..."
  tmux new-session -d -s "$SESSION" -c "$DIR" \
    "bash -lc '$CMD; echo \"\"; echo \"--- agy s est terminé. Shell interactif ouvert pour préservation ---\"; exec bash'"
fi

# Rattachement à la session tmux (adaptatif selon contexte)
if [ -n "${TMUX:-}" ]; then
  tmux switch-client -t "$SESSION"
else
  tmux attach-session -t "$SESSION"
fi
