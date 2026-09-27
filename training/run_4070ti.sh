#!/usr/bin/env bash
# =============================================================================
# Lanceur Fine-Tuning Gemma 4 QLoRA - Optimisé RTX 4070 Ti (12 Go VRAM)
# =============================================================================
# - Modèle : Gemma 4 E4B (ou 12B QLoRA 4-bit)
# - Longueur max : 4096 tokens (évite les OOM sur 12 Go)
# - Découpage gradient strict : max_grad_norm = 0.1 (stabilité QK-RMSNorm)
# - Taux d'apprentissage : 5e-5 (bfloat16)
# - Mode simulation rapide : --simulate ou --dry-run (15 pas pour valider la VRAM)
# =============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

SIMULATE=0
MODEL="google/gemma-4-e4b-it"

for arg in "$@"; do
  case "$arg" in
    --simulate|--dry-run|-s)
      SIMULATE=1
      ;;
    *)
      if [[ ! "$arg" =~ ^- ]]; then
        MODEL="$arg"
      fi
      ;;
  esac
done

echo "=== VÉRIFICATION DE L'ENVIRONNEMENT GPU (RTX 4070 Ti) ==="
python3 -c "
import torch
print(f'PyTorch version : {torch.__version__}')
print(f'CUDA disponible : {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'Périphérique : {torch.cuda.get_device_name(0)}')
    vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f'VRAM totale : {vram:.1f} Go')
    print(f'Support bfloat16 : {torch.cuda.is_bf16_supported()}')
else:
    print('ATTENTION : Aucun GPU CUDA détecté.')
"

OUT_DIR="$ROOT/training/lora_4070ti"
DATA_FILES="$ROOT/trajectories/train.jsonl,$ROOT/trajectories/self.jsonl"

EXTRA_ARGS=()
if [ "$SIMULATE" -eq 1 ]; then
  echo ""
  echo "🚀 MODE SIMULATION ACTIVÉ (--dry-run) : 15 pas sur 20 trajectoires pour tester la VRAM et les gradients."
  EXTRA_ARGS+=("--dry-run")
fi

echo ""
echo "=== DÉMARRAGE DU FINE-TUNING ==="
echo "Modèle : $MODEL"
echo "Données : $DATA_FILES"
echo "Dossier de sortie : $OUT_DIR"
echo ""

python3 training/train_agentic_debugger.py \
  --model "$MODEL" \
  --data "$DATA_FILES" \
  --out "$OUT_DIR" \
  --max-len 4096 \
  --epochs 3 \
  --lr 5e-5 \
  --max-grad-norm 0.1 \
  --rank 32 \
  --alpha 64 \
  --grad-accum 8 \
  --batch-size 1 \
  ${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}

echo ""
if [ "$SIMULATE" -eq 1 ]; then
  echo "=== SIMULATION TERMINÉE AVEC SUCCÈS ==="
  echo "Votre RTX 4070 Ti est parfaitement configurée et prête pour le fine-tuning complet."
else
  echo "=== ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS ==="
  echo "Adaptateur sauvegardé dans : $OUT_DIR/final"
fi
