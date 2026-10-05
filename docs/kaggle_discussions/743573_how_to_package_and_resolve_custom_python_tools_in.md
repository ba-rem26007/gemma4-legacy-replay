# Topic 743573: How to package and resolve custom Python tools in submission.zip given adk-submission's closed ToolRegistry?

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/743573
- **Date** : 2026-09-26T08:40:56.274000
- **Votes** : 1 | **Commentaires** : 2

---

### Message #1 — Participant (2026-09-26T08:40:56.273000) [Votes: 1]

Hi everyone and the competition organizers,


The competition overview states:



  "You must provide a zip archive (submission.zip) that contains your Agent Config, comprising system prompts, custom tools, skills, and LoRA adapters. An agent.yaml file must be located at the root of the archive."



However, in `HARNESS_README.md` (Section 2.1 — Declarative-Only Security Model), it states:



  "Competitors do not submit Python code entrypoints (`agent.py` or `agent_fn`). Standard ADK's `from_config()` permits arbitrary dynamic Python imports; `adk-submission` replaces it with a sandboxed YAML compiler (`compile_submission`). All agents, sub-agents, workflows, tools, and generation parameters are declared in YAML and resolved against closed host registries (`ToolRegistry`, `ModelRegistry`, `SkillRegistry`, `CallbackRegistry`). `importlib` is never used."



Furthermore, Section 6 specifies that `SwegemmaContext.create_tools()` only registers 9 built-in tools into `ToolRegistry` (`run_command`, `submit_patch`, `read_file`, `edit_file`, `write_file`, `get_status`, and 3 code graph tools).


This creates an important technical question regarding custom tools:



How should a custom Python tool function be packaged and registered?
If we write custom tools in Python (for example, AST-based symbol extractors, specialized symmetric diff patchers, or token-capped search utilities) under a `custom_tools/` or `tools/` folder in `submission.zip`, how can they be registered into `ToolRegistry` if `importlib` is disallowed? What is the expected YAML declaration syntax in `agent.yaml` to bind a custom tool file/callable?
Is "custom tools" strictly intended as `AgentTool` (sub-agents)?
In the schema, `agent_tool: {config_path: ..., skip_summarization: true}` wraps a sub-agent as a tool. Does the mention of "custom tools" in the rules refer solely to sub-agents wrapped as `AgentTool`, or is there a supported path for standalone Python tool functions?
Running inside Sandbox vs Host:
If standalone custom tool functions cannot run on the Host, the only alternative is invoking them inside the sandbox container via `run_command` (e.g. `python3 /path/to/tool.py ...`). However, this incurs substantial token bloat (bash escaping, quoting, and process overhead) compared to direct native tool calling, which heavily impacts the 12-hour evaluation budget.

Could the organizers provide a minimal schema example or demo snippet showing how a custom Python tool is expected to be declared in `agent.yaml` and resolved during evaluation?


Thank you for your support and clarification!

---

### Message #2 — Participant (2026-09-26T11:38:42.687000) [Votes: 0]

Include them as scripts in a skill. They will be available in the sandbox and your agent can execute them there.

---
