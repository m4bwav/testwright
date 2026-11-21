# testwright

![testwright banner](.github/images/banner.jpg)

Testing for any code in any language or stack, and any kind of test: unit, integration, end-to-end, API, property-based, mutation, snapshot and visual, performance, data and pipeline, game, manual and exploratory. A Claude Code plugin with one skill and a standard-library script.

The method works anywhere; stack knowledge grows. It already knows C#/.NET, Unity, TypeScript/npm, Python and Roblox Luau. When it meets a stack it has no notes for, it researches the runner and report format and writes a new reference, so the next run starts from there.

- Plans tests by risk: money, saves, deletes, auth, migrations and parsing first, untested files ranked higher, getters skipped.
- Runs a suite into one summary: failures, flaky tests (failed, then passed on rerun), slow tests, and coverage of the lines you changed.
- Judges whether the tests are any good: assertions that can never fail, tests with no assertion, tests that only check mocks, and mutation testing (Stryker.NET, StrykerJS, mutmut, or hand mutants for Unity and Luau).
- Pins legacy code with characterization tests before a refactor.
- Learns new stacks: `tw.py detect` reports `unknown`, and the skill adds `references/<stack>.md` plus a learning.
- Game testing: play mode, simulated input, seed replays, save/load round trips with old saves, bot playthroughs. Failing bot logs go to logwright.

Not for skill evals (evergreen-test).

## Install

Clone the repo and add its parent folder as a local Claude Code marketplace, or copy `skills/testwright` and `scripts/` into your own plugin.

## Use

Ask in plain words: "what should I test in this repo", "run the tests and tell me what failed", "are my tests any good", "coverage on my diff", "add tests before I refactor this", "test my Unity game". The script also runs on its own:

```
python scripts/tw.py plan path/to/repo
python scripts/tw.py run path/to/repo --reruns 2
python scripts/tw.py parse TestResults/*.trx
python scripts/tw.py slow results.xml --top 10
python scripts/tw.py changed coverage.xml --base origin/main
python scripts/tw.py lint tests/
```

Python 3.9 or later, standard library only. diff-cover is used when installed.

## License

MIT
