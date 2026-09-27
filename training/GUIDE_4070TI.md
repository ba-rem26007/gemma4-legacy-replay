# Guide Clé en Main : Entraînement sur RTX 4070 Ti (12 Go)

Ce guide permet de lancer le fine-tuning QLoRA de Gemma 4 sur votre PC Windows / WSL2 sans aucune configuration complexe.

---

## 1. Préparation rapide (sur votre PC)

Ouvrez un terminal **WSL2 (Ubuntu)** :

```bash
# 1. Cloner ou mettre à jour le dépôt
git clone <url-du-depot> gemma4-legacy-replay && cd gemma4-legacy-replay
# ou si déjà cloné : git pull origin main

# 2. Créer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 3. Installer PyTorch CUDA 12.4 et les dépendances
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install -r training/requirements.txt

# 4. Connexion Hugging Face (pour télécharger Gemma 4)
huggingface-cli login
```

---

## 2. Mode Simulation Rapide (Dry-Run en 1 minute) ⚡

Avant de lancer 3 heures d'entraînement, vous pouvez simuler l'exécution complète sur votre RTX 4070 Ti en une seule commande :

```bash
./training/run_4070ti.sh --simulate
```

**Ce que fait la simulation :**
- Charge le modèle Gemma 4 en 4-bit NF4 et SDPA dans votre GPU.
- Exécute **15 étapes d'optimisation** sur un échantillon de 20 trajectoires réelles.
- Mesure la **VRAM crête** (doit rester ≤ 8 Go sur les 12 Go disponibles).
- Valide la **stabilité des gradients** (aucun NaN grâce au `max_grad_norm=0.1`).
- Dure environ **45 à 60 secondes** et ne pollue pas le disque.

---

## 3. Lancement de l'Entraînement Complet

Une fois la simulation validée :

```bash
./training/run_4070ti.sh
```

Par défaut, il utilise **`google/gemma-4-e4b-it`** avec :
- Quantisation QLoRA 4-bit NF4 avec calcul en `bfloat16`.
- Longueur de séquence plafonnée à **4096 tokens** (consommation VRAM estimée : **~7,5 Go sur 12 Go**).
- Découpage strict du gradient **`max_grad_norm = 0.1`** (indispensable pour la stabilité QK-RMSNorm).
- Taux d'apprentissage **`5e-5`** et rang LoRA $r=32$.

### Variante Gemma 4 12B :
Si vous souhaitez tester directement le modèle 12B :
```bash
./training/run_4070ti.sh google/gemma-4-12b-it
```
*(Sur 12B en 4-bit, la VRAM montera à ~11 Go ; fermer les autres applications gourmandes sur le GPU).*

---

## 4. Reprise automatique & Sortie

- **En cas d'arrêt ou d'interruption** : Relancez simplement `./training/run_4070ti.sh`. L'entraînement reprend automatiquement au dernier checkpoint sauvegardé (`checkpoint-*`).
- **Résultat final** : L'adaptateur LoRA final est exporté dans :
  `training/lora_4070ti/final/`
- Vous pourrez ensuite tester directement cet adaptateur sur les 33 bugs TEST pour mesurer le gain de la **Condition D** !
