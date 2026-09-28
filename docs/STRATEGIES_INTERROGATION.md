# Les Stratégies d'Interrogation pour le Débogage : Du Plus Haut Niveau au Plus Bas Niveau

Ce document détaille la hiérarchie complète des techniques d'interrogation et de résolution de bugs par intelligence artificielle, ordonnée **du plus haut niveau d'abstraction (contexte pur en prompt) au plus bas niveau déterministe (machines, types et mémoire)**.

Cette taxonomie formalise pourquoi une simple injection de contexte atteint un plafond de verre et comment notre approche hybride (*Gemma 4 LoRA + Déroulé Fixe + Rejeu Déterministe*) surmonte ces limites.

---

## Vue d'Ensemble de la Hiérarchie

```
  ▲  [NIVEAU 1] Haut Niveau : Injection Totale de Contexte (Prompting Massif & RAG)
  │  [NIVEAU 2] Niveau Intermédiaire : Spécialisation Paramétrique (Fine-Tuning QLoRA)
  │  [NIVEAU 3] Niveau Méthodologique : Déroulé Agentique Contraint (Machine à États & Outils)
  │  [NIVEAU 4] Niveau Dynamique : Boucle Courte d'Exécution (Feedback de Rejeu / Replay)
  │  [NIVEAU 5] Niveau Formel : Analyse Statique de Code (PHPStan, Types & AST)
  ▼  [NIVEAU 6] Plus Bas Niveau : Bac à Sable Déterministe (État Mémoire, BDD & Oracles)
```

---

## Niveau 1 : Le Plus Haut Niveau — Injection Complète de Contexte (In-Context Learning & RAG)

### Principe
On s'appuie sur la capacité brute d'attention du modèle de fondation. On lui injecte dans son prompt l'intégralité du problème :
* Le ticket de bug (titre, description, étapes de reproduction).
* Les fichiers PHP complets suspectés (parfois plusieurs milliers de lignes).
* Des exemples historiques similaires (*Few-Shot / RAG* : 2 ou 3 correctifs passés trouvés par similarité vectorielle ou TF-IDF).
* Le glossaire métier et la documentation de l'architecture.

### Correspondance dans notre Benchmark
* **Condition A** : Ticket seul.
* **Condition R** : Ticket + 2 correctifs TRAIN similaires injectés (RAG).
* **Condition C** : Ticket + glossaire métier bilingue injecté dans le prompt.

### Avantages
* **Zéro entraînement préalable** : Utilisable immédiatement sur n'importe quel LLM générique du marché.
* **Flexibilité totale** : On peut changer les consignes ou les exemples à la volée sans compiler ni recalculer de poids.

### Limites & Coûts
* **Saturation d'attention ("Lost in the Middle")** : Plus le contexte grandit (15k à 100k tokens), plus l'attention du modèle se dilue. Il "oublie" des contraintes cruciales situées au milieu du prompt.
* **Coût financier & latence exorbitants** : Multiplier 30 000 tokens d'entrée par 5 tours d'échange coûte une fortune sur des modèles comme Claude 3.5 Sonnet ou GPT-4o, tout en créant une latence de plusieurs secondes par requête.
* **Résultat empirique dans notre étude** : La Condition R (injection d'exemples similaires) n'apporte **strictement aucun gain (+0.0%)** par rapport au ticket seul (39.0% vs 39.0%). L'injection de contexte brut ne suffit pas à résoudre des bugs complexes.

---

## Niveau 2 : Niveau Intermédiaire — Spécialisation Paramétrique (Fine-Tuning / QLoRA)

### Principe
Au lieu de réexpliquer au modèle à chaque tour comment s'articule PrestaShop, la dualité Symfony/Legacy, ou comment formater un bloc `SEARCH/REPLACE`, **ces réflexes sont gravés directement dans les poids neuronaux** via un adaptateur LoRA de bas rang ($r=16, \alpha=32$).

### Correspondance dans notre Benchmark
* **Condition D** : Modèle Gemma 4 (4B) fine-tuné sur 585 trajectoires de résolution officielles et synthétiques.
* **Condition E** : Modèle fine-tuné combiné aux règles d'architecture métier PrestaShop.

### Avantages
* **Prompts ultra-compacts** : La fenêtre de contexte est divisée par 5 à 10. Le modèle "sait déjà" ce qu'est un `CountryQueryBuilder` ou la table `ps_stock_available`.
* **Frugalité et souveraineté** : Permet à un petit modèle de **4 Milliards de paramètres** (tournant sur une simple carte graphique de 12 Go) d'égaler des monstres propriétaires de plusieurs centaines de milliards de paramètres.
* **Zéro euro de coût d'inférence** : Inférence 100% locale, sans dépendre d'une API tierce.

### Limites
* Nécessite un pipeline d'entraînement rigoureux : filtrage drastique anti-fuite (*leak-proof*), exclusion des bugs de test, formulation mathématique adaptée (*ChunkedLossTrainer* pour éviter l'OOM sur grand vocabulaire).

---

## Niveau 3 : Niveau Méthodologique — Déroulé Agentique Contraint (Machine à États & Outils)

### Principe
Laisser un LLM libre de générer ce qu'il veut conduit à l'échec (*SWE-Gym* démontre qu'un agent libre 7B s'effondre à 1% de réussite). Le modèle est enfermé dans un **déroulé d'états finis obligatoire** :

$$\text{TICKET} \xrightarrow{\text{Étape 1}} \text{LOCALISER (mots-clés)} \xrightarrow{\text{Étape 2}} \text{LIRE (fenêtres } \le 3 \text{ fichiers)} \xrightarrow{\text{Étape 3}} \text{ÉDITER (SEARCH/REPLACE)} \xrightarrow{\text{Étape 4}} \text{TESTER}$$

### Avantages
* **Élimination des divagations** : Le modèle ne peut pas réécrire un fichier entier de 2 000 lignes (ce qui introduit des régressions) ; il est forcé de fournir un diff atomique `SEARCH / REPLACE`.
* **Économie drastique de tokens** : L'outil `windows()` découpe les classes autour des symboles pertinents au lieu de charger tout le fichier.
* **Backtracking contrôlé** : Si la recherche échoue, l'agent dispose d'un droit de retour en arrière explicite sans boucle infinie.

---

## Niveau 4 : Niveau Dynamique — Boucle Courte d'Exécution (Feedback de Rejeu / Replay)

### Principe
Le modèle produit une hypothèse de patch, mais celle-ci n'est pas acceptée aveuglément. Le patch est appliqué dans un conteneur et exécuté contre un **test de reproduction dynamique** (Playwright ou PHPUnit). Si le test échoue, le rapport d'échec exact (assertion manquée, URL inattendue, message d'erreur SQL) est réinjecté dans le prompt pour le tour suivant.

### Correspondance dans notre Benchmark
* **Condition B** : Ticket + feedback d'exécution des tests de reproduction réels (jusqu'à 2 retries).

### Avantages
* **Le bond qualitatif majeur (+6.5 points de pourcentage)** : Dans notre benchmark, la Condition B fait bondir le taux de résolution de **39.0% à 45.5%** (15 bugs résolus sur 33, zéro régression).
* **Sauvetage de bugs réputés impossibles** :
  - **#41007** : Échec au tour 4, l'agent analyse l'erreur reçue de Playwright et produit le bon code au tour 5.
  - **#41923** : Échec à 0/8 en conditions A et R. Sauvé au tour 7 grâce au feedback d'échec de Playwright.

---

## Niveau 5 : Niveau Formel — Analyse Statique de Code (PHPStan, Typage & AST)

### Principe
Avant même de lancer un serveur web ou une base de données, le code modifié est soumis à un vérificateur formel :
* **PHPStan Niveau 8/9** : Analyse mathématique du graphe de flux de contrôle.
* **Contrôle strict de nullabilité** : Détection des cas où une variable peut être `null`.

### Exemple Concret Résolu par Gemma 4
* **Bug [#41130](https://github.com/PrestaShop/PrestaShop/pull/41130)** : Lors d'un appel API Admin via OAuth2, `Context::getContext()->employee` est `null`. L'ancien code appelait directement `->hasAuthOnShop()`.
* PHPStan signale instantanément en moins de 500 ms :
  ```
  Cannot call method hasAuthOnShop() on PrestaShop\PrestaShop\Core\Domain\Employee\ValueObject\EmployeeId|null
  ```
* Ce niveau de vérification court-circuite les hallucinations sans nécessiter 30 secondes de navigation Playwright.

---

## Niveau 6 : Le Plus Bas Niveau — Bac à Sable Déterministe (BDD, État Mémoire & Oracles)

### Principe
C'est le niveau machine absolu :
* **Instantané BDD Transactionnel (`.snap.sql.gz`)** : Avant chaque essai, la base de données MariaDB est réinitialisée par dump SQL compressé. Aucun test précédent ne peut contaminer le suivant.
* **Contrôle d'intégrité relationnelle** : Vérification des tables multi-boutiques (`ps_stock_available`, `ps_shop_url`).
* **Sonde anti-régression HTTP** : Vérification binaire que l'accueil Front-Office et le Back-Office répondent en `HTTP 200` et ne crashent pas en `500`.
* **Oracle Caché Final (Condition O)** : L'oracle ultime qui décide de la validité réelle du correctif dans un navigateur Chromium réel sans que le modèle n'ait jamais accès à son code source.

---

## Synthèse Comparée des 6 Niveaux

| Niveau | Nom de la Stratégie | Temps de Réponse | Consommation Tokens / Énergie | Pouvoir de Résolution Réel | Rôle dans l'Agent Gemma 4 |
|---|---|---|---|---|---|
| **Niveau 1** | **Contexte Brut (Prompt / RAG)** | Immédiat | Très lourd (~30k tokens/tour) | Faible à moyen (plafond de verre 39%) | Fournit l'énoncé du problème |
| **Niveau 2** | **Fine-Tuning (QLoRA 4B)** | Pré-calculé | Ultra-léger (~1.5k tokens/tour) | Élevé (spécialisation native) | Supprime le bavardage, ancre les réflexes |
| **Niveau 3** | **Déroulé Agentique (Tools)** | En cours de route | Optimisé (fenêtres ciblées) | Structurel (évite les divagations) | Guide l'exploration méthodique |
| **Niveau 4** | **Rejeu Dynamique (Replay)** | 10 à 30 secondes | Modéré (+1 tour par retry) | **Majeur (+6.5 points de gain net)** | Corrige les erreurs en cours de vol |
| **Niveau 5** | **Analyse Statique (PHPStan)** | < 500 ms | Nul (vérification machine locale) | Précision chirurgicale (null checks) | Garde-fou de compilation |
| **Niveau 6** | **Bac à Sable & BDD (Docker)** | 5 à 15 secondes | Nul (infrastructure locale) | **Vérité terrain absolue (0% régression)** | Arbitre final et garant de sécurité |
