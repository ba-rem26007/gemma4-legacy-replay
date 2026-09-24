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


def chat(messages, model, temperature=0.2, seed=42, max_tokens=2048):
    base = os.environ.get("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai").rstrip("/")
    body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
    req = urllib.request.Request(f"{base}/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json",
                                  "Authorization": f"Bearer {os.environ.get('GEMMA_API_KEY', '')}"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.loads(r.read())
            return d["choices"][0]["message"]["content"] or "", d.get("usage", {})
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(20 * (attempt + 1)); continue
            raise RuntimeError(f"LLM HTTP {e.code}: {e.read().decode()[:300]}")


def catalog():
    return {c["pr"]: c for c in map(json.loads, open(ROOT / "bench" / "catalog.jsonl"))}


def replay_spec(pr):
    d = ROOT / "bench" / "replay" / str(pr)
    return "\n\n".join(p.read_text() for p in sorted(d.glob("*.spec.js"))) if d.exists() else ""


def run_bug(bug, condition, model, retries, out):
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
    ap.add_argument("--bugs", nargs="+", type=int, required=True)
    ap.add_argument("--condition", default="B", choices=["A", "B", "C", "D"])
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL", "gemma-4-26b-a4b-it"))
    ap.add_argument("--retries", type=int, default=2)
    a = ap.parse_args()
    cat = catalog()
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{a.condition}"
    root = ROOT / "runs" / run_id
    res = []
    for pr in a.bugs:
        print(f"== #{pr} condition {a.condition} ({a.model})", flush=True)
        r = run_bug(cat[pr], a.condition, a.model, a.retries, root / str(pr))
        print(json.dumps({k: r[k] for k in ("applied", "fixed", "regression", "loc_hit", "turns")}), flush=True)
        res.append(r)
    summary = {"run": run_id, "condition": a.condition, "model": a.model, "n": len(res),
               "fixed": sum(r["fixed"] for r in res), "loc_hit": sum(r["loc_hit"] for r in res), "results": res}
    (root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"→ {root}  corrigés {summary['fixed']}/{len(res)}  localisation {summary['loc_hit']}/{len(res)}")


if __name__ == "__main__":
    main()
