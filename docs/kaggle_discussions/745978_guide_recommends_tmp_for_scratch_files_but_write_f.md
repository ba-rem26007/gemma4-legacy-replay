# Topic 745978: Guide recommends /tmp for scratch files, but write_file rejects it

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745978
- **Date** : 2026-10-05T15:53:57.626000
- **Votes** : -2 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-05T15:53:57.627000) [Votes: -2]

Hi @ryanholbrook,
there seems to be a small mismatch between the harness guide and the workspace tools.
HARNESS_README section 10 recommends putting temporary reproduction scripts in /tmp so they don’t accidentally become part of the submitted patch.


But when the agent tries that with write_file, it gets:


{"status": "error", "error_type": "FileWriteError",
 "error_message": "Path traversal detected: '/tmp/test_issue.py' escapes workspace root."}
We’ve reproduced this on Kaggle with swegemma 0.2.7 on public tasks requests_7315 and rich_4077. The restriction appears to come from swegemma/tools/workspace.py.


The agent can work around it with a shell heredoc through run_command, but that costs a failed tool call before it discovers the restriction and makes creating non-trivial scripts more awkward.


Is /tmp intended to be usable by the file tools?


If yes, could write_file / read_file / edit_file allow paths under /tmp?


If not, could the guide (and ideally the task instructions) mention that /tmp scratch files need to be created through run_command?


Thanks!
Mugur B.

---
