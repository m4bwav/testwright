import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
import tw  # noqa: E402

FX = HERE / "fixtures"


def run(*args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = tw.main(list(args))
    return code, buf.getvalue()


class Parse(unittest.TestCase):
    def check(self, name, fmt, total, failed, skipped):
        f, tests = tw.parse_file(FX / name)
        s = tw.summarize(tests, f)
        self.assertEqual((s["format"], s["total"], s["failed"], s["skipped"]), (fmt, total, failed, skipped))
        return s

    def test_trx(self):
        s = self.check("sample.trx", "trx", 3, 1, 1)
        self.assertIn("Expected 2", s["failures"][0]["message"])
        self.assertAlmostEqual(s["time"], 1.512)

    def test_nunit(self):
        self.check("nunit.xml", "nunit", 2, 1, 0)

    def test_junit(self):
        s = self.check("junit.xml", "junit", 3, 1, 1)
        self.assertEqual(s["failures"][0]["name"], "test_a.test_bad")

    def test_jest(self):
        self.check("jest.json", "jest", 3, 1, 1)

    def test_parse_cli_exit(self):
        code, out = run("parse", str(FX / "junit.xml"), "--json")
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["passed"], 1)


class Slow(unittest.TestCase):
    def test_order(self):
        code, out = run("slow", str(FX / "nunit.xml"), str(FX / "sample.trx"), "--top", "2")
        self.assertEqual(code, 0)
        self.assertIn("Game.Spawn", out.splitlines()[0])


class Changed(unittest.TestCase):
    def test_diff_and_lcov(self):
        diff = "+++ b/src/calc.ts\n@@ -1,0 +2,2 @@\n"
        self.assertEqual(tw.parse_diff(diff), {"src/calc.ts": {2, 3}})
        _, unc = tw.parse_coverage(FX / "lcov.info")
        self.assertEqual(unc["src/calc.ts"], {2, 3})


class Lint(unittest.TestCase):
    def test_findings(self):
        found = {why for _, why in tw.lint_file(FX / "bad_test.py")}
        self.assertIn("assert True can never fail", found)
        self.assertIn("asserts only on mock calls; checks wiring, not behaviour", found)
        self.assertIn("test has no assertion (passes unless it throws)", found)
        lines = [l for l, _ in tw.lint_file(FX / "bad_test.py")]
        self.assertNotIn(14, lines)  # test_good is clean


class Detect(unittest.TestCase):
    def test_python_and_plan(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "conftest.py").write_text("")
        (d / "shop.py").write_text("def refund(wallet, price):\n    wallet.balance += price\n")
        self.assertEqual(tw.detect(d)[0]["runner"], "pytest")
        code, out = run("plan", str(d), "--json")
        rows = json.loads(out)
        self.assertEqual(rows[0]["file"], "shop.py")
        self.assertFalse(rows[0]["has_test"])


if __name__ == "__main__":
    unittest.main()


class BarePytestDetect(unittest.TestCase):
    def test_bare_test_files_detect_python(self):
        import tempfile
        d = Path(tempfile.mkdtemp())
        (d / "test_x.py").write_text("def test_a():\n    assert 1 == 1\n")
        self.assertEqual([f["stack"] for f in tw.detect(d)], ["python"])
