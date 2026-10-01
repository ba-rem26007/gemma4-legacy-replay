#!/usr/bin/env bash
# scripts/pack.sh : Package le dossier submission/ en submission.zip et valide sa conformité
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

echo "📦 Préparation du packaging submission.zip..."

if [ ! -d "submission" ]; then
  echo "❌ Erreur : Dossier 'submission' introuvable dans $ROOT_DIR."
  exit 1
fi

if [ ! -f "submission/agent.yaml" ] && [ ! -f "submission/agent.yml" ]; then
  echo "❌ Erreur : Aucun fichier agent.yaml trouvé dans submission/."
  exit 1
fi

# Nettoyage d'une archive précédente
rm -f submission.zip

echo "🗜️  Compression propre de submission/ vers submission.zip..."
python3 -c "
import zipfile, os
from pathlib import Path

root = Path('submission')
out_zip = Path('submission.zip')

with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(root.rglob('*')):
        if f.is_file():
            # Exclusions de sécurité
            parts = f.relative_to(root).parts
            if any(p.startswith('.') or p == '__pycache__' or p.endswith('.pyc') for p in parts):
                continue
            arcname = str(f.relative_to(root))
            z.write(f, arcname)
            print(f'  + {arcname}')
"

echo "✅ Archive submission.zip créée ($(du -h submission.zip | cut -f1))."

# Exécution du script de validation formelle
python3 scripts/validate.py submission.zip

echo "🚀 Prêt pour la soumission Kaggle !"
