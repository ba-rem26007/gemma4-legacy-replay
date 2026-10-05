# Topic 745882: Local evaluation failure report: Gemma 4 baseline

- **Lien Kaggle** : https://www.kaggle.com/competitions/gemma-4-developer-agent/discussion/745882
- **Date** : 2026-10-05T04:17:21.662000
- **Votes** : 0 | **Commentaires** : 1

---

### Message #1 — Participant (2026-10-05T04:17:21.663000) [Votes: 0]

## Summary

We evaluated all 129 supplied tasks locally. The run resolved 31 tasks (24.03%) and did not resolve 98 (75.97%).


Some failures include test-environment errors. These results must not be interpreted as 98 confirmed model implementation failures. This report does not establish that Kaggle's official environment has the same problems.



## Run configuration




Setting
Value




Model
gemma-4-31b-it-qat-w4a16-ct


Agent
Local sample_submission agent and its two sample adapters


Time limit per task
60 minutes


Tool-call limit
100


Turn limit
500


Command timeout
300 seconds


Concurrency
32 tasks across six model endpoints


Model context window
65,536 tokens


Container Python
3.13


Test environment
Local Docker sandbox



The agent prompt and adapters were copied from the local sample_submission. Their identity with the published originals has not been independently verified. This is not a controlled reproduction of all official evaluation settings.



## Observed failure markers

Counts are task counts, not individual test failures or API attempts. Each task is counted once within a row. A task can occur in multiple rows. Percentages therefore must not be added.





Observed marker
Tasks
% of all 129 tasks
% of 98 unresolved tasks




Any package installation/import marker
37
28.68%
37.76%


Missing inline-snapshot
27
20.93%
27.55%


Missing dirty-equals
9
6.98%
9.18%


python-multipart installation/detection error
6
4.65%
6.12%


Missing attr
1
0.78%
1.02%


Recursive httpbin fixtures
7
5.43%
7.14%


Network unreachable
7
5.43%
7.14%


60-minute session timeout
12
9.30%
12.24%


Test comparisons/assertions failed
41
31.78%
41.84%


Test-output errors (selected exception types)
18
13.95%
18.37%


Agent patch modified tests/
3
2.33%
3.06%


Evaluation test-patch application failure
1
0.78%
1.02%


Context-window overflow
1
0.78%
1.02%


Test-command timeout
1
0.78%
1.02%


Test process exit 137 (cause unconfirmed)
2
1.55%
2.04%



“Test-output errors” groups SyntaxError, NameError, AttributeError, TypeError, ImportError, FileNotFoundError, IndexError, and MissingStyle. The labels describe output markers, not verified root causes. Exception text can appear in an expected-error test, so this row is a diagnostic signal, not an automatic attribution of blame.



## Environment concerns for organizer confirmation


### FastAPI test packages

Existing tests import inline_snapshot and dirty_equals. The supplied fastapi_14978 snapshot declares dirty-equals >=0.9.0 and inline-snapshot >=0.21.1 in pyproject.toml. The packages were unavailable during some local test runs.


Six tasks report that python-multipart must be installed. This message can indicate an installation, version, or detection problem. We have not confirmed package absence in each affected container. One task cannot import attr.


We have not installed these packages as a workaround for this run. We want to confirm the intended setup first.



### Requests test fixtures and network

Seven tasks report both recursive httpbin/httpbin_secure fixture dependencies and network errors, including Errno 101 (Network is unreachable). These are the same seven tasks; they are not 14 separate affected tasks.


Fixture-provider setup and network requirements need confirmation. We have not established whether the cause is a missing plugin, plugin loading, sandbox policy, or another setup issue.



## Other observed failures


- Some patches omit required project modules, symbols, parameters, or fields. A missing project module is not necessarily an external dependency issue.

- Some patches produce incorrect error messages, route behavior, dependency scopes, Unicode widths, or terminal output.

- Syntax-highlight color snapshots differ in several cases. Package-version effects have not been ruled out.

- Twelve tasks reached the 60-minute limit. Some also have environment errors.

- One request exceeded the 65,536-token context limit: at least 49,153 input tokens plus 16,384 requested output tokens.

- One task modified tests/test_highlighter.py and then could not apply the evaluator test patch.

- Two test processes returned exit code 137. No system evidence was collected to confirm an out-of-memory cause.



## Questions for the organizers


- Which repository test dependencies are installed automatically, and at which setup step?

- Does the official environment supply inline-snapshot, dirty-equals, python-multipart, and attrs?

- How should local evaluation configure the httpbin fixtures and required network access?

- Is there a pinned dependency manifest or supported image that reproduces the official environment?

- How does the official evaluator distinguish environment failures from implementation failures?



## Evidence and limitations

The report is based on final task_results.jsonl and the per-task test output in summary.json. Per-task logs and traces are retained locally. The detailed table of all 98 unresolved tasks is in TROUBLESHOOTING.md.


No evaluation tests or scores were changed for this report. No hidden-test feedback was added to the agent. Fixing an environment problem would not establish that the affected patch passes. Other errors can occur in the same task.



## Affected task IDs by marker


### Any package installation/import marker

`fastapi_11194`, `fastapi_11355`, `fastapi_12942`, `fastapi_13207`, `fastapi_13537`, `fastapi_13713`, `fastapi_13786`, `fastapi_14099`, `fastapi_14186`, `fastapi_14246`, `fastapi_14262`, `fastapi_14266`, `fastapi_14297`, `fastapi_14303`, `fastapi_14349`, `fastapi_14356`, `fastapi_14360`, `fastapi_14361`, `fastapi_14371`, `fastapi_14430`, `fastapi_14455`, `fastapi_14459`, `fastapi_14482`, `fastapi_14485`, `fastapi_14512`, `fastapi_14583`, `fastapi_14605`, `fastapi_14616`, `fastapi_14791`, `fastapi_14953`, `fastapi_14962`, `fastapi_14964`, `fastapi_14978`, `fastapi_15023`, `fastapi_15030`, `fastapi_15745`, `rich_3472`



### Missing inline-snapshot

`fastapi_11355`, `fastapi_13207`, `fastapi_14099`, `fastapi_14186`, `fastapi_14246`, `fastapi_14262`, `fastapi_14266`, `fastapi_14297`, `fastapi_14349`, `fastapi_14361`, `fastapi_14371`, `fastapi_14430`, `fastapi_14455`, `fastapi_14459`, `fastapi_14482`, `fastapi_14485`, `fastapi_14512`, `fastapi_14583`, `fastapi_14605`, `fastapi_14791`, `fastapi_14953`, `fastapi_14962`, `fastapi_14964`, `fastapi_14978`, `fastapi_15023`, `fastapi_15030`, `fastapi_15745`



### Missing dirty-equals

`fastapi_12942`, `fastapi_13713`, `fastapi_13786`, `fastapi_14303`, `fastapi_14356`, `fastapi_14360`, `fastapi_14371`, `fastapi_14605`, `fastapi_14791`



### python-multipart installation/detection error

`fastapi_11194`, `fastapi_13537`, `fastapi_14297`, `fastapi_14616`, `fastapi_14791`, `fastapi_14953`



### Missing attr

`rich_3472`



### Recursive httpbin fixtures

`requests_6589`, `requests_6592`, `requests_6629`, `requests_7328`, `requests_7433`, `requests_7502`, `requests_7505`



### Network unreachable

`requests_6589`, `requests_6592`, `requests_6629`, `requests_7328`, `requests_7433`, `requests_7502`, `requests_7505`



### 60-minute session timeout

`fastapi_12942`, `fastapi_14246`, `fastapi_14258`, `fastapi_14303`, `fastapi_14430`, `fastapi_14459`, `fastapi_14482`, `fastapi_14605`, `rich_3063`, `rich_3064`, `rich_3471`, `rich_4079`



### Test comparisons/assertions failed

`fastapi_13920`, `fastapi_14258`, `fastapi_14306`, `fastapi_14419`, `fastapi_14448`, `fastapi_14479`, `fastapi_14487`, `fastapi_14851`, `fastapi_14986`, `fastapi_15588`, `fastapi_15763`, `fastapi_15800`, `fastapi_5624`, `requests_7427`, `rich_3052`, `rich_3061`, `rich_3063`, `rich_3064`, `rich_3130`, `rich_3180`, `rich_3296`, `rich_3468`, `rich_3469`, `rich_3470`, `rich_3506`, `rich_3521`, `rich_3535`, `rich_3675`, `rich_3676`, `rich_3777`, `rich_3782`, `rich_3934`, `rich_3935`, `rich_3938`, `rich_3942`, `rich_3944`, `rich_3953`, `rich_4070`, `rich_4076`, `rich_4077`, `rich_4079`



### Test-output errors (selected exception types)

`fastapi_14186`, `fastapi_14262`, `fastapi_14306`, `fastapi_14448`, `fastapi_14978`, `fastapi_15030`, `fastapi_15280`, `fastapi_15745`, `fastapi_15785`, `fastapi_15800`, `requests_6757`, `rich_3061`, `rich_3471`, `rich_3486`, `rich_3930`, `rich_3938`, `rich_3942`, `rich_4070`



### Agent patch modified tests/

`fastapi_13537`, `fastapi_13786`, `rich_3454`



### Evaluation test-patch application failure

`rich_3454`



### Context-window overflow

`rich_3105`



### Test-command timeout

`rich_4006`



### Test process exit 137 (cause unconfirmed)

`rich_3480`, `rich_3772`

---
