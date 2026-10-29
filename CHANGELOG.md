# Unreleased — 2026-10-29

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
