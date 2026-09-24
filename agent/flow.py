"""Déroulé FIXE de l'agent (localiser → lire → éditer → tester) et outils déterministes.

Partagé par agent/run.py (évaluation, Gemma génère les tours assistant) et
trajectories/reconstruct.py (entraînement, tours assistant reconstruits depuis le correctif officiel).
Le format des messages est donc STRICTEMENT identique en évaluation et en entraînement.
"""
import csv, json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PS = ROOT / "bench" / "ps"
EXCLUDE = ("tests/", "vendor/", "translations/", "install-dev/", "js/tiny_mce", "admin-dev/themes/default/public", ".github/")
MAX_FILES_READ, WINDOW, MAX_LINES_PER_FILE, MAX_GREP_FILES = 3, 30, 260, 25

SYSTEM = """Tu es un agent qui corrige des bugs dans PrestaShop (PHP, legacy + Symfony).
Tu suis un déroulé FIXE en étapes. À chaque étape, tu réponds UNIQUEMENT dans le format demandé, sans explication.
1. LOCALISER : proposer des mots-clés de recherche (noms de classes, méthodes, variables, clés de traduction).
2. LIRE : choisir au plus 3 fichiers à lire parmi les résultats de recherche.
3. ÉDITER : produire des blocs SEARCH/REPLACE. Le texte SEARCH doit être copié EXACTEMENT depuis le fichier lu.
4. TESTER : si un test échoue, corriger avec de nouveaux blocs SEARCH/REPLACE."""

EDIT_FORMAT = """Format (un ou plusieurs blocs) :
FILE: chemin/relatif.php
<<<<<<< SEARCH
lignes exactes existantes
=======
lignes corrigées
>>>>>>> REPLACE"""


# ---------------------------------------------------------------- outils (déterministes)
def git(*a):
    r = subprocess.run(["git", "-C", str(PS), *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def show(commit, path):
    return git("show", f"{commit}:{path}")


def grep(commit, keywords):
    """git grep sur le commit de base → {fichier: nb de lignes trouvées}, trié."""
    hits = {}
    pats = [x for kw in keywords[:8] if len(kw.strip()) >= 3 for x in ("-e", kw.strip())]
    if not pats:
        return hits
    # une seule passe sur l'arbre du commit (tous les mots-clés à la fois)
    out = git("grep", "-I", "-c", "-F", "-i", *pats, commit, "--", "*.php", "*.tpl", "*.twig", "*.js", "*.ts", "*.vue")
    for l in out.splitlines():
        _, f, n = l.split(":", 2)
        if not f.startswith(EXCLUDE):
            hits[f] = hits.get(f, 0) + int(n)
    # les fichiers dont le NOM contient un mot-clé passent devant (classe PrestaShop = nom de fichier)
    kl = [k.strip().lower() for k in keywords if len(k.strip()) >= 3]
    name_hit = lambda f: any(k in f.rsplit("/", 1)[-1].lower() for k in kl)
    return dict(sorted(hits.items(), key=lambda x: (not name_hit(x[0]), -x[1]))[:MAX_GREP_FILES])


def windows(src, keywords, extra_lines=()):
    """Extraits du fichier autour des lignes contenant un mot-clé (et des lignes imposées)."""
    rows = src.splitlines()
    kws = [k.lower() for k in keywords if len(k) >= 3]
    marks = [i for i, l in enumerate(rows) if any(k in l.lower() for k in kws)] + [i for i in extra_lines if i < len(rows)]
    spans = []
    for i in sorted(set(marks)):
        a, b = max(0, i - WINDOW), min(len(rows), i + WINDOW + 1)
        if spans and a <= spans[-1][1]:
            spans[-1][1] = max(spans[-1][1], b)
        else:
            spans.append([a, b])
    out, total = [], 0
    for a, b in spans:
        if total >= MAX_LINES_PER_FILE:
            out.append("[… tronqué …]")
            break
        b = min(b, a + MAX_LINES_PER_FILE - total)
        out.append(f"[lignes {a + 1}-{b}]\n" + "\n".join(rows[a:b]))
        total += b - a
    return "\n".join(out) if out else "\n".join(rows[:MAX_LINES_PER_FILE])


def glossary_hits(ticket_text):
    """Condition C : entrées du glossaire métier dont le terme ou un synonyme apparaît dans le ticket."""
    p = ROOT / "glossaire" / "glossaire.csv"
    if not p.exists():
        return ""
    t = ticket_text.lower()
    lines = []
    for r in csv.DictReader(open(p)):
        names = [r["terme"]] + [s for s in r["synonymes"].split("|") if s]
        if any(n.lower() in t for n in names):
            lines.append(f"- {r['terme']} ({', '.join(names[1:4])}) → {r['symboles'].replace('|', ', ')}")
    return "\n".join(lines)


# ---------------------------------------------------------------- messages (format figé)
def ticket_text(bug):
    t = bug["ticket"]
    parts = [f"# {t['title']}", t.get("bug", ""), "## Attendu\n" + t["expected"] if t.get("expected") else "",
             "## Étapes\n" + t["steps"] if t.get("steps") else ""]
    return "\n\n".join(p for p in parts if p).strip()[:4000]


def msg_ticket(bug, condition, replay_spec=""):
    s = f"TICKET\n{ticket_text(bug)}\n"
    if condition in ("B", "C", "D") and replay_spec:
        s += f"\nTEST DE REJEU (doit passer après correction)\n```js\n{replay_spec[:3000]}\n```\n"
    if condition in ("C", "D"):
        g = glossary_hits(ticket_text(bug))
        if g:
            s += f"\nCONTEXTE PRESTASHOP (vocabulaire métier → code)\n{g}\n"
    s += '\nÉTAPE 1 LOCALISER. Réponds en JSON : {"keywords": ["...", "..."]} (3 à 8 mots-clés).'
    return s


def msg_grep(hits):
    lst = "\n".join(f"{f} ({n})" for f, n in hits.items()) or "(aucun résultat)"
    return f'RÉSULTATS DE RECHERCHE (fichier, nb de lignes)\n{lst}\n\nÉTAPE 2 LIRE. Réponds en JSON : {{"files": ["..."]}} (1 à 3 fichiers).'


def msg_read(contents):
    body = "\n\n".join(f"===== {f} =====\n{c}" for f, c in contents.items())
    return f"CONTENU\n{body}\n\nÉTAPE 3 ÉDITER.\n{EDIT_FORMAT}"


def msg_test(result):
    if result.get("fixed"):
        return "RÉSULTAT DU TEST : OK."
    err = result.get("replay_error") or "patch non applicable"
    return f"RÉSULTAT DU TEST : ÉCHEC\n{err}\n\nÉTAPE 4 CORRIGER.\n{EDIT_FORMAT}"


# ---------------------------------------------------------------- parsing / application des éditions
def parse_json(text, key):
    m = re.search(r"\{.*\}", text, re.S)
    try:
        v = json.loads(m.group(0))[key] if m else []
        return [str(x) for x in v] if isinstance(v, list) else []
    except Exception:
        return re.findall(r'"([^"]{3,80})"', text)[:8]


BLOCK = re.compile(r"FILE:\s*(\S+)\s*\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n?>>>>>>> REPLACE", re.S)


def parse_edits(text):
    return [(f.strip("`"), s, r) for f, s, r in BLOCK.findall(text)]


def apply_edits(commit, edits, files_state=None):
    """Applique les blocs sur l'état courant des fichiers → (nouvel état, erreurs)."""
    state = dict(files_state or {})
    errors = []
    for f, s, r in edits:
        src = state.get(f) if f in state else show(commit, f)
        if not src:
            errors.append(f"{f} : fichier introuvable"); continue
        if s not in src:
            errors.append(f"{f} : bloc SEARCH introuvable (copie exacte requise)"); continue
        state[f] = src.replace(s, r, 1)
    return state, errors


def to_diff(commit, state):
    """État modifié → diff unifié (a/ b/) applicable par patch -p1."""
    import difflib
    out = []
    for f, new in state.items():
        old = show(commit, f)
        d = difflib.unified_diff(old.splitlines(True), new.splitlines(True), f"a/{f}", f"b/{f}")
        out.append("".join(d))
    return "".join(out)
