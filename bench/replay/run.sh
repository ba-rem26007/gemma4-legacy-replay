#!/usr/bin/env bash
# Rejoue les tests d'un bug contre une instance. Usage : [PSB=n] bench/replay/run.sh <pr> [oracle|replay]
# (filtre facultatif : « oracle » = verdict caché, « replay » = tests visibles par l'agent)
set -euo pipefail
cd "$(dirname "$0")"; PR="${1:?pr}"
PSB="${PSB:-1}"; PROJ="psbench$([ "$PSB" = 1 ] || echo "$PSB")"
export PS_PORT="${PS_PORT:-$((8080 + PSB))}"
[ -f "$PR/setup.sql" ] && docker exec -i "$PROJ-db-1" mysql -padmin prestashop < "$PR/setup.sql" 2>/dev/null
docker exec "$PROJ-ps-1" sh -c 'rm -rf /var/www/html/var/cache/*'
# Par défaut : l'oracle seul s'il existe (verdict) ; sinon tous les tests du dossier (bugs pilotes).
FILTER="${2:-}"
[ -z "$FILTER" ] && ls "$PR"/oracle*.spec.js >/dev/null 2>&1 && FILTER=oracle
npx playwright test "$PR/$FILTER"
