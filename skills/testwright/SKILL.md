---
name: testwright
description: "Test real application code in C#/.NET, Unity, TypeScript/npm, Python or Roblox Luau: plan tests by risk, run a suite into one summary (failures, flaky reruns, slow tests, changed-line coverage), judge suite quality (mutation testing, assertions that never fail, tests of mocks), pin legacy code with characterization tests, test games (play mode, input, seed replays, save/load round trips, bot playthroughs). Use on 'what should I test', 'write tests for this', 'run the tests and tell me what failed', 'is this test flaky', 'are my tests any good', 'coverage on my diff', 'add tests before I refactor this', 'test my Unity game'. Not for browser end-to-end tests (webapp-testing, Playwright) or skill evals (evergreen-test)."
license: MIT
metadata:
  version: 0.1.0
---

# testwright

Outcome: tests that would fail if the code broke, aimed at what costs most when it breaks, with every claim about the suite backed by a run.

`TW` means `python scripts/tw.py` from the plugin root (run it, do not read it). Standard library only; `--json` gives one JSON object.

## 1. Plan by risk, not by coverage

1. `TW plan <repo>` ranks source files by risk (money, saves, deletes, auth, migrations, parsing, public API) and doubles the score of files with no test. Read the top ten, not the whole repo.
2. For each risky unit write the failure you fear in one line ("a save from 1.2 loads with no inventory"), then the smallest test that catches it. Edge cases first: empty, one, many, boundary, bad input, concurrency.
3. Skip tests for getters, framework glue and generated code. A coverage percentage is never the goal; changed-line coverage (section 3) is the check.

## 2. Run and read

1. `TW detect <repo>` names the stack and runner. Load only that stack's reference: [dotnet](../../references/dotnet.md), [unity](../../references/unity.md), [js](../../references/js.md), [python](../../references/python.md), [luau](../../references/luau.md).
2. `TW run <repo> --reruns 2` runs dotnet, Vitest/Jest or pytest with report flags and prints failures, flaky tests (failed, then passed on rerun) and totals. Unity and Luau run by the commands in their reference; then `TW parse <results files>`.
3. `TW slow <results> --top 10` lists the slowest tests.
4. Report failures with file, test name and first message line. A flaky test is a bug to report, never a pass; do not raise retries to hide it.

## 3. Coverage on the change

`TW changed <coverage.xml|lcov.info> --base origin/main` gives covered and missed changed lines (diff-cover when installed, else git diff plus the coverage file). "No changed lines" usually means coverage paths do not match repo paths; fix the paths, never report 100%.

## 4. Are the tests any good

1. `TW lint <tests dir>` flags assertions that can never fail (`assert True`, `Assert.True(true)`, a value compared with itself), tests with no assertion, and tests that assert only on mocks.
2. Mutation testing on changed code proves the tests catch breakage: [quality](../../references/quality.md) has Stryker.NET, StrykerJS and mutmut. Unity and Luau have no tool: make three to five hand mutants (flip a comparison, drop a call, off by one) in a worktree and confirm a test fails for each.
3. Before claiming a new test works, break the code it covers once and watch it fail.

## 5. Legacy code without tests

Pin behaviour before changing it: characterization tests record what the code does now (Verify, syrupy, snapshots), then change. Seams, sprout and wrap: [legacy](../../references/legacy.md).

## 6. Games

Play-mode tests, simulated input, seed replays, save/load round trips with old save fixtures, bot playthroughs that fail on errors or softlocks: [games](../../references/games.md). Failing bot logs go to logwright (`lgw.py query`); proposed work goes to grindwright, never written into its ledger from here.

## Rules

- Test edits happen in a worktree and a PR, like any code change.
- Never weaken or delete a failing assertion to get green; fix the code or report it.
- Never skip or quarantine a test without saying so in the report.
- Browser end-to-end: webapp-testing or Playwright MCP. Skill evals: evergreen-test.

## Maintenance

Evergreen unit at the plugin root (`evergreen.json`, RESEARCH.md, LEARNINGS.md, CHANGELOG.md, TESTS.md). On 'refresh testwright', re-check the volatile claims in `evergreen.json` against primary docs, log changes in CHANGELOG and lessons in LEARNINGS, and rerun `evals/evals.json`.
