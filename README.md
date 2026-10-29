# Geoscience AI-readiness research toolkit

**Version 0.3.0 · October 29, 2026** · Marine Denolle, University of Washington.

Collected code used or prepared for the proposal's investigation of data
readiness, multimodal research and AI adoption. Includes the metascience analysis
extension, an earlier retrieval prototype, task-conditioned readiness instrument,
historical analyses, plotting code, frozen public inputs and reference figures.
This is a repository-ready package; it does not publish a repository or launch
a literature study.

**Evidence status:** the completed quantitative result is a frozen OpenAlex DAS
publication-activity series. The broader multimodality/AI/deep-learning/foundation-
model review **has not been run on a reviewed corpus**. No measured field-wide
AI-readiness score or adoption trend is supplied. Test fixtures are synthetic.

## Contents

| Location | Purpose and status |
|---|---|
| `tools/ai_readiness/` | Preferred analysis for existing literature records: identity-bound sampling, annotations, evidence-gated reports, endpoint comparisons and plots. Matches the current metascience snapshot. |
| `standalone/` | Earlier standard-library harvest/sample/report prototype. Retrieval is opt-in; example source IDs are unresolved. Separate schema and runs from the preferred workflow. |
| `instrument/` | Task-conditioned readiness rubric, Word/text forms and Python builder. Research instrument, not a validated universal score. |
| `src/aidatasets_figures/` | Offline figure generators: revised DAS graph and two labeled conceptual schematics. |
| `data/`, `reference/` | Frozen DAS inputs, query hashes and dated reference exports. |
| `protocols/` | Proposed study design/codebook; some planned analyses remain unimplemented. |
| `integration/metascience_support/` | Optional retrieval/semantic-coding snapshot with its own provenance. Not installed/run by default. |
| `legacy/` | Original exploratory analysis and targeted evidence assembler, preserved for audit, not new inference. |
| `provenance/`, `docs/` | Source hashes, interpretation, status and validation receipts. |

## Install and reproduce the completed figure

The recommended environment is managed with [pixi](https://pixi.sh). The
manifest `pixi.toml` and lock file `pixi.lock` pin Python 3.12, NumPy, ReportLab,
Pillow, Poppler (for `pdftoppm`), Matplotlib and python-docx from conda-forge for
macOS (Apple silicon and Intel) and Linux (x86-64 and aarch64), and install this
package in editable mode.

```sh
pixi install          # create the environment from pixi.lock
pixi run all          # verify hashes, run the three offline test suites, rebuild figures
pixi run figures      # figures only, written to build/figures
pixi task list        # other tasks: check, verify, instrument, dry-run, readiness-help
```

`pixi shell` opens a shell with the commands `aidatasets-figures` and
`ai-readiness` on the path. A smaller environment without Matplotlib and
python-docx is available as `pixi run -e core figures`.

Without pixi, use Python 3.10+ and install Poppler (`pdftoppm`) through your
system package manager, or set `PDFTOPPM` to its executable:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install .
python -m aidatasets_figures --out build/figures
```

This makes three SVG/PDF/PNG figures, captions, DAS data and a reproduction receipt
**offline** using packaged, hash-checked inputs. No API/model call or private file
is needed. Installed commands `aidatasets-figures` and `ai-readiness` also work
outside this folder. Without installation, from this folder:

```sh
PYTHONPATH=src:tools python -m aidatasets_figures --out build/figures
PYTHONPATH=tools python -m ai_readiness --help
```

The DAS counts for 2020–2025 are **118, 137, 194, 238, 311 and 424**: worldwide
indexed article/review matches in titles/abstracts. The normalized panel uses all
indexed articles/reviews, not a geoscience denominator. These are not actual AI
use, multimodality, users, reuse, community demand or causal adoption barriers.
See [methods and provenance](docs/provenance.md).

## Continue the broader study

1. Use `ai_readiness` for existing metascience records, or the separate standalone
   prototype for a new bounded harvest. Keep their schemas and run folders separate.
2. Verify/freeze a defensible frame, including conference coverage for AI/CS.
   Keep AI keywords out of the primary denominator; align planned and implemented
   sampling allocations before acquisition.
3. Preserve metadata receipts, stable identities and sampling probabilities.
   Ranked convenience cohorts remain descriptive.
4. Calibrate the codebook, review full-text evidence, double-code the pilot and
   adjudicate. Unknown/inaccessible never means no.
5. Assess uncertainty, coverage and nonresponse before field-wide claims. Sparse
   FM mentions cannot establish adoption barriers or whether lean models meet needs.

Labels distinguish AI, DL, neural FM use and FM pretraining; scientific measurement
families and CS information channels; co-use and joint model inputs; supervised,
self-supervised and pseudo-label self-training regimes. Supervised readiness needs
reliable task-specific targets; pretraining readiness needs defensible samples,
objectives, correspondence, permissions and scalable access. File homogenization
alone establishes neither.

Start with [the preferred workflow guide](tools/ai_readiness/README.md):

```sh
ai-readiness --help
python standalone/literature_study.py harvest \
  --config standalone/config.example.json --dry-run
```

The dry run makes no network call and reports unresolved source IDs. Historical
API syntax/limits must be checked before new retrieval. No acquisition or model
job was launched for this release. Optional metascience clients can retrieve
content or spend model credits when explicitly run; the default package never
imports them or loads credentials. See their separate README.

Optional plotting of **reviewed** reports uses Matplotlib:

```sh
python -m pip install '.[study]'
python -m ai_readiness.plot_report reviewed_report.json \
  --outprefix build/study/readiness
```

The plotter refuses empty/unreviewed templates. No placeholder adoption curve is
presented as a result. To rebuild the instrument, install `.[instrument]` then
run `python instrument/build_readiness_instrument.py`; this overwrites the dated
example forms beside the builder. Make a working copy before annotating them.
Documentation and task adequacy remain separate; **do not sum a universal score**.

## Offline checks

```sh
python scripts/check_offline.py
python scripts/verify_release.py
python -m aidatasets_figures --out build/figures
```

The first runs the figure, preferred-analysis and standalone suites, without
retrieval or model execution. The second checks release-file hashes; use it before
editing. Current checks are recorded in
`provenance/release_validation_2026-10-29.json`; earlier receipts are historical.
Optional Matplotlib rendering status is recorded separately.

## GitHub and citation

The repository is hosted at <https://github.com/gaia-hazlab/geoscience-ai-readiness>.
Python sources, tests, frozen inputs, the pixi manifest and lock file, and citation
metadata are under version control. The ignore file excludes environments,
credentials, working corpora and generated outputs. No emails, budgets, personnel disclosures, author proposal text,
private partner inventories or article PDFs are included.

`CITATION.cff`, `citation.bib` and `.zenodo.json` describe version 0.3.0. Tag a
release and archive it on Zenodo if a DOI is wanted; no DOI has been registered.

> Denolle, M. (2026). *Geoscience AI-readiness research toolkit* (Version 0.3.0)
> [Computer software].

Append the real repository URL or release DOI once available. Cite OpenAlex
separately for DAS inputs. A software citation does not establish execution of
the broader study. See `LICENSE` and `THIRD_PARTY_NOTICES.md` for licensing.
