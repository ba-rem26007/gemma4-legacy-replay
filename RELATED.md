# Travaux connexes (kit phase 1)

Règle : **chaque référence a un lien vérifié** (API arXiv ou page arXiv consultée le 2026-09-26). Rien n'entre sans vérification.

## Benchmarks d'agents de correction
| Référence | Résumé | Différence avec nous |
|---|---|---|
| Jimenez et al., 2023 — *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?* — https://arxiv.org/abs/2310.06770 | Issues GitHub réelles de dépôts Python, jugées par les tests unitaires du dépôt. | Python uniquement ; suppose une suite de tests existante. Nous : PHP legacy **sans tests**, oracles de bout en bout (navigateur) construits bug par bug. |
| Zan et al., 2025 — *Multi-SWE-bench: A Multilingual Benchmark for Issue Resolving* — https://arxiv.org/abs/2504.02605 | 1 632 instances en Java, TypeScript, JavaScript, Go, Rust, C, C++. | **Pas de PHP**. Nous : PHP, un seul grand projet legacy, versions 1.6 → 9.1 rejouables en Docker. |

## Agents
| Référence | Résumé | Différence avec nous |
|---|---|---|
| Yang et al., 2024 — *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering* — https://arxiv.org/abs/2405.15793 | Interface agent-ordinateur dédiée pour résoudre des issues. | Agent libre ; nous : déroulé fixe court (localiser → lire → éditer → tester), adapté aux petits modèles. |
| Xia et al., 2024 — *Agentless: Demystifying LLM-based Software Engineering Agents* — https://arxiv.org/abs/2407.01489 | Pipeline sans agent : localisation, réparation, validation. | Proche de notre déroulé fixe ; nous ajoutons des vérificateurs exécutés sur l'application réelle (navigateur + base). |

## Entraînement d'agents sur trajectoires
| Référence | Résumé | Différence avec nous |
|---|---|---|
| Pan et al., 2024 — *Training Software Engineering Agents and Verifiers with SWE-Gym* — https://arxiv.org/abs/2412.21139 | Environnement d'entraînement, trajectoires, vérificateurs ; gains par fine-tuning. | Trajectoires issues de modèles propriétaires ; nous : **aucune distillation propriétaire** (chemins reconstruits depuis les correctifs officiels + réussites de Gemma). |
| Yang et al., 2025 — *SWE-smith: Scaling Data for Software Engineering Agents* — https://arxiv.org/abs/2504.21798 | 50 k tâches synthétiques sur 128 dépôts Python ; 5 016 trajectoires Claude 3.7 Sonnet ; SWE-agent-LM-32B à 40,2 % sur SWE-bench Verified. | Bugs synthétiques cassant des tests existants, Python ; nous : bugs **réels** corrigés en amont, PHP legacy sans tests, pas de trajectoires propriétaires. |

## Tests de caractérisation & Code Legacy
| Référence | Résumé | Différence avec nous |
|---|---|---|
| Feathers, 2004 — *Working Effectively with Legacy Code* — Pearson / Prentice Hall, ISBN 0-13-117705-2 — https://dl.acm.org/doi/book/10.5555/1044873 | Définition fondamentale : « le code legacy est du code sans tests ». Introduction des tests de caractérisation pour figer le comportement avant modification. | Suppose l'écriture manuelle de harnais et de « points de rupture » (seams) dans le code ; nous : chaîne d'oracles de bout en bout (navigateur + base) et vérificateurs PHP externes sans modifier l'architecture legacy. |

## Record and Replay Web & Robustesse des Tests
| Référence | Résumé | Différence avec nous |
|---|---|---|
| Choudhary et al., 2011 — *WATERFALL: An Incremental Approach for Repairing Record-and-Replay Tests of Web Applications* — FSE 2011 / https://doi.org/10.1145/2025113.2025167 | Capture et rejeu d'interactions utilisateur sur applications web avec réparation incrémentale des tests cassés. | Conçu pour la non-régression humaine sur l'interface ; nous : réutilisation du rejeu comme signal de guidage et de récompense dynamique pour un agent LLM autonome en mode débogage. |
| Zhao et al., 2024 — *A Survey on Web Application Testing: A Decade of Evolution* — https://arxiv.org/abs/2412.10476 | Revue décennale des techniques de test web, de la fragilité des enregistrements DOM à l'émergence des agents IA. | Synthèse de l'état de l'art soulignant le manque d'environnements exécutables avec persistance d'état complet (BDD/backend) ; exactement ce que fournit notre banc PrestaShop. |

## Modèle & Coupure des connaissances
| Référence | Résumé | Différence avec nous |
|---|---|---|
| Google DeepMind, 2026 — *Gemma 4: Open Models for Autonomous Agents* — Model Card & Documentation — https://ai.google.dev/gemma | Famille de modèles ouverts Gemma 4 (E2B, E4B, 12B, 26B A4B, 31B). Coupure des connaissances déclarée : 2025-06-01. | Base de notre étude ; nous évaluons le modèle sur des bugs corrigés strictement **après** sa coupure (2025-06 à 2026) pour garantir l'absence de contamination. |


## Notre nouveauté en 3 phrases
1. Un benchmark d'agents de code sur un **grand projet PHP legacy réel** (PrestaShop 1.6 → 9.1), absent des benchmarks multilingues existants, avec des bugs corrigés **après** la coupure du modèle et des oracles de bout en bout exécutés dans le navigateur.
2. Une mesure contrôlée de ce que **l'environnement vérifiable** apporte à un petit modèle ouvert : vérificateur parfait (borne haute), tests générés depuis le ticket, glossaire métier, exemples récupérés — avec des résultats négatifs rapportés tels quels.
3. Une fabrique de données **sans distillation propriétaire** (≈ 4 800 bugs réels, chemins reconstruits vérifiés) pour le fine-tuning de Gemma sur du code legacy.
