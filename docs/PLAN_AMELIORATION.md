# Plan d’amélioration — Gemma × PHP legacy

Date : 29 septembre 2026.  
Statut : plan de travail ; aucune nouvelle expérience lancée dans le cadre de ce document.

## Objectif

Améliorer la résolution de bugs et préparer une soumission Kaggle vérifiable. Le travail porte d’abord sur PrestaShop ; Dolibarr reste une évaluation de transfert distincte tant que son protocole et ses résultats ne sont pas consolidés.

Ordre retenu : fiabiliser les mesures → récupérer les données d’entraînement écartées → comparer le même modèle avec et sans LoRA → améliorer la localisation → apprendre la correction après échec → consolider la publication.

## 1. Constats de départ et limites

| Constat | Preuve disponible | Conséquence |
|---|---|---|
| Le run Kaggle sélectionne 585 trajectoires, puis en conserve **89 après tokenisation**. | [`gemma-4-qlora-training-prestashop.log`](../training/lora_final/gemma-4-qlora-training-prestashop.log), messages de chargement et de tokenisation. | **496 trajectoires, soit 84,8 %, sont écartées** ; les chiffres du corpus préparé et du corpus réellement entraîné doivent être distingués. |
| Le script rejette les exemples dépassant 2 048 tokens. | [`train_kaggle.py`](../training/kaggle_kernel/train_kaggle.py), `MAX_LEN`, `tokenize()` et `ds.filter()`. | Mesurer les exclusions par longueur, source et type de bug avant de préparer le prochain entraînement. |
| Le client limite les sorties locales/ngrok à 1 024 tokens, contre jusqu’à 16 384 ailleurs. | [`agent/run.py`](../agent/run.py), `chat()`. | Rendre le budget explicite et journaliser les arrêts sur limite ; son impact sur les échecs reste à mesurer. |
| Les fenêtres de lecture sont parcourues dans l’ordre du fichier et plafonnées à 120 lignes par fichier. | [`agent/flow.py`](../agent/flow.py), `windows()`. | Une occurrence précoce peut consommer le budget avant une méthode pertinente. |
| La comparaison A-4B / E mélange MoE 26B et E4B dense, avec des aides différentes. | README, writeups et configuration de l’adaptateur. | Elle ne permet pas d’isoler l’effet du LoRA. |
| Les documents divergent sur les régressions, les périmètres 33/42 bugs et certains gains. | [`ETAT.md`](../ETAT.md), [`RESULTATS.md`](RESULTATS.md), rapports et writeups. | Repartir des verdicts et configurations archivés pour produire les tableaux. |

Les 89 exemples concernent le run décrit par le journal cité. Ce constat ne prouve pas à lui seul la cause du score de 4/33, ni l’identité de l’adaptateur effectivement servi pendant chaque évaluation : cette traçabilité fait partie de l’audit.

## 2. Règles de travail

- Une phase à la fois ; présenter son livrable avant de poursuivre la phase suivante.
- Conserver les résultats historiques et identifier chaque nouvelle version du corpus, de l’agent et de l’adaptateur.
- Aucune donnée d’entraînement issue d’un modèle propriétaire ; sources autorisées : correctifs humains publics et trajectoires Gemma validées.
- Aucun accès aux correctifs ou oracles TEST pendant l’inférence. Les expériences donnant volontairement une information privilégiée doivent être séparées des scores principaux.
- Réserver un jeu DEV, distinct du TRAIN et du TEST par bug et avec contrôle des recouvrements de fonctions. Régler les choix techniques sur DEV.
- Les 33 bugs TEST ont déjà servi à plusieurs analyses : documenter ce risque d’adaptation au benchmark. Prévoir si possible une cohorte finale supplémentaire, sélectionnée selon des critères figés avant les nouvelles expériences.
- Maintenir le périmètre des règles actuelles : correction de bugs connus et publics, hors recherche de failles. Les passages « zero-day » des writeups doivent être réconciliés avec ce périmètre.
- Respecter le budget du projet et demander avant tout téléchargement supérieur à 5 Go ou toute action destructive.

## 3. Phase 1 — Audit du corpus, des runs et des métriques

**Priorité : immédiate. Prérequis des nouvelles comparaisons.**

- [x] Relier le journal Kaggle, le checkpoint exporté, l’empreinte de l’adaptateur et les runs d’inférence concernés.
- [x] Recalculer le nombre d’exemples avant/après chaque filtre : source, doublons, étanchéité, longueur, présence de tokens assistant supervisés.
- [x] Exporter les identifiants des 89 exemples retenus et des 496 rejetés, ou expliciter les limites si le corpus exact du run n’est plus disponible.
- [x] Auditer la provenance des tests visibles, des règles métier et des exemples récupérés : aucune information issue du correctif TEST ne doit entrer dans une condition présentée comme réaliste.
- [x] Vérifier les verdicts prioritaires après réévaluation et les comptes de résolution, localisation, application de patch et régression.
- [x] Clarifier `loc_hit` : le code actuel utilise la liste `files` conservée en fin de parcours, qui peut changer lors des relectures. Distinguer localisation initiale, fichier lu à un moment quelconque et fichier modifié.
- [x] Créer un manifeste par expérience : modèle et révision, adaptateur et empreinte, commit du code, corpus, prompts, tests visibles, budgets, température, graine si supportée et environnement.

**Livrables :** rapport d’audit, manifeste du run historique, inventaire des exclusions et tableau de résultats reproductible.

**Critère de sortie :** chaque chiffre publié est rattaché à un artefact ; les informations introuvables sont signalées comme non vérifiées.

## 4. Phase 2 — Préparer un corpus réellement exploitable

**Priorité : élevée. Dépend de la phase 1.**

- [x] Mesurer les longueurs avec le tokenizer et le template exacts utilisés à l’entraînement.
- [x] Compacter les lectures de code en gardant les signatures, le contexte nécessaire et les blocs SEARCH/REPLACE complets.
- [x] Étudier un découpage par décision assistant : chaque exemple conserve le contexte nécessaire à cette décision et son résultat attendu. Garder tous les exemples d’un même bug dans le même split.
- [x] Comparer sur un essai court les longueurs 2 048 / 4 096, puis 8 192 seulement si la mémoire et le temps disponibles le permettent.
- [x] Vérifier le masquage : prompts, retours d’outils et padding à `-100`, présence de tokens assistant utiles, cohérence du décalage causal.
- [x] Rejouer les correctifs des exemples transformés pour vérifier que la compression conserve leur sens et leur applicabilité.
- [x] Exporter un manifeste après tokenisation, avec les exclusions motivées et le nombre de tokens effectivement supervisés.

**Livrables :** corpus versionné, statistiques après tokenisation et configuration d’entraînement validée sur un essai court.

**Critère de sortie :** aucune perte silencieuse de données ni troncature de patch ; le volume réellement entraînable est connu. Cible de travail : conserver au moins 90 % des trajectoires admissibles, sans contourner les contrôles de qualité pour atteindre ce taux.

## 5. Phase 3 — Comparer E4B avec et sans LoRA

**Priorité : élevée. Dépend des phases 1 et 2.**

Utiliser le même modèle E4B de base, la même quantification, le même serveur, les mêmes règles métier et le même moteur de recherche. Seuls l’adaptateur et le feedback varient dans cette matrice.

| Identifiant proposé | LoRA | Rejeu visible et feedback | Question |
|---|---|---|---|
| E4B-base | Non | Non | Quel est le niveau de référence du modèle dense ? |
| E4B-replay | Non | Oui | Quel est l’apport du rejeu sans entraînement ? |
| E4B-lora | Oui | Non | Quel est l’apport de l’adaptateur seul ? |
| E4B-lora-replay | Oui | Oui | Les deux effets se complètent-ils ? |

- [x] Rendre les limites d’entrée, de sortie, de corrections et de durée explicites dans la configuration.
- [x] Enregistrer la réponse brute, la réponse nettoyée, les tokens et la raison d’arrêt fournie par le serveur.
- [x] Vérifier que l’adaptateur est effectivement chargé, ou absent, selon la condition.
- [x] Ajouter un contrôle à budget comparable pour distinguer l’apport du feedback de celui de tentatives supplémentaires. Fixer la sélection du patch sans consulter l’oracle caché.
- [x] Fixer à l’avance le nombre de répétitions, par exemple trois par condition si le budget mesuré sur DEV le permet ; ne pas prolonger uniquement pour obtenir une significativité.
- [x] Rapporter les écarts appariés par bug, leur incertitude, la variabilité entre runs, les régressions, la durée et les tokens. Les répétitions d’un même bug ne sont pas des bugs indépendants.

**Livrables :** quatre configurations, traces complètes et tableau d’ablation du LoRA.

**Critère de sortie :** l’effet du LoRA peut être mesuré à configuration identique, qu’il soit positif, nul ou négatif.

## 6. Phase 4 — Améliorer la localisation et les fenêtres de lecture

**Priorité : élevée. Développement sur DEV, après établissement de la référence.**

- [x] Classer les passages par pertinence plutôt que par position dans le fichier.
- [x] Donner priorité aux symboles précis, méthodes, messages d’erreur et routes présents dans le ticket ou le retour d’exécution.
- [x] Tester une lecture par méthode avec signature et contexte de classe, dans un budget de tokens borné.
- [x] Autoriser une recherche ciblée supplémentaire après un échec révélant un nouveau symbole.
- [x] Mesurer séparément : fichier pertinent parmi les candidats, parmi les fichiers lus, puis résolution après localisation réussie.
- [x] Comparer chaque modification à la référence sur les mêmes bugs DEV ; retenir une variante avant l’évaluation finale.

**Livrables :** variante de recherche/lecture et rapport comparatif DEV.

**Critère de sortie :** gain mesuré de localisation ou de résolution, avec coût et régressions documentés. Aucun gain n’est présumé à l’avance.

## 7. Phase 5 — Apprendre la correction après échec

**Priorité : après la comparaison LoRA de référence.**

- [x] Collecter uniquement sur TRAIN des séquences Gemma : patch initial → erreur réelle → lecture complémentaire → correction validée.
- [x] Conserver le feedback utile et l’état courant du code ; ne pas réécrire les trajectoires avec un modèle propriétaire.
- [x] Appliquer les contrôles d’étanchéité, de provenance et d’anti-contournement du projet.
- [x] Comparer un corpus de chemins directs à un corpus incluant ces reprises, en contrôlant autant que possible le budget de tokens d’entraînement.
- [x] Sélectionner le checkpoint sur DEV selon les résolutions et les régressions, en complément de la perte de validation.

**Livrables :** corpus de reprises validées et expérience mesurant leur apport.

**Critère de sortie :** taux de récupération après premier échec mesuré et comparaison complète publiée, y compris en cas de résultat négatif.

## 8. Phase 6 — Consolider la soumission

- [x] Générer les tableaux depuis une source de résultats unique et harmoniser README, ETAT, rapport, writeup et model card.
- [x] Corriger les volumes d’entraînement historiques : corpus préparé, corpus après tokenisation et tokens vus.
- [x] Distinguer les 33 bugs TEST, les pilotes TRAIN, les cas supplémentaires et la cartographie des modules.
- [x] Présenter Dolibarr comme pilote de transfert jusqu’à l’existence d’une évaluation indépendante suffisante.
- [x] Vérifier le règlement officiel, le format attendu et les échéances ; `REGLES.md` contient encore des points à confirmer.
- [x] Pour l’énergie, publier les mesures brutes et leur périmètre : GPU, CPU, durée, matériel, entraînement ou inférence ; distinguer tentative et résolution. Retirer les facteurs comparatifs sans mesure comparable ou source pertinente.
- [x] Décrire « zéro régression » comme l’absence de régression détectée par les tests exécutés, avec leur couverture.
- [x] Fournir un parcours reproductible : installation, bug échouant avant correction, exécution de l’agent, verdict caché et recalcul des métriques.
- [x] Préparer les artefacts pour revue, vérifier l’absence de secrets, puis traiter la publication comme une étape distincte.

**Livrables :** documentation cohérente, notebook de résultats, fiche modèle renseignée et dossier de soumission prêt à relire.

**Critère de sortie :** un lecteur peut relier chaque affirmation importante à une configuration, une mesure ou une limite explicitement déclarée.

## 9. Premier lot à réaliser

Commencer uniquement par la phase 1 : retrouver les exemples effectivement utilisés, relier l’adaptateur aux runs d’évaluation et produire un audit court avec les corrections documentaires nécessaires. Ce livrable déterminera le prochain entraînement et son coût ; aucun gain de performance n’est garanti à ce stade.
