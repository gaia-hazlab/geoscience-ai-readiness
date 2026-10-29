# Optional metascience acquisition and semantic support

Prepared October 29, 2026. This is a compact source snapshot (Python code unchanged; three historical directory examples generalized) from
`Denolle-Lab/metascience-and-AI`, commit
`dc19d45b0bfd2eb98ffb8ad4bbd26f2e87f2ba6f`.

`SOURCE_MANIFEST.json` records the repository-relative source path, SHA-256 and
original size of every copied file, plus each release hash and any intentional documentation change. The source working tree was clean when copied. The
snapshot is for local reuse and review; it does not create or publish a GitHub
repository, obtain credentials, retrieve a corpus, submit model jobs or establish
new scientific findings.

## Why this directory is separate

The parent project's `tools/ai_readiness/` runs the offline evidence, sampling,
annotation and reporting workflow. These optional scripts support the larger
metascience project's acquisition and semantic-coding pipeline. Their original
relative directory layout is retained so imports and codebook lookups continue
to resolve. A duplicate of its unchanged `tools/ai_readiness/` is retained here
because the semantic coder looks for it under its own repository root.

Nothing in this directory runs automatically. Do not bulk-execute Python files:
some commands download publications or submit paid model requests when invoked.
Read each command's help and its original instructions before deliberately using
it. Historical provider parameters, prices, model names, availability and access
terms in unchanged sources must be checked again before a new acquisition or
model run.

## Included tools and their boundaries

| Files | Purpose | Execution boundary |
|---|---|---|
| `tools/select_dois.py`, `tools/nature_dataset.py` | Select and freeze DOI cohorts with design/provenance records | Live selection and refresh contact OpenAlex; Nature download subcommands can contact Springer Nature |
| `tools/download_nature.py`, `tools/download_wiley.py` | Publisher full-text retrieval | Network and appropriate existing publisher access/credentials; downloaded texts stay private |
| `tools/corpus.py` | Earlier corpus selection | Network; capped/legacy pools are descriptive, not an established probability frame |
| `tools/jats_text.py` | Local JATS/XML conversion | Local input only; no article text is supplied here |
| `tools/fetch_pdfs.py`, `tools/apa.py` | Existing PDF queue and citation support | Queue acquisition commands can use network, publisher credentials and local library paths |
| `tools/code_papers.py` | Optional inquiry, readiness and advance draft coding | Model API calls, document transmission and charges require deliberate invocation; no such calls were made to prepare this snapshot |
| `tools/check_coding.py`, `tools/check_coding_nature.py`, `tools/check_advance.py` | Validate coding records | Local user-supplied records and applicable evidence are required |
| `tools/blind_text.py`, `tools/roadmap/{common,g27_author_responses,g27_nature_units}.py` | Transitive text, review-unit and provenance support | Some paths can fetch missing source metadata or use local private records; these are support modules, not a bundled full roadmap study |
| `tools/aggregate_codings.py` | Summarize existing inquiry codings | Local records only; not an AI-readiness adoption estimate |
| `tools/ai_readiness/` | Evidence-gated readiness study sidecar | Core is offline; no reviewed real-data result is included |

The `--task readiness` coder writes draft annotations with `review_status:
pending`; model suggestions cannot substitute for a completed, evidence-based
human review. Citing or inheriting an earlier paper's method is not proof of
actual use by the coded paper. Missing evidence remains unknown.

## Dependencies

Use Python 3.10 or later; the prepared parent project uses Python 3.12. DOI
selection, publisher download tools and their four included test modules use the
standard library. The offline readiness core also uses the standard library.

- Matplotlib: optional readiness plots and some review-analysis helpers.
- `anthropic`: the optional semantic coder imports the Anthropic SDK; it is not
  installed or invoked automatically.
- `jsonschema`: advance validation and the optional coding environment.
- Poppler `pdftotext` (and, for some review helpers, `pdftohtml`): PDF-to-text and
  review-document processing. Install separately only if those paths are used.
- Existing user-controlled API keys or institutional publisher entitlements may
  be required for live operations. No key or credential file is included.

`tools/keys.py` is the original loader **code**, not a credential. Some original
modules call it during import. For offline checks, set `METASCIENCE_KEYS` to a
nonexistent path to prevent reading any local credential file. Do not copy your
actual keys into this project or commit them to version control.

## Offline checks

From this directory, these four test modules use mocked/synthetic responses and
temporary directories, with no live acquisition or model calls:

```sh
METASCIENCE_KEYS=/nonexistent/metascience-keys.env \
  python -m unittest discover -s tools -p 'test_*.py' -v

METASCIENCE_KEYS=/nonexistent/metascience-keys.env PYTHONPATH=tools \
  python -m unittest discover -s tools/ai_readiness/tests -v
```

The second command tests report-data extraction without Matplotlib; rendering
reviewed reports separately needs Matplotlib. Test fixtures are
synthetic; passing tests are software checks, not a measured literature result.
`OFFLINE_CHECK_RECEIPT.json` records the actual checks performed on this snapshot.

## Deliberately omitted inputs and repository features

No `private/` tree, credentials, `.env` file, Git history, article PDFs/XML,
abstract corpus, licensed review material, email, proposal or study outputs are
copied. The source seminar book and complete roadmap are also omitted.

Consequently, commands that require a prior private queue, corpus, review texts,
source caches or codings require the user's own inputs. `fetch_pdfs.py` commands
that operate on an explicit DOI list or manifest can be used with those inputs;
its curriculum-reading route and the standalone `apa.py` demonstration expect
the source book's `curriculum.json`, which is intentionally absent. Review and
advance branches retain their schemas and transitive modules but do not include
the private roadmap context or claim to reproduce that separate study.

The included example Nature configuration is an example, not a prespecified,
representative geoscience-versus-CS sampling frame. Resolve a transparent frame
and freeze the study design before estimating adoption. Raw publication counts,
keyword matches or model drafts do not establish why a field uses fewer
foundation models, the adequacy of small models, or a universal readiness grade.

## Licensing and citation

The original `LICENSE` is preserved: software under `tools/` is MIT; seminar
content is CC BY 4.0 with the source repository's stated exclusions for third-party
papers. Preserve attribution when reusing the accompanying codebooks and prose.
No rights in downloaded publications are granted by this code package.

Cite the actual repository and commit above for this integration snapshot. It
has no assigned standalone DOI. Cite the parent release's final archive DOI only
after an archive has issued it; none is invented here.
