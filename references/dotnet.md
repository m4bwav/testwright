# .NET (dotnet test)

- VSTest mode: `dotnet test --logger "trx;LogFileName=r.trx" --results-directory out`, then `TW parse out/r.trx`.
- Microsoft.Testing.Platform (MTP): needs Microsoft.Testing.Extensions.TrxReport. In VSTest mode pass after `--`: `dotnet test -- --report-trx`. On the .NET 10 SDK with global.json `"test": {"runner": "Microsoft.Testing.Platform"}`, use `dotnet test --report-trx`; `--logger` is then ignored without an error. Sources: https://learn.microsoft.com/dotnet/core/testing/unit-testing-with-dotnet-test and https://learn.microsoft.com/dotnet/core/testing/migrating-vstest-microsoft-testing-platform (checked 2026-11-21).
- xUnit v3 on MTP (`<UseMicrosoftTestingPlatformRunner>true</UseMicrosoftTestingPlatformRunner>`): `--report-xunit-trx`, file name only, no path. https://xunit.net/docs/getting-started/v3/microsoft-testing-platform (checked).
- Coverage: coverlet.collector `--collect:"XPlat Code Coverage"` gives Cobertura; MTP uses Microsoft.Testing.Extensions.CodeCoverage. Feed the Cobertura file to `TW changed`; reportgenerator merges several files. Check flags with `dotnet test --help` before relying on them.
- Retries: the MTP Retry extension (check its flag on the project), else `TW run --reruns N`.
- Characterization: Verify (`*.verified.*` files committed next to the tests). Property tests: FsCheck or CsCheck.
- Mutation: quality.md.
