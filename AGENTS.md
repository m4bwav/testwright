# AGENTS.md

Rules for any AI agent working in this repository. `CLAUDE.md` imports this file; `.github/copilot-instructions.md` points here.

## What this is

testwright: one hub skill, `skills/testwright/`. `scripts/tw.py` is the CLI (standard library only), `references/` holds one file per stack plus quality, legacy and games (load one when a step needs it), `evals/` the skill eval suite, `ai-docs/` the notes, plans, log and handoff (start with `ai-docs/HANDOFF.md`).

## Rules

- Python 3.9+, standard library only. UTF-8, LF. Exit 2 is a usage error.
- Every change gets a test: `python -m unittest discover -s tests`.
- Evergreen unit at the root: read `evergreen.json` before editing; changes go in CHANGELOG with the reason, lessons in LEARNINGS.
- A release bumps `.claude-plugin/plugin.json`, `metadata.version` in SKILL.md and CHANGELOG together.
- Plain short sentences, no em dashes, relative links. No AI attribution anywhere.

## Commands

- Tests: `python -m unittest discover -s tests`
- Detect: `python scripts/tw.py detect <repo>`
- Run: `python scripts/tw.py run <repo> --reruns 2`
