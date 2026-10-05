# Topic 745748: [Resource & Benchmark] 50 Multi-Turn Gemma 4 SWE-bench Trajectories + Closed-Loop TFD-Agent Framework

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745748
- **Date** : 2026-10-04T05:24:41.308000
- **Votes** : 1 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-04T05:24:41.310000) [Votes: 1]

Hi everyone,


To contribute to the Gemma 4 Developer Agent community and support reproducibility, we have released an open-source trajectory benchmark dataset alongside our research notebook.



### 🌟 Key Open-Source Artifacts:


- 📦 Dataset (50 Clean Trajectories): Gemma 4 TFD Agentic Trajectories & Benchmark

- 📓 Research Notebook / Architecture: TFD-Agent: Autonomous SWE-bench Resolution with Gemma 4

- 💻 Open-Source Code: GitHub Repository




### 🔍 What is in this Resource?


- 50 Granular Agentic Trajectories: Contains multi-turn tool invocations (`search_similar_code`, `get_code_neighbors`, `edit_file`, and isolated bash reproduction) across real-world Python repositories.

- Closed-Loop Verification Signals: Full test-feedback loops showing how the agent detects regression failures and refines patches dynamically.

- Graph Tool Diagnostics: Case studies comparing direct string-search localization against AST code-graph traversal (`networkx` dependency subgraphs).



### 💡 Why this helps competitors:


- LoRA & SFT Fine-Tuning: If you are fine-tuning Gemma 4 31B, standard instruction pairs often lack multi-turn agent coherence. These trajectories provide end-to-end multi-turn demonstrations formatted for SFT.

- Failure Mode Analysis: Review where agents stall or exceed step limits to tune your `thinking_budget` and turn ceilings.


We would love to hear feedback from fellow competitors and researchers. Feel free to explore the dataset and fork the notebook! 


Let us know in the comments: what context window and thinking budget configuration is giving you the best stability on the hidden split?

---
