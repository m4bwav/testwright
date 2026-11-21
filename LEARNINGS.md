# Learnings

- L-001 `bare-pytest-not-detected` (2026-11-21): `tw.py detect` needed pytest.ini, conftest.py or pyproject; folders with only test_*.py returned nothing, so agents fell back to raw pytest. Fixed: any test_*.py or *_test.py now detects python.
- L-002 `strong-baseline` (2026-11-21): on small Python fixtures the bare model already reruns flaky tests, spots mock-only asserts, fixes code over tests and writes characterization tests. The skill's gain is the routing (tw.py plan and lint, hand mutants, the never-weaken rules) and the non-Python stacks; small Python cases are regression checks, not proof of value.
