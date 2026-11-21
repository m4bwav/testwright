#!/usr/bin/env python3
"""testwright CLI (standard library only).

Commands:
  detect [DIR]                  stacks and runners found in DIR
  parse FILE... [--json]        TRX / NUnit / JUnit XML / Jest-Vitest JSON -> one summary
  run [DIR] [--reruns N]        run the detected suite with report flags, parse, rerun failures
  slow FILE... [--top N]        slowest tests from reports
  changed COVERAGE [--base REF] changed lines without coverage (diff-cover if installed)
  lint PATH...                  tests whose assertions can never fail, tests that only test mocks
  plan [DIR]                    risk-first list of source files worth testing first
Exit codes: 0 ok, 1 failures/findings, 2 usage or tool error.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "bin", "obj", "Library", "Temp", ".venv", "venv",
             "__pycache__", "dist", "build", "Packages", "Logs", "UserSettings"}


def walk(root, max_files=20000):
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            n += 1
            if n > max_files:
                return
            yield Path(dirpath) / f


# ---------- detect ----------
def detect(root):
    root = Path(root)
    found = []
    if (root / "ProjectSettings" / "ProjectVersion.txt").is_file():
        found.append({"stack": "unity", "runner": "unity-test-framework",
                      "cmd": "Unity -batchmode -runTests -testPlatform EditMode -testResults results.xml"})
    names = {p.name for p in walk(root)}
    files = list(walk(root))
    if any(p.suffix in (".csproj", ".sln", ".slnx") for p in files) and not found:
        found.append({"stack": "dotnet", "runner": "dotnet test",
                      "cmd": "dotnet test --logger trx --results-directory TestResults"})
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except ValueError:
            data = {}
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "vitest" in deps:
            found.append({"stack": "js", "runner": "vitest",
                          "cmd": "npx vitest run --reporter=json --outputFile=tw-results.json"})
        elif "jest" in deps:
            found.append({"stack": "js", "runner": "jest",
                          "cmd": "npx jest --json --outputFile=tw-results.json"})
    if names & {"pytest.ini", "conftest.py"} or (root / "pyproject.toml").is_file() and \
            "pytest" in (root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore"):
        found.append({"stack": "python", "runner": "pytest",
                      "cmd": "python -m pytest --junitxml=tw-results.xml"})
    if names & {"default.project.json", "wally.toml"} or any(p.suffix == ".luau" for p in files):
        found.append({"stack": "luau", "runner": "jest-lua or TestEZ (run-in-roblox / Lune)",
                      "cmd": None})
    return found


# ---------- parse ----------
def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _dur(s):
    """TRX duration hh:mm:ss.fffffff -> seconds."""
    if not s:
        return 0.0
    if ":" not in s:
        return _f(s)
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + _f(sec)


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def parse_xml(path):
    root = ET.parse(path).getroot()
    kind = _local(root.tag)
    tests = []
    if kind == "TestRun":  # TRX
        for el in root.iter():
            if _local(el.tag) == "UnitTestResult":
                outcome = el.get("outcome", "")
                status = {"Passed": "passed", "Failed": "failed", "NotExecuted": "skipped"}.get(outcome, outcome.lower())
                msg = ""
                for m in el.iter():
                    if _local(m.tag) == "Message" and m.text:
                        msg = m.text.strip()
                        break
                tests.append({"name": el.get("testName"), "status": status,
                              "time": _dur(el.get("duration")), "message": msg})
        return "trx", tests
    if kind == "test-run":  # NUnit 3 (Unity Test Framework)
        for el in root.iter("test-case"):
            res = el.get("result", "")
            status = {"Passed": "passed", "Failed": "failed", "Skipped": "skipped",
                      "Inconclusive": "skipped"}.get(res, res.lower())
            msg_el = el.find("failure/message")
            tests.append({"name": el.get("fullname") or el.get("name"), "status": status,
                          "time": _f(el.get("duration")),
                          "message": (msg_el.text or "").strip() if msg_el is not None else ""})
        return "nunit", tests
    # JUnit (pytest, jest-junit, many others)
    for el in root.iter("testcase"):
        status, msg = "passed", ""
        for child in el:
            t = _local(child.tag)
            if t in ("failure", "error"):
                status, msg = "failed", (child.get("message") or child.text or "").strip()
            elif t == "skipped":
                status = "skipped"
        name = el.get("name")
        if el.get("classname"):
            name = f"{el.get('classname')}.{name}"
        tests.append({"name": name, "status": status, "time": _f(el.get("time")), "message": msg})
    return "junit", tests


def parse_json(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    tests = []
    for suite in data.get("testResults", []):
        for a in suite.get("assertionResults", []):
            st = a.get("status", "")
            status = {"passed": "passed", "failed": "failed"}.get(st, "skipped")
            tests.append({"name": a.get("fullName") or a.get("title"), "status": status,
                          "time": _f(a.get("duration")) / 1000.0,
                          "message": "\n".join(a.get("failureMessages") or [])[:2000]})
    return "jest", tests


def parse_file(path):
    text = Path(path).read_text(encoding="utf-8", errors="ignore").lstrip()
    if text.startswith("{"):
        return parse_json(path)
    return parse_xml(path)


def summarize(tests, fmt=None):
    s = {"format": fmt, "total": len(tests)}
    for k in ("passed", "failed", "skipped"):
        s[k] = sum(1 for t in tests if t["status"] == k)
    s["time"] = round(sum(t["time"] for t in tests), 3)
    s["failures"] = [{"name": t["name"], "message": t["message"][:500]}
                     for t in tests if t["status"] == "failed"]
    return s


def load_tests(files):
    tests, fmts = [], set()
    for f in files:
        fmt, t = parse_file(f)
        fmts.add(fmt)
        tests += t
    return ",".join(sorted(fmts)), tests


def print_summary(s, as_json):
    if as_json:
        print(json.dumps(s, indent=2))
        return
    print(f"{s['format']}: {s['total']} tests, {s['passed']} passed, {s['failed']} failed, "
          f"{s['skipped']} skipped, {s['time']}s")
    for f in s["failures"]:
        print(f"FAIL {f['name']}\n  {f['message'].splitlines()[0] if f['message'] else ''}")
    for f in s.get("flaky", []):
        print(f"FLAKY {f}")


# ---------- run ----------
def run_suite(root, reruns, as_json):
    stacks = [s for s in detect(root) if s["cmd"] and s["stack"] != "unity"]
    if not stacks:
        print("no runnable suite detected (Unity and Luau: see the skill's references)", file=sys.stderr)
        return 2
    out = Path(tempfile.mkdtemp(prefix="tw-"))
    stack = stacks[0]
    cmd = stack["cmd"].replace("tw-results", str(out / "tw-results")).replace(
        "TestResults", str(out))
    subprocess.run(cmd, shell=True, cwd=root)
    reports = [p for p in out.rglob("*") if p.suffix in (".trx", ".xml", ".json")]
    if not reports:
        print(f"suite ran but wrote no report in {out}", file=sys.stderr)
        return 2
    fmt, tests = load_tests(reports)
    s = summarize(tests, fmt)
    s["stack"], s["command"] = stack["stack"], cmd
    flaky = []
    for _ in range(reruns):
        failed = [t for t in tests if t["status"] == "failed"]
        if not failed:
            break
        rerun = Path(tempfile.mkdtemp(prefix="tw-rerun-"))
        rcmd = stack["cmd"].replace("tw-results", str(rerun / "tw-results")).replace(
            "TestResults", str(rerun))
        subprocess.run(rcmd, shell=True, cwd=root)
        _, again = load_tests([p for p in rerun.rglob("*") if p.suffix in (".trx", ".xml", ".json")])
        passed_now = {t["name"] for t in again if t["status"] == "passed"}
        for t in failed:
            if t["name"] in passed_now:
                flaky.append(t["name"])
                t["status"] = "flaky"
    s["flaky"] = sorted(set(flaky))
    s["failed"] = sum(1 for t in tests if t["status"] == "failed")
    s["failures"] = [f for f in s["failures"] if f["name"] not in s["flaky"]]
    print_summary(s, as_json)
    return 1 if s["failed"] else 0


# ---------- changed ----------
def parse_coverage(path):
    """Return {relative file: set(covered lines), ...}, {file: set(uncovered)} from lcov or Cobertura."""
    cov, unc = {}, {}
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    if text.lstrip().startswith("<"):
        root = ET.fromstring(text)
        for cls in root.iter("class"):
            fn = cls.get("filename", "").replace("\\", "/")
            for ln in cls.iter("line"):
                (cov if int(ln.get("hits", "0")) > 0 else unc).setdefault(fn, set()).add(int(ln.get("number")))
    else:
        fn = None
        for line in text.splitlines():
            if line.startswith("SF:"):
                fn = line[3:].strip().replace("\\", "/")
            elif line.startswith("DA:") and fn:
                n, hits = line[3:].split(",")[:2]
                (cov if int(hits) > 0 else unc).setdefault(fn, set()).add(int(n))
    return cov, unc


def diff_lines(base, cwd):
    out = subprocess.run(["git", "diff", "-U0", base, "--"], cwd=cwd, capture_output=True,
                         text=True, encoding="utf-8", errors="ignore")
    if out.returncode:
        raise SystemExit(f"git diff failed: {out.stderr.strip()}")
    return parse_diff(out.stdout)


def parse_diff(text):
    changed, fn = {}, None
    for line in text.splitlines():
        if line.startswith("+++ "):
            p = line[4:].strip()
            fn = None if p == "/dev/null" else re.sub(r"^b/", "", p)
        elif line.startswith("@@") and fn:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(m.group(1)), int(m.group(2) or 1)
            changed.setdefault(fn, set()).update(range(start, start + count))
    return changed


def changed_report(coverage, base, cwd, as_json):
    if shutil.which("diff-cover"):
        r = subprocess.run(["diff-cover", coverage, f"--compare-branch={base}"], cwd=cwd)
        return r.returncode
    _, unc = parse_coverage(coverage)
    changed = diff_lines(base, cwd)
    miss = {}
    for fn, lines in changed.items():
        for cfn, ulines in unc.items():
            if cfn.endswith(fn) or fn.endswith(cfn):
                hit = sorted(lines & ulines)
                if hit:
                    miss[fn] = hit
    if as_json:
        print(json.dumps(miss, indent=2))
    else:
        if not miss:
            print("every changed, instrumented line is covered")
        for fn, ls in miss.items():
            print(f"{fn}: uncovered changed lines {ls}")
    return 1 if miss else 0


# ---------- slow ----------
def slow(files, top):
    _, tests = load_tests(files)
    for t in sorted(tests, key=lambda t: -t["time"])[:top]:
        print(f"{t['time']:9.3f}s  {t['name']}")
    return 0


# ---------- lint ----------
TEST_FILE = re.compile(r"(test_.*\.py|.*_test\.py|.*\.(test|spec)\.[jt]sx?|.*Tests?\.cs|.*\.spec\.luau)$")
NEVER_FAIL = [
    (re.compile(r"\bassert\s+True\b"), "assert True can never fail"),
    (re.compile(r"Assert\.(?:IsTrue|True)\(\s*true\s*\)"), "Assert.True(true) can never fail"),
    (re.compile(r"Assert\.Pass\(\)"), "Assert.Pass() asserts nothing"),
    (re.compile(r"expect\(\s*true\s*\)\.toBe\(\s*true\s*\)"), "expect(true).toBe(true) can never fail"),
    (re.compile(r"expect\(([^()]+)\)\.(?:toBe|toEqual)\(\s*\1\s*\)"), "compares a value with itself"),
    (re.compile(r"Assert\.(?:AreEqual|Equal)\(\s*([\w.]+)\s*,\s*\1\s*\)"), "compares a value with itself"),
    (re.compile(r"\bassert\s+(\w+)\s*==\s*\1\b"), "compares a value with itself"),
    (re.compile(r"\.(?:toBeDefined|not\.toBeNull)\(\)\s*;?\s*$"), "only checks the value exists"),
    (re.compile(r"Assert\.(?:IsNotNull|NotNull)\("), "only checks the value exists (weak alone)"),
]
MOCK_DEF = re.compile(r"(new Mock<|Substitute\.For<|A\.Fake<|vi\.fn\(|jest\.fn\(|MagicMock\(|Mock\(|mocker\.patch)")
TEST_START = re.compile(r"^\s*(?:def test_\w+|(?:it|test)\s*\(|\[(?:Test|Fact|Theory|UnityTest)[^\]]*\])")
ASSERT_ANY = re.compile(r"\b(assert|Assert\.|expect\(|Verify\(|Should|\.should|Received\(|toHaveBeenCalled|pytest\.raises|Throws)")


def lint_file(path):
    findings = []
    lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    for i, line in enumerate(lines, 1):
        for rx, why in NEVER_FAIL:
            if rx.search(line):
                findings.append((i, why))
                break
    # per-test blocks: no assertion at all, or only mock-call assertions with no real object
    starts = [i for i, l in enumerate(lines) if TEST_START.search(l)]
    starts.append(len(lines))
    for a, b in zip(starts, starts[1:]):
        block = lines[a:b]
        body = "\n".join(block)
        if not ASSERT_ANY.search(body):
            findings.append((a + 1, "test has no assertion (passes unless it throws)"))
            continue
        asserts = [l for l in block if ASSERT_ANY.search(l)]
        if MOCK_DEF.search(body) and asserts and all(
                re.search(r"(Verify\(|Received\(|toHaveBeenCalled|assert_called|called_once)", l) for l in asserts):
            findings.append((a + 1, "asserts only on mock calls; checks wiring, not behaviour"))
    return findings


def lint(paths, as_json):
    out = []
    for p in paths:
        p = Path(p)
        files = [p] if p.is_file() else [f for f in walk(p) if TEST_FILE.match(f.name)]
        for f in files:
            for line, why in lint_file(f):
                out.append({"file": str(f), "line": line, "finding": why})
    if as_json:
        print(json.dumps(out, indent=2))
    else:
        for o in out:
            print(f"{o['file']}:{o['line']}: {o['finding']}")
        print(f"{len(out)} finding(s)")
    return 1 if out else 0


# ---------- plan ----------
RISK = [
    (r"\b(price|payment|money|currency|gold|coins?|purchase|refund|balance|wallet|invoice)\b", 5, "money or economy"),
    (r"\b(save|load|serializ|deserializ|PlayerPrefs|DataStore|persist|migration)\w*", 5, "saves and persistence"),
    (r"\b(delete|remove|drop|truncate|overwrite|rmtree|unlink)\b", 4, "data loss"),
    (r"\b(auth|password|token|permission|secret)\w*", 4, "security"),
    (r"\b(random|seed|Random\.|Math\.random)\b", 2, "randomness (seed it to test)"),
    (r"\b(async|await|Task<|Coroutine|thread|lock)\b", 2, "concurrency"),
    (r"^\s*(public|export)\s", 1, "public surface"),
]
SRC_EXT = {".cs", ".ts", ".tsx", ".js", ".mjs", ".py", ".luau", ".lua"}


def plan(root, top, as_json):
    root = Path(root)
    files = [f for f in walk(root) if f.suffix in SRC_EXT]
    tests = [f for f in files if TEST_FILE.match(f.name) or "test" in str(f.parent).lower()]
    test_text = " ".join(f.stem.lower() for f in tests)
    rows = []
    for f in files:
        if f in tests:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        score, why = 0, []
        for rx, w, label in RISK:
            n = len(re.findall(rx, text, re.I | re.M))
            if n:
                score += w * min(n, 5)
                why.append(label)
        if not score:
            continue
        covered = f.stem.lower() in test_text
        if not covered:
            score *= 2
        rows.append({"file": str(f.relative_to(root)), "score": score, "risks": why,
                     "has_test": covered, "lines": text.count("\n") + 1})
    rows.sort(key=lambda r: -r["score"])
    rows = rows[:top]
    if as_json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            mark = "tested" if r["has_test"] else "NO TEST"
            print(f"{r['score']:4d}  {mark:7s}  {r['file']}  ({', '.join(r['risks'])})")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="tw.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("detect"); p.add_argument("dir", nargs="?", default=".")
    p = sub.add_parser("parse"); p.add_argument("files", nargs="+"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("run"); p.add_argument("dir", nargs="?", default=".")
    p.add_argument("--reruns", type=int, default=0); p.add_argument("--json", action="store_true")
    p = sub.add_parser("slow"); p.add_argument("files", nargs="+"); p.add_argument("--top", type=int, default=10)
    p = sub.add_parser("changed"); p.add_argument("coverage"); p.add_argument("--base", default="origin/main")
    p.add_argument("--dir", default="."); p.add_argument("--json", action="store_true")
    p = sub.add_parser("lint"); p.add_argument("paths", nargs="+"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("plan"); p.add_argument("dir", nargs="?", default=".")
    p.add_argument("--top", type=int, default=15); p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "detect":
            print(json.dumps(detect(a.dir), indent=2)); return 0
        if a.cmd == "parse":
            fmt, tests = load_tests(a.files)
            s = summarize(tests, fmt); print_summary(s, a.json); return 1 if s["failed"] else 0
        if a.cmd == "run":
            return run_suite(a.dir, a.reruns, a.json)
        if a.cmd == "slow":
            return slow(a.files, a.top)
        if a.cmd == "changed":
            return changed_report(a.coverage, a.base, a.dir, a.json)
        if a.cmd == "lint":
            return lint(a.paths, a.json)
        if a.cmd == "plan":
            return plan(a.dir, a.top, a.json)
    except (ET.ParseError, ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
