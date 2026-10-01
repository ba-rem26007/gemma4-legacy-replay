#!/usr/bin/env python3
"""Validation de conformité d'un submission.zip pour la compétition Kaggle Gemma 4 Developer Agent.

Vérifie les critères stricts du harness adk-submission :
1. Présence d'un et un seul fichier de configuration racine (agent.yaml).
2. Absence de liens symboliques (symlinks).
3. Absence de chemins relatifs interdits (../).
4. Modèle unique déclaré : gemma-4-31b-it-qat-w4a16-ct.
5. Taille totale décompressée < 3 GiB.
6. Intégrité des adaptateurs LoRA PEFT (adapter_config.json + adapter_model.safetensors).
"""
import os
import sys
import zipfile
import yaml
from pathlib import Path

ALLOWED_MODELS = {"gemma-4-31b-it-qat-w4a16-ct"}
MAX_UNPACKED_BYTES = 3 * 1024 * 1024 * 1024  # 3 GiB

# Enregistrement du constructeur !include pour adk-submission
def yaml_include_constructor(loader, node):
    return loader.construct_scalar(node)

yaml.SafeLoader.add_constructor('!include', yaml_include_constructor)


def validate_zip(zip_path_str: str) -> bool:
    zip_path = Path(zip_path_str)
    if not zip_path.exists():
        print(f"❌ Erreur : Le fichier {zip_path} n'existe pas.")
        return False

    print(f"🔍 Vérification de l'archive {zip_path.name}...")
    errors = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            infos = z.infolist()
            total_size = sum(i.file_size for i in infos)
            names = [i.filename for i in infos]

            # 1. Vérification de la taille
            print(f"  • Taille décompressée : {total_size / (1024*1024):.2f} Mo / 3 072 Mo max")
            if total_size > MAX_UNPACKED_BYTES:
                errors.append(f"Taille décompressée trop volumineuse : {total_size} octets (> 3 GiB)")

            # 2. Vérification des symlinks et chemins interdits
            for info in infos:
                # Vérification attribut symlink Unix
                is_symlink = (info.external_attr >> 16) & 0o120000 == 0o120000
                if is_symlink:
                    errors.append(f"Lien symbolique interdit détecté : {info.filename}")
                if ".." in info.filename or info.filename.startswith("/"):
                    errors.append(f"Chemin relatif interdit détecté : {info.filename}")

            # 3. Présence d'un et un seul agent.yaml racine
            root_configs = [n for n in names if n in ("agent.yaml", "agent.yml", "root_agent.yaml", "root_agent.yml")]
            if len(root_configs) == 0:
                errors.append("Fichier de configuration racine manquant (agent.yaml attendu à la racine du zip).")
            elif len(root_configs) > 1:
                errors.append(f"Multiples fichiers racine détectés : {root_configs}")
            else:
                print(f"  • Fichier racine détecté : {root_configs[0]}")

            # 4. Lecture et validation du modèle dans agent.yaml
            if root_configs:
                try:
                    with z.open(root_configs[0]) as f:
                        cfg = yaml.safe_load(f)
                    
                    models_declared = set()
                    
                    def extract_models(data):
                        if isinstance(data, dict):
                            if "model" in data and isinstance(data["model"], str):
                                m = data["model"].split("/")[-1].strip()
                                models_declared.add(m)
                            for v in data.values():
                                extract_models(v)
                        elif isinstance(data, list):
                            for item in data:
                                extract_models(item)

                    extract_models(cfg)

                    print(f"  • Modèle(s) déclaré(s) : {models_declared}")
                    if len(models_declared) == 0:
                        errors.append("Aucun modèle déclaré dans agent.yaml.")
                    elif len(models_declared) > 1:
                        errors.append(f"Règle du modèle unique violée : plusieurs modèles déclarés ({models_declared}).")
                    else:
                        m = list(models_declared)[0]
                        if m not in ALLOWED_MODELS:
                            errors.append(f"Modèle non autorisé pour le scoring officiel : '{m}'. Seul {ALLOWED_MODELS} est permis.")

                except Exception as e:
                    errors.append(f"Erreur lors de la lecture YAML de {root_configs[0]} : {e}")

            # 5. Vérification des adaptateurs PEFT
            adapter_dirs = set()
            for n in names:
                if n.startswith("adapters/") and "/" in n[len("adapters/"):].strip("/"):
                    adapter_name = n[len("adapters/"):].split("/")[0]
                    adapter_dirs.add(adapter_name)

            for ad in adapter_dirs:
                has_cfg = f"adapters/{ad}/adapter_config.json" in names
                has_weights = (f"adapters/{ad}/adapter_model.safetensors" in names or 
                               f"adapters/{ad}/adapter_model.bin" in names)
                print(f"  • Adaptateur LoRA '{ad}' : config={has_cfg}, poids={has_weights}")
                if not has_cfg or not has_weights:
                    errors.append(f"Adaptateur LoRA incomplet 'adapters/{ad}/' (doit contenir adapter_config.json et adapter_model.safetensors).")

    except Exception as e:
        errors.append(f"Archive zip corrompue ou illisible : {e}")

    if errors:
        print("\n❌ ÉCHEC DE VALIDATION :")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("\n✅ VALIDATION RÉUSSIE : submission.zip est 100% conforme aux règles officielles Kaggle !")
        return True


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "submission.zip"
    success = validate_zip(target)
    sys.exit(0 if success else 1)
