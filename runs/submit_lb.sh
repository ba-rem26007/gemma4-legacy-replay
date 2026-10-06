#!/usr/bin/env bash
# Soumission Leaderboard : réenvoie le bundle V5 À L'IDENTIQUE (zip sha256 00c376252810…, meilleur score 0,12) pour mesurer
# la variance du classement (V6 = V5 + max_output_tokens 2048 a fait 0,05 ; or seuls 4 appels sur 8 909 dépassent 2 048 tokens
# dans nos traces : l'écart 0,12 → 0,05 ressemble à du bruit). Quota : 1 soumission par jour UTC → pas avant 00 h 00 UTC (2 h Paris).
set -e
cd /home/elrems/kaggle/kaggle
Z=/home/elrems/kaggle/kaggle/submission_v5.zip
[ "$(sha256sum $Z | cut -c1-12)" = "00c376252810" ] || { echo "zip V5 modifié, abandon"; exit 1; }
D=$(mktemp -d); cp $Z $D/submission.zip
PYTHONPATH=$HOME/.local/lib/ipv4only /home/elrems/.local/share/uv/tools/kaggle/bin/python - "$D/submission.zip" <<'PY'
import sys, json, datetime
from kaggle.api.kaggle_api_extended import KaggleApi
a = KaggleApi(); a.authenticate()
r = a.competition_submit(sys.argv[1], "V5 resubmitted unchanged (variance check)", "gemma-4-developer-agent")
print(r)
ref = getattr(r, "ref", None) or (r.get("ref") if isinstance(r, dict) else None)
with open("/home/elrems/kaggle/kaggle/submissions.jsonl", "a") as f:
    f.write(json.dumps({"ref": ref, "date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "kernel": "direct_zip",
        "version": 7, "condition": "V5_rejoue_identique", "model": "gemma-4-31b-it-qat-w4a16-ct",
        "description": "V5 resubmitted unchanged (variance check)", "zip_sha256_12": "00c376252810", "status": "PENDING", "cost_eur": 0.0}) + "\n")
PY
