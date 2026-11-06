"""Checks that report figures carry their methods and that numerators and denominators match. Offline."""
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/archive_readiness_2026-10-30"
FIELDS = ("Question", "Inputs", "Selection", "Calculation", "Code and output", "Checked", "Does not show")


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = re.sub(r'src="data:image/png;base64,[^"]+"', 'src=""', (ROOT / "docs/report/ai_readiness_solid_earth.html").read_text())

    def test_every_figure_follows_a_complete_method_block(self):
        parts = self.html.split("<figure>")
        self.assertEqual(len(parts) - 1, 12)
        for number, before in enumerate(parts[:-1], start=1):
            tail = before.rstrip()
            self.assertTrue(tail.endswith("</dl></div>"), f"figure {number} has no method block directly before it")
            block = tail[tail.rindex('<div class="method">'):]
            self.assertIn(f"How Figure", block)
            for field in FIELDS:
                self.assertIn(f"<dt>{field}</dt>", block, f"figure {number} lacks {field}")

    def test_withdrawn_claims_appear_only_in_the_change_log(self):
        body = self.html.split("10. Changes from the version")[0]
        for claim in ("The readiness gap is volume", "Method uptake is not the bottleneck", "largest untapped", "six orders of magnitude"):
            self.assertNotIn(claim, body)

    def test_figure_builder_refuses_a_missing_method_field(self):
        report = load("build_report")
        with self.assertRaises(ValueError):
            report.method_block(1, {"question": "q"})


class PairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.arf = load("archive_readiness_figures")
        cls.rows = cls.arf.pairs_table()

    def test_whole_record_copies_are_not_benchmarks(self):
        names = [d["name"] for d in json.loads((DOCS / "benchmarks.json").read_text())["datasets"]]
        self.assertFalse([n for n in names if n.startswith("ARCO")])

    def test_a_share_needs_both_volumes_and_a_lower_bound_marks_it(self):
        for r in self.rows:
            if r["share_percent"] is not None:
                self.assertTrue(r["archive_bytes"] and r["packaged_bytes"], r["row"])
                self.assertEqual(r["share_is_upper_bound"], r["archive_lower_bound"], r["row"])

    def test_labels_do_not_name_one_mission_over_a_multi_mission_denominator(self):
        labels = [r["row"] for r in self.rows]
        self.assertNotIn("SAR: Sentinel-1", labels)
        self.assertNotIn("Optical: Sentinel-2", labels)

    def test_benchmarks_from_other_archives_stay_out_of_the_us_seismic_row(self):
        row = next(r for r in self.rows if r["row"].startswith("Seismology: EarthScope"))
        self.assertNotIn("INSTANCE", row["benchmarks"])
        self.assertNotIn("ETHZ", row["benchmarks"])

    def test_abstract_matched_counts_are_consistent(self):
        counts, _ = self.arf.latest_ml_counts()
        o = counts["openalex"]
        for key in ("all", "earth_env"):
            for year, row in o[f"ml_works_{key}_by_year"].items():
                self.assertLessEqual(row["count"], o[f"works_{key}_by_year"][year]["count"])

    def test_geodesy_hub_count_comes_from_the_data(self):
        hf = json.loads((DOCS / "platform_counts.json").read_text())["hf"]
        self.assertEqual(self.arf.hf_geodesy_count(hf), hf["geodesy_sar"]["per_term"]["insar"] + hf["geodesy_sar"]["per_term"]["gnss"])


class DasCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checks = load("das_screen_checks")
        cls.frozen = json.loads((ROOT / "docs/das_screen_checks_2026-11-06/checks.json").read_text())

    def row(self, das_used, ai_role):
        return {"das_used": das_used, "ai_role": ai_role}

    def test_bounds_count_unknowns_both_ways(self):
        rows = [self.row("yes", "ai_as_method"), self.row("yes", "none"), self.row("no", "none"), self.row("unclear", "unclear"), self.row("yes", "unclear")]
        b = self.checks.share_bounds(rows)
        self.assertEqual((b["known"], b["unknown"], b["das_used_no"]), (2, 2, 1))
        self.assertAlmostEqual(b["point_percent"], 50)
        self.assertAlmostEqual(b["lower_percent"], 25)
        self.assertAlmostEqual(b["upper_percent"], 75)

    def test_frozen_bounds_contain_the_point_estimate(self):
        for b in self.frozen["bounds"]:
            self.assertLessEqual(b["lower_percent"], b["point_percent"])
            self.assertLessEqual(b["point_percent"], b["upper_percent"])

    def test_crosstab_adds_up_on_one_denominator(self):
        for c in self.frozen["keyword_crosstab"]:
            self.assertEqual(c["both"] + c["keyword_only"] + c["screen_only"] + c["neither"], c["population"])

    def test_kappa(self):
        self.assertAlmostEqual(self.checks.cohen_kappa(["a", "b", "a", "b"], ["a", "b", "a", "b"]), 1.0)
        self.assertAlmostEqual(self.checks.cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]), 0.0)

    def test_checks_file_holds_no_abstract_text(self):
        self.assertNotIn("abstract_inverted_index", json.dumps(self.frozen))


class TailCountTests(unittest.TestCase):
    def test_rows_split_into_tested_not_tested_and_unknown(self):
        rows = json.loads((ROOT / "docs/complexity_2026-10-30/power_laws.json").read_text())["rows"]
        geo = [r for r in rows if r["domain"] == "geoscience" and any(r[k] is not None for k in ("value", "value_min", "value_max"))]
        verdicts = [r["tested_vs_alternatives"] for r in geo]
        self.assertEqual(len(geo), 24)
        self.assertEqual(sum(v.startswith("tested") for v in verdicts), 13)
        self.assertEqual(verdicts.count("not tested in this source"), 7)
        self.assertEqual(verdicts.count("not stated"), 4)


if __name__ == "__main__":
    unittest.main()
