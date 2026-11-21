# TypeScript / npm (Vitest, Jest)

- Vitest: `npx vitest run --reporter=json --outputFile=out/vitest.json` (add `--reporter=junit` as a second reporter if CI wants JUnit). Retries `--retry=2`. Coverage `--coverage.enabled --coverage.provider=v8 --coverage.reporter=lcov` gives `coverage/lcov.info` for `TW changed`.
- Jest: `npx jest --json --outputFile=out/jest.json`; coverage `--coverage --coverageReporters=lcov`; retries `jest.retryTimes(n)` in the test file.
- `TW run` uses these; `TW parse out/vitest.json` reads either JSON.
- Check flags against `npx vitest --help` or `npx jest --help` for the installed version before putting them in CI.
- Characterization: `toMatchSnapshot`, `toMatchFileSnapshot`; update with `-u` only after reading the diff. Property tests: fast-check.
- Browser end-to-end is not this plugin: webapp-testing or Playwright.
