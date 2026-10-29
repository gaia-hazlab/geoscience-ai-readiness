# Literature study update 23 October 2026

The October 21 scaffold exists and passed its 20 offline tests. It has **not produced a broad multimodal, deep-learning or foundation-model prevalence result**. The separate October 21 DAS title/abstract counts are a keyword activity series and cannot answer this study's broader questions.

This dated copy is version 0.2.0. It adds evidence-gated actual deep-learning use, foundation-model use and foundation-model pretraining, plus conditional proportions. It preserves the original harvester, modality definitions and unknown-versus-no rules. No corpus retrieval, paid service, account creation or remote publication has been launched for this update. Synthetic tests are software checks, not scientific results.

## What can be measured

For each complete year, estimate the share of eligible papers that actually use two or more measurement families; use AI; use deep learning; use or adapt a foundation model; or pretrain a foundation model. Also estimate DL among AI papers and FM among AI/DL papers. AI, DL and FM labels overlap; they are not three disjoint bins. This codebook restricts FM to neural foundation models and enforces verified FM use as a subset of verified DL use. FM use/adaptation is distinct from training a new FM. Joint scientific use, joint model inputs, and joint multimodal pretraining are separate claims.

`deep_learning_actual_use`, `foundation_model_actual_use` and `foundation_model_pretraining` require methods/results evidence. Positive labels require actual AI use, and positive pretraining also requires verified FM use. Old annotations without these fields remain unknown and cannot silently become negatives. Record a foundation model only where broad pretraining and downstream adaptation are demonstrated; a transformer or a large parameter count alone is insufficient. Record architecture, training objective, training data, parameter count, compute budget, adaptation and evaluated tasks where stated. Self-supervised learning constructs training targets from the data; self-training with pseudo-labels is separately coded. Supervised task readiness requires reliable targets and a specified task, while pretraining readiness requires defensible examples, views/masks, physical support and correspondence, sampling, provenance, permissions and scalable access.

## Comparison with AI and computer science

Freeze two transparent publication frames before acquisition: a geoscience frame spanning the proposed communities and a comparison frame for AI/CS. The current example journal identifiers are unresolved; no run may be called complete until they are verified and frozen. AI/CS depends heavily on conference proceedings, so an article-only journal comparison would be misleading. Verify each venue's actual OpenAlex source/type indexing and coverage. Report journals and conferences separately, then conduct prespecified matched document-type and year comparisons. Do not silently mix preprints with peer-reviewed proceedings. A single paper may span fields; preserve overlap and report a sensitivity analysis rather than labeling an author as either a domain or CS expert from affiliation alone.

Use the same eligibility rules and coding in both frames. Calculate within-frame shares as well as counts; raw publication volume cannot establish adoption speed. Report complete years 2016–2025, missing abstracts/full text, weighted estimates and uncertainty, and sensitivity to subfield composition and modality definitions. The existing sampler is year × venue × AI-screen, not the proposed 240-paper subject × year-band design. Align and validate that allocation before launching the named 240-paper pilot. The CLI can be used on each frame separately; it does **not** yet implement the joint CS/geoscience comparator, a trend model, or a cross-field causal analysis.

## Why adoption may differ

Technical access/interoperability, compute, skills, label availability, transfer/evaluation and task-specific model adequacy are hypotheses, not conclusions from sparse FM mentions. Code explicit author statements separately from our interpretation. Record task-matched small-model/FM comparisons, including training and inference cost, data/label budget, tuning and performance. A compact model succeeding on a fixed task does not prove that larger transferable representations lack value. Publication counts cannot establish that researchers had no need for FMs. A causal account would need targeted surveys/interviews or designed comparisons alongside the literature evidence.

## Planned figure

Panel A: weighted share using multiple measurement families over time. Panel B: AI, DL and FM shares with clearly stated denominators. Panel C: matched geoscience and AI/CS FM shares, with separate venue strata and confidence intervals. Panel D, only if evidence supports it: task-specific performance and compute comparisons. Keep barriers in a separate evidence table. No placeholder curve may be presented as measured results. The 240-paper pilot is better suited to year-band estimates; expansion and annual precision depend on pilot variance and rare-event counts.

## Run status and next work

32 offline tests pass in the updated copy. The source-frame dry run lists eight unresolved geoscience journals and zero executable queries. Next: resolve/freeze balanced source IDs and CS venues, align the probability-sampling design, retrieve bounded metadata, calibrate the codebook, double-review the pilot, adjudicate, and report uncertainty. Read-only public metadata work is sufficient for frame resolution; larger cursor retrieval requires an existing verified OpenAlex key under current official documentation. No key was requested, created or exposed. Human full-text verification remains necessary for actual-use results. The expanded protocol and code may be handed to an independent research agent; a remote repository and public release are not created here.

## Original scaffold instructions and limitations

# Geoscience multimodal-literature study — local pilot scaffold

Dated **2026-10-21**. This is a repository-ready prototype, not a completed bibliometric result. It uses the Python standard library, makes no LLM calls, creates no accounts or credentials, downloads no full text, and spends no API/LLM budget by default. **No live corpus was harvested to test this scaffold.** Tests use explicitly synthetic fixtures. No GitHub repository has been created or pushed.

The question is whether papers actually analyze multiple measurement families, whether AI is used in that analysis, and how inputs are integrated. A title/abstract keyword match is **screening evidence only**. It cannot establish actual data use, absence of a modality, joint training, foundation-model training, or community readiness.

## Run locally

Use Python 3.10+ from this directory. No package installation is needed.

```sh
python3 -m unittest discover -s tests -v
python3 literature_study.py harvest --config config.example.json --dry-run
```

The sample config intentionally leaves journal identifiers unresolved. Verify each journal by title and ISSN in OpenAlex, record the source URL/ID and inclusion decision, then freeze a copied config. Retrieval refuses unresolved source IDs. The candidate journal list is illustrative, not an approved representative frame. Its missing oceanographic, atmospheric, food-system and interdisciplinary coverage must be settled before population claims. **2016–2025** excludes the partial 2026 publication year.

After frame approval, retrieval is opt-in and bounded:

```sh
python3 literature_study.py harvest --config frozen_config.json --out runs/pilot --execute --max-pages 1
```

Repeat the command to resume. `--max-pages` is a total per invocation, not per journal. A changed config requires a different output directory. Current OpenAlex documentation limits `per_page` to **100**, and cursor continuation beyond page one may require a **verified existing key**. If the user has provided one, make it available as `OPENALEX_API_KEY` using the user's normal secret manager; never commit or print it. The program does not create a key, writes public URLs with credentials omitted, and stops if continuation requires a missing key. Confirm current account/API terms before a larger run. There is no paid full-text endpoint in this code.

Retrieval stores raw response envelopes, timestamps, public query URLs, SHA-256 hashes, a frozen configuration, cursor checkpoints and deduplicated works. Queries use publication year, source ID and article type, with **no AI/modal keywords in the denominator**. An optional language restriction is visible in the config; null means no restriction. Reviews and preprints are excluded from this primary frame; study reviews separately if useful. There is a one-second default interval, bounded retries for 429/transient server/network failures, and `Retry-After` handling for integer seconds. A page is saved before its checkpoint advances; interruption can repeat that page without multiplying corpus records. Resume is not a point-in-time API snapshot: complete the collection promptly, retain receipts, and document the acquisition window and changing-index limitation.

Once `manifest.json` reports `frame_complete: true`:

```sh
python3 literature_study.py screen --input runs/pilot/works.jsonl --out runs/pilot/screen.jsonl
python3 literature_study.py sample --input runs/pilot/screen.jsonl --manifest runs/pilot/manifest.json --out runs/pilot/sample.jsonl --design runs/pilot/design.json --n-per-stratum 10
python3 literature_study.py template --input runs/pilot/sample.jsonl --out runs/pilot/annotations.jsonl
```

The prototype sampler takes a reproducible simple random sample within **year × source × AI-screen-positive/negative** strata, including negative-screen papers. It records each stratum's population/sample sizes and inclusion probability. Small strata are censused. **This fallback layout is not the companion protocol's exact 240-paper pilot, which uses four subject groups × three year bands × AI-screen-positive/negative cells.** Implement/align the registered allocation before launching that pilot; the shown command does not promise a sample of 240. Assess precision and review effort before expanding. Source membership must be unique after DOI/OpenAlex-ID deduplication; inspect transitive merge groups and published-version identity. The sampler refuses incomplete metadata frames and verifies the entire screen file against the manifest's record count, unique-ID digest and original works-file hash; a filtered positive-only screen cannot inherit the complete-frame label. A broad query-conditioned convenience corpus must never be relabeled a journal-frame census.

## Human annotation and independent review

Edit `annotations.jsonl`, guided by `annotation.schema.json`. A tabular annotation interface is a useful next step. Keep the immutable source metadata and the completed human record separate.

1. Obtain legally accessible full text through open-access/publisher/institutional routes. Record unavailable/parse-failed/partial text; an OA flag is not a license. This prototype does not download publisher PDFs or circumvent access controls.
2. Read methods, data and results, not only the abstract. Determine Earth-science eligibility. Mark `review_status: reviewed`, a reviewer ID, and `evidence_level: full_text` only after completing this review. Inaccessible text stays `inaccessible`; unknown is not no.
3. Record each data source's measurement family, actual analysis use versus background mention, observed/simulated/derived origin, platform, representation and native support. **Two satellite products are not automatically two modalities; two DAS deployments are not two modalities; simulated versus observed is an origin distinction.** An optical and radar pair can be two measurement families even after both are rasterized. A waveform and a displacement time series can be different families even when both are arrays.
4. Keep AI mention separate from actual computational use; record the method and role. Traditional data assimilation/inversion is not automatically AI. Fusion labels are multi-label: co-use only, joint non-ML inversion, late output fusion, joint ML inputs, cross-modal representation learning, and a demonstrated cross-modal transfer test. These distinctions prevent claiming that joint use is joint foundation-model training.
5. Every positive actual-use/fusion label needs a source URL, section/page and a short evidence excerpt with a `supports` label. Each excerpt must be ≤25 words, and total quotation per source must stay within applicable limits. Prefer short paraphrase notes. An empty modality/fusion list means reviewed absence; null means unknown. Explain eligibility exclusions, dataset DOI/version use, and barriers.
6. For the proposed 240-paper pilot, **independently double-code every paper**, then adjudicate. A later expanded study may use a prespecified double-reviewed stratified subset after the pilot validates the rubric. Preserve both original annotations and the adjudicated file; report agreement per family/AI/fusion label. LLM-assisted extraction, if authorized later, is a suggestion queue requiring evidence and human review, never the reported ground truth. Do not send licensed full text to an external model without permission.

The optional readiness block separates access, machine readability, cross-experiment interoperability, scalable training, independent evaluation and community reuse. An infrastructure demonstration by one team is not independent replication or routine community uptake. Grades require evidence and are not intended as a universal scalar readiness score. A literature-only study cannot determine occupied archive bytes, access costs, operational availability, license compliance, or the full set of non-publishing users; audit repositories and interview providers separately.

## Report only reviewed evidence

```sh
python3 literature_study.py report --input runs/pilot/annotations_adjudicated.jsonl --design runs/pilot/design.json --out runs/pilot/reviewed_report.json
```

Without `--design`, the output gives descriptive proportions in the **reviewed accessible subset only**, with no population CI. With a complete documented stratified SRS design and complete known labels, it calculates annual inverse-inclusion-weighted ratio estimates and a **95% normal-approximation interval from Taylor residual variance with finite-population correction**. It reports separate denominators for known AI and modality labels. Missing sampled reviews, uncertain eligibility, unknown labels, incorrect inclusion probabilities, or singleton non-census variance strata suppress population estimates; they are never recoded as zero. Boundary estimates do not receive a misleading zero-width interval. Sparse/rare outcomes require exact finite-population or sensitivity bounds in a later statistical pass. Intervals cover sampling uncertainty only, not indexing omissions, source-frame bias, annotation error or full-text nonresponse.

The five metrics are: ≥2 actually used measurement families; actual AI use; P(multifamily use | actual AI); P(actual AI | multifamily use); and ≥2 families jointly input to an ML model or cross-modal representation learner. They do not count foundation-model training specifically; add architecture/training-scale labels and adjudicated evidence before making that narrower claim. Annual estimates alone do not establish an increasing trend; predefine a weighted trend analysis and assess changing source coverage, missing abstracts and publication lag. A model-based follow-up should include journal/subfield effects and uncertainty. Do not infer a community's desire for AI-ready data from rising paper counts: explicit requests for interoperability, reuse barriers, benchmark adoption and named pilot users require separate evidence. `need_claims` preserves the distinction between an explicit author request and the assessor's inference. The main sensing-family definition should later receive a sensitivity analysis using coarse measured-phenomenon and fine sensor-type definitions; this prototype does not yet calculate those alternate groupings.

## Files and extension boundary

- `literature_study.py`: dry-run/harvest, metadata screen, stratified sample, blank annotation template, reviewed report.
- `config.example.json`: unresolved frame for approval; no guessed journal IDs.
- `annotation.schema.json`: portable human annotation contract. The CLI enforces key evidence and label rules; full JSON Schema validation is optional and would require an external validator.
- `tests/`: synthetic fixtures and tests for deduplication, cursor resume, key redaction, screen/actual-use separation, sampling and estimates.
- `.gitignore`: excludes runs, credentials, caches and local full text.

A next independent agent can resolve journal identities and propose a balanced frozen frame; a separate human-approved acquisition run can harvest metadata; annotators can then test the rubric on 30–50 papers before scaling. Repository creation, publishing a dataset, spending API credits, or deploying an automated full-text/LLM review remains a separate action. License/project ownership and a repository license should be decided before publishing this scaffold; no open-source license is invented here.

## Verified API documentation

- [OpenAlex search](https://help.openalex.org/api/searching/): current scoped exploratory parameter `search.title_and_abstract` (not used to condition the primary denominator).
- [Paging](https://help.openalex.org/api/paging/): current per-page limit and cursor behavior.
- [Authentication](https://help.openalex.org/api/authentication/): existing-key requirements and limits.
- [Works attributes](https://help.openalex.org/data/works/attributes/): inverted-index abstracts and metadata fields.
- [Full-text access](https://help.openalex.org/access/fulltext/): separate content endpoints and terms, not invoked here.

Documentation was reviewed for this proposal task on 2026-10-21; verify again before live acquisition. Search syntax and limits can change. The prior proposal's dated OpenAlex pilot is a separate frozen historical receipt and is not a live test of this new scaffold.
