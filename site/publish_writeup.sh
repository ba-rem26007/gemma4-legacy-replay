#!/usr/bin/env bash
# Publie sur https://kaggle.d1dev.fr (privé) : la page /writeups, le writeup à jour et ses figures (pour le copier-coller).
set -e
cd "$(dirname "$0")/.."
D=/home/elrems/kaggle.d1dev.fr/public
mkdir -p "$D/writeup/figures"
cp site/writeups.html "$D/writeups.html"
cp docs/KAGGLE_FINAL_WRITEUP.md "$D/writeup/KAGGLE_FINAL_WRITEUP.md"
cp docs/figures/*.png "$D/writeup/figures/"
echo "publié : https://kaggle.d1dev.fr/writeups"
