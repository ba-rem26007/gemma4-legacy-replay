# Enregistrer la reproduction d'un bug (expert → test rejouable)

Idée : le vérificateur qui aide l'agent doit **reproduire le bug fidèlement**. Les tests inventés par Gemma à partir du ticket ne le sont qu'1 fois sur 10 (`docs/RESULTATS.md`). L'expert métier (Rémi) enregistre la reproduction en quelques clics ; la chaîne en fait un test de rejeu donné à l'agent (condition B-expert).
C'est le scénario réaliste du papier : un intégrateur PrestaShop reproduit le bug une fois, l'agent corrige et vérifie.

## 1. Préparer une instance sur le serveur
```bash
PSB=7 bench/checkout.sh <pr> pre          # boutique dans l'état AVANT correctif, port 8087
```

## 2. Enregistrer depuis ton PC
```bash
ssh -L 8087:localhost:8087 <serveur>      # tunnel
npx playwright codegen --target=javascript -o replay_expert.spec.js http://localhost:8087/
```
- Reproduis le bug en suivant le ticket (FO : http://localhost:8087/ · BO : http://localhost:8087/admin-dev , demo@prestashop.com / prestashop_demo).
- Dans la barre codegen, ajoute **l'assertion du comportement attendu** (bouton « Assert text / value / visibility ») sur ce qui est faux aujourd'hui.
- Pour le BO, commence l'enregistrement par la connexion (le test sera autonome).

## 3. Déposer et valider
Copie le fichier dans `bench/replay/<pr>/replay_expert.spec.js` (ou envoie-le dans la conversation), puis :
```bash
python3 bench/validate_expert.py <pr>     # doit ÉCHOUER en pre (reproduit) — on note s'il PASSE en post (fidélité)
```
Le test devient visible par l'agent (fichier `replay*`) ; l'oracle reste caché.

## Coût estimé
2 à 5 minutes par bug pour un expert PrestaShop. 33 bugs ≈ 2 heures.
