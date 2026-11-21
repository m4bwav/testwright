# testwright scope and plan (2026-11-21)

Source: [research pass](../research/2026-11-21-research-pass.md).

## Scope (agent's ruling, flagged in the chain HANDOFF)
- In: risk-first test planner; one results format across dotnet, Unity, Vitest/Jest, pytest, Luau; flaky reruns, slow tests; changed-line coverage by calling diff-cover on Cobertura/lcov; suite quality (wrap Stryker.NET, StrykerJS, mutmut; tw.py lint for assertions that never fail and tests of mocks); characterization tests (Verify, syrupy, Vitest snapshots); game testing (Unity play-mode with Input System fixture, seed replays, save/load round trips, bot playthroughs) with hooks to grindwright and logwright.
- Out: browser end-to-end (webapp-testing, Playwright MCP); skill evals (evergreen-test).

## Layout
- skills/testwright/SKILL.md hub (planner method, stack table, routes) plus references/ per stack loaded on demand: dotnet.md, unity.md, js.md, python.md, luau.md, quality.md, legacy.md, games.md.
- scripts/tw.py (stdlib): `detect` (stack and runner), `run` (runs suite with report flags, parses TRX / NUnit XML / JUnit / Jest JSON into one JSON summary; `--reruns N` for flaky), `slow`, `changed` (diff-cover wrapper or git diff + lcov/cobertura fallback), `lint` (never-failing asserts, mock-only tests), `plan` (risk scan: money, saves, data loss, public API, untested files).
- tests/ with fixture reports per runner; evals/ with baselines: passing test on broken code, flaky async test, coverage-chasing vs risk-first.

## Order
1. Repo scaffold (done this session), 2. tw.py parsers + tests, 3. SKILL.md + references, 4. evergreen unit, 5. evals, 6. README with banner, 7. release 0.1.0 and install.
