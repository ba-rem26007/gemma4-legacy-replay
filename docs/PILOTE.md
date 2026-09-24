# Pilote : 3 bugs validés (vivier TRAIN, corrigés en 2024)

Chaque bug est rejoué contre PrestaShop en Docker : image officielle de la release la plus proche, avec les fichiers du correctif remis dans leur état d'avant (`pre`) ou d'après (`post`).
Critère : le test de replay **échoue en `pre`** et **passe en `post`**.

| PR | Issue | Zone | Bug | Image | pre | post |
|---|---|---|---|---|---|---|
| [#35902](https://github.com/PrestaShop/PrestaShop/pull/35902) | #35888 | FO | La quantité minimale n'est pas ramenée à 1 quand elle est déjà atteinte dans le panier | 8.1.6 | ✘ (3) | ✓ (1) |
| [#35384](https://github.com/PrestaShop/PrestaShop/pull/35384) | #35280 | BO | Stock : la recherche avec 2 mots-clés ne renvoie rien | 8.1.4 | ✘ (0 produit) | ✓ |
| [#35322](https://github.com/PrestaShop/PrestaShop/pull/35322) | — | FO | Historique de commande : frais de port affichés HT au lieu de TTC | 8.1.4 | ✘ (7,00 €) | ✓ (8,40 €) |

Exclu : #35530 (contrôle d'accès des factures par secure_key, trop proche de la sécurité, voir `REGLES.md`).

## Reproduire
```
bench/checkout.sh 35322 pre  && bench/replay/run.sh 35322   # échoue
bench/checkout.sh 35322 post && bench/replay/run.sh 35322   # passe
```

## Notes
- La mise en place des données passe par SQL (`<pr>/setup.sql`), le scénario du bug par l'interface (Playwright).
- Le BO utilise une session partagée (`replay/auth.setup.js`, specs `*.bo.spec.js`).
- Ces tests sont écrits à la main : ils servent de référence pour valider le harness. Ils n'entrent **pas** dans le dataset d'entraînement.
