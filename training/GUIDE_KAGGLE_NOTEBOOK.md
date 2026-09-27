# Guide Clé en Main : Fine-Tuning Gemma 4 sur Kaggle Notebook (GPU Gratuit)

Ce guide permet de lancer le fine-tuning ou la simulation de Gemma 4 à distance directement sur l'infrastructure gratuite de Kaggle (GPU P100 ou T4 x 2), sans consommer les ressources de votre PC.

---

## 1. Création du Notebook sur Kaggle

1. Rendez-vous sur [kaggle.com/code](https://www.kaggle.com/code) et cliquez sur **"New Notebook"**.
2. Dans le panneau latéral droit (**Notebook options**) :
   - **Accelerator** : Sélectionnez **GPU T4 x 2** ou **GPU P100**.
   - **Internet** : Basculez sur **Internet on** (indispensable pour cloner le repo et télécharger Gemma 4).
   - **Environment** : "Always use latest environment".

---

## 2. Configuration du Token Hugging Face (Secrets Kaggle)

Pour télécharger les poids de `google/gemma-4-e4b-it` sans exposer votre token en clair :
1. Dans le menu du Notebook : **Add-ons** > **Secrets**.
2. Créez un secret avec :
   - **Label** : `HF_TOKEN`
   - **Value** : Votre token d'accès Hugging Face (Read).

---

## 3. Cellules du Notebook (Copier-Coller)

### Cellule 1 : Clonage du projet et installation des dépendances
```python
!git clone https://github.com/ba-rem26007/gemma4-legacy-replay.git
%cd gemma4-legacy-replay
!pip install -q -r training/requirements.txt
```

### Cellule 2 : Connexion sécurisée à Hugging Face
```python
from kaggle_secrets import UserSecretsClient
from huggingface_hub import login

user_secrets = UserSecretsClient()
hf_token = user_secrets.get_secret("HF_TOKEN")
login(token=hf_token)
```

### Cellule 3 : Test rapide de simulation (Dry-Run en 1 minute sur le GPU Kaggle)
```bash
!python3 training/train_agentic_debugger.py --dry-run
```
*Vérifie immédiatement en 15 pas que la mémoire du GPU Kaggle et les gradients sont stables.*

### Cellule 4 : Lancement du Fine-Tuning complet
```bash
!python3 training/train_agentic_debugger.py \
  --model "google/gemma-4-e4b-it" \
  --data "trajectories/train.jsonl,trajectories/self.jsonl" \
  --out "/kaggle/working/lora_gemma4" \
  --max-len 4096 \
  --epochs 3 \
  --lr 5e-5 \
  --max-grad-norm 0.1 \
  --rank 32 \
  --alpha 64 \
  --grad-accum 8 \
  --batch-size 1
```

### Cellule 5 : Sauvegarde de l'adaptateur LoRA final
```python
import shutil
# Archiver les poids de l'adaptateur pour téléchargement ou export en dataset Kaggle
shutil.make_archive("/kaggle/working/gemma4_lora_final", "zip", "/kaggle/working/lora_gemma4/final")
print("✅ Archive prête dans /kaggle/working/gemma4_lora_final.zip !")
```

---

## 4. Avantages de la méthode Kaggle
- **Zéro charge sur votre machine locale**.
- **30 heures par semaine** de calcul GPU gratuit offertes par Kaggle.
- **Téléchargement rapide** des poids Gemma 4 (bande passante Google Cloud interne à Kaggle > 100 Mo/s).
