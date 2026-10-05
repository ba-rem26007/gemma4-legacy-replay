# Topic 743353: Not able to download data

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743353
- **Date** : 2026-09-25T18:09:46.200000
- **Votes** : 0 | **Commentaires** : 4

---

### Message #1 — Participant (2026-09-25T18:25:56.137000) [Votes: 0]

Broken from the Data page, too. I will try re-uploading the dataset. Thanks for the heads up.

---

### Message #2 — Participant (2026-09-25T18:28:24.183000) [Votes: 0]

Hi Ryan, is it possible to get RTX PRO 6000 gpus instead of L4x4?

---

### Message #3 — Participant (2026-09-25T18:34:51.520000) [Votes: 0]

That's unlikely, unfortunately.

---

### Message #4 — Participant (2026-09-25T18:09:46.200000) [Votes: 0]

Running `kaggle competitions download -c gemma-4-developer-agent` gives me `404 Client Error: Not Found for url: https://api.kaggle.com/v1/competitions.CompetitionApiService/DownloadDataFiles`. The same is true when I used 



```
import kagglehub; path = kagglehub.competition_download('gemma-4-developer-agent')

```

Is this known?

---
