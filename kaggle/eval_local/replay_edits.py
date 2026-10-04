#!/usr/bin/env python3
"""Rejeu des points de décision « édition » sous plusieurs variantes (VM Colab, vLLM sur :8000, sans relais lent).

Entrée : edits_<tag>.jsonl écrit par slow_proxy.py --dump (requête complète + réponse d'origine).
Pour chaque contexte et chaque variante : N tirages ; on classe le premier appel edit_file de la réponse :
  ok        filepath, old_string et new_string présents
  perdu     un argument obligatoire manque (le parseur gemma4 a découpé une chaîne mal délimitée)
  autre     pas d'appel edit_file (autre outil, ou texte)
Sortie : tableau par variante, séparé selon que l'appel d'origine était réussi ou raté ; détail JSONL.
Usage : python3 replay_edits.py edits_lent2.jsonl --n 4 --out replay_edits.jsonl
"""
import argparse, collections, concurrent.futures as cf, copy, json, urllib.request

SHORT = ("\n\nWhen you call edit_file, keep old_string short: one to three consecutive lines copied exactly from the file, "
         "just enough to be unique. Never pass a whole function or block as old_string; for a larger change, make several "
         "small edits. Give the arguments in the order filepath, old_string, new_string.")


def add_to_system(req, text):
    m = req["messages"][0]
    if m.get("role") != "system":
        req["messages"].insert(0, {"role": "system", "content": text.strip()})
        return
    if isinstance(m["content"], str):
        m["content"] += text
    else:
        m["content"].append({"type": "text", "text": text})


VARIANTS = {
    "origine": lambda r: r,
    "T0.2": lambda r: {**r, "temperature": 0.2, "top_k": 40},
    "court": lambda r: (add_to_system(r, SHORT), r)[1],
    "court+T0.2": lambda r: (add_to_system(r, SHORT), {**r, "temperature": 0.2, "top_k": 40})[1],
}


def classify(msg):
    for c in msg.get("tool_calls") or []:
        if c["function"]["name"] != "edit_file":
            continue
        try:
            a = json.loads(c["function"]["arguments"] or "{}")
        except Exception:
            return "perdu"
        return "ok" if {"filepath", "old_string", "new_string"} <= set(a) else "perdu"
    return "autre"


def call(api, req):
    body = json.dumps({**req, "stream": False}).encode()
    r = urllib.request.Request(api + "/chat/completions", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=900) as f:
        return json.loads(f.read())["choices"][0]["message"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dump")
    p.add_argument("--api", default="http://127.0.0.1:8000/v1")
    p.add_argument("--n", type=int, default=4)
    p.add_argument("--out", default="replay_edits.jsonl")
    p.add_argument("--workers", type=int, default=16)
    a = p.parse_args()
    ctx = [json.loads(l) for l in open(a.dump)]
    ctx = [c for c in ctx if any(t["function"]["name"] == "edit_file" for t in c["response"].get("tool_calls") or [])]
    jobs = []
    for i, c in enumerate(ctx):
        origin = classify(c["response"])
        for v, f in VARIANTS.items():
            for k in range(a.n):
                req = f(copy.deepcopy(c["request"]))
                req.pop("seed", None)
                jobs.append((i, origin, v, k, req))
    print(f"{len(ctx)} contextes d'édition, {len(jobs)} requêtes")
    stats = collections.defaultdict(collections.Counter)
    with cf.ThreadPoolExecutor(a.workers) as ex, open(a.out, "w") as out:
        futs = {ex.submit(call, a.api, j[4]): j for j in jobs}
        for fu in cf.as_completed(futs):
            i, origin, v, k, _ = futs[fu]
            try:
                res = classify(fu.result())
            except Exception as e:
                res = "erreur"
            stats[(v, origin)][res] += 1
            out.write(json.dumps({"ctx": i, "origine": origin, "variante": v, "tirage": k, "resultat": res}) + "\n")
    print(f"{'variante':12} {'origine':8} {'ok':>5} {'perdu':>6} {'autre':>6} {'taux ok parmi les edit_file':>28}")
    for (v, origin), c in sorted(stats.items()):
        e = c["ok"] + c["perdu"]
        print(f"{v:12} {origin:8} {c['ok']:5} {c['perdu']:6} {c['autre']:6} {(c['ok'] / e if e else 0):28.0%}")


if __name__ == "__main__":
    main()
