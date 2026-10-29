# Figure provenance and interpretation — historical October 23 record

## October 23 snapshot versus earlier figures

The October 23 author-base release (PD v14) preserves the October 21 author
document. Its event-linked and readiness images have exactly the same RGB pixels
as the two Python-generated October 20 diagrams; Word recompressed the PNG files.
Their reference pixel SHA256 values are:

- Event-linked: `d0e193e9d51f31faff6c63d867df686ff0fe91832d3136b9b42a3d19971f12f8`
- Readiness: `5e71f1950758c08dd0f31b90f5921576957d5c3d6d9a340473d7f22ed942d665`

The DAS publication-activity graph was prepared October 21 and used in an earlier
draft. It is not embedded in PD v14. It is included here because it was one of
the plots generated during proposal preparation. Neither diagram is a measured
performance result. The third current-PD illustration is author supplied;
no Python source was found, so this package does not claim to regenerate it.

## DAS activity graph

Frozen source: OpenAlex Works API snapshot dated October 21, 2026.

- Years: 2020–2025, inclusive.
- Numerator: OpenAlex works typed article or review, with a title/abstract search
  for the quoted stemmed phrase “distributed acoustic sensing,” across fields.
- Denominator: all indexed articles/reviews worldwide in the same years.
- Plot: numerator counts; a separate panel computes `100000 * numerator / denominator`.
- Raw inputs, query URLs and SHA256 values: `data/openalex/2026-10-21/manifest.json`.
- Numerator counts: 118, 137, 194, 238, 311, 424.

Both raw files must match their manifest hashes. The code derives both annual
series from the responses and rejects missing/duplicate years, invalid counts,
nonpositive denominators and a nonpositive growth baseline. It does not silently
fill missing years with zero or clip values beyond the original graph's axes.
Validation and arithmetic tests use synthetic payloads plus the frozen inputs.

These aggregate counts are not a probability sample, so the graph does not invent
sampling confidence intervals. Search/index coverage uncertainty remains
unquantified. Worldwide normalization is not a geoscience denominator and does
not correct missing abstracts, language coverage, database backfilling, publication
lags or classification errors. Article/review labels are not a peer-review audit.

Live reruns can return different counts. Preserve this snapshot for reproducing
the proposal figure; a new snapshot requires a separately dated release and
reviewed caption/axes. The network is never contacted by the reproduction command.

## Code history and portability changes

Original source paths and hashes are in `provenance/original_source_hashes.json`.
The two original `build_figure_examples.py` functions are now in `conceptual.py`;
the historical `vector_drawing.py` adapter is retained to preserve appearance.
The original DAS builder is refactored as `das_activity.py`. Wrapper scripts with
the familiar builder names remain in `scripts/`.

Changes: explicit output directories and guarded entry points, portable Poppler
discovery, packaged snapshots, both raw-file hash checks, and generated provenance.
The conceptual geometry, all plotted values and semantic limitations are retained.
Version 0.2.0 explicitly redesigns the DAS plot as bars plus a normalized line;
its new artwork is dated October 23 while the data snapshot remains October 21.
The original adapter intentionally approximates a small plotting API; replacing
it with Matplotlib would alter the historical figures.

The wider legacy community-demand scripts are not needed to reproduce these
figures. Version 0.3.0 preserves them separately under `legacy/` for audit.
An old screening assembly assigned judgments by topic/rank; new search rankings
must never inherit those judgments.
The separate `ai_readiness` package binds evidence to stable paper identities and
uses reviewed annotations. Its broad study remains unrun.

## Included and excluded material

Original v0.2 figure bundle included: plotting code, two public aggregate responses, public query metadata,
original generated reference figures/captions, and synthetic study test fixtures.
Excluded: proposal text, budgets, personnel disclosures, email records, unpublished
partner holdings, article PDFs/full text, credentials, caches and Git metadata.

## October 29 expanded package

The root README describes version 0.3.0. Earlier PD labels above identify only
the historical source verification; no current proposal version or figure
placement was inferred from filenames. New components include the standalone
prototype, task-conditioned instrument, proposed protocols and optional
metascience support snapshot. These additions do not turn an unrun literature
review into results. The wider public exploratory inputs are quarantined in
`legacy/`, with their selection/annotation limitations.

`provenance/source_manifest.json` maps copied files to original relative paths
and hashes, with intentional derivative changes recorded. The integration
snapshot records source commit and hashes separately. `SHA256SUMS.txt` verifies
the full prepared release except the checksum file itself.
