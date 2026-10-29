"""Scientific integrity checks for the frozen DAS activity plot."""

import csv
import hashlib
import importlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from aidatasets_figures import das_activity


class DasActivityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.snapshot = self.root / "snapshot"
        self.snapshot.mkdir()
        self.payloads = {
            das_activity.NUMERATOR_FILE: {
                "group_by": [
                    {"key": str(y), "count": n}
                    for y, n in zip(das_activity.YEARS, (118, 137, 194, 238, 311, 424))
                ],
            },
            das_activity.DENOMINATOR_FILE: {
                "group_by": [
                    {"key": str(y), "count": n}
                    for y, n in zip(das_activity.YEARS,
                                    (6707768, 6257963, 5805839, 6050280, 6495527, 7490116))
                ],
            },
        }
        self.write_snapshot()

    def write_snapshot(self):
        files = {}
        for name, payload in self.payloads.items():
            raw = json.dumps(payload).encode("utf-8")
            (self.snapshot / name).write_bytes(raw)
            files[name] = hashlib.sha256(raw).hexdigest()
        (self.snapshot / "manifest.json").write_text(json.dumps({"files": files}))

    def test_derives_counts_normalization_and_growth_from_raw(self):
        result = das_activity.load_snapshot(self.snapshot)
        self.assertEqual([row["das_articles_reviews"] for row in result["rows"]],
                         [118, 137, 194, 238, 311, 424])
        first, last = result["rows"][0], result["rows"][-1]
        self.assertAlmostEqual(first["das_per_100000_worldwide"], 118 / 6707768 * 100000)
        self.assertAlmostEqual(last["das_per_100000_worldwide"], 424 / 7490116 * 100000)
        self.assertAlmostEqual(result["ratio_counts_2025_over_2020"], 424 / 118)
        self.assertAlmostEqual(result["ratio_normalized_2025_over_2020"],
                               (424 / 7490116) / (118 / 6707768))

    def test_rejects_tampering_to_either_file(self):
        for name in self.payloads:
            with self.subTest(name=name):
                path = self.snapshot / name
                original = path.read_bytes()
                path.write_bytes(original + b"\n")
                with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                    das_activity.load_snapshot(self.snapshot)
                path.write_bytes(original)

    def test_missing_year_is_not_zero(self):
        self.payloads[das_activity.NUMERATOR_FILE]["group_by"].pop()
        self.write_snapshot()
        with self.assertRaisesRegex(ValueError, "missing years"):
            das_activity.load_snapshot(self.snapshot)

    def test_duplicate_and_extra_years_are_rejected(self):
        groups = self.payloads[das_activity.NUMERATOR_FILE]["group_by"]
        groups.append(dict(groups[0]))
        self.write_snapshot()
        with self.assertRaisesRegex(ValueError, "duplicate year"):
            das_activity.load_snapshot(self.snapshot)
        groups[-1] = {"key": "2026", "count": 42}
        self.write_snapshot()
        with self.assertRaisesRegex(ValueError, "unexpected year"):
            das_activity.load_snapshot(self.snapshot)

    def test_invalid_counts_are_rejected(self):
        group = self.payloads[das_activity.NUMERATOR_FILE]["group_by"][1]
        for invalid in (-1, 1.5, True, "194", None):
            with self.subTest(invalid=invalid):
                group["count"] = invalid
                self.write_snapshot()
                with self.assertRaisesRegex(ValueError, "invalid count"):
                    das_activity.load_snapshot(self.snapshot)

    def test_denominator_must_be_positive(self):
        self.payloads[das_activity.DENOMINATOR_FILE]["group_by"][2]["count"] = 0
        self.write_snapshot()
        with self.assertRaisesRegex(ValueError, "denominator must be positive"):
            das_activity.load_snapshot(self.snapshot)

    def test_count_cannot_exceed_denominator(self):
        self.payloads[das_activity.NUMERATOR_FILE]["group_by"][2]["count"] = 9000000
        self.write_snapshot()
        with self.assertRaisesRegex(ValueError, "exceeds worldwide denominator"):
            das_activity.load_snapshot(self.snapshot)

    def test_growth_baseline_must_be_positive(self):
        self.payloads[das_activity.NUMERATOR_FILE]["group_by"][0]["count"] = 0
        self.write_snapshot()
        with self.assertRaisesRegex(ValueError, "2020 DAS count must be positive"):
            das_activity.load_snapshot(self.snapshot)

    def test_hash_manifest_required_for_both_files(self):
        manifest_path = self.snapshot / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        del manifest["files"][das_activity.DENOMINATOR_FILE]
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "missing or invalid SHA256"):
            das_activity.load_snapshot(self.snapshot)

    def test_validation_finishes_before_output_creation(self):
        (self.snapshot / das_activity.DENOMINATOR_FILE).write_text("altered")
        out = self.root / "must-not-exist"
        with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            das_activity.build(out, self.snapshot)
        self.assertFalse(out.exists())

    def test_changed_snapshot_cannot_silently_clip_the_plot(self):
        self.payloads[das_activity.NUMERATOR_FILE]["group_by"][-1]["count"] = 600
        self.write_snapshot()
        out = self.root / "must-not-exist"
        with self.assertRaisesRegex(ValueError, "exceeds the figure axes"):
            das_activity.build(out, self.snapshot)
        self.assertFalse(out.exists())

    def test_import_is_inert(self):
        with mock.patch.object(Path, "write_text", side_effect=AssertionError("write")), \
             mock.patch.object(Path, "write_bytes", side_effect=AssertionError("write")), \
             mock.patch("urllib.request.urlopen", side_effect=AssertionError("network")), \
             mock.patch("subprocess.run", side_effect=AssertionError("subprocess")):
            importlib.reload(das_activity)

    def test_build_outputs_and_semantic_disclaimers(self):
        # Rasterization is exercised by the project's shared renderer tests; this
        # test checks the scientific plot, source series and provenance outputs.
        def fake_render(pdf, png, dpi=300):
            self.assertTrue(Path(pdf).is_file())
            self.assertEqual(dpi, 300)
            Path(png).write_bytes(b"test raster")

        out = self.root / "nested" / "output"
        with mock.patch("aidatasets_figures.rendering.render_png", side_effect=fake_render):
            result = das_activity.build(out, self.snapshot)
        self.assertEqual(set(result["outputs"]), {"svg", "pdf", "png", "csv", "caption", "provenance"})
        for relative in result["outputs"].values():
            self.assertFalse(Path(relative).is_absolute())
            self.assertGreater((out / relative).stat().st_size, 0)
        with (out / result["outputs"]["csv"]).open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[-1]["das_articles_reviews"], "424")
        caption = (out / result["outputs"]["caption"]).read_text()
        self.assertIn("not measures of multimodal AI use", caption)
        self.assertIn("dataset reuse or expressed demand", caption)
        provenance_text = (out / result["outputs"]["provenance"]).read_text()
        self.assertNotIn(str(self.root), provenance_text)
        provenance = json.loads(provenance_text)
        self.assertEqual(set(provenance["raw_sha256"]), set(self.payloads))
        self.assertIn("actual AI use", provenance["not_measured"])
        self.assertIn("Database/search coverage uncertainty", provenance["uncertainty"])
        self.assertIn('width="468"', (out / result["outputs"]["svg"]).read_text())


if __name__ == "__main__":
    unittest.main()
