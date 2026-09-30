#!/usr/bin/env bash
# Raccourci : codex sur ce projet. Options et conversations epinglees : voir ./tmux.sh
exec "$(dirname "${BASH_SOURCE[0]}")/tmux.sh" codex "$@"
