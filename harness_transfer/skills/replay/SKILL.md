---
name: test_driven_replay
description: "Discipline de rejeu dynamique : reproduction du bug via pytest ou script minimal, localisation ciblée, édition atomique par edit_file et vérification itérative avant soumission."
---

# Skill : Test-Driven Replay & Repair Loop

Cette compétence applique une discipline de débogage et de rejeu rigoureuse sur le code Python.

## Déroulé Séquentiel Obligatoire

1. **Reproduction Minimale** :
   - Identifier le test existant ou écrire un mini-script de test reproduisant l'échec décrit dans le ticket.
   - Lancer la reproduction via `run_command("pytest -k <test_name>")` ou `run_command("python3 <repro.py>")`.
   - Constater l'échec initial (code retour != 0) et analyser la stack trace.

2. **Localisation Étroite** :
   - Extraire le fichier et la ligne exacte incriminés depuis la trace.
   - Ne lire que les portions de code nécessaires avec `read_file(filepath, start_line, end_line)`.

3. **Édition Atomique** :
   - Utiliser `edit_file(filepath, old_string, new_string)`.
   - Vérifier que `old_string` correspond rigoureusement aux lignes existantes.
   - Ne modifier que le strict nécessaire pour corriger la cause racine.

4. **Rejeu & Vérification Immédiate** :
   - Relancer immédiatement la commande de test via `run_command`.
   - Si le test passe (exit_code == 0) : s'assurer qu'aucune régression n'a été introduite sur les tests environnants.
   - Si le test échoue : analyser l'erreur résiduelle et appliquer un second `edit_file` correctif (2 retries autorisés).

5. **Soumission Définitive** :
   - Dès que le test de reproduction et les tests associés sont verts, appeler `submit_patch()`.
   - Ne pas faire d'appels d'outils exploratoires supplémentaires après la validation.
