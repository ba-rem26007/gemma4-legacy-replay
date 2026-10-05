# Topic 745850: inline_snapshot wheel missing for notebook environment but required by tasks

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745850
- **Date** : 2026-10-04T21:27:50.285000
- **Votes** : 0 | **Commentaires** : 2

---

### Message #1 — Participant (2026-10-05T15:57:53.670000) [Votes: 0]

Same as me.


I found dependency issues in my local baseline environment. Tests could not import `inline-snapshot`, `dirty-equals`, or `attrs`, and some reported multipart validation errors or recursive `httpbin` fixture dependencies.


I built a separate sandbox image with the required packages and test plugins, keeping the original official image unchanged. Those errors disappeared in the completed results.


I also checked package versions after harness setup, because setup can overwrite packages installed in the image. This revealed a remaining issue: `httpcore` requires `h11`, but `h11` is missing. I confirmed that it breaks `httpcore` imports and default `httpx.Client` initialization; I haven’t fixed that yet.


Some apparent “dependency errors” were actually incomplete model patches. I tested five cases with the same environment: the model patches failed, while the reference source fixes passed without adding packages.


These findings are from my local setup. I haven’t confirmed whether the official Kaggle environment has the same issues.

---

### Message #2 — Participant (2026-10-04T21:27:50.287000) [Votes: 0]

In the starter notebook, tests that import inline_snapshot fail at collection with ModuleNotFoundError (e.g. fastapi tasks where tests/ use from inline_snapshot import snapshot). The wheels/ folder has no inline-snapshot wheel. Is this expected in the scoring environment too, or does the scorer env have it installed?

---
