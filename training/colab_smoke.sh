#!/usr/bin/env bash
# Test préalable du fine-tuning dans le TERMINAL Colab (GPU T4) — à coller tel quel. Cf. docs/FINETUNING_KAGGLE.md §0.
# Demande le jeton Kaggle (saisie masquée), récupère données + script depuis Kaggle (datasets privés), lance SMOKE=1.
set -e
[ -n "$KAGGLE_API_TOKEN" ] || { read -rsp "Jeton Kaggle (KAGGLE_API_TOKEN) : " KAGGLE_API_TOKEN; echo; export KAGGLE_API_TOKEN; }
nvidia-smi --query-gpu=name,memory.total --format=csv
python3 --version
pip -q install -U kaggle kagglehub
kaggle datasets download rmisoubeyrand/gemma4-prestashop-trajectories --unzip -p /content/data -o
kaggle datasets download rmisoubeyrand/gemma4-training-script --unzip -p /content/script -o
cd /content/script
SMOKE=1 DATA_DIR=/content/data WORK_DIR=/content/work python3 train_kaggle.py 2>&1 \
  | grep -vE 'Loading weights|Map:|Filter:' | tee /content/smoke.log | tail -40
