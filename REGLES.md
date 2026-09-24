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
- **ÉTANCHÉITÉ** : aucun bug TEST, ni aucun correctif touchant les mêmes lignes ou fichiers, dans les données d'entraînement. Contrôle à chaque étape.
- `ETAT.md` à jour à la fin de chaque étape ; `DECISIONS.md` pour chaque choix structurant.
- Demander avant toute commande destructive ou tout téléchargement > 5 Go.
- Une phase à la fois ; on s'arrête et on présente le livrable.
