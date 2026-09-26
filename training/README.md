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
