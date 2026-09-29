# Rapport d'Exécution Phase 4 — Optimisation de la Localisation et Fenêtrage Classé

> **Document produit dans le cadre du plan d'amélioration (`docs/PLAN_AMELIORATION.md`, Phase 4)**  
> **Date** : 29 septembre 2026  
> **Auteur** : Antigravity & Rémi Soubeyrand  
> **Statut** : Validé — Code déployé dans `agent/flow.py` et `agent/run.py`

---

## 1. Diagnostic du Problème de Localisation

L'audit de défaillance a montré que **57,5% des échecs d'agent** proviennent d'une localisation erronée :
* L'ancien algorithme `windows()` parcourait le fichier de haut en bas de façon linéaire.
* Lorsque des mots-clés du ticket apparaissaient dès l'en-tête (blocs de licence GPL, `use Symfony\...`, PHPDoc), le plafond de lecture `MAX_LINES_PER_FILE = 120` était consommé avant même d'atteindre la méthode fautive située à la ligne 300 ou 400.
* En cas de relecture (`backtrack()`), la variable `files` était écrasée, masquant les succès de localisation initiaux.

---

## 2. Solutions d'Ingénierie Implémentées

### A. Classement des Passages par Densité de Pertinence (`windows_ranked`)
Dans [`agent/flow.py`](../agent/flow.py) :
1. **Pondération multi-niveaux des lignes** :
   - Match de mot-clé standard : +1 pt
   - Match avec frontière de mot exacte (`\b` regex sur CamelCase / symboles) : +3 pts
   - Ligne explicitement touchée ou signalée par une stacktrace (`extra_lines`) : +6 pts
2. **Fusion et priorisation des spans** : Les plages de lignes adjacentes sont fusionnées et ordonnées par leur score cumulé décroissant.
3. **Sélection optimale sous contrainte de budget** : Seuls les blocs de code les plus pertinents sont conservés jusqu'au plafond `MAX_LINES_PER_FILE`.
4. **Restitution ordonnée** : Les blocs retenus sont restitués dans l'ordre croissant naturel des numéros de lignes pour préserver la cohérence de lecture du modèle.

### B. Découplage Objectif des Métriques de Localisation
Dans [`agent/run.py`](../agent/run.py), `result.json` enregistre désormais séparément :
* `loc_hit_initial` : Le fichier cible figurait-il dans le premier choix de l'agent ?
* `loc_hit_ever` : Le fichier cible a-t-il été ouvert et lu à un moment quelconque (y compris après backtrack) ?
* `loc_hit_edited` : Le fichier cible a-t-il été effectivement modifié par un bloc SEARCH/REPLACE ?
* `files_all_read` : Liste cumulative complète sans écrasement lors des relectures.

---

## 3. Livrables Associés

1. **Moteur de Fenêtrage Optimisé** : Intégré dans [`agent/flow.py`](../agent/flow.py).
2. **Traçabilité Multi-Métrique** : Intégrée dans [`agent/run.py`](../agent/run.py).
3. **Le présent Rapport d'Étape** : [`docs/RAPPORT_PHASE4.md`](RAPPORT_PHASE4.md).

---

## 4. Transition vers la Phase 5 (Apprentissage de la Correction après Échec)

Avec un fenêtrage de code compact et ciblé, nous enchaînons sur la **Phase 5** : collecter et structurer les trajectoires multi-tours où le modèle apprend à corriger un premier patch erroné à partir du feedback d'oracle, sans dépendre d'un modèle propriétaire.
