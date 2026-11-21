# testwright research pass (2026-11-21)

Scope: what exists already, runner output flags per stack, changed-line coverage, mutation and property testing, flaky and approval testing, game testing. "Checked" means a primary page was seen in this pass (search result from the vendor's docs, 2026-11-21). "From memory" means stated from prior knowledge and not re-fetched; verify before shipping it in a script.

## 1. Existing agent skills, plugins and MCP servers

| Thing | What it covers | Overlap with testwright |
|---|---|---|
| anthropics/skills `webapp-testing` (https://github.com/anthropics/skills, mirrors e.g. https://mcpservers.org/agent-skills/anthropic/webapp-testing, checked) | Python Playwright scripts against a local web app, server lifecycle helper, console log capture | Browser E2E only. No unit runners, coverage, mutation. Point to it, do not duplicate. |
| Playwright MCP (microsoft/playwright-mcp, from memory) | Browser driving by accessibility snapshot; Playwright test agents (planner/generator/healer) ship with Playwright 1.56+ (from memory) | Web E2E generation and healing. Skip that lane. |
| Trail of Bits mutation-testing skill (https://trailofbits.com/skills/mutation-testing/, checked) | Routes to mutation workflows (mewt/muton), loads references | Mutation only, its own engines; not Stryker/mutmut wiring per stack. |
| Community mutation skills: claude-code-plugins-plus-skills "Running Mutation Tests" (https://tessl.io/registry/skills/github/jeremylongshore/claude-code-plugins-plus-skills/Running%20Mutation%20Tests), laurigates/claude-plugins (https://skills.sh/laurigates/claude-plugins/mutation-testing), chrisallenlane test-mutation (https://www.claudepluginhub.com/skills/chrisallenlane-claude-swe-workflows/test-mutation), checked as listings | Wrap Stryker/mutmut/PITest or have the model act as mutator; one writes tests for survivors | Tessl reviews rate several as conceptual with no concrete commands. Low quality bar; no game stacks. |
| awesome-claude-code lists and plugin hubs (claudepluginhub.com, skills.sh) | Many "test generator", "TDD", "coverage" skills | Generic, prompt-only, JS/Python biased. |
| Unity MCP servers (CoplayDev unity-mcp, Unity's own AI assistant MCP; from memory) | Can trigger Test Runner runs from the editor | Run trigger only; no failure triage, flaky reruns, coverage diff. Mark's own unity-agent skills also cover CLI runs. |
| robloxstudio-mcp (https://www.mintlify.com/code-and-relax/robloxstudio-mcp/development/testing, seen) | Studio control incl. running code | No test reporting layer. |

Gaps nobody covers (as far as this pass found): one risk-first planner across .NET/Unity/TS/Python/Luau; one normalised result format (failures, flaky, slow, changed-line coverage) across all five; "assertions that never fail" detection; characterization-test workflow for legacy code; game testing (bot playthroughs, save/load round trip, seed replay, Unity play-mode input).

## 2. Runners and machine-readable output

### .NET
- VSTest mode: `dotnet test --logger "trx;LogFileName=r.trx" --results-directory out` ; JUnit via JunitXml.TestLogger package `--logger "junit;LogFilePath=..."` (from memory).
- Microsoft.Testing.Platform (MTP): `--report-trx` needs package Microsoft.Testing.Extensions.TrxReport. In VSTest mode pass after `--`: `dotnet test -- --report-trx`. On .NET 10 SDK opt in via global.json `"test": {"runner": "Microsoft.Testing.Platform"}`, then `dotnet test --report-trx` and VSTest `--logger` is silently ignored. Source: https://learn.microsoft.com/dotnet/core/testing/unit-testing-with-dotnet-test and https://learn.microsoft.com/dotnet/core/testing/migrating-vstest-microsoft-testing-platform (checked), https://devblogs.microsoft.com/dotnet/dotnet-test-with-mtp/ (2025-08-21).
- xUnit v3: MTP via `<UseMicrosoftTestingPlatformRunner>true</UseMicrosoftTestingPlatformRunner>`; own flags `--report-xunit-trx`, also `--report-xunit` / `--report-junit` style reports; filename only, no path. https://xunit.net/docs/getting-started/v3/microsoft-testing-platform (checked, page dated 2024).
- MTP retries: Microsoft.Testing.Extensions.Retry `--retry-failed-tests 3` (from memory). Coverage: Microsoft.Testing.Extensions.CodeCoverage `--coverage --coverage-output-format cobertura`; or coverlet.collector `--collect:"XPlat Code Coverage"` (VSTest).
- NUnit: NUnit3TestAdapter, TRX via logger; NUnit console `--result=r.xml` (NUnit3 XML). Supports MTP via `EnableNUnitRunner` (from memory).
- Slow tests: TRX has per-test `duration`; parse it.

### Unity Test Framework
`Unity.exe -batchmode -projectPath P -runTests -testPlatform PlayMode -testResults out/results.xml -logFile out/log.txt [-testFilter "Ns.Class;!Ns.Skip"] [-testCategory ...]`. Results are NUnit 3 XML. Do not pass `-quit` with `-runTests`. Default platform EditMode; a build target name runs player tests. Sources: https://docs.unity3d.com/Manual/test-framework/reference-command-line.html (6.2), https://docs.unity3d.com/Packages/com.unity.test-framework@2.0/manual/reference-command-line.html (checked). Exit codes are not uniform: parse the XML. Coverage: com.unity.testtools.codecoverage `-enableCodeCoverage -coverageResultsPath ... -coverageOptions "generateAdditionalMetrics;generateHtmlReport"` (from memory; outputs OpenCover XML, feed to reportgenerator).

### TypeScript / npm
- Vitest: `vitest run --reporter=json --outputFile=out/vitest.json` or `--reporter=junit --outputFile=out/junit.xml` (multiple reporters allowed); coverage `--coverage.enabled --coverage.provider=v8 --coverage.reporter=lcov --coverage.reporter=json-summary`; retries `--retry=2`; Vitest reports slow tests by threshold `slowTestThreshold` (from memory, docs https://vitest.dev/guide/reporters).
- Jest: `jest --json --outputFile=out/jest.json`; JUnit via jest-junit (`--reporters=default --reporters=jest-junit`, env JEST_JUNIT_OUTPUT_FILE); coverage `--coverage --coverageProvider=v8 --coverageReporters=lcov`; retries via `jest.retryTimes(n)` with jest-circus (from memory).

### Python
`pytest --junitxml=out/junit.xml --durations=20 -p rerunfailures --reruns 2 --reruns-delay 1 --cov=pkg --cov-report=xml:out/coverage.xml --cov-report=json:out/coverage.json` (pytest-cov; or `coverage run -m pytest` then `coverage json`/`coverage xml`). pytest-rerunfailures (MPL-2.0) marks reruns in junit output. pytest-json-report gives JSON (from memory).

### Roblox Luau
- TestEZ (Roblox/TestEZ, https://github.com/Roblox/TestEZ): legacy; status codes Success/Failure/Skipped from the results tree, you print your own summary. Roblox moved to Jest.
- Jest Roblox (https://roblox.github.io/jest-roblox-internal, checked): `Jest.runCLI(root, {ci=true, ...}, projects)` returns results with numFailedTests etc.; needs jest.config.lua; officially run with roblox-cli (not public to most). Community jsdotlua/jest-lua (https://github.com/jsdotlua/jest-lua) runs via run-in-roblox (needs Studio on the machine).
- Open Cloud Luau Execution API (https://create.roblox.com/docs/cloud/reference/features/luau-execution.md, checked): headless run against a place version, full DataModel, 5 min limit, 10 tasks per place, scope `universe.place.luau-execution-session:write`. Reference CI repo Roblox/place-ci-cd-demo is archived. Rate limit figures conflict (45/min vs 5/min). Best CI route without Studio.
- Lune: pure-logic tests only (no engine APIs). Output: emit JSON yourself from runCLI results; no standard JUnit.

## 3. Changed-line coverage
- diff-cover (Apache-2.0, https://pypi.org/project/diff_cover, README https://sources.debian.org/src/diff-cover/10.2.0-1/README.rst, checked): reads Cobertura XML, Clover, JaCoCo, or lcov.info; `diff-cover coverage.xml --compare-branch=origin/main --fail-under=80 --json-report out/diff.json` (json/markdown/html report flags from memory). Path mismatch is the usual "no lines" cause. Works for every stack once coverage is Cobertura or lcov, so testwright should wrap it, not rebuild it.
- coverlet (MIT): `--collect:"XPlat Code Coverage"` -> cobertura; reportgenerator (Apache-2.0) merges/convert (`-reporttypes:Cobertura;lcov;JsonSummary`). Unity OpenCover -> reportgenerator -> Cobertura -> diff-cover.
- Istanbul/V8: Vitest/Jest lcov output -> diff-cover.

## 4. Mutation and property-based testing (licences from memory unless noted)
- Stryker.NET (Apache-2.0): `dotnet stryker --since:main --reporter json --reporter html`; `--since` limits to changed code.
- StrykerJS (Apache-2.0): `npx stryker run --incremental`, mutation-testing-elements JSON report schema shared across Stryker.
- mutmut (BSD-3): `mutmut run`, `mutmut results`; v3 rewrote config.
- cosmic-ray (MIT): session db, `cosmic-ray init/exec/cr-report`.
- No maintained Luau or Unity mutation tool found; Stryker.NET does not run inside Unity's compile pipeline (would need code outside Unity assemblies). Gap: LLM-driven mutants for Luau/Unity.
- Property-based: FsCheck (BSD-3), CsCheck (Apache-2.0), fast-check (MIT), Hypothesis (MPL-2.0). Luau: none mature.

## 5. Flaky, approval, legacy
- Flaky conventions: rerun failed tests N times, a test that fails then passes is "flaky" (pytest-rerunfailures marks `rerun`; MTP Retry; Vitest `--retry`, reports retryCount; Jest retryTimes). Quarantine with a tag/category, track per-test pass rate over runs (Google's "Flaky tests at Google" practice). Store history to compute rates; no runner keeps history.
- Approval/golden: Verify (.NET, MIT, `*.verified.*` files, https://github.com/VerifyTests/Verify), ApprovalTests (Apache-2.0, .NET/Java/Python/JS), syrupy (pytest, Apache-2.0, `--snapshot-update`), Vitest/Jest snapshots (`toMatchSnapshot`, `toMatchFileSnapshot`, `-u`). Jest Roblox has snapshots too.
- Feathers (Working Effectively with Legacy Code, 2004): legacy code is code without tests. Change it with the legacy change algorithm: find change points, find test points, break dependencies, write tests, then change and refactor. Characterization tests pin what the code does now (not what it should do) by asserting on observed output. Break dependencies at seams (object seams via extract interface/subclass-and-override, link and preprocessing seams), use sprout method/class and wrap method/class to add new tested code without touching untested code, and scratch refactoring to learn. Approval tools make characterization cheap.

## 6. Game testing
- Unity Test Framework play mode: `[UnityTest]` IEnumerator tests yield frames (`yield return null`, `WaitForSeconds`), load scenes with `SceneManager.LoadSceneAsync`, `[UnitySetUp]`/`[UnityTearDown]`; run headless with `-batchmode` (`-nographics` breaks rendering-dependent tests). Docs above.
- Input System test fixture (https://docs.unity3d.com/Packages/com.unity.inputsystem@1.20/manual/Testing.html, API https://docs.unity3d.com/Packages/com.unity.inputsystem@1.8/api/UnityEngine.InputSystem.InputTestFixture.html, checked): derive from InputTestFixture, `InputSystem.AddDevice<Keyboard>()`, `Press/Release/PressAndRelease/Set/Trigger`; multi-frame play mode tests process input in the player loop; add the package to `testables` in manifest; custom layouts must be registered in setup.
- Deterministic seeds: route all randomness through one seeded RNG (System.Random / Unity.Mathematics.Random / Luau `Random.new(seed)`), fixed timestep, log seed on failure, replay test = same seed + recorded inputs -> same state hash.
- Save/load round trip: generate state (property-based or seeded), save, load, compare (deep equality or Verify snapshot of serialized form), plus load old fixture saves (golden files per save version) for migration.
- Bot playthroughs: scripted or random-walk agents drive input (InputTestFixture or a game-level command API), assert invariants (no exceptions in log, no softlock = progress within N seconds, FPS floor), Unity ML-Agents for learned agents (heavy). Industry: monkey/smoke bots for crash finding (e.g. talks at GDC on automated playtesting, from memory). Pair with logwright for log triage.

## Redundancy calls
- diff-cover makes a custom changed-line coverage engine redundant: normalise to Cobertura/lcov and call it.
- Stryker (.NET, JS), mutmut make own mutation engines redundant there; only Luau/Unity need LLM mutants.
- webapp-testing / Playwright MCP make a browser E2E lane redundant.
- Nothing found that makes the planner, cross-stack report, never-failing assertion check, characterization workflow, or game-testing lane redundant.
