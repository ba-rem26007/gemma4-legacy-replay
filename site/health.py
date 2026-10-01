#!/usr/bin/env python3
"""État des liaisons du projet avec les services externes → site/health.json (lu par site/health.html).

Lancé par cron toutes les 5 min. Aucun secret n'est écrit dans la sortie : les clés sont lues localement
(.env, ~/.kaggle) et seuls des statuts / codes HTTP sont publiés.
Usage : python3 site/health.py [--out /home/elrems/kaggle.d1dev.fr/public/health.json]
"""
import concurrent.futures as cf, datetime as dt, json, os, re, shutil, subprocess, time, urllib.request
import socket
from pathlib import Path

# IPv4 seulement : l'IPv6 sortant de ce serveur ne répond pas (huggingface.co, googleapis.com) → urllib bloquait
_gai = socket.getaddrinfo
socket.getaddrinfo = lambda host, port, family=0, *a, **k: _gai(host, port, socket.AF_INET, *a, **k)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "health.json"
REPO = "ba-rem26007/gemma4-legacy-replay"
REPO_PUBLIC = "ba-rem26007/gemma4-legacy-replay-public"
KAGGLE_KERNEL = "rmisoubeyrand/gemma-4-qlora-training-prestashop"
KAGGLE_DATASET = "rmisoubeyrand/gemma4-prestashop-trajectories"
HF_MODELS = {"Adaptateur E4B PrestaShop": "elrems/lora_gemma4-4b-prestashop-v1",
             "Fiche Dolibarr": "elrems/lora_gemma4-4b-dolibarr-v1"}


def env():
    e = {}
    p = ROOT / ".env"
    if p.exists():
        for l in p.read_text().splitlines():
            m = re.match(r"\s*([A-Z_]+)\s*=\s*(.*)", l)
            if m:
                e[m.group(1)] = m.group(2).strip().strip('"')
    return e


def sh(*cmd, timeout=30):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return p.returncode, (p.stdout + p.stderr).strip()


def http(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # réseau, DNS, timeout
        return 0, str(e).encode()


def res(name, group, status, detail, url=None):
    """status : ok | warn | ko | info"""
    return {"name": name, "group": group, "status": status, "detail": detail, "url": url}


def site():
    code, _ = http("https://kaggle.d1dev.fr/")
    return res("Site (Traefik + auth)", "Site", "ok" if code == 401 else "warn" if code == 200 else "ko",
               f"HTTP {code} ({'protégé par mot de passe' if code == 401 else 'PUBLIC' if code == 200 else 'injoignable'})",
               "https://kaggle.d1dev.fr")


def github():
    out = []
    rc, txt = sh("gh", "api", f"repos/{REPO}", "-q", "[.private, .pushed_at] | @tsv")
    if rc:
        out.append(res("Dépôt de travail", "GitHub", "ko", txt[-120:], f"https://github.com/{REPO}"))
    else:
        private, pushed = txt.split("\t")
        _, head = sh("git", "rev-parse", "HEAD")
        _, remote = sh("git", "ls-remote", "origin", "refs/heads/main")
        sync = remote.split()[0] == head if remote else False
        out.append(res("Dépôt de travail", "GitHub", "ok" if sync else "warn",
                       f"{'privé' if private == 'true' else 'PUBLIC'} · dernier push {pushed[:16].replace('T', ' ')} UTC · "
                       f"{'synchronisé' if sync else 'commits locaux non poussés'}", f"https://github.com/{REPO}"))
    rc, txt = sh("gh", "api", f"repos/{REPO_PUBLIC}", "-q", ".private")
    out.append(res("Dépôt public (soumission)", "GitHub", "ok" if txt == "false" else "info",
                   "public" if txt == "false" else "privé" if txt == "true" else "pas encore créé",
                   f"https://github.com/{REPO_PUBLIC}"))
    return out


def kaggle():
    out = []
    rc, txt = sh("kaggle", "kernels", "status", KAGGLE_KERNEL, timeout=60)
    m = re.search(r'status "(?:KernelWorkerStatus\.)?(\w+)"', txt)
    st = m.group(1) if m else None
    out.append(res("Kernel QLoRA", "Kaggle", "ok" if st in ("COMPLETE", "RUNNING", "QUEUED") else "ko",
                   (st or txt[-120:]).lower(), f"https://www.kaggle.com/code/{KAGGLE_KERNEL}"))
    rc, txt = sh("kaggle", "datasets", "status", KAGGLE_DATASET, timeout=60)
    out.append(res("Dataset trajectoires", "Kaggle", "ok" if txt.strip().endswith("ready") else "ko",
                   txt.strip().splitlines()[-1][-80:] if txt.strip() else "?", f"https://www.kaggle.com/datasets/{KAGGLE_DATASET}"))
    return out


def huggingface():
    out = []
    for label, mid in HF_MODELS.items():
        code, body = http(f"https://huggingface.co/api/models/{mid}")
        if code == 200:
            files = [s["rfilename"] for s in json.loads(body).get("siblings", [])]
            w = any(f.endswith(".safetensors") for f in files)
            out.append(res(label, "Hugging Face", "ok" if w else "warn",
                           f"public · {'poids présents' if w else 'aucun poids (fiche seule)'}", f"https://huggingface.co/{mid}"))
        else:
            out.append(res(label, "Hugging Face", "info" if code in (401, 404) else "ko",
                           {401: "privé (invisible pour le jury)", 404: "introuvable"}.get(code, f"HTTP {code}"),
                           f"https://huggingface.co/{mid}"))
    return out


def gemma(e):
    key = e.get("GEMMA_API_KEY")
    if not key:
        return res("API Gemma (Google AI Studio)", "Modèles", "ko", "clé absente de .env", "https://aistudio.google.com/apikey")
    code, body = http("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", {"x-goog-api-key": key})
    if code != 200:
        return res("API Gemma (Google AI Studio)", "Modèles", "ko", f"HTTP {code}", "https://aistudio.google.com/apikey")
    names = {m["name"].split("/")[-1] for m in json.loads(body).get("models", [])}
    want = [n for n in ("gemma-4-31b-it", "gemma-4-26b-a4b-it") if n in names]
    b = {}
    try:
        b = json.loads((ROOT / "runs" / "_budget.json").read_text())
    except Exception:
        pass
    return res("API Gemma (Google AI Studio)", "Modèles", "ok" if want else "warn",
               f"clé valide · {', '.join(want) or 'modèles Gemma 4 absents'} · {b.get('calls', '?')} appels, {b.get('eur', '?')} €",
               "https://aistudio.google.com")


def ago(s):
    """« 18 hours ago » → « 18 h »"""
    s = re.sub(r"\s*ago\s*$", "", s.strip())
    for en, fr in (("About an hour", "1 h"), ("About a minute", "1 min"), ("hours", "h"), ("hour", "h"), ("days", "j"), ("day", "j"),
                   ("weeks", "sem."), ("week", "sem."), ("minutes", "min"), ("seconds", "s"), ("months", "mois"), ("an ", "1 "), ("a ", "1 ")):
        s = s.replace(en, fr)
    return s


def docker():
    rc, txt = sh("docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}")
    rows = dict(l.split("\t", 1) for l in txt.splitlines() if l.startswith("psbench") and "-ps-" in l)
    out = []
    for n in sorted(rows, key=lambda s: int(re.sub(r"\D", "", s.split("-")[0]) or 1)):
        i = re.sub(r"\D", "", n.split("-")[0]) or "1"
        port = 8080 + int(i)
        code, _ = http(f"http://127.0.0.1:{port}/", timeout=10)
        up, st = rows[n].startswith("Up"), rows[n]
        if up:
            out.append(res(f"PrestaShop instance {i} (:{port})", "Banc Docker", "ok" if code in (200, 301, 302) else "warn",
                           f"démarrée · HTTP {code}"))
        else:  # arrêt propre (code 0) = volontaire, pour libérer le serveur ; sinon panne
            clean = "Exited (0)" in st
            out.append(res(f"PrestaShop instance {i} (:{port})", "Banc Docker", "info" if clean else "ko",
                           ("arrêtée proprement" if clean else "arrêtée en erreur") + " depuis " + ago(st.split(")", 1)[-1])))
    if not out:
        out.append(res("Instances PrestaShop", "Banc Docker", "ko", "aucun conteneur psbench"))
    return out


def jobs():
    rc, txt = sh("ps", "-eo", "args")
    n = sum(1 for l in txt.splitlines() if re.search(r"agent/run\.py|bench/gentest\.py|bench/eval\.py|bench/reeval\.py", l) and "grep" not in l)
    runs = sorted((ROOT / "runs").glob("2026*-*"), key=lambda p: p.stat().st_mtime)
    last = runs[-1] if runs else None
    when = dt.datetime.fromtimestamp(last.stat().st_mtime, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC") if last else "—"
    disk = shutil.disk_usage(ROOT)
    free = disk.free / 2**30
    return [res("Tâches agent / éval en cours", "Serveur", "info", f"{n} processus · dernier run {last.name if last else '—'} ({when})"),
            res("Disque", "Serveur", "ok" if free > 20 else "warn" if free > 5 else "ko", f"{free:.0f} Go libres")]


def colab():
    return res("Serveur d'inférence Colab (ngrok)", "Modèles", "info", "à la demande (URL temporaire, non surveillé)")


def main():
    global OUT
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    OUT = Path(ap.parse_args().out)
    t0 = time.time()
    e = env()
    tasks = [site, github, kaggle, huggingface, lambda: gemma(e), docker, jobs, colab]
    checks = []
    with cf.ThreadPoolExecutor(8) as ex:
        for f in [ex.submit(t) for t in tasks]:
            try:
                r = f.result(timeout=120)
                checks += r if isinstance(r, list) else [r]
            except Exception as err:
                checks.append(res("vérification", "Erreur", "ko", str(err)[:120]))
    OUT.write_text(json.dumps({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               "seconds": round(time.time() - t0, 1), "checks": checks}, ensure_ascii=False, indent=1))
    print(f"{len(checks)} vérifications → {OUT}")


if __name__ == "__main__":
    main()
