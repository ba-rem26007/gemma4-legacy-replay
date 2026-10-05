# Topic 745267: Supported authorization, skill-startup and patch-recovery hooks

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745267
- **Date** : 2026-10-02T20:48:13.193000
- **Votes** : 0 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-02T20:48:13.193000) [Votes: 0]

Thanks for clarifying that custom Python tools should be packaged as sandbox
skill scripts. For adk-submission 0.2.12 and swegemma 0.2.7, is there a supported
submission configuration for any of the following?

- A trusted approval check before each exact built-in tool or skill operation.

- Isolated Python startup for skills before workspace modules can be imported.

Automatic patch recovery restricted to an explicitly selected candidate,
including on timeout.

Please point to the supported configuration/hooks, or confirm which items
require an organizer runtime change. We want development and official scoring
to use the same supported interface.

---
