# Changelog

## 0.1.2 (2026-11-21)
- Adds .claude-plugin/marketplace.json so the README install works; README lists `detect` and `changed --dir` and links the wiki; pytest.ini keeps `pytest` from collecting the lint fixtures.

## 0.1.1 (2026-11-21)
- Scope widened to all testing in any language, stack and kind; the five stacks are the first known, not the limit. New-stack procedure in the skill; `tw.py detect` reports `unknown` cleanly (tested).

## 0.1.0 (2026-11-21)
- First release: hub skill `testwright`, `scripts/tw.py` (detect, parse, run with reruns, slow, changed, lint, plan), references for dotnet, unity, js, python, luau, quality, legacy and games.
- `detect` finds a bare pytest folder (test_*.py with no config); the eval runs showed `run` refusing such folders.
- Eval suite of five cases with no-skill baselines.
