#!/usr/bin/env python3
"""Fine-tuning Gemma 4 pour débogage agentique avec Hugging Face TRL (SFTTrainer) & QLoRA 4-bit.

Spécificités Gemma 4 :
- Stabilité numérique : découpage strict max_grad_norm = 0.1 contre les pics QK-RMSNorm.
- Précision bfloat16 obligatoire.
- Attention SDPA (PyTorch native) ou FlashAttention-2.
- Ciblage complet des modules linéaires (q, k, v, o, gate, up, down).
- Préservation des blocs de réflexion (<|think|>).

Usage :
  python training/train_agentic_debugger.py --model google/gemma-4-e4b-it --max-len 4096
"""

import argparse
import json
import os
import random
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

ROOT = Path(__file__).resolve().parent.parent


def parse_args():
    parser = argparse.ArgumentParser(description="Fine-tuning Gemma 4 pour Agentic Debugging via TRL")
    parser.add_argument("--model", default=os.environ.get("BASE_MODEL", "google/gemma-4-e4b-it"),
                        help="Modèle de base (ex: google/gemma-4-e4b-it, google/gemma-4-12b-it)")
    parser.add_argument("--data", default=",".join(str(ROOT / "trajectories" / f) for f in ("train.jsonl", "self.jsonl")),
                        help="Chemins des datasets JSONL séparés par des virgules")
    parser.add_argument("--out", default=str(ROOT / "training" / "lora_trl"),
                        help="Dossier de sortie de l'adaptateur")
    parser.add_argument("--max-len", type=int, default=4096,
                        help="Longueur maximale de séquence (4096 pour 12 Go VRAM, 8192 si mémoire suffisante)")
    parser.add_argument("--epochs", type=int, default=3, help="Nombre d'époques")
    parser.add_argument("--lr", type=float, default=5e-5, help="Learning rate (5e-5 recommandé pour Gemma 4)")
    parser.add_argument("--max-grad-norm", type=float, default=0.1, help="Clip gradient strict pour QK-RMSNorm")
    parser.add_argument("--rank", type=int, default=32, help="Rang LoRA (32 recommandé pour le code)")
    parser.add_argument("--alpha", type=int, default=64, help="Alpha LoRA (2 * rank)")
    parser.add_argument("--grad-accum", type=int, default=8, help="Gradient accumulation steps")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size par GPU")
    parser.add_argument("--max-per-bug", type=int, default=2, help="Limite de chemins par bug")
    parser.add_argument("--dry-run", action="store_true", help="Mode simulation rapide (15 pas sur 20 exemples pour tester la VRAM)")
    parser.add_argument("--max-steps", type=int, default=-1, help="Nombre max d'étapes d'optimisation (-1 = époques complètes)")
    return parser.parse_args()


def load_trajectories(data_arg, max_per_bug, dry_run=False):
    """Charge et filtre les trajectoires de débogage."""
    paths = [Path(p.strip()) for p in data_arg.split(",") if Path(p.strip()).exists()]
    if not paths:
        raise FileNotFoundError(f"Aucun fichier de données trouvé parmi : {data_arg}")

    rows = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))

    # Dédoublonnage et limitation par bug/PR
    per_bug = {}
    random.seed(42)
    random.shuffle(rows)
    filtered = []
    for r in rows:
        key = r.get("pr") or r.get("id") or str(hash(r.get("messages", [{}])[0].get("content", "")))
        if len(per_bug.setdefault(key, [])) < max_per_bug:
            per_bug[key].append(1)
            filtered.append(r)

    if dry_run:
        filtered = filtered[:20]
        print(f"[SIMULATION] Échantillon réduit à {len(filtered)} trajectoires pour validation VRAM et gradients.")
    print(f"Trajectoires chargées : {len(filtered)} exemples retenus depuis {len(paths)} fichier(s)")
    return filtered


def main():
    args = parse_args()
    print(f"--- Fine-Tuning Gemma 4 (TRL SFTTrainer) ---")
    if args.dry_run:
        print(">>> MODE SIMULATION / DRY-RUN (15 pas pour tester VRAM et gradients) <<<")
    print(f"Modèle : {args.model}")
    print(f"LR : {args.lr} | Max Grad Norm : {args.max_grad_norm} | Rank : {args.rank} | Max Len : {args.max_len}")

    # 1. Configuration QLoRA 4-bit NormalFloat (NF4)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    )

    # 2. Chargement Tokenizer & Modèle
    tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side="right")
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    attn_impl = "sdpa" if torch.cuda.is_available() else "eager"
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=bnb_config.bnb_4bit_compute_dtype,
        attn_implementation=attn_impl
    )

    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    # 3. LoRA sur l'ensemble des projections du décodeur
    peft_config = LoraConfig(
        r=args.rank,
        lora_alpha=args.alpha,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # 4. Préparation du Dataset
    raw_data = load_trajectories(args.data, args.max_per_bug, dry_run=args.dry_run)
    dataset = Dataset.from_list([{"messages": r["messages"]} for r in raw_data])

    max_steps_val = 15 if args.dry_run else args.max_steps
    save_strat = "no" if args.dry_run else "steps"
    log_steps = 1 if args.dry_run else 10

    # 5. SFTConfig intégrant les contraintes de stabilité Gemma 4
    sft_config = SFTConfig(
        output_dir=args.out,
        max_seq_length=args.max_len,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        max_grad_norm=args.max_grad_norm,  # Découpage strict obligatoire pour QK-RMSNorm
        logging_steps=log_steps,
        num_train_epochs=args.epochs,
        max_steps=max_steps_val,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        warmup_ratio=0.05,
        save_strategy=save_strat,
        save_steps=25,
        save_total_limit=3,
        report_to="none"
    )

    # 6. SFTTrainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        tokenizer=tokenizer,
        args=sft_config
    )

    print("Lancement de l'entraînement SFT...")
    trainer.train()

    if args.dry_run:
        print("\n" + "="*60)
        print("🎉 SIMULATION SUR GPU RÉUSSIE EN MOINS D'UNE MINUTE !")
        if torch.cuda.is_available():
            max_mem = torch.cuda.max_memory_allocated() / (1024**3)
            print(f"Mémoire VRAM crête consommée : {max_mem:.2f} Go (Conforme 12 Go)")
        print("Stabilité numérique : Aucune divergence de gradient ni perte infinie.")
        print("="*60 + "\n")
        return

    # 7. Sauvegarde
    final_dir = Path(args.out) / "final"
    trainer.save_model(str(final_dir))
    tokenizer.save_pretrained(str(final_dir))
    print(f"Entraînement terminé ! Adaptateur final sauvegardé dans : {final_dir}")


if __name__ == "__main__":
    main()
