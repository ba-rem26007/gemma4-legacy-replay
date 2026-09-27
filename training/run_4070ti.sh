#!/usr/bin/env bash
# =============================================================================
# Lanceur Fine-Tuning Gemma 4 QLoRA - Optimisé RTX 4070 Ti (12 Go VRAM)
# =============================================================================
# - Modèle : Gemma 4 E4B (ou 12B QLoRA 4-bit)
# - Longueur max : 4096 tokens (évite les OOM sur 12 Go)
# - Découpage gradient strict : max_grad_norm = 0.1 (stabilité QK-RMSNorm)
# - Taux d'apprentissage : 5e-5 (bfloat16)
# - Reprise automatique sur le dernier checkpoint en cas d'arrêt
# =============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

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

# Modèle par défaut pour 12 Go : gemma-4-e4b-it
MODEL="${1:-google/gemma-4-e4b-it}"
OUT_DIR="$ROOT/training/lora_4070ti"
DATA_FILES="$ROOT/trajectories/train.jsonl,$ROOT/trajectories/self.jsonl"

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
  --batch-size 1

echo ""
echo "=== ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS ==="
echo "Adaptateur sauvegardé dans : $OUT_DIR/final"
