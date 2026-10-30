"""Topic-frame harvest mode (synthetic fixtures; no network)."""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import literature_study as study


def topic_config(phrase='"distributed acoustic sensing"', **frame):
    return {"years": {"start": 2020, "end": 2021}, "per_page": 100,
            "frame": dict({"kind": "topic", "topic_search": phrase, "types": ["article", "review"]}, **frame)}


class TopicFrameTests(unittest.TestCase):
    def setUp(self):
        self.works = study.read_jsonl(Path(__file__).parent / "fixtures" / "works.jsonl")

    def test_topic_queries_are_per_year_with_phrase_and_types(self):
        queries, unresolved = study.build_queries(topic_config())
        self.assertEqual(unresolved, [])
        self.assertEqual([q["year"] for q in queries], [2020, 2021])
        for query in queries:
            self.assertIsNone(query["source_id"])
            flt = query["parameters"]["filter"]
            self.assertIn('title_and_abstract.search:"distributed acoustic sensing"', flt)
            self.assertIn("type:article|review", flt)
            self.assertNotIn("primary_location.source.id", flt)
        self.assertEqual(queries[0]["query_id"], "topic_distributed_acoustic_sensing_2020")
        # OpenAlex rejects sort=id (HTTP 400, probed 2026-10-29); publication_date works with cursor paging.
        self.assertEqual(queries[0]["parameters"]["sort"], "publication_date:asc")
        url = study.query_url(queries[0]["parameters"])
        self.assertIn("title_and_abstract.search%3A%22distributed+acoustic+sensing%22", url)

    def test_unquoted_phrase_is_quoted(self):
        queries, _ = study.build_queries(topic_config("distributed acoustic sensing"))
        self.assertIn('search:"distributed acoustic sensing"', queries[0]["parameters"]["filter"])

    def test_ai_terms_in_topic_phrase_are_refused(self):
        for phrase in ('"deep learning"', '"DAS machine learning"', "neural networks for DAS"):
            with self.assertRaises(ValueError):
                study.build_queries(topic_config(phrase))

    def test_invalid_topic_frames_are_refused(self):
        with self.assertRaises(ValueError):
            study.build_queries(topic_config(kind="census"))
        with self.assertRaises(ValueError):
            study.build_queries({"years": {"start": 2020, "end": 2021}, "frame": {"kind": "topic"}})
        with self.assertRaises(ValueError):
            study.build_queries(topic_config(types=["article; drop"]))

    def test_journal_frame_is_default_kind(self):
        config = {"years": {"start": 2020, "end": 2020}, "frame": {"sources": [{"label": "x", "openalex_source_id": "S1"}]}}
        self.assertEqual(study.frame_kind(config), "journal")
        queries, _ = study.build_queries(config)
        self.assertIn("primary_location.source.id:S1", queries[0]["parameters"]["filter"])

    def test_dry_run_plan_declares_topic_denominator(self):
        with tempfile.TemporaryDirectory() as temporary:
            config_path = Path(temporary) / "config.json"
            study.atomic_json(config_path, topic_config())
            buffer = io.StringIO()
            with patch.object(study, "fetch_json") as fetch, contextlib.redirect_stdout(buffer):
                study.main(["harvest", "--config", str(config_path), "--out", str(Path(temporary) / "run")])
            fetch.assert_not_called()
            plan = json.loads(buffer.getvalue())
            self.assertEqual(plan["frame_kind"], "topic")
            self.assertFalse(plan["parameters_contain_no_modality_or_AI_keywords"])
            self.assertTrue(plan["parameters_contain_no_AI_keywords"])

    def test_topic_manifest_is_labeled_and_sample_strata_ignore_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            out, config_path = temporary / "run", temporary / "config.json"
            study.atomic_json(config_path, topic_config())
            args = argparse.Namespace(config=str(config_path), out=str(out), execute=True, max_pages=2)
            responses = [{"meta": {"count": 2, "next_cursor": None}, "results": self.works[:2]},
                         {"meta": {"count": 1, "next_cursor": None}, "results": self.works[2:]}]
            with patch.dict(os.environ, {}, clear=False), patch.object(study, "fetch_json", side_effect=responses), \
                    patch.object(study.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                os.environ.pop("OPENALEX_API_KEY", None)
                study.harvest(args)
            manifest = study.read_json(out / "manifest.json")
            self.assertEqual(manifest["frame_kind"], "topic")
            self.assertEqual(manifest["topic_search"], '"distributed acoustic sensing"')
            self.assertTrue(manifest["frame_complete"])
            self.assertIn("not a journal census", manifest["population"])
            screen_path, sample_path, design_path = temporary / "screen.jsonl", temporary / "sample.jsonl", temporary / "design.json"
            study.screen(argparse.Namespace(input=str(out / "works.jsonl"), out=str(screen_path)))
            study.sample(argparse.Namespace(input=str(screen_path), manifest=str(out / "manifest.json"),
                                            out=str(sample_path), design=str(design_path), n_per_stratum=2, seed="s"))
            design = study.read_json(design_path)
            self.assertEqual(design["frame_kind"], "topic")
            for stratum in design["strata"]:
                self.assertEqual(stratum["sampling_stratum"].split("|")[1], "topic")
            self.assertIn("not a journal census", design["scope"])

    def test_first_page_without_key_stops_before_second_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            out, config_path = temporary / "run", temporary / "config.json"
            study.atomic_json(config_path, topic_config())
            args = argparse.Namespace(config=str(config_path), out=str(out), execute=True, max_pages=5)
            responses = [{"meta": {"count": 3, "next_cursor": "more"}, "results": self.works[:2]},
                         {"meta": {"count": 1, "next_cursor": None}, "results": self.works[2:]}]
            with patch.dict(os.environ, {}, clear=False), patch.object(study, "fetch_json", side_effect=responses) as fetch, \
                    patch.object(study.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                os.environ.pop("OPENALEX_API_KEY", None)
                study.harvest(args)
            manifest = study.read_json(out / "manifest.json")
            self.assertFalse(manifest["frame_complete"])
            self.assertFalse(manifest["population_claim_allowed"])
            self.assertIn("key", manifest["stop_reason"])
            self.assertEqual(fetch.call_count, 1)


if __name__ == "__main__":
    unittest.main()
