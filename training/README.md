# Fine-tuning QLoRA Frugal de Gemma 4

Ce module contient les scripts d'entraînement supervisé (SFT) et les optimiseurs d'attention pour fine-tuner **Gemma 4 (4B)** avec un adaptateur LoRA compact de 134 Mo sur GPU 16 Go (Nvidia Tesla T4 ou RTX 4070 Ti 12 Go).

---

## 1. L'Innovation `ChunkedLossTrainer` (`training/chunked_loss.py`)

Gemma 4 intègre un vocabulaire étendu de **262 144 tokens**.  
Sur une séquence de 4 096 tokens, la projection complète des logits en float32 génère une matrice temporaire de plus de 4,3 Go, déclenchant des erreurs `CUDA Out of Memory` systématiques sur les GPU grand public.

Notre classe `ChunkedLossTrainer` résout ce goulot d'étranglement :
1. **Extraction des états cachés** : Le modèle retourne les états cachés de l'avant-dernière couche (`hidden_states`).
2. **Filtrage des labels utiles** : Seules les positions des réponses de l'assistant (`labels != -100`) sont conservées.
3. **Projection par micro-blocs différentiables** : La tête `lm_head` est appliquée séquentiellement par tranches de **256 tokens**, calculant la cross-entropy au vol.
4. **Impact** : **94% de réduction du pic de VRAM** de la fonction de perte (< 300 Mo de mémoire requise pour la loss).

---

## 2. Lancement sur GPU Kaggle (Tesla T4 Gratuit)

Voir le guide détaillé : [`training/GUIDE_KAGGLE_NOTEBOOK.md`](GUIDE_KAGGLE_NOTEBOOK.md).

```bash
python3 training/kaggle_kernel/train_kaggle.py \
  --model "google/gemma-4-e4b-it" \
  --data "trajectories/train.jsonl,trajectories/self.jsonl" \
  --out "lora_gemma4_final" \
  --epochs 3 \
  --lr 2e-4 \
  --chunk-size 256
```

### Paramètres de la Version Finale Officielle (Kaggle Run v15)
* **Époques** : 3 époques complètes sur 585 trajectoires vérifiées.
* **Perte finale** : Descente de 1.564 à 0.9309 (perte moyenne : 1.192).
* **Taille de l'adaptateur produit** : **134 Mo** (`adapter_model.safetensors`).
* **Consommation VRAM active** : 4.29 Go en inférence 4-bit.
* **Budget financier** : 0,00 € (`runs/_budget.json`).

---

## 3. Scripts et Configurations Disponibles

1. **`training/chunked_loss.py`** : Module autonome et découplé implémentant le `ChunkedLossTrainer` pour Hugging Face `transformers`.
2. **`training/kaggle_kernel/train_kaggle.py`** : Script d'entraînement complet exécuté sur l'environnement Kaggle.
3. **`training/train_agentic_debugger.py`** : Entraîneur `trl` (`SFTTrainer`) optimisé pour les traces agentiques avec masquage strict des prompts.
4. **`training/axolotl_gemma4.yaml`** : Configuration déclarative pour Axolotl avec attention hybride et packing de séquences.
5. **`training/lora_final/`** : Répertoire contenant les poids extraits et le rapport de convergence.
