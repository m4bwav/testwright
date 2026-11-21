# Suite quality

1. `TW lint <tests>`: never-failing assertions, tests with no assertion, mock-only assertions. Fix each or say why it stays.
2. Mutation testing on changed code only (full runs take hours):
   - .NET: `dotnet stryker --since:main --reporter json --reporter html` (Stryker.NET).
   - JS/TS: `npx stryker run --incremental` (StrykerJS).
   - Python: `mutmut run`, then `mutmut results` (v3 changed its config; read `mutmut --help`).
   Check flags with each tool's `--help` first. Report the mutation score and every surviving mutant in risky code, then write the test that kills it.
3. Unity and Luau: three to five hand mutants in a worktree; each must turn a test red.
4. Flaky tests fail then pass on rerun. Report each with its rerun count, find the cause (time, order, shared state, network, unseeded random, async wait), and quarantine only with a tag the owner can see.
5. Slow tests: `TW slow`. Over a second in a unit suite usually means real I/O or sleeps.
