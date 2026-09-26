#!/usr/bin/env python3
"""Gemma ÉCRIT l'oracle d'un bug (ticket + correctif officiel), validé automatiquement pre/post.

But : produire des milliers de tests (vivier TRAIN 1.6/1.7/8.x) sans agent Claude.
Le test n'est gardé que s'il ÉCHOUE sur le code d'avant et PASSE sur le correctif officiel.
En cas d'échec de validation, l'erreur est renvoyée à Gemma (2 corrections max).
Les tests générés sont des VÉRIFICATEURS, jamais des données d'entraînement (pas de trajectoire).

Usage : PSB=5 python3 bench/gentest.py <pr> [<pr>…] [--model gemma-4-31b-it] [--tries 3]
Sortie : bench/replay/g<pr>/ (oracle_gemma*.spec.js, setup.sql, STATUS) ; résumé bench/gentest.jsonl
"""
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parent
sys.path.insert(0, str(ROOT / "agent"))
import run as agentrun  # chat() (limiteur de débit, budget), load_env()
import flow

PSB = os.environ.get("PSB", "1")
EXAMPLES = {"bo": 40651, "fo": 41036}  # oracles validés à la main, sur d'AUTRES bugs (jamais celui traité)

ENV_NOTES = """ENVIRONNEMENT DE TEST (PrestaShop en Docker, données de démo FR installées)
- Playwright (JS, CommonJS) : `const { test, expect } = require('@playwright/test');`. baseURL déjà configurée.
- Front : '/', '/index.php?id_product=1&controller=product', '/index.php?controller=category&id_category=3', etc.
  Client démo : pub@prestashop.com / 123456789. Produits 1..19, commandes 1..5, thème des images 9.x = hummingbird.
- Back-office : fichier `oracle_gemma.bo.spec.js` → session admin DÉJÀ ouverte. Aller sur page.goto('/admin-dev/'),
  puis récupérer les liens du menu (les URL Symfony exigent un _token). Un lien sans jeton mène à une page de sécurité :
  cliquer le texte /comprends les risques|understand the risks/i.
- Base MySQL (préfixe ps_) accessible dans le test :
  const { execSync } = require('child_process');
  const PROJ = 'psbench' + ((process.env.PS_PORT||'8081')==='8081' ? '' : String(Number(process.env.PS_PORT)-8080));
  const sql = q => execSync(`docker exec ${PROJ}-db-1 mysql -padmin prestashop -N -e "${q}"`).toString();
- setup.sql : exécuté AVANT chaque run (base remise à zéro juste avant) ; doit être idempotent.
- Boutique en mode production (erreurs PHP non affichées) ; aucune règle de taxe installée.
- Le test doit vérifier le comportement CORRIGÉ : il doit ÉCHOUER sur le code d'avant le correctif et PASSER après.
  Vise une assertion métier précise (valeur, texte, statut HTTP, ligne en base), pas un simple chargement de page.
- ROBUSTESSE : boutique en FRANÇAIS. Ne devine JAMAIS un libellé exact (titres, messages) : préfère le statut HTTP,
  la présence/absence d'un élément, une valeur numérique, un montant, une ligne en base (sql(...)), ou une regex large.
  Une seule assertion décisive vaut mieux que plusieurs assertions fragiles."""

FORMAT = """RÉPONDS EXACTEMENT dans ce format (rien d'autre) :
KIND: fo|bo
```sql
-- contenu de setup.sql (ou vide)
```
```js
// contenu du test Playwright
```"""


def catalog(pr):
    for f in ("catalog.jsonl", "catalog_legacy.jsonl"):
        p = B / f
        if p.exists():
            for l in open(p):
                c = json.loads(l)
                if c["pr"] == pr:
                    return c
    raise SystemExit(f"#{pr} absent du catalogue")


def example(kind):
    d = B / "replay" / str(EXAMPLES[kind])
    spec = next(d.glob("oracle*.spec.js")).read_text()
    setup = (d / "setup.sql").read_text() if (d / "setup.sql").exists() else ""
    return f"--- EXEMPLE de test validé ({kind}, autre bug)\n```sql\n{setup[:1500]}\n```\n```js\n{spec[:3500]}\n```"


def context(bug):
    diff = (B / "diffs" / f"{bug['pr']}.diff").read_text()[:6000]
    kws = [fn.split("::")[-1] for fns in bug["functions"].values() for fn in fns if not fn.startswith("(")][:6]
    code = "\n\n".join(f"===== {f} =====\n{flow.windows(flow.show(bug['base_commit'], f), kws)[:3000]}"
                       for f in bug["files"][:2] if flow.show(bug["base_commit"], f))
    return f"TICKET\n{flow.ticket_text(bug)[:3000]}\n\nCORRECTIF OFFICIEL (diff)\n```diff\n{diff}\n```\n\nCODE AVANT CORRECTIF (extraits)\n{code[:6000]}"


def parse(reply):
    kind = "bo" if re.search(r"KIND:\s*bo", reply, re.I) else "fo"
    sql = re.search(r"```sql\n(.*?)```", reply, re.S)
    js = re.search(r"```(?:js|javascript)\n(.*?)```", reply, re.S)
    return kind, (sql.group(1).strip() if sql else ""), (js.group(1).strip() if js else "")


def sh(cmd, timeout=1800):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def validate(pr, gdir):
    """(ok, message) : ok si échec en pre ET succès en post."""
    sh(f"PSB={PSB} {B}/checkout.sh {pr} pre")
    c_pre, o_pre = sh(f"PSB={PSB} {B}/replay/run.sh {gdir.name}", 600)
    sh(f"PSB={PSB} {B}/checkout.sh {pr} post")
    c_post, o_post = sh(f"PSB={PSB} {B}/replay/run.sh {gdir.name}", 600)
    err = lambda o: "\n".join(l for l in o.splitlines() if re.search(r"Error|Expected|Received|Timeout|✘|SyntaxError|at .*spec", l))[:1500]
    if c_pre != 0 and c_post == 0:
        return True, "OK"
    if c_pre == 0:
        return False, "Le test PASSE déjà sur le code AVANT correctif : il ne détecte pas le bug. Rends l'assertion plus précise."
    return False, f"Le test ÉCHOUE sur le code APRÈS correctif (il devrait passer) :\n{err(o_post)}"


def process(pr, model, tries):
    bug = catalog(pr)
    gdir = B / "replay" / f"g{pr}"
    gdir.mkdir(exist_ok=True)
    kind0 = "bo" if bug.get("area") == "BO" or any("admin" in f.lower() or "/Admin/" in f for f in bug["files"]) else "fo"
    msgs = [{"role": "system", "content": "Tu écris des tests Playwright de non-régression pour PrestaShop. Réponds uniquement dans le format demandé."},
            {"role": "user", "content": f"{ENV_NOTES}\n\n{example(kind0)}\n\n{context(bug)}\n\n{FORMAT}"}]
    t0, log = time.time(), []
    for attempt in range(tries):
        reply, usage = agentrun.chat(msgs, model)
        agentrun.spend(usage)
        msgs.append({"role": "assistant", "content": reply})
        kind, sql, js = parse(reply)
        for f in gdir.glob("oracle_gemma*.spec.js"):
            f.unlink()
        if not js:
            msg = "Réponse sans bloc ```js```. Respecte le format."
        else:
            (gdir / f"oracle_gemma{'.bo' if kind == 'bo' else ''}.spec.js").write_text(f"// Oracle écrit par Gemma ({model}) pour PR #{pr}, validé pre/post automatiquement\n{js}\n")
            (gdir / "setup.sql").write_text(sql + "\n") if sql else (gdir / "setup.sql").unlink(missing_ok=True)
            ok, msg = validate(pr, gdir)
            log.append({"attempt": attempt + 1, "ok": ok, "msg": msg[:300]})
            if ok:
                (gdir / "STATUS").write_text(f"valide\ngemma essai {attempt + 1}\n")
                return {"pr": pr, "statut": "valide", "essais": attempt + 1, "s": round(time.time() - t0), "log": log}
        msgs.append({"role": "user", "content": f"VALIDATION : {msg}\nCorrige le test. {FORMAT}"})
    (gdir / "STATUS").write_text(f"exclu:gemma_{tries}_essais\n{log[-1]['msg'] if log else ''}\n")
    return {"pr": pr, "statut": "echec", "essais": tries, "s": round(time.time() - t0), "log": log}


def main():
    agentrun.load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("prs", nargs="+", type=int)
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL", "gemma-4-31b-it"))
    ap.add_argument("--tries", type=int, default=3)
    a = ap.parse_args()
    with open(B / "gentest.jsonl", "a") as out:
        for pr in a.prs:
            try:
                r = process(pr, a.model, a.tries)
            except Exception as e:
                r = {"pr": pr, "statut": "erreur", "err": str(e)[:300]}
            print(json.dumps({k: v for k, v in r.items() if k != "log"}, ensure_ascii=False), flush=True)
            out.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
