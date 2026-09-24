#!/usr/bin/env bash
# Rejoue le test d'un bug contre la stack courante. Usage : bench/replay/run.sh <pr>
set -euo pipefail
cd "$(dirname "$0")"; PR="${1:?pr}"
[ -f "$PR/setup.sql" ] && docker exec -i psbench-db-1 mysql -padmin prestashop < "$PR/setup.sql" 2>/dev/null
docker exec psbench-ps-1 sh -c 'rm -rf /var/www/html/var/cache/*'
npx playwright test "$PR/"
