# RÈGLES

## 1. Règlement officiel
Concours Kaggle « Google - The Gemma 4 Developer Agent », **Paper Track**.

### Vérifié (d'après le kit)
- 5 critères à poids égal, notés de 0 à 5, note finale = moyenne : **nouveauté, qualité, pertinence, vérifiabilité, clarté**.
- 3 papiers récompensés ; grille non communiquée.
- Interdiction de soumettre du contenu qui viole des droits de tiers ou des obligations de confidentialité.
- Deadline : **12 novembre 2026, 23:59 UTC** (interne : 9 nov. ; à égalité, le papier soumis le plus tôt l'emporte).

### À vérifier
- [ ] Aucune version de Gemma 4 imposée pour le Paper Track ?
- [ ] Compétition principale : modèle `gemma-4-31b-it-qat-w4a16`, 4 × L4, évaluateur « swegemma » avec 9 outils et compilation ADK ?
- [ ] Doc des 9 outils publiée ? Si oui, notre agent les reprend à l'identique.
- [ ] Clauses sur la distillation / l'usage de modèles externes.
- [ ] Format du Writeup (3 000 mots max ?) et pièces attendues.

### Texte officiel (à coller par Rémi)
#### Paper Track : Overview
_à coller_
#### Paper Track : Evaluation
_à coller_
#### Paper Track : Rules
_à coller_
#### Paper Track : Data
_à coller_
#### Compétition principale : Overview / Evaluation / Rules / Data
_à coller_

### Points qui touchent notre plan
_à remplir après lecture du texte officiel_

## 2. Règles du projet (non négociables)
- **Aucun code client ou privé.** Uniquement du public, tout finira en public.
- **Aucune citation inventée.** Chaque référence a un lien vérifié, sinon elle n'entre pas.
- **Pas de recherche de failles de sécurité.** On corrige des bugs connus et publiés ; tout ce qui touche la sécurité, l'authentification ou le contrôle d'accès est exclu.
- **Aucun modèle propriétaire pour générer des données d'entraînement** (Claude, GPT…), y compris via des datasets publics d'instruction de provenance douteuse. Claude Code écrit le code de la fabrique, jamais son contenu.
- **JAMAIS d'ajustement sur le TEST** (décision du 2 oct. 2026) : aucun réglage de l'agent, du prompt, des outils, des hyperparamètres ni des données d'entraînement ne se décide en regardant les bugs TEST. Un levier trouvé en analysant des échecs TEST (ex. `docs/ECHECS.md`, diagnostic des bugs non résolus) est d'abord **validé sur des bugs TRAIN** (ex. les 99 bugs TRAIN à oracle Gemma, `docs/BOUCLE.md`) ; seul un levier qui aide sur TRAIN est ensuite mesuré **une fois** sur TEST, et le papier dit d'où vient le levier. Pas d'itérations successives « régler → mesurer sur TEST ».
- **ÉTANCHÉITÉ** : aucun bug TEST, ni aucun correctif touchant les mêmes lignes ou fichiers, dans les données d'entraînement. Contrôle à chaque étape.
- `ETAT.md` à jour à la fin de chaque étape ; `DECISIONS.md` pour chaque choix structurant.
- Demander avant toute commande destructive ou tout téléchargement > 5 Go.
- Une phase à la fois ; on s'arrête et on présente le livrable.

---

## 3. Contraintes d'Ingénierie & d'Entraînement Gemma 4 (Agentic Debugging)

### 3.1 Sémantique d'exécution & Traces multi-tours
- **Apprentissage de l'exécution (`CodeTrace`)** : Le modèle doit intégrer la sémantique dynamique (états mémoire `VAR`, branchements `BRANCH`, boucles `LOOP`, erreurs `ERR`) plutôt que de simples paires statiques bug/patch.
- **Scénarios agentiques multi-tours (`CodeDialogue` / `CodeDev`)** : Les données d'entraînement doivent reproduire les cycles complets de débogage : *Localisation / Stack trace → Patch proposé → Retour d'exécution terminal / tests → Correctif ciblé*.
- **Masquage strict de la perte (Loss Masking)** : Perte appliquée **uniquement sur les tours assistant**. Tous les retours de l'environnement (tickets, sorties d'outils, codes d'erreur, contenus bruts) ont leurs labels masqués (`-100`).
- **Préservation de la réflexion (`<|think|>` / `<thought>`)** : Conserver au moins 75 % d'exemples comprenant des blocs de réflexion explicites afin d'apprendre au modèle à analyser la cause racine avant d'émettre des blocs d'édition.

### 3.2 Validation dynamique en Sandbox (Zéro Hallucination)
- **Filtrage par exécution réelle** : Aucune trajectoire n'entre dans le vivier d'entraînement sans passer à 100 % les tests unitaires / oracles d'intégration exécutés dans un bac à sable isolé (Docker / conteneur).
- **Garde-fous anti-contournement (*Reward Hacking*)** : Tout correctif d'entraînement validé par un oracle doit obligatoirement toucher les fonctions/fichiers légitimes du bug officiel pour être conservé.

### 3.3 Hyperparamètres de stabilité Gemma 4 (Fine-Tuning / QLoRA)
En raison du facteur d'échelle d'attention et de la normalisation **QK-RMSNorm** spécifique à Gemma 4 :
- **Découpage de gradient strict** : `max_grad_norm = 0.1` (obligatoire pour contrer les pics numériques et l'instabilité de gradient).
- **Taux d'apprentissage** : `learning_rate = 5e-5` (avec cosine scheduler et warmup de 5 %).
- **Précision** : `bfloat16` natif (ou 4-bit NF4 double quant + compute `bfloat16`).
- **Choix du backbone selon le matériel** :
  - *Serveur / Cluster* : Gemma 4 26B A4B (MoE) ou Gemma 4 31B Dense.
  - *Poste local (RTX 4070 Ti, 12 Go VRAM)* : Gemma 4 E4B (ou 12B QAT 4-bit avec limite de longueur de séquence adaptée).

---

## 4. Piliers d'Architecture Concours Kaggle (Alignement Évaluateurs)
- **Exécution Edge-First / Zero Connectivité** : Conception prioritairement déployable en local ou sur matériel contraint sans dépendance cloud propriétaire.
- **Confidentialité absolue (*Privacy-by-Design*)** : Aucune donnée ni code source sensible ne quitte l'environnement local.
- **Conception Hybride Non-Hallucinatoire** : Association des capacités de génération du LLM à des vérificateurs et oracles déterministes.
- **Vérifiabilité & Reproductibilité totale** : Code source complet exécutable, writeup documenté (3 000 mots pour le Paper Track), métriques mesurées sans citation inventée ni données propriétaires.
