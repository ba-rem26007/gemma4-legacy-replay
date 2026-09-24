#!/usr/bin/env bash
# Lance (ou reprend) une session tmux avec Claude Code sur ce projet.
# Usage : ./tmux.sh
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION="$(basename "$DIR")"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  # Nouvelle session : reprend la dernière conversation Claude du projet, sinon en démarre une
  tmux new-session -d -s "$SESSION" -c "$DIR" -n claude
  tmux send-keys -t "$SESSION:claude" "claude --continue || claude" C-m
fi

# Attache (ou bascule si on est déjà dans tmux)
if [ -n "${TMUX:-}" ]; then
  tmux switch-client -t "$SESSION"
else
  tmux attach-session -t "$SESSION"
fi
