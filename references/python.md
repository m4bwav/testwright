# Python (pytest)

```
pytest --junitxml=out/junit.xml --durations=20 --reruns 2 --cov=PKG --cov-report=xml:out/coverage.xml
```

- `--reruns` needs pytest-rerunfailures; `--cov` needs pytest-cov. Without them drop the flag and use `TW run --reruns N`.
- `TW parse out/junit.xml`, then `TW changed out/coverage.xml --base origin/main`.
- Characterization: syrupy (`--snapshot-update` only after reading the diff). Property tests: Hypothesis.
- Mutation: mutmut, quality.md.
