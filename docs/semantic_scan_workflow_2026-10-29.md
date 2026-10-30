# Semantic-scan workflow for proposal Comment 4

Dated 29 October 2026, updated the same evening after Marine chose the DAS
corpus first. Written after the v0.3.0 toolkit was installed and run end to end
on Marine's laptop (macOS, pixi 0.76.2, Python 3.12.14). It records what runs,
what the proposal comment asks for, what was built for the DAS path, and what
remains. It contains no new scientific result.

## Built on 29 October 2026 (uncommitted)

| Piece | Where | State |
|---|---|---|
| Topic-frame harvest mode | `standalone/literature_study.py` 0.3.0, `frame.kind: topic` | 8 new tests, 40 standalone tests pass |
| DAS topic frame | `standalone/config.das_topic.json` | same filter as the frozen 2026-10-21 counts; dry run 6 queries |
| Abstract-level semantic screen | `tools/ai_readiness/semantic_screen.py`, codebook `semantic_screen_codebook_v0.1.md` | 21 tests pass; no batch submitted |
| Opt-in client environment | pixi env `semantic` (anthropic 1.17.0), extra `.[semantic]`, tasks `das-harvest`, `das-screen-*` | installed, lock updated |
| Keyless harvest, 2020 page 1 | `runs/das_topic_2026-10-29/` (gitignored) | 100 of 118 works; stopped: key needed for page 2 |
| Prepared requests | `runs/das_topic_2026-10-29/semantic/` | 86 requests, 14 works without abstract, estimate below |

Two facts from the live run. OpenAlex rejects `sort=id:asc` (HTTP 400, "id is
not a valid field"); both query builders now sort by `publication_date:asc`,
which works with cursor paging. Keyless requests share one $0.10 daily budget
per network IP, so the remaining 17 pages need Marine's own key in
`OPENALEX_API_KEY`; the tools create none.

Prepare estimate for the 2020 first page, Claude Opus 5.5 at effort medium,
batch prices, 4 characters per token and 1,200 output tokens per paper assumed:

| Quantity | Value |
|---|---|
| System prompt (codebook plus schema) | 1,834 tokens, cached |
| User text, 86 abstracts | 35,628 tokens |
| Batch cost, 86 abstracts | $1.12 |
| Projected batch cost, 1,422 works at the same abstract rate | about $16 |

The output-token assumption dominates and is unmeasured; `pilot --limit 5
--execute` measures it. Of the 100 works, 96 contain the literal phrase; the
first request is a dark-matter paper that mentions DAS, which is what the
`das_used` label is for: the figure's default denominator is abstracts whose
own analysis uses DAS.

## Target

Comment 4 in the proposal's "Documented community need" paragraph asks for
results of the literature semantic-scanning workflow on three quantities:
AI-as-tool use, multimodal-data papers and DAS adoption. The comment says they
could replace the keyword counts in Fig. 2B. Today Fig. 2B is the
worldwide-normalized DAS keyword series from the frozen 21 October 2026 OpenAlex
snapshot (`data/openalex/2026-10-21/`): 118 to 424 articles and reviews, 2020 to
2025, 3.59x.

The repository's own rule stands. A title/abstract label is screening evidence.
Actual use needs full-text evidence bound to a stable paper identity. The plan
therefore has two tiers. An abstract-level semantic screen can cover a whole
frame and gives a validated, labeled proportion. A full-text evidence-gated
review on a probability sample gives the numbers that `ai-readiness report` and
`ai_readiness.plot_report` accept.

## Verified state on 29 October 2026

| Check | Command | Result |
|---|---|---|
| Environment | `pixi install` | default env installed from `pixi.lock` |
| Release hashes | `pixi run verify` | 187 files verified |
| Figure suite | `pixi run check` | 18 tests pass |
| Preferred analysis suite | `pixi run check` | 61 tests pass |
| Standalone suite | `pixi run check` | 32 tests pass |
| Figures | `pixi run figures` | 3 PNGs byte-identical to `reference/`; DAS CSV identical |
| CLI | `pixi run readiness-help` | 9 subcommands, none retrieve |
| Harvester dry run | `pixi run dry-run` | 0 executable queries, 8 unresolved journals |
| Instrument builder | run on a copy in scratch | TXT identical to tracked form, 66 fillable controls |
| Metascience snapshot | 4 test modules, `METASCIENCE_KEYS` unset | 70 tests pass |

Nothing in the working tree changed except this note and the
`docs/frame_resolution_2026-10-29/` folder.

## What exists and what is missing

Exists: a guarded OpenAlex harvester with cursor paging and receipts
(`standalone/literature_study.py`); the identity-bound import, keyword screen,
stratified sampler, annotation template, design-weighted report and plotter
(`tools/ai_readiness/`); a PDF-based semantic coder that drafts readiness
annotations with the Claude API and always marks them pending
(`integration/metascience_support/tools/code_papers.py --task readiness`); the
frozen DAS keyword snapshot; and the legacy keyword co-occurrence series under
`legacy/community_demand/`.

Missing: a frozen source frame; any harvested corpus; an abstract-level semantic
classifier (no module in the repository does this); a human-coded validation
set; reviewed annotations. The semantic scan has never been run on real papers.

## Frame candidates

Read-only OpenAlex source lookups on 29 October 2026, no key, no corpus
retrieved. Raw responses with hashes are in
`docs/frame_resolution_2026-10-29/source_candidates.json` and
`source_sizing.json`. Counts are OpenAlex `type:article` works with
`primary_location.source.id` equal to the listed source, 2016 to 2025. They
depend on OpenAlex type labels and source mapping and are not a frozen frame.

| Journal | Source | ISSN-L | Articles 2016-2025 |
|---|---|---|---|
| JGR Solid Earth | S4210228715 | 2169-9313 | 5,993 |
| Geophysical Journal International | S108821158 | 0956-540X | 5,281 |
| Seismological Research Letters | S183957208 | 0895-0695 | 2,449 |
| Water Resources Research | S204847658 | 0043-1397 | 6,211 |
| Hydrology and Earth System Sciences | S93121129 | 1027-5606 | 3,095 |
| Remote Sensing of Environment | S141808269 | 0034-4257 | 4,770 |
| J. Advances in Modeling Earth Systems | S185824406 | 1942-2466 | 2,082 |
| Geoscientific Model Development | S60406085 | 1991-959X | 3,120 |
| Eight-journal frame (standalone config) | | | 33,001 |
| Geophysical Research Letters | S36624081 | 0094-8276 | 16,549 |
| JGR Atmospheres | S207178839 | 0148-0227 | 8,791 |
| JGR Earth Surface | S4210168721 | 2169-9003 | 1,574 |
| JGR Oceans | S4210200322 | 2169-9275 | 4,917 |
| Earth System Science Data | S106909380 | 1866-3508 | 1,936 |
| Geophysics | S106174089 | 0016-8033 | 4,093 |
| IEEE Trans. Geoscience and Remote Sensing | S111326731 | 0196-2892 | 14,722 |
| Fifteen-journal frame (protocol candidates) | | | 85,583 |

Three things to settle before freezing.

- The Discussions sources of HESS, GMD and ESSD are separate OpenAlex sources and
  were excluded; keep them out, they are preprints.
- The ISSN-L OpenAlex attaches to JGR Atmospheres, 0148-0227, is the historical
  umbrella Journal of Geophysical Research. Its 2016 to 2025 counts look like
  Atmospheres alone, but check a few 2016 works before freezing.
- IEEE TGRS grows from 609 to 2,608 articles per year over the period. A pooled
  trend without the protocol's fixed subfield weights would be an IEEE TGRS
  trend.

At 100 works per page the eight-journal frame is 331 pages and the fifteen-journal
frame is 856 pages. Cursor paging beyond the first page needs an existing
OpenAlex key in `OPENALEX_API_KEY`; the harvester stops otherwise and creates
nothing.

## DAS run, evening of 29 October 2026

Keys loaded from Marine's existing `~/.config/metascience/keys.env` (the
metascience project's key file) into the command environment only; no key was
written to the run folder (checked by search).

| Step | Result |
|---|---|
| Harvest, `runs/das_topic_2026-10-29/` | 18 pages, `frame_complete: true`, 1,423 unique works |
| OpenAlex counts per year, 2020 to 2025 | 118, 137, 194, 238, 312, 425 (2024 and 2025 one higher than the frozen 2026-10-21 snapshot) |
| Prepare, `semantic/` | 1,264 requests, 159 works without abstract |
| Measured input, `count_tokens` on 40 requests | 3,330 tokens per request including the system prompt |
| Pilot, 5 abstracts, Opus 5.5, effort medium | 5 valid labels, $0.046 synchronous, median 152 output tokens |
| Prompt cache in the pilot | 3,651 system tokens written once, read on the other four |

Pilot labels read against the abstracts: the dark-matter paper is `das_used: no`;
two railway papers using a neural network on DAS are `ai_as_method`; a
train-tracking algorithm and a DAS instrument-response study are `none`. All five
agree with a reading of the abstract.

Batch estimate for 1,264 abstracts at batch prices, from pilot usage (454 user
input tokens, 3,651 system tokens, 152 output tokens per request):

| Cache outcome in the batch | Cost |
|---|---|
| System prompt read from cache on every request | about $3.50 |
| No cache hits at all | about $12.30 |

Batch cache hits are best-effort, so the real cost falls between the two. The
`das-screen-submit` task refuses above $40.

## DAS batch results, 29 October 2026 (unvalidated)

Batch `msgbatch_01HdBu5onQdhwxu6adW2ZjqL`, Claude Opus 5.5, effort medium,
prompt hash `fea5a7ac...`, submitted 21:02 UTC, ended 21:16 UTC. All 1,264
requests succeeded; 1,262 passed validation and 2 had rationales over 40 words
(kept as `unclear`). Recorded cost $4.48 at batch prices; 4.59 million input
tokens were read from the prompt cache. Output files are in
`runs/das_topic_2026-10-29/semantic/` (gitignored): `screen_semantic.jsonl`
(SHA256 `1323610c...`), `collect_manifest.json`, `summary.json`, `summary.csv`.

| Year | Works | No abstract | Screen: analysis uses DAS | AI as method among those | Share | Wilson 95% |
|---|---|---|---|---|---|---|
| 2020 | 118 | 18 | 85 | 13 | 15.3% | 9.2 to 24.4% |
| 2021 | 137 | 10 | 98 | 16 | 16.3% | 10.3 to 24.9% |
| 2022 | 193 | 17 | 142 | 26 | 18.3% | 12.8 to 25.5% |
| 2023 | 238 | 25 | 186 | 42 | 22.6% | 17.2 to 29.1% |
| 2024 | 312 | 34 | 243 | 59 | 24.3% | 19.3 to 30.0% |
| 2025 | 425 | 55 | 325 | 93 | 28.6% | 24.0 to 33.8% |

The Wilson intervals cover label sampling only, not classifier error. For
comparison, the keyword co-occurrence share in the frozen snapshot ("machine
learning" or "deep learning" in DAS title/abstract) is 10.2% in 2020 and 16.7%
in 2025; the semantic screen is higher because it also counts named methods
(CNN, U-Net, random forest) without the generic phrase. Of the 249 papers the
screen marks as using DAS with AI as a method, 198 name deep learning, 47
classical ML, 14 a generative model and 3 a foundation model; 22 state ML
without a family (labels can overlap).

Multimodality caution: 120 of the papers with two or more families pair
`seismic_elastic` with `other`, mostly distributed temperature sensing on the
same fiber. That share (15% in 2020, 18% in 2025) depends on whether DTS counts
as a separate family, which the protocol leaves to ontology review. Do not
report it until that is decided.

## Validation, in progress

`validation-sample --n-per-stratum 8 --seed das-validation-2026-10-29` drew 130
abstracts across 22 year x model-label strata (`validation_design.json`). Two
blank spreadsheets are ready: `validation_coder_A.csv` and
`validation_coder_B.csv` in the semantic folder. Each coder, independently and
without opening `screen_semantic.jsonl`:

- reads `semantic_screen_codebook_v0.1.md` and codes from title and abstract only;
- fills `human_ai_role` (ai_as_method, ai_as_subject, none, unclear),
  `human_das_used` (yes, no, unclear), and optionally
  `human_ai_method_families` and `human_measurement_families` as codebook names
  separated by `;`;
- leaves `coder_id` as A or B and uses `notes` for hard cases.

Then the two coders agree on a third file, `validation_adjudicated.csv`, and:

```sh
python -m ai_readiness.semantic_screen validate --out runs/das_topic_2026-10-29/semantic \
  --human validation_adjudicated.csv --human2 validation_coder_B.csv
python -m ai_readiness.semantic_screen aggregate --out runs/das_topic_2026-10-29/semantic_validated \
  --validation runs/das_topic_2026-10-29/semantic/validation_metrics.json
```

`validate` reports unweighted and design-weighted precision and recall (each
coded row weighted by N/n of its stratum, because "none" strata are sampled at
about 1 in 10 to 1 in 30 and unweighted recall would hide misses there). The
second `aggregate` needs `screen_semantic.jsonl` copied into the new folder.
The figure caption uses the weighted values. A draft, watermarked figure is in
`runs/das_topic_2026-10-29/figures/das_ai_method_DRAFT.png`.

## Steps

Steps 3 and 4 are implemented; the commands are in
`tools/ai_readiness/README.md` (semantic screen section) and as pixi tasks.
Steps 1 and 2 (journal frame) are unchanged and wait on the frame decision.

1. Freeze the frame. Copy `standalone/config.example.json`, fill each
   `openalex_source_id` from the table, record the inclusion decision per
   journal, and keep the copy out of Git until the frame is final. Decision
   needed: eight or fifteen journals.
2. Harvest metadata. `python standalone/literature_study.py harvest --config
   <frozen>.json --out runs/<date> --execute --max-pages <n>` with the key set.
   Repeat to resume. The harvester puts no AI or modality keyword in the
   denominator, by design.
3. Harvest the DAS corpus as its own run. The DAS adoption quantity needs a
   topic frame, all articles and reviews matching "distributed acoustic
   sensing" in title or abstract, 2020 to 2025 (1,422 works at the October 21
   snapshot, 18 pages: one query per year, 2+2+2+3+4+5). The harvester refuses keyword-conditioned frames, so
   this needs a small, explicit topic-frame mode that labels the manifest as a
   topic frame rather than a journal frame. Keep the two runs separate.
4. Build the abstract-level semantic screen. A new module, for example
   `tools/ai_readiness/semantic_screen.py`, reads a run's `works.jsonl`, sends
   title plus reconstructed abstract to the Claude API through the Message
   Batches API, and writes one JSONL row per paper with: `ai_role` in
   {ai_as_method, ai_as_subject, none, unclear}; the list of measurement
   families from `protocols/modality_codebook_v0.1.json` and their count;
   `das_used` in {yes, no, unclear}; a one-line rationale; model, prompt hash
   and timestamp. A missing abstract is `unclear`, never negative. Aggregation
   per year reports the share of papers with abstracts, and the missing-abstract
   count beside it. The repository's `screen` command stays keyword-based and
   separate.
5. Validate the screen before any figure. Draw 100 to 200 papers stratified by
   year and screen label. Two human coders label the same fields from the
   abstracts. Report per-label precision, recall and inter-coder agreement.
   Optionally correct the shares for misclassification using the validation
   set and bootstrap the interval. This is the protocol's Gate 3 applied to the
   abstract tier.
6. Run the full-text tier on the probability sample. `ai-readiness import`,
   `sample`, `template`, then annotation (model drafts from PDFs through
   `code_papers.py --task readiness` are optional and stay pending until a named
   reviewer confirms them), then `report` and `plot_report`. This yields the
   design-weighted estimates with intervals. The 240-paper pilot supports
   year-band estimates, not annual curves.

## Figure 2B replacement

Panel A keeps the DAS article counts as activity. Panel B becomes the annual
share of DAS papers whose abstract shows AI used as a method, from the semantic
screen, with the denominator (papers with abstracts) on each point and the
validation precision and recall in the caption. Panel C shows the journal frame:
share of articles using two or more measurement families and share using AI as
a method, by year band from the full-text pilot where available and by year
from the screen otherwise, each labeled with its tier. Points are not connected
across missing years; unknown stays unknown.

## Interim numbers available now

These are keyword co-occurrences from the frozen 21 October 2026 snapshot
(`legacy/community_demand/annual_title_abstract_article_review_counts.csv`),
not a semantic scan. They can stand in Fig. 2B only if labeled as such.

| Year | DAS articles/reviews | with "machine learning" or "deep learning" | Share |
|---|---|---|---|
| 2020 | 118 | 12 | 10.2% |
| 2021 | 137 | 13 | 9.5% |
| 2022 | 194 | 21 | 10.8% |
| 2023 | 238 | 34 | 14.3% |
| 2024 | 311 | 42 | 13.5% |
| 2025 | 424 | 71 | 16.7% |

## Next actions for the DAS path

1. Marine sets `OPENALEX_API_KEY` (her own key) and Claude credentials
   (`ANTHROPIC_API_KEY` or `ant auth login`) in her shell.
2. `pixi run -e semantic das-harvest` finishes the 17 remaining pages into the
   same run folder (resume is automatic; the manifest then says
   `frame_complete: true`).
3. Delete or move `runs/das_topic_2026-10-29/semantic/` (it holds requests for
   the partial corpus) and run `das-screen-prepare` on the complete corpus; read
   the estimate.
4. `das-screen-pilot` on five abstracts; read the labels and the median output
   tokens; adjust the codebook if the labels are wrong, which changes the prompt
   hash and requires a fresh prepare.
5. `das-screen-submit` (refuses above $40 by default), then `das-screen-collect`
   when the batch has ended, then `das-screen-aggregate`.
6. `validation-sample --n-per-stratum 8` gives about 100 to 190 blind abstracts
   across year x label strata; two coders fill the human fields; adjudicate;
   `validate`; `aggregate --validation`; `plot`. Without validation, `plot`
   refuses unless `--draft`.

## Actions before the journal frame (step 2)

- Choose the frame scope and confirm the JGR mapping and the article-only type
  filter.
- Size the classification before submitting: the eight-journal frame is about
  23 times the DAS corpus, so roughly $370 at the DAS estimate above, before the
  pilot's measured output tokens replace the assumption.
