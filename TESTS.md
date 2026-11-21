# Tests

- Unit: `python -m unittest discover -s tests` (10 tests, fixtures in `tests/fixtures`).
- Skill evals: `evals/evals.json` (5 cases: flaky, weak, plan, red, legacy; fixtures in `evals/fixtures`). Each run works on a fresh copy of the fixture.
- T-001 2026-11-21, one run each, graded by the parent session on the subagent reports: with skill 5/5, bare baseline 5/5. With the skill, agents used `tw.py lint`, `tw.py plan` and hand mutants (legacy: 4 of 5 mutants caught, the fifth equivalent). Two with-skill runs found `tw.py run` refused a bare pytest folder (fixed, L-001). One with-skill red fix changed `// 10` to `/ 100`, returning a float; still a pass. No trigger proxy run yet: the plugin was not installed during the run.
