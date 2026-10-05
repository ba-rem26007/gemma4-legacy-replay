# Topic 743566: Local eval with docker sandbox, Error Module not found

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743566
- **Date** : 2026-09-26T08:23:41.227000
- **Votes** : 1 | **Commentaires** : 1

---

### Message #1 — Participant (2026-09-26T08:23:41.227000) [Votes: 1]

I'm trying to run the swegemma eval in local. I'm using ollama(cloud) for inference.
I've created the docker image using the Dockefile.public
`docker build -t swebench-sandbox:latest -f Dockerfile.public .`


When I ran the eval, for fastapi tasks it is giving 


`ModuleNotFoundError: No module named 'typing_inspection'`


and the whl is not there for typing_inspection. So I've to add the wheels manually and run it.


Did anyone face the same issue?

---
