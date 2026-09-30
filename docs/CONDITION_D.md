# Protocole & Exécution : Condition D (Modèle Fine-Tuné LoRA)

Ce document décrit la procédure complète pour évaluer le modèle Gemma 4 après fine-tuning QLoRA (Condition D) sur les 33 bugs du vivier TEST PrestaShop 9.1.x.

---

## 1. Objectif Scientifique

Mesurer l'impact du fine-tuning autonome sur :
1. **Le taux de résolution (pass@1)** : Comparer aux 39,0% de la Condition A (modèle non tuné) et aux 45,5% de la Condition B (+ replay des tests).
2. **La localisation des fichiers fautifs (loc_hit)** : Vérifier si l'apprentissage des trajectoires réelles PrestaShop améliore la découverte du bon fichier dès le tour 1.
3. **Le nombre de tours par résolution** : Observer si le modèle résout les bugs plus rapidement (économie de tours d'exploration).
4. **L'absence de régressions** : Maintenir un taux de régression de 0,0%.

---

## 2. Architecture Technique (Colab GPU + Serveur Local)

Puisque le serveur local Dedibox est optimisé pour les conteneurs Docker PrestaShop (CPU AMD Ryzen 5, 31 Go RAM), l'inférence du LLM est déportée sur un GPU Colab :
* **Hôte LLM (Google Colab T4 / A100)** :
  * Modèle : `google/gemma-4-e4b-it` en 4-bit NF4 + adaptateur LoRA PrestaShop (`adapter_model.safetensors`).
  * Serveur : FastAPI exposant l'API `/v1/chat/completions`.
  * Tunnel : ngrok (`https://xxxx.ngrok-free.dev`).
* **Hôte Benchmark (Serveur Dedibox)** :
  * Exécute `agent/run.py` sur l'instance isolée `psbench2` (`localhost:8082`).
  * Les requêtes de décision de l'agent partent vers l'URL ngrok.
  * Les commandes de code (`chercher`, `lire`, `editer`) et les tests Playwright/PHPUnit s'exécutent en local dans Docker.

---

## 3. Cellule Colab pour Démarrer le Serveur LLM

Coller ce script dans Google Colab pour monter le serveur en 1 clic :

```python
# ==============================================================================
# SERVEUR D'INFERENCE GEMMA 4 AVEC TUNNEL NGROK & LORA PRESTASHOP
# ==============================================================================
import os, time, subprocess, sys, threading, torch
from pathlib import Path

# 1. Dépendances
print("[1/5] Installation des dépendances...")
!pip install -q fastapi uvicorn pydantic pyngrok peft accelerate bitsandbytes

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

# 2. Configuration
NGROK_AUTHTOKEN = os.environ["NGROK_AUTHTOKEN"]  # jamais en clair
BASE_MODEL_NAME = "google/gemma-4-e4b-it"
ADAPTER_PATH = "/content/lora/final"
PORT = 8000

# 2b. Téléchargement direct de l'adaptateur LoRA si absent
if not (Path(ADAPTER_PATH) / "adapter_model.safetensors").exists():
    print("[+] Téléchargement de l'adaptateur LoRA...")
    !wget -q https://anniv.soubeyrand.dev/lora.zip -O /content/lora.zip
    !mkdir -p /content/lora/final
    !python3 -m zipfile -e /content/lora.zip /content/lora/final
    print("✅ Adaptateur LoRA installé !")

# 3. Lancement du tunnel ngrok
print("[2/5] Démarrage du tunnel ngrok...")
!killall ngrok uvicorn 2>/dev/null || true
!mkdir -p /root/.config/ngrok
!cp -f /root/.ngrok2/ngrok.yml /root/.config/ngrok/ngrok.yml 2>/dev/null || true

proc = subprocess.Popen(
	["ngrok", "http", str(PORT), "--authtoken", NGROK_AUTHTOKEN, "--log=stdout"],
	stdout=subprocess.PIPE,
	stderr=subprocess.STDOUT,
	text=True
)

public_url = None
start_time = time.time()
while time.time() - start_time < 12:
	line = proc.stdout.readline()
	if line and "url=" in line:
		for part in line.split():
			if part.startswith("url="):
				public_url = part.split("=", 1)[1]
				break
		if public_url:
			break

print("URL PUBLIQUE DU TUNNEL :", public_url)

# 4. Chargement du Modèle et LoRA
print("[3/5] Tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
	tokenizer.pad_token = tokenizer.eos_token

print("[4/5] Modèle de base 4-bit...")
quant_config = BitsAndBytesConfig(
	load_in_4bit=True,
	bnb_4bit_compute_dtype=torch.bfloat16,
	bnb_4bit_quant_type="nf4",
	bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(
	BASE_MODEL_NAME,
	quantization_config=quant_config,
	device_map="auto",
	trust_remote_code=True,
)

if (Path(ADAPTER_PATH) / "adapter_model.safetensors").exists():
	print(f"🔥 Application de l'adaptateur LoRA depuis {ADAPTER_PATH}...")
	model = PeftModel.from_pretrained(model, ADAPTER_PATH)
	model.eval()
	print("✅ Modèle Fine-Tuné prêt !")

# 5. Serveur FastAPI
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ChatMessage(BaseModel):
	role: str
	content: str

class ChatReq(BaseModel):
	model: str = "gemma-4-ft"
	messages: list[ChatMessage]
	temperature: float = 0.2
	max_tokens: int = 4096

@app.get("/")
def root():
	return {"status": "ready", "model": BASE_MODEL_NAME, "adapter": ADAPTER_PATH}

@app.post("/v1/chat/completions")
def chat(req: ChatReq):
	formatted = [{"role": m.role, "content": m.content} for m in req.messages]
	prompt = tokenizer.apply_chat_template(formatted, tokenize=False, add_generation_prompt=True)
	inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
	prompt_len = inputs["input_ids"].shape[1]

	with torch.no_grad():
		out = model.generate(
			**inputs,
			max_new_tokens=min(req.max_tokens, 4096),
			temperature=max(req.temperature, 0.01),
			do_sample=req.temperature > 0.05,
			pad_token_id=tokenizer.eos_token_id,
		)

	reply = tokenizer.decode(out[0][prompt_len:], skip_special_tokens=True).strip()
	return {
		"id": f"chatcmpl-{int(time.time()*1000)}",
		"object": "chat.completion",
		"created": int(time.time()),
		"model": req.model,
		"choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
		"usage": {"prompt_tokens": prompt_len, "completion_tokens": len(out[0]) - prompt_len, "total_tokens": len(out[0])},
	}

threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=PORT), daemon=True).start()
print("Serveur opérationnel sur ngrok !")
```

---

## 4. Commande de Lancement de la Condition D en Local

Sur le serveur local (`/home/elrems/kaggle`) :

```bash
# Vérifier la connectivité de l'API
curl -s "https://aracely-postillioned-lennox.ngrok-free.dev/" -H "ngrok-skip-browser-warning: true"

# Lancer le benchmark sur les 33 bugs TEST
export LLM_BASE_URL="https://aracely-postillioned-lennox.ngrok-free.dev/v1"
export LLM_MODEL="gemma-4-ft"
export TPM_LIMIT="1000000"

PSB=2 python3 -u agent/run.py \
  --bugs $(cat runs/test_all.txt) \
  --condition D \
  --model gemma-4-ft \
  --retries 2 > runs/test_D_current.log 2>&1 &
```

Le journal d'exécution se consulte en temps réel :
```bash
tail -f runs/test_D_current.log
```
Le résultat consolidé est enregistré dans `runs/<date-heure>-D/summary.json`.
