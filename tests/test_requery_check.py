"""Offline tests for the reproducibility check and the platform collector helpers (no network)."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RequeryCheckTests(unittest.TestCase):
    def setUp(self):
        self.rq = load("requery_check")

    def test_flatten_keeps_numbers_and_skips_lists_and_booleans(self):
        flat = self.rq.flatten({"a": 1, "b": {"c": 2.5, "d": [1, 2], "e": True, "f": "x"}})
        self.assertEqual(flat, {"a": 1, "b/c": 2.5})

    def test_compare_reports_relative_change_and_missing(self):
        rows = {r["metric"]: r for r in self.rq.compare({"a": 100, "b": 0, "c": 5}, {"a": 110, "b": 3, "d": 1})}
        self.assertAlmostEqual(rows["a"]["relative_change"], 0.10)
        self.assertIsNone(rows["b"]["relative_change"])
        self.assertIsNone(rows["c"]["live"])
        self.assertIsNone(rows["d"]["frozen"])
        summary = self.rq.summarize(list(rows.values()))
        self.assertEqual((summary["metrics_compared"], summary["within_5_percent"], summary["within_20_percent"]), (1, 0, 1))

    def test_frozen_files_match_their_manifests(self):
        results = self.rq.check_hashes()
        self.assertGreaterEqual(len(results), 12)
        self.assertTrue(all(r["ok"] for r in results), [r for r in results if not r["ok"]])

    def test_missing_frozen_file_fails_the_check_without_raising(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "present.json").write_text("{}")
            digest = __import__("hashlib").sha256(b"{}").hexdigest()
            manifest = folder / "manifest.json"
            manifest.write_text(json.dumps({"files": {"present.json": digest, "absent.json": digest}}))
            results = {Path(r["file"]).name: r["ok"] for r in self.rq.check_hashes([manifest])}
            self.assertEqual(results, {"present.json": True, "absent.json": False})
            with patch.object(self.rq, "DAS_MANIFEST", manifest):
                self.assertEqual(self.rq.main(["--offline"]), 1)

    def test_offline_mode_makes_no_request(self):
        with patch("urllib.request.urlopen") as urlopen:
            self.assertEqual(self.rq.main(["--offline"]), 0)
            urlopen.assert_not_called()


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.pc = load("platform_readiness_counts")

    def test_queries_keep_ai_terms_out_of_the_simulation_denominator(self):
        for term in ("machine learning", "deep learning", "neural"):
            self.assertNotIn(term, self.pc.SIM)
        self.assertIn("neural operator", self.pc.SURR_ML)

    def test_collector_saves_raw_response_and_hash(self):
        class Response:
            headers = {"Link": None}
            def __init__(self, body): self.body = body
            def read(self): return self.body
            def __enter__(self): return self
            def __exit__(self, *a): return False
        with tempfile.TemporaryDirectory() as temporary:
            c = self.pc.Collector(Path(temporary))
            body = json.dumps({"meta": {"total": 7}}).encode()
            with patch.object(self.pc, "urlopen", return_value=Response(body)), patch.object(self.pc.time, "sleep"):
                self.assertEqual(self.pc.datacite_total(c, "probe", None), 7)
            receipt = c.receipts[0]
            self.assertEqual(receipt["status"], 200)
            self.assertEqual(Path(temporary, receipt["file"]).read_bytes(), body)


if __name__ == "__main__":
    unittest.main()
