# Unreleased — 2026-10-29

- Standalone harvester 0.3.0: `frame.kind: "topic"` harvests a quoted
  title/abstract phrase per year (AI/ML terms refused in the phrase); manifests,
  plans and sample designs label the frame kind and population. Added
  `standalone/config.das_topic.json`, the DAS topic frame for Comment 4.
- New `ai_readiness.semantic_screen`: abstract-level semantic screen through the
  Claude API Message Batches (prepare, pilot, submit, collect, aggregate,
  validation-sample, validate, plot) with `semantic_screen_codebook_v0.1.md`.
  Rows are screening evidence with model, prompt hash and cost recorded; missing
  abstracts and failed answers stay `unclear`. The client is imported only by
  the commands that call it; `pilot` and `submit` need `--execute`.
- Optional `semantic` extra and pixi environment (anthropic 1.x) with DAS tasks;
  the default environment is unchanged.
- Ran the DAS path on 29 October 2026: 1,423 works harvested, 1,264 abstracts
  screened (batch msgbatch_01HdBu5onQdhwxu6adW2ZjqL, $4.48). Results are
  unvalidated and live in the gitignored `runs/` folder; the summary and the
  validation instructions are in `docs/semantic_scan_workflow_2026-10-29.md`.
- `validate` reads coder spreadsheets (CSV) and reports design-weighted
  precision and recall.
- Added `scripts/explore_das_semantic.py`, four exploratory draft plots of the
  DAS screen.
- Added a pixi environment (`pixi.toml`, `pixi.lock`) for macOS and Linux with
  tasks for verification, the offline test suites, figures, the instrument
  builder and the standalone dry run. Poppler is now provided by the environment.
- Continuous integration runs through pixi.
- README updated with pixi instructions and the repository location.
- SHA256SUMS regenerated to cover the new and edited files. Analysis code,
  frozen inputs and reference figures are unchanged.

# 0.3.0 — 2026-10-29

- Repackaged all identified AI-readiness analysis components: current metascience
  extension, standalone harvester, task-conditioned instrument/builder, original
  protocol, optional retrieval/semantic support and historical exploratory code.
- Added source manifests, clear executed/planned/historical boundaries, offline
  verification commands and fresh validation. No new scientific result generated.
- Both figure and readiness modules now install from the root pyproject, with
  command-line entry points; the core analysis modules remain unchanged.
- Software distribution renamed geoscience-ai-readiness; figure module name kept.
- Updated release citation metadata without inventing a DOI or repository URL.
- No author proposal document, source repository, private corpus, credentials or
  partner inventory modified or included.

# Changelog

## 0.2.0 — 2026-10-23

- Redesign DAS absolute counts as bars and worldwide-normalized activity as a line.
- Add explicit units, compact headings and readable direct values.
- Retain all six frozen annual observations, source hashes and zero baselines.
- Preserve version 0.1.0 reference artwork and the original release ZIP.

## 0.1.0 — 2026-10-23

- Collect the October 20 conceptual figure generators and October 21 DAS activity
  generator with their frozen aggregate inputs and reference outputs.
- Add a portable offline CLI, Python project metadata, citation files and CI.
- Validate both OpenAlex raw-data hashes and reject missing/invalid series.
- Include the 16 unchanged `ai_readiness` study files and their synthetic tests.
- Record which figures appear in PD v14 and which are historical or unrun.

This is a prepared local release, not a claim of public GitHub/Zenodo publication.
