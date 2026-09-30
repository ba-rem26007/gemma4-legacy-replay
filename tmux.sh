#!/usr/bin/env bash
# Lance ou rattache une IA sur ce projet dans tmux (survit aux coupures SSH).
#
#   ./tmux.sh [claude|agy|codex] [-n nouvelle | -c derniere | <id> | -k ferme | -h]
#
# Sans IA : rattache la session du projet si une seule tourne, sinon demande.
# Raccourcis : ./cl.sh, ./agy.sh, ./codex.sh (= ./tmux.sh <ia> ...).
# Sessions : claude-kaggle / agy-kaggle / codex-kaggle (les memes que `cl`, `ag`, `cx`).
# Moteur commun : ~/bin/ia-tmux — doc : ~/dotfiles/IA.md
# Detacher sans rien couper : Ctrl-b puis d.

# Conversations reprises par defaut (vide = la derniere de ce dossier) :
export IA_PIN_CLAUDE=""
export IA_PIN_AGY="40d48b50-e1cf-4827-bbf1-1deb52d1fb69"
export IA_PIN_CODEX=""

export IA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$HOME/bin/ia-tmux" "$@"
