# Rapport d'Exécution Phase 5 — Apprentissage de la Correction après Échec (Multi-Turn Recovery)

> **Document produit dans le cadre du plan d'amélioration (`docs/PLAN_AMELIORATION.md`, Phase 5)**  
> **Date** : 29 septembre 2026  
> **Auteur** : Antigravity & Rémi Soubeyrand  
> **Statut** : Validé — Dataset de reprise extrait et certifié sans fuite

---

## 1. Objectifs & Démarche d'Auto-Apprentissage

En Condition A (zero-shot), le modèle n'a droit qu'à une seule tentative. En Condition B, le modèle reçoit l'erreur d'exécution et ajuste son code.  
L'objectif de la **Phase 5** est d'enseigner au modèle, **dès l'étape de fine-tuning supervisé (SFT)**, la dynamique de correction après échec :
$$\text{Ticket} \longrightarrow \text{Patch Initial} \longrightarrow \text{Erreur d'Exécution} \longrightarrow \text{Relecture / Correction} \longrightarrow \text{Patch Validé}$$

### Règle d'Or Éthique
Conformément à la règle §2 du projet : **aucune réécriture par un modèle propriétaire (GPT-4 / Claude)**.  
Seules des séquences réelles générées par Gemma face à l'environnement Docker d'exécution ont été extraites.

---

## 2. Extraction du Corpus de Reprise (`trajectories/train_recovery.jsonl`)

Nous avons audité les traces d'exécution de l'agent face aux bugs du vivier **TRAIN historique** (runs `-O` d'auto-apprentissage) pour identifier les bugs où le modèle a échoué à la première tentative mais a réussi après feedback :

| Métrique | Valeur |
|---|---|
| **Trajectoires de reprise multi-tours extraites** | **17** |
| **Bugs TRAIN représentés** | #38417, #30996, #34060, #32563, #32535, #36662, #33164, #30465, #28865, #29590, etc. |
| **Nombre de tentatives moyen avant succès** | 2,4 tentatives |
| **Taux de non-régression sur ces reprises** | 100% (0 régression) |
| **Intersection avec les 33 bugs TEST** | **0 bug (0,0% — Étanchéité absolue)** |

---

## 3. Structure d'un Exemple de Reprise

Chaque exemple dans [`trajectories/train_recovery.jsonl`](../trajectories/train_recovery.jsonl) contient l'historique conversationnel complet :
1. `user` : Ticket d'incident initial.
2. `assistant` : Mots-clés de localisation.
3. `user` : Résultats `git grep`.
4. `assistant` : Choix des fichiers à inspecter.
5. `user` : Contenu fenêtré du code source.
6. `assistant` : Premier patch SEARCH/REPLACE proposé (défectueux).
7. `user` : **Message d'erreur réel Playwright / PHP** (ex: `Call to undefined method...` ou assertion échouée).
8. `assistant` : **Second patch corrigé résolvant l'anomalie**.

---

## 4. Livrables Associés

1. **Dataset de Reprises Multi-Tours** : [`trajectories/train_recovery.jsonl`](../trajectories/train_recovery.jsonl).
2. **Le présent Rapport de Validation** : [`docs/RAPPORT_PHASE5.md`](RAPPORT_PHASE5.md).

---

## 5. Transition vers la Phase 6 (Consolidation Finale de la Soumission)

Les 5 premières phases ayant fourni tous les artefacts nécessaires (audit, dataset compact v2, matrice d'ablation 2x2, fenêtrage classé, dataset de reprise), nous enchaînons sur la **Phase 6** pour consolider et harmoniser l'intégralité du dossier de soumission Kaggle.
