# Fine-tuning QLoRA (phase 7)

Entraîne un adaptateur LoRA de Gemma 4 sur les chemins condensés `trajectories/train.jsonl`.
Loss uniquement sur les tours assistant ; 2 chemins max par bug ; checkpoints + reprise auto.

## Sur ton PC (RTX 4070 Ti, 12 Go)
Recommandé : **WSL2 Ubuntu** (Docker Desktop l'utilise déjà). Sous Windows natif, bitsandbytes marche aussi.
```bash
git clone <url-du-depot> gemma4-legacy-replay && cd gemma4-legacy-replay
python -m venv .venv && source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install -r training/requirements.txt
huggingface-cli login                                       # accepter la licence Gemma sur huggingface.co au préalable
python training/train_qlora.py --model google/gemma-4-e4b-it --max-len 4096
```
- 12 Go : `gemma-4-e4b-it` passe confortablement. Le 12B en 4 bits est limite, à essayer avec `--max-len 3072` ; sinon passer sur Kaggle (16 Go).
- Coupure : relancer la même commande, la reprise part du dernier checkpoint (`training/lora/checkpoint-*`).
- Sortie : `training/lora/final` (adaptateur) + `log_history.json` (courbe de perte).

⚠ Vérifier l'identifiant exact du modèle sur https://huggingface.co/google (famille Gemma 4).

## Sur Kaggle (P100 / T4, 16 Go)
Pousser le dépôt comme dataset Kaggle, puis dans le notebook :
`python training/train_qlora.py --model google/gemma-4-12b-it --out /kaggle/working/lora` (mode « Save & Run All »).

## Données
- `trajectories/self.jsonl` : **chemins Gemma vérifiés** (boucle d’auto-apprentissage, `source=gemma_self`), régénéré par `bench/loop_stats.py` ; lus avec train.jsonl par défaut.
- `trajectories/train.jsonl` : **chemins reconstruits** depuis les correctifs officiels (vivier TRAIN, avant la coupure), vérifiés.
- Régénérer : `python trajectories/reconstruct.py --cutoff <date>` (nécessite `bench/ps`, voir le README racine).
- Aucune donnée générée par un modèle propriétaire.

## Longueur de séquence
`--max-len 8192` par défaut : les chemins font jusqu'à ~8 000 tokens (médiane ≈ 3 900). Les exemples plus longs sont **écartés**, pas tronqués (l'édition finale est à la fin), et leur nombre est affiché.
Mémoire insuffisante (12 Go) → `--max-len 6144` (perd ≈ 10 % des chemins) plutôt que 4096 (≈ 40 %).

## Hyperparamètres de stabilité Gemma 4
En raison de la sensibilité de Gemma 4 à la normalisation QK-RMSNorm et à l'attention mise à l'échelle :
- **Taux d'apprentissage** : `5e-5` par défaut (`--lr 5e-5`), cosine schedule avec warmup 5 %.
- **Découpage de gradient strict** : `max_grad_norm = 0.1` (`--max-grad-norm 0.1`) pour éviter l'instabilité numérique.
- **Précision** : `bfloat16` natif (ou 4-bit NF4 double quant avec compute `bfloat16`).
- **Masquage des labels** : Loss calculée **uniquement** sur les tours assistant (labels à `-100` pour tous les retours d'outils, tickets et sorties de bac à sable).
- **Attention** : `sdpa` (PyTorch Scaled Dot-Product Attention) ou `flash_attention_2` avec dimension de tête 512.

## Scripts & Configurations disponibles
1. **`training/train_qlora.py`** : Entraîneur standard Hugging Face `Trainer` + `peft` avec masquage manuel rigoureux des tokens hors assistant.
2. **`training/train_agentic_debugger.py`** : Entraîneur Hugging Face `trl` (`SFTTrainer`) optimisé pour les traces de débogage agentiques, rank 32 / alpha 64 et attention SDPA.
3. **`training/axolotl_gemma4.yaml`** : Configuration déclarative pour **Axolotl** avec `gemma4_hybrid_attn_impl: true` et support multi-GPU / sample packing.


