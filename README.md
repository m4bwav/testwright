# testwright

![testwright banner](.github/images/banner.jpg)

Testing for real application code in C#/.NET, Unity, TypeScript/npm, Python and Roblox Luau. A Claude Code plugin with one skill and a standard-library script.

- Plans tests by risk: money, saves, deletes, auth, migrations and parsing first, untested files ranked higher, getters skipped.
- Runs a suite into one summary: failures, flaky tests (failed, then passed on rerun), slow tests, and coverage of the lines you changed.
- Judges whether the tests are any good: assertions that can never fail, tests with no assertion, tests that only check mocks, and mutation testing (Stryker.NET, StrykerJS, mutmut, or hand mutants for Unity and Luau).
- Pins legacy code with characterization tests before a refactor.
- Game testing: play mode, simulated input, seed replays, save/load round trips with old saves, bot playthroughs. Failing bot logs go to logwright.

Not for browser end-to-end tests (use Playwright) or skill evals (evergreen-test).

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
