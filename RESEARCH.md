# Research

Refresh log for the evergreen unit. Full first pass: [ai-docs/research/2026-11-21-research-pass.md](ai-docs/research/2026-11-21-research-pass.md).

## Search plan
- Per known stack (references/*.md): runner release notes and report-flag changes.
- Across stacks: new or changed runners and JUnit-XML reporters for common languages (Go, Rust, Java/Kotlin, Ruby, PHP, Swift, C/C++), property-based tools (Hypothesis, fast-check, FsCheck, proptest), e2e and API tools (Playwright, Cypress), snapshot and visual testing, performance testing (k6, BenchmarkDotNet), data and pipeline testing (Great Expectations, dbt tests), mutation tools.
- A stack met in use with no reference gets researched then and written to references/<stack>.md.

## R-001 2026-11-21 first pass
Runners and report formats per stack (TRX, NUnit XML, JUnit XML, Jest/Vitest JSON), diff-cover, Stryker.NET, StrykerJS, mutmut, Unity Test Framework batchmode, Roblox jest-lua and TestEZ, characterization testing (Verify, syrupy). Claims that could not be fetch-checked are written as "check with --help" in the references.
