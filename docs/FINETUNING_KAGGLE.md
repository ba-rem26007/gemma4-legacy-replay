# Fine-Tuning QLoRA Gemma 4 sur Kaggle GPU (Version 15)

Ce document consigne la réalisation, les paramètres, le défi mémoire résolu et les résultats du fine-tuning autonome de Gemma 4 sur GPU Tesla T4 via Kaggle.

---

## 1. Contexte & Objectifs

L'objectif du fine-tuning est d'adapter le modèle Gemma 4 à l'architecture PrestaShop 9.x à partir des trajectoires de résolution vérifiées issues de la boucle d'auto-apprentissage (chemins purs sans hallucinations, sans sorties propriétaires).
* **Date d'exécution** : 28 septembre 2026 (11h10 - 13h20 UTC).
* **Plateforme** : Kaggle GPU (2x Tesla T4, 15 Go VRAM par GPU).
* **Statut final** : `KernelWorkerStatus.COMPLETE`.

---

## 2. Données d'Entraînement

* **Source** : Dataset Kaggle `rmisoubeyrand/gemma4-prestashop-trajectories`.
* **Volume brut** : 1 007 trajectoires candidates.
* **Filtrage & Équilibrage** :
  * Dédoublonnage strict et plafonnement à max 2 trajectoires par bug.
  * Masquage causal : perte calculée **uniquement sur les tokens de réponse assistant** (`labels == -100` pour tous les tours système, utilisateur et retours d'outils).
  * 585 trajectoires pures retenues.
  * Longueur de contexte calibrée à 2 048 tokens.

---

## 3. Configuration Modèle & QLoRA

* **Modèle de base** : `google/gemma-4-e4b-it` (4 milliards de paramètres).
* **Quantification** : 4-bit NormalFloat (NF4), double quantification (`bnb_4bit_use_double_quant=True`), compute dtype `bfloat16` / `float16`.
* **Couches cibles LoRA** : Ciblage exclusif des projections linéaires du sous-module textuel `language_model` :
  * `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`.
  * Total : **258 modules linéaires adaptés** (exclusion explicite des tours vision et audio).
* **Hyperparamètres LoRA** :
  * Rang $r = 16$, $\alpha = 32$.
  * Dropout LoRA : $0.05$.
  * Paramètres entraînables : **34 881 536** sur 7 975 982 368 (0,437% du modèle).
* **Optimiseur** : `paged_adamw_8bit` (pagination automatique des états d'optimiseur vers la RAM CPU en cas de tension VRAM).
* **Paramètres d'entraînement** :
  * Époques : 3
  * Learning rate : $5 \times 10^{-5}$ avec scheduler cosinus.
  * Gradient accumulation steps : 8 (batch effectif = 16 avec 2 GPU).
  * Max gradient norm : 0.1 (stabilisation RMSNorm Gemma 4).

---

## 4. Défi Mémoire Résolu : `ChunkedLossTrainer`

### Le problème
Le vocabulaire de Gemma 4 compte **262 144 tokens**.
Avec une longueur de séquence de 2 048 tokens, le tenseur complet des logits `(batch, seq, vocab)` requiert :
$$2 \times 2048 \times 262144 \times 4 \text{ octets} \approx 4{,}29 \text{ Go}$$
Dans Transformers standard, `ForCausalLMLoss` effectue `logits = logits.float()`, ce qui alloue instantanément 4,29 Go de mémoire additionnelle, provoquant un `OutOfMemoryError` immédiat sur Tesla T4 (où la mémoire disponible après chargement du modèle est de ~2,3 Go).

### La solution : Micro-chunks de 256 tokens
Création d'un sous-classeur de `Trainer` : `ChunkedLossTrainer`.
1. Appel au modèle avec `logits_to_keep=1` et `output_hidden_states=True` (aucun tenseur de logits 4 Go n'est généré).
2. Récupération de l'état caché final `outputs.hidden_states[-1]`.
3. Sélection par masque booléen des seuls tokens de réponse assistant (`labels != -100`).
4. Projection linéaire par micro-chunks de 256 tokens :
   $$256 \times 262144 \times 4 \text{ octets} \approx 268 \text{ Mo}$$
5. Calcul de la cross-entropy par chunk et sommation différentiable.
**Résultat** : Réduction de **94%** du pic VRAM de la fonction de perte, exécution fluide sans aucun OOM.

---

## 5. Dynamique d'Apprentissage & Résultats

* **Durée totale** : 7 209 secondes (~2h00).
* **Courbe de perte** :
  * Époque 0.89 : Perte = **1.564** (norme gradient 2.906)
  * Époque 1.71 : Perte = **1.425** (norme gradient 2.366)
  * Époque 2.53 : Perte = **0.9309** (norme gradient 1.302)
  * Époque 3.00 : Perte moyenne globale = **1.192**
* **Stabilité** : Aucune instabilité numérique, la norme des gradients a décru de manière monotone de 2.9 à 1.3.

---

## 6. Artefacts Produits & Stockage

* **Archive complète** : `gemma4_lora_final.zip` (128 Mo).
* **Emplacement local extrait** : `training/lora_final/extracted/`
  * `adapter_model.safetensors` (134 Mo)
  * `adapter_config.json`
  * `tokenizer.json` (31 Mo)
  * `tokenizer_config.json`
  * `chat_template.jinja`
* **Miroir de téléchargement public** : `https://anniv.soubeyrand.dev/lora.zip`
