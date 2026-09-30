#!/usr/bin/env bash
# Raccourci : agy sur ce projet. Options et conversations epinglees : voir ./tmux.sh
exec "$(dirname "${BASH_SOURCE[0]}")/tmux.sh" agy "$@"
