#!/usr/bin/env python3
"""Lance l'agent Gemma (déroulé fixe) sur des bugs, évalue le patch, journalise la trajectoire complète.

Usage : python3 agent/run.py --bugs 35902 35384 35322 --condition B [--model gemma-4-26b-a4b-it] [--retries 2]
LLM : API compatible OpenAI. Variables (.env) :
  GEMMA_API_KEY   clé (Google AI Studio, OpenRouter… ; vide pour Ollama)
  LLM_BASE_URL    défaut https://generativelanguage.googleapis.com/v1beta/openai  (Ollama : http://<ip>:11434/v1)
  LLM_MODEL       défaut gemma-4-26b-a4b-it
Sortie : runs/<run_id>/<pr>/trace.jsonl + patch.diff + result.json, runs/<run_id>/summary.json
"""
import argparse, json, os, sys, time, urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bench"))
import flow  # noqa: E402
from eval import evaluate  # noqa: E402

ROOT = flow.ROOT


def load_env():
    p = ROOT / ".env"
    if p.exists():
        for l in p.read_text().splitlines():
            if "=" in l and not l.lstrip().startswith("#"):
                k, v = l.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def chat(messages, model, temperature=0.2, seed=42, max_tokens=16384):
    """Appel chat/completions compatible OpenAI via curl (urllib bloque en IPv6 sur ce serveur).
    Les blocs <thought>…</thought> de Gemma 4 sont retirés de la réponse (conservés dans la trace brute)."""
    import re, subprocess
    base = os.environ.get("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai").rstrip("/")
    body = json.dumps({"model": model, "messages": messages, "temperature": temperature,
                       "max_tokens": max_tokens})  # seed non supporté par l'API Gemini (fixé en local)
    for attempt in range(4):
        r = subprocess.run(["curl", "-s", "-m", "600", "-w", "\n%{http_code}", f"{base}/chat/completions",
                            "-H", "Content-Type: application/json",
                            "-H", f"Authorization: Bearer {os.environ.get('GEMMA_API_KEY', '')}",
                            "--data-binary", "@-"], input=body, capture_output=True, text=True)
        out, _, code = r.stdout.rpartition("\n")
        if code == "200":
            d = json.loads(out)
            raw = d["choices"][0]["message"].get("content") or ""
            clean = re.sub(r"<thought>.*?(</thought>|$)", "", raw, flags=re.S).strip()
            return clean, {**d.get("usage", {}), "raw_len": len(raw)}
        if code in ("429", "500", "503", "000") and attempt < 3:
            time.sleep(20 * (attempt + 1)); continue
        raise RuntimeError(f"LLM HTTP {code}: {out[:300]}")


def catalog():
    return {c["pr"]: c for c in map(json.loads, open(ROOT / "bench" / "catalog.jsonl"))}


def replay_spec(pr):
    d = ROOT / "bench" / "replay" / str(pr)
    return "\n\n".join(p.read_text() for p in sorted(d.glob("*.spec.js"))) if d.exists() else ""


def scripted(bug):
    """Politique « reconstruit » : réponses tirées du chemin reconstruit (aucun modèle) → valide la chaîne."""
    sys.path.insert(0, str(ROOT / "trajectories"))
    import reconstruct
    msgs, why = reconstruct.build(bug)
    if not msgs:
        raise SystemExit(f"#{bug['pr']} : chemin non reconstructible ({why})")
    replies = iter(m["content"] for m in msgs if m["role"] == "assistant")
    return lambda _msgs, _model: (next(replies, ""), {})


def run_bug(bug, condition, model, retries, out, policy="llm"):
    global chat
    if policy == "reconstruit":
        chat = scripted(bug)
    out.mkdir(parents=True, exist_ok=True)
    trace = open(out / "trace.jsonl", "w")
    base = bug["base_commit"]
    msgs = [{"role": "system", "content": flow.SYSTEM}]

    def turn(step, user, tool=None, tool_result=None):
        msgs.append({"role": "user", "content": user})
        t = time.time()
        reply, usage = chat(msgs, model)
        msgs.append({"role": "assistant", "content": reply})
        trace.write(json.dumps({"step": step, "user": user, "assistant": reply, "seconds": round(time.time() - t, 1),
                                "usage": usage, "tool": tool, "tool_result": tool_result}, ensure_ascii=False) + "\n")
        trace.flush()
        return reply

    # 1. LOCALISER
    kws = flow.parse_json(turn("localiser", flow.msg_ticket(bug, condition, replay_spec(bug["pr"]))), "keywords")
    hits = flow.grep(base, kws)
    # 2. LIRE
    files = [f for f in flow.parse_json(turn("lire", flow.msg_grep(hits), "grep", {"keywords": kws, "hits": hits}), "files")
             if flow.show(base, f)][:flow.MAX_FILES_READ]
    contents = {f: flow.windows(flow.show(base, f), kws) for f in files}
    # 3. ÉDITER
    reply = turn("editer", flow.msg_read(contents), "read", {"files": files})
    state, result = {}, None
    for attempt in range(retries + 1):
        state, errors = flow.apply_edits(base, flow.parse_edits(reply), state)
        diff = flow.to_diff(base, state) if state else ""
        (out / "patch.diff").write_text(diff)
        if errors and not diff:
            result = {"pr": bug["pr"], "applied": False, "fixed": False, "regression": None,
                      "replay_error": "; ".join(errors)}
        else:
            result = evaluate(bug["pr"], str(out / "patch.diff")) if diff else {"pr": bug["pr"], "applied": False, "fixed": False, "regression": None, "replay_error": "aucune édition"}
            if errors:
                result["replay_error"] = ("; ".join(errors) + "\n" + result.get("replay_error", "")).strip()
        # 4. TESTER : retour d'exécution seulement si la condition donne les tests (B, C, D)
        if result["fixed"] or condition == "A" or attempt == retries:
            break
        reply = turn("corriger", flow.msg_test(result), "test", result)
    result.update({"condition": condition, "model": model, "files_read": files, "keywords": kws,
                   "official_files": bug["files"],
                   "loc_hit": bool(set(files) & set(bug["files"])), "turns": len(msgs) // 2})
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=1))
    trace.close()
    return result


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bugs", nargs="+", type=int, default=[])
    ap.add_argument("--condition", default="B", choices=["A", "B", "C", "D"])
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL", "gemma-4-31b-it"))
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--policy", default="llm", choices=["llm", "reconstruit"],
                    help="reconstruit = rejoue le chemin reconstruit du correctif officiel (démo sans modèle)")
    ap.add_argument("--list-models", action="store_true", help="liste les modèles gemma de l'API et quitte")
    a = ap.parse_args()
    if a.list_models:
        import subprocess
        out = subprocess.run(["curl", "-s", "-m", "30", "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
                              "-H", f"x-goog-api-key: {os.environ.get('GEMMA_API_KEY', '')}"], capture_output=True, text=True).stdout
        print("\n".join(m["name"].split("/")[1] for m in json.loads(out).get("models", []) if "gemma" in m["name"]))
        return
    if a.policy == "reconstruit":
        a.model = "reconstruit"
    cat = catalog()
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{a.condition}"
    root = ROOT / "runs" / run_id
    res = []
    for pr in a.bugs:
        print(f"== #{pr} condition {a.condition} ({a.model})", flush=True)
        try:
            r = run_bug(cat[pr], a.condition, a.model, a.retries, root / str(pr), a.policy)
        except (SystemExit, RuntimeError) as e:
            print(f"   ignoré : {e}", flush=True)
            continue
        print(json.dumps({k: r[k] for k in ("applied", "fixed", "regression", "loc_hit", "turns")}), flush=True)
        res.append(r)
    summary = {"run": run_id, "condition": a.condition, "model": a.model, "n": len(res),
               "fixed": sum(r["fixed"] for r in res), "loc_hit": sum(r["loc_hit"] for r in res), "results": res}
    (root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"→ {root}  corrigés {summary['fixed']}/{len(res)}  localisation {summary['loc_hit']}/{len(res)}")


if __name__ == "__main__":
    main()
