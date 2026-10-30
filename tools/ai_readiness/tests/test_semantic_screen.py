"""Semantic screen: request building, parsing, collection, aggregation, validation. No network, no client."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from ai_readiness import core, semantic_screen as ss

ROOT = Path(__file__).resolve().parents[3]


def work(n, title, abstract_words, year=2020):
    index = {w: [i] for i, w in enumerate(abstract_words)} if abstract_words else None
    return {"id": f"https://openalex.org/W{n}", "doi": f"https://doi.org/10.9999/w{n}", "display_name": title,
            "publication_year": year, "abstract_inverted_index": index,
            "primary_location": {"source": {"id": "https://openalex.org/S1"}}}


def labels(**override):
    base = {"ai_role": "ai_as_method", "ai_method_families": ["deep_learning"], "measurement_families": ["seismic_elastic"],
            "other_family_note": None, "das_used": "yes", "simulated_only": False, "confidence": "high",
            "rationale": "A convolutional network detects events in DAS strain-rate records."}
    base.update(override)
    return base


def message(text=None, stop_reason="end_turn", model="claude-opus-5-5", output_tokens=300):
    content = [types.SimpleNamespace(type="thinking", thinking=""), types.SimpleNamespace(type="text", text=text or json.dumps(labels()))]
    usage = types.SimpleNamespace(input_tokens=400, output_tokens=output_tokens, cache_creation_input_tokens=0, cache_read_input_tokens=1500)
    return types.SimpleNamespace(content=content, stop_reason=stop_reason, model=model, usage=usage)


class FakeBatches:
    def __init__(self, results, status="ended"):
        self._results, self.status, self.created = results, status, []

    def create(self, requests):
        self.created.append(requests)
        return types.SimpleNamespace(id="msgbatch_fixture", processing_status="in_progress")

    def retrieve(self, batch_id):
        return types.SimpleNamespace(processing_status=self.status, request_counts=types.SimpleNamespace(processing=0, succeeded=1, errored=0, canceled=0, expired=0))

    def results(self, batch_id):
        return iter(self._results)


def fake_client(results, status="ended"):
    batches = FakeBatches(results, status)
    return types.SimpleNamespace(messages=types.SimpleNamespace(batches=batches, create=lambda **kw: message()))


def result(custom_id, kind="succeeded", msg=None, error_message="rate limit"):
    if kind == "succeeded":
        return types.SimpleNamespace(custom_id=custom_id, result=types.SimpleNamespace(type="succeeded", message=msg or message()))
    error = types.SimpleNamespace(error=types.SimpleNamespace(message=error_message))
    return types.SimpleNamespace(custom_id=custom_id, result=types.SimpleNamespace(type=kind, error=error))


class SemanticScreenTests(unittest.TestCase):
    def setUp(self):
        self.works = [work(1, "Deep learning picks on DAS", "We train a convolutional network on distributed acoustic sensing data".split(), 2020),
                      work(2, "A DAS review without an abstract", None, 2020),
                      work(3, "Ambient noise with DAS", "We cross-correlate DAS records to image the shallow crust".split(), 2021)]

    def temp_run(self):
        temporary = tempfile.TemporaryDirectory()
        base = Path(temporary.name)
        works_path = base / "works.jsonl"
        core.write_jsonl(works_path, self.works)
        out = base / "semantic"
        with contextlib.redirect_stdout(io.StringIO()):
            ss.main(["prepare", "--works", str(works_path), "--out", str(out)])
        return temporary, out

    def test_import_does_not_load_the_client(self):
        self.assertNotIn("anthropic", sys.modules)

    def test_schema_families_match_protocol_codebook(self):
        protocol = ROOT / "protocols" / "modality_codebook_v0.1.json"
        if not protocol.exists():
            self.skipTest("protocol codebook not beside the package")
        families = set(json.loads(protocol.read_text())["families"])
        self.assertEqual(families, set(ss.MEASUREMENT_FAMILIES))
        codebook = ss.codebook_text()
        for family in ss.MEASUREMENT_FAMILIES:
            self.assertIn(f"`{family}`", codebook)

    def test_requests_skip_missing_abstracts_and_carry_identity(self):
        requests, missing = ss.build_requests(self.works, "claude-opus-5-5", "medium", 8000)
        self.assertEqual([r["custom_id"] for r in requests], ["W1", "W3"])
        self.assertEqual([m["paper_id"] for m in missing], ["https://openalex.org/W2"])
        params = requests[0]["params"]
        self.assertEqual(params["model"], "claude-opus-5-5")
        self.assertEqual(params["output_config"]["format"]["type"], "json_schema")
        self.assertIn("Abstract: We train a convolutional network", params["messages"][0]["content"][0]["text"])
        self.assertEqual(params["system"][0]["cache_control"], {"type": "ephemeral"})
        self.assertNotIn("thinking", params)

    def test_prompt_hash_is_stable_and_model_specific(self):
        self.assertEqual(ss.prompt_sha256("claude-opus-5-5", "medium"), ss.prompt_sha256("claude-opus-5-5", "medium"))
        self.assertNotEqual(ss.prompt_sha256("claude-opus-5-5", "medium"), ss.prompt_sha256("claude-sonnet-5-5", "medium"))
        self.assertNotEqual(ss.prompt_sha256("claude-opus-5-5", "medium"), ss.prompt_sha256("claude-opus-5-5", "low"))

    def test_duplicate_ids_are_refused(self):
        with self.assertRaises(ValueError):
            ss.build_requests([self.works[0], dict(self.works[0], doi=None)], "claude-opus-5-5", "medium", 8000)

    def test_parse_accepts_valid_and_refuses_invalid_labels(self):
        parsed, reason = ss.parse_labels(json.dumps(labels()))
        self.assertIsNone(reason)
        self.assertEqual(parsed["das_used"], "yes")
        for bad in (json.dumps(labels(ai_role="maybe")), json.dumps(labels(measurement_families=["lidar"])),
                    json.dumps(labels(ai_role="none")), json.dumps(labels(rationale=" ".join(["w"] * 41))),
                    json.dumps(labels(das_used=None)), json.dumps({**labels(), "extra": 1}), "not json", "[]"):
            parsed, reason = ss.parse_labels(bad)
            self.assertIsNone(parsed, bad)
            self.assertTrue(reason)
        parsed, _ = ss.parse_labels(json.dumps(labels(ai_role="none", ai_method_families=[])))
        self.assertEqual(parsed["ai_role"], "none")

    def test_prepare_writes_requests_manifest_and_estimate(self):
        temporary, out = self.temp_run()
        with temporary:
            manifest = core.read_json(out / "prepare_manifest.json")
            self.assertEqual((manifest["works"], manifest["requests"], manifest["missing_abstract"]), (3, 2, 1))
            self.assertEqual(manifest["prompt_sha256"], ss.prompt_sha256("claude-opus-5-5", "medium"))
            self.assertGreater(manifest["estimate"]["usd_batch"], 0)
            self.assertLess(manifest["estimate"]["usd_batch"], manifest["estimate"]["usd_synchronous"])
            self.assertIsNone(manifest["measured_input_tokens"])
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ss.main(["prepare", "--works", str(out.parent / "works.jsonl"), "--out", str(out)]), 2)

    def test_submit_and_pilot_need_execute_and_never_touch_the_client_otherwise(self):
        temporary, out = self.temp_run()
        with temporary, patch.object(ss, "api_client") as client:
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ss.main(["submit", "--out", str(out)]), 2)
                self.assertEqual(ss.main(["pilot", "--out", str(out)]), 2)
            client.assert_not_called()

    def test_submit_records_batch_and_refuses_a_second_submission(self):
        temporary, out = self.temp_run()
        fake = fake_client([])
        modules = {"anthropic.types.message_create_params": types.SimpleNamespace(MessageCreateParamsNonStreaming=dict),
                   "anthropic.types.messages.batch_create_params": types.SimpleNamespace(Request=lambda custom_id, params: {"custom_id": custom_id, "params": params})}
        with temporary, patch.object(ss, "api_client", return_value=fake), patch.dict(sys.modules, modules), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ss.main(["submit", "--out", str(out), "--execute", "--max-usd", "100"]), 0)
            record = core.read_json(out / "batch.json")
            self.assertEqual(record["id"], "msgbatch_fixture")
            self.assertEqual([r["custom_id"] for r in fake.messages.batches.created[0]], ["W1", "W3"])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ss.main(["submit", "--out", str(out), "--execute"]), 2)
                self.assertEqual(len(fake.messages.batches.created), 1)

    def test_submit_respects_max_usd(self):
        temporary, out = self.temp_run()
        with temporary, patch.object(ss, "api_client") as client, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ss.main(["submit", "--out", str(out), "--execute", "--max-usd", "0.0001"]), 2)
            client.assert_not_called()

    def test_collect_keeps_every_paper_and_never_recodes_failures_as_negatives(self):
        temporary, out = self.temp_run()
        core.atomic_json(out / "batch.json", {"id": "msgbatch_fixture", "collected": False})
        results = [result("W1"), result("W3", msg=message(stop_reason="max_tokens"))]
        with temporary, patch.object(ss, "api_client", return_value=fake_client(results)), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ss.main(["collect", "--out", str(out)]), 0)
            rows = {r["paper_id"].rsplit("/", 1)[-1]: r for r in core.read_jsonl(out / "screen_semantic.jsonl")}
            self.assertEqual(set(rows), {"W1", "W2", "W3"})
            self.assertEqual(rows["W1"]["status"], "labeled")
            self.assertEqual(rows["W1"]["ai_role"], "ai_as_method")
            self.assertTrue(rows["W1"]["screen_only"])
            self.assertIsNone(rows["W1"]["actual_use_label"])
            self.assertEqual(rows["W1"]["prompt_sha256"], ss.prompt_sha256("claude-opus-5-5", "medium"))
            self.assertAlmostEqual(rows["W1"]["usd"], (400 * 4 + 300 * 20 + 1500 * 0.2) / 1e6 * 0.5)
            self.assertEqual(rows["W2"]["status"], "missing_abstract")
            self.assertEqual((rows["W2"]["ai_role"], rows["W2"]["das_used"]), ("unclear", "unclear"))
            self.assertEqual(rows["W3"]["status"], "max_tokens")
            self.assertEqual(rows["W3"]["ai_role"], "unclear")
            receipt = core.read_json(out / "collect_manifest.json")
            self.assertEqual(receipt["statuses"], {"labeled": 1, "max_tokens": 1, "missing_abstract": 1})
            self.assertTrue(core.read_json(out / "batch.json")["collected"])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ss.main(["collect", "--out", str(out)]), 2)

    def test_collect_reports_errored_refusal_and_unparsable_results(self):
        temporary, out = self.temp_run()
        core.atomic_json(out / "batch.json", {"id": "msgbatch_fixture", "collected": False})
        results = [result("W1", kind="errored"), result("W3", msg=message(text="{not json", stop_reason="end_turn"))]
        with temporary, patch.object(ss, "api_client", return_value=fake_client(results)), contextlib.redirect_stdout(io.StringIO()):
            ss.main(["collect", "--out", str(out)])
            rows = {r["paper_id"].rsplit("/", 1)[-1]: r for r in core.read_jsonl(out / "screen_semantic.jsonl")}
            self.assertTrue(rows["W1"]["status"].startswith("errored"))
            self.assertEqual(rows["W3"]["status"], "invalid_json")
            self.assertIn("raw_text_sha256", rows["W3"])
            self.assertEqual(rows["W3"]["ai_role"], "unclear")

    def test_collect_waits_while_the_batch_runs(self):
        temporary, out = self.temp_run()
        core.atomic_json(out / "batch.json", {"id": "msgbatch_fixture", "collected": False})
        with temporary, patch.object(ss, "api_client", return_value=fake_client([], status="in_progress")), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(ss.main(["collect", "--out", str(out)]), 0)
            self.assertFalse((out / "screen_semantic.jsonl").exists())

    def test_collect_refuses_a_changed_codebook(self):
        temporary, out = self.temp_run()
        core.atomic_json(out / "batch.json", {"id": "msgbatch_fixture", "collected": False})
        with temporary, patch.object(ss, "codebook_text", return_value="changed"), patch.object(ss, "api_client") as client, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ss.main(["collect", "--out", str(out)]), 2)
            client.assert_not_called()

    def test_wilson_interval_and_shares(self):
        low, high = ss.wilson(1, 4)
        self.assertAlmostEqual(low, 0.0456, places=3)
        self.assertAlmostEqual(high, 0.6994, places=3)
        self.assertIsNone(ss.wilson(0, 0))
        self.assertEqual(ss.share(0, 0)["share"], None)

    def rows_for_summary(self):
        meta = lambda n, year, status="available": {"paper_id": f"https://openalex.org/W{n}", "doi": None, "year": year, "title": "t", "source_id": None, "abstract_status": status}
        h = ss.prompt_sha256("claude-opus-5-5", "medium")
        return [ss.screen_row(meta(1, 2020), labels(), "labeled", model="m", prompt_hash=h),
                ss.screen_row(meta(2, 2020), labels(ai_role="none", ai_method_families=[], das_used="no", measurement_families=["seismic_elastic", "geodetic_position_displacement"]), "labeled", model="m", prompt_hash=h),
                ss.screen_row(meta(3, 2020), labels(ai_role="unclear", das_used="unclear", measurement_families=[]), "labeled", model="m", prompt_hash=h),
                ss.screen_row(meta(4, 2020, "missing"), None, "missing_abstract", model="m", prompt_hash=h),
                ss.screen_row(meta(5, 2021), labels(ai_role="ai_as_subject", ai_method_families=["uncertain"]), "labeled", model="m", prompt_hash=h)]

    def test_summary_denominators_exclude_unclear_and_unlabeled(self):
        years = {y["year"]: y for y in ss.summarize(self.rows_for_summary())}
        y = years[2020]
        self.assertEqual((y["works"], y["abstract_missing"], y["labeled"], y["not_labeled"]), (4, 1, 3, 1))
        self.assertEqual(y["ai_as_method"], {"count": 1, "denominator": 2, "share": 0.5, "wilson95": ss.wilson(1, 2)})
        self.assertEqual(y["ai_role_counts"]["unclear"], 1)
        self.assertEqual(y["das_used"]["denominator"], 2)
        self.assertEqual(y["multimodal_two_or_more_families"], ss.share(1, 2))
        self.assertEqual(y["families_unstated"], 1)
        self.assertEqual(y["deep_learning_among_ai_as_method"], ss.share(1, 1))
        self.assertEqual(y["ai_as_method_among_das_confirmed"], ss.share(1, 1))
        self.assertEqual(years[2021]["ai_as_method"]["share"], 0.0)
        self.assertEqual(years[2021]["ai_as_method_among_das_confirmed"], ss.share(0, 1))

    def test_figure_points_carry_series_and_das_counts(self):
        summary = {"years": ss.summarize(self.rows_for_summary())}
        points = ss.figure_points(summary)
        self.assertEqual((points[0]["series"], points[0]["das_yes"], points[0]["denominator"]), ("ai_as_method_among_das_confirmed", 1, 1))
        self.assertEqual(ss.figure_points(summary, "ai_as_method")[0]["denominator"], 2)
        with self.assertRaises(ValueError):
            ss.figure_points(summary, "unknown")

    def test_aggregate_writes_summary_and_csv_and_refuses_mixed_prompts(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            core.write_jsonl(out / "screen_semantic.jsonl", self.rows_for_summary())
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ss.main(["aggregate", "--out", str(out)]), 0)
            summary = core.read_json(out / "summary.json")
            self.assertFalse(summary["validated"])
            self.assertEqual(len(summary["years"]), 2)
            header, first = (out / "summary.csv").read_text().splitlines()[:2]
            self.assertEqual(first.split(",")[:5], ["2020", "4", "3", "3", "1"])
            self.assertEqual(dict(zip(header.split(","), first.split(",")))["das_confirmed"], "1")
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            rows = self.rows_for_summary()
            rows[0]["prompt_sha256"] = "other"
            core.write_jsonl(out / "screen_semantic.jsonl", rows)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(ss.main(["aggregate", "--out", str(out)]), 2)

    def test_validation_template_is_blind_and_metrics_are_computed(self):
        temporary, out = self.temp_run()
        core.atomic_json(out / "batch.json", {"id": "msgbatch_fixture", "collected": False})
        results = [result("W1"), result("W3", msg=message(text=json.dumps(labels(ai_role="none", ai_method_families=[], das_used="yes"))))]
        with temporary, patch.object(ss, "api_client", return_value=fake_client(results)), contextlib.redirect_stdout(io.StringIO()):
            ss.main(["collect", "--out", str(out)])
            self.assertEqual(ss.main(["validation-sample", "--out", str(out), "--n-per-stratum", "5", "--seed", "s"]), 0)
            template = core.read_jsonl(out / "validation_template.jsonl")
            self.assertEqual(len(template), 2)
            for row in template:
                self.assertNotIn("ai_role", row)
                self.assertIsNone(row["human_ai_role"])
                self.assertIn("abstract", row)
            self.assertEqual(core.read_json(out / "validation_design.json")["sample_size"], 2)
            coded = [dict(template[0], human_ai_role="ai_as_method", human_das_used="yes", human_measurement_families=["seismic_elastic"], coder_id="A"),
                     dict(template[1], human_ai_role="ai_as_method", human_das_used="yes", human_measurement_families=["seismic_elastic"], coder_id="A")]
            core.write_jsonl(out / "coded.jsonl", coded)
            second = [dict(coded[0], coder_id="B"), dict(coded[1], human_ai_role="none", coder_id="B")]
            core.write_jsonl(out / "coded2.jsonl", second)
            self.assertEqual(ss.main(["validate", "--out", str(out), "--human", str(out / "coded.jsonl"), "--human2", str(out / "coded2.jsonl")]), 0)
            metrics = core.read_json(out / "validation_metrics.json")
            self.assertIn("weighted", metrics["ai_role"])
            method = metrics["ai_role"]["per_class"]["ai_as_method"]
            self.assertEqual((method["true_positive"], method["false_negative"], method["false_positive"]), (1, 1, 0))
            self.assertEqual(method["recall"], 0.5)
            self.assertEqual(metrics["ai_role"]["percent_agreement"], 0.5)
            self.assertEqual(metrics["das_used"]["percent_agreement"], 1.0)
            self.assertEqual(metrics["inter_coder"]["ai_role"]["percent_agreement"], 0.5)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ss.main(["aggregate", "--out", str(out), "--validation", str(out / "validation_metrics.json")]), 0)
            self.assertTrue(core.read_json(out / "summary.json")["validated"])
            with patch.object(ss, "render") as render:
                self.assertEqual(ss.main(["plot", "--out", str(out), "--outprefix", str(out / "fig" / "das")]), 0)
                render.assert_called_once()
            try:
                import matplotlib  # noqa: F401
            except ImportError:
                return
            self.assertEqual(ss.main(["plot", "--out", str(out), "--outprefix", str(out / "real" / "das")]), 0)
            caption = (out / "real" / "das.caption.txt").read_text()
            self.assertIn("design-weighted AI-as-method precision 1.00", caption)
            self.assertTrue((out / "real" / "das.png").stat().st_size > 1000)

    def test_weighted_recall_counts_undersampled_misses(self):
        # truth ai_as_method in both rows; model said none on the second, which stands for 10 papers in its stratum
        pairs = [(True, True), (True, False)]
        plain = ss.label_comparison(pairs, (False, True))
        weighted = ss.label_comparison(pairs, (False, True), [1.0, 10.0])
        self.assertEqual(plain["per_class"][True]["recall"], 0.5)
        self.assertAlmostEqual(weighted["weighted"]["per_class"][True]["recall"], 1 / 11)
        self.assertEqual(weighted["per_class"][True]["recall"], 0.5)

    def test_csv_coder_sheet_is_read_with_lists(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "coder.csv"
            path.write_text("paper_id,year,human_ai_role,human_ai_method_families,human_measurement_families,human_das_used,coder_id\n"
                            "https://openalex.org/W1,2020,ai_as_method,deep_learning; classical_ml,seismic_elastic;other,yes,A\n"
                            "https://openalex.org/W3,2021,,,,,A\n", encoding="utf-8")
            rows = ss.read_human(path)
            self.assertEqual(rows[0]["human_ai_method_families"], ["deep_learning", "classical_ml"])
            self.assertEqual(rows[0]["human_measurement_families"], ["seismic_elastic", "other"])
            self.assertEqual(rows[0]["year"], 2020)
            self.assertIsNone(rows[1]["human_ai_role"])

    def test_kappa_matches_hand_computation(self):
        pairs = [("a", "a"), ("a", "b"), ("b", "b"), ("b", "b")]
        expected = 0.5 * 0.25 + 0.5 * 0.75
        self.assertAlmostEqual(ss.kappa(pairs, ("a", "b")), (0.75 - expected) / (1 - expected))
        self.assertIsNone(ss.kappa([], ("a", "b")))

    def test_plot_refuses_unvalidated_summary_without_draft(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary)
            core.write_jsonl(out / "screen_semantic.jsonl", self.rows_for_summary())
            with contextlib.redirect_stdout(io.StringIO()):
                ss.main(["aggregate", "--out", str(out)])
            with patch.object(ss, "render") as render, contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(ss.main(["plot", "--out", str(out), "--outprefix", str(out / "fig")]), 2)
                render.assert_not_called()
                self.assertEqual(ss.main(["plot", "--out", str(out), "--outprefix", str(out / "fig"), "--draft"]), 0)
                self.assertTrue(render.call_args.kwargs["draft"])


if __name__ == "__main__":
    unittest.main()
