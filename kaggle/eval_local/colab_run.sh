#!/usr/bin/env bash
# Éval locale Leaderboard (VM Colab, après colab_setup.sh + colab_prep2.sh) : vLLM comme l'évaluateur (HARNESS_README §3.3),
# puis harnais officiel via g4kit-harness, sandbox subprocess. Chaque bras est coupé en 2 moitiés → 4 harnais en parallèle.
# Usage (VM) : bash colab_run.sh <tag> "<bras>=<dossier>=<time_scale>" …     Résultats : runs/<tag>/<bras>_<moitié>/
cd /content/lb
TAG=$1; shift
pkill -INT -f g4kit-fake-llm 2>/dev/null
if ! curl -s localhost:8000/v1/models | grep -q gemma; then
  nohup vllm serve models/gemma-4-31b-it-qat-w4a16-ct --served-model-name gemma-4-31b-it-qat-w4a16-ct --port 8000 \
    --max-model-len 32768 --enable-auto-tool-choice --tool-call-parser gemma4 --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": true}' --chat-template kit/assets/chat_template.jinja \
    --gpu-memory-utilization 0.92 --enable-prefix-caching > vllm.log 2>&1 &
  until curl -s localhost:8000/v1/models | grep -q gemma; do sleep 15; done
fi
echo "vLLM prêt $(date -u +%FT%T)"
# SLOW=1 : relais à la vitesse de l'évaluateur (slow_proxy.py, port 8001) — défaut depuis le 4 oct. (0,05 sur Kaggle vs 28 % en local)
API=http://127.0.0.1:8000/v1
if [ "${SLOW:-1}" = 1 ]; then
  curl -s localhost:8001/v1/models | grep -q gemma || { nohup python3 slow_proxy.py --listen 8001 --log "slow_proxy_$TAG.jsonl" > slow_proxy.log 2>&1 & sleep 3; }
  API=http://127.0.0.1:8001/v1
fi
read -r A B <<< "$(python3 -c "
import json;ids=[x['instance_id'] for x in json.load(open('lot.json'))]
print(','.join(ids[0::2]), ','.join(ids[1::2]))")"
PIDS=()
for arm in "$@"; do
  IFS='=' read -r name dir scale <<< "$arm"
  for half in A B; do
    ids=${!half}
    g4kit-harness run --arm "$name=$dir" --tasks comp/tasks.jsonl --snapshots comp/snapshots --ids ${ids//,/ } \
      --api-base "$API" --out "runs/$TAG/${name}_$half" --time-scale "$scale" --sandbox subprocess \
      --wheels-dir comp/wheels --task-env /content/lb/taskenv --graph-dir comp/graphs --embeddings-dir comp/embeddings \
      > "runs_${TAG}_${name}_$half.log" 2>&1 &
    PIDS+=($!)
  done
done
wait "${PIDS[@]}"
echo "PASSAGE TERMINÉ $TAG $(date -u +%FT%T)"
