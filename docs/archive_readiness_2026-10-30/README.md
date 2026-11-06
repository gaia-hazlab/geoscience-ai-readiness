# AI readiness of the geosciences as a domain, 30 October 2026

This note compares three measures: how often geoscience papers mention ML, how
geoscience datasets show up on data platforms, and how much of each raw archive has
been packaged as ML-ready benchmarks. Everything here is keyword or metadata
evidence. None of it measures actual use or reuse.

Files in this folder:

| File | Content | How it was produced |
|---|---|---|
| `archives.json` | 20 raw-archive volumes with source, date and quote | subagent web research, 2026-10-30; 4 rows added 2026-11-06 from page summaries |
| `benchmarks.json` | 30 curated ML benchmarks | subagent web research, 2026-10-30; ARCO-ERA5 moved out and Major TOM L1C added 2026-11-06 |
| `analysis_ready_copies.json` | whole-record copies, separate from benchmarks | page summaries, 2026-11-06 |
| `ml_share_abstract_2026-11-06.json`, `_receipts.json` | ML rate with articles with an abstract as denominator | `scripts/ml_share_abstract_counts.py`, 6 keyless requests |
| `platform_counts.json` | DataCite, Hugging Face and OpenAlex counts | `scripts/platform_readiness_counts.py`, 93 keyless requests, 2026-10-30 |
| `platform_receipts.json` | URL, status and SHA256 of every response | same run; raw responses in gitignored `runs/platform_counts_2026-10-30/raw/` |
| `simulation_counts.json`, `simulation_receipts.json` | simulation and ML-surrogate article counts by field, subfield, year | same script, simulation block, 9 requests |
| `simulation_corpora.json` | 16 simulation archives and ML-ready simulation corpora | subagent web research, 2026-10-30 |
| `requery_2026-10-30.md`, `requery_2026-10-30_summary.json` | live re-query against the frozen counts | `scripts/requery_check.py` |

Figures and `archive_pairs.csv` rebuild offline with
`python scripts/archive_readiness_figures.py` into `build/archive_readiness/`.

## Corrected on 6 November 2026

This note replaces the findings of 30 October. The HTML report, section 10, lists every change. The earlier tables mixed curated benchmarks with whole-record copies, used denominators that did not match their row labels, and divided abstract matches by articles with no abstract.

Readiness depends on the use, because the use sets the intended population. For data mining and pretraining the total archive tends to be that population, so a share of the archive is the right kind of number. For a supervised task the population may be a set of events, sites or conditions.

## Finding 1: ML is mentioned at least as often here as across all fields

Share of OpenAlex articles with an abstract whose title or abstract mentions "machine learning", "deep learning" or "neural network" (`ml_share_abstract_2026-11-06.json`; Earth and environmental sciences are OpenAlex fields 19 and 23 by primary topic):

| Year | All fields | Earth and environmental sciences | Share of articles with an abstract, all fields | Same, Earth and environmental |
|---|---|---|---|---|
| 2016 | 0.43% | 0.50% | 53.9% | 50.5% |
| 2020 | 1.61% | 1.69% | 64.7% | 62.7% |
| 2025 | 4.02% | 5.03% | 78.2% | 75.7% |

The old rates, over all articles, were 3.89% and 5.11% in 2025. These are keyword counts, not use. Remote sensing papers are mostly filed outside these two fields.

## Finding 2: "AI-ready" is a rare label everywhere

DataCite dataset DOIs on 2026-10-30:

| Set | Datasets | Mention ML | Say AI- or ML-ready |
|---|---|---|---|
| All dataset DOIs | 78,241,222 | 666,883 | 707 |
| Tagged "FOS: Earth and related environmental sciences" | 200,070 | 914 | 3 |
| Seismology keywords | 43,477 | 1,126 (2.6%) | 12 |
| Optical remote sensing keywords | 82,789 | 8,552 (10.3%) | 81 |
| Weather and climate keywords | 322,903 | 7,167 (2.2%) | 69 |
| Hydrology keywords | 54,846 | 2,089 (3.8%) | 12 |
| Ocean keywords | 148,653 | 1,120 (0.8%) | 10 |
| Biomedicine keywords (comparison) | 453,674 | 12,551 (2.8%) | 90 |

The subject tag undercounts Earth datasets, because PANGAEA and most agency archives do not use it. DataCite datasets using the label number 5 in 2020, 27 in 2023 and 156 in 2025.

Hugging Face name counts cannot settle whether geoscience lags on hubs. The geoscience total uses far more terms than the 3 biomedical terms, matches names only, and has no hub total as a denominator. The proposal sentence that geoscience datasets on AI-native hubs lag general repositories has no local source; these counts neither support nor refute it, so it should be sourced or reworded.

## Finding 3: two different measures of packaging

**Curated ML benchmarks against the archive they were drawn from** (`archive_pairs.csv`). Each label names the denominator.

| Row and denominator | Source archive | Curated benchmarks | Share |
|---|---|---|---|
| Reanalysis: ERA5 | 10 PB (ECMWF, Sep 2026) | WeatherBench 2, size not stated | not computable |
| Seismology: EarthScope, NCEDC, SCEDC | more than 1.3 PB (Ni et al. 2025) | 2.48 TB (5 benchmarks) | at most 0.19% |
| Seismology: INGV and Swiss archives | no volume in hand | 182 GB (INSTANCE, ETHZ) | not computable |
| SAR: all ASF holdings | more than 20 PB (2023, secondary source) | 16 TB | at most 0.08% |
| Sentinel missions: all, Copernicus | 91 PB (end 2025) | 64.1 TB (7 benchmarks) | 0.07% |
| Climate projections: CMIP6 | more than 16 PB distinct (2025) | 2.39 GB (ClimateBench) | below 0.001% |
| Geodesy: GNSS | more than 300 TB (2020) | none found | none |
| Ocean observatory: OOI | 2.8 PB raw (2025) | none found | none |
| DAS | no published archive volume | 680 GB (4 datasets) | not computable |
| Hydrology: gauges | USGS NWIS publishes no byte total | 54 GB | not computable |

No per-mission Sentinel volume was found. The report PDFs that may hold one exceeded the fetch limit and were not read.

**Whole-record copies a compute job can read** (`analysis_ready_copies.json`). This is the measure that fits data mining.

| Discipline | Copy | Form | Size |
|---|---|---|---|
| ERA5 | ARCO-ERA5 pressure and surface levels | regridded, analysis ready | 2.05 PB |
| ERA5 | ARCO-ERA5 model levels | regridded, analysis ready | 5.88 PB |
| ERA5 | ARCO-ERA5 four native-grid stores | cloud optimized | 2.27 PB (computed sum) |
| CMIP6 | Pangeo on Google Cloud, AWS mirror | analysis ready, subset | more than 1 PB (2022) |
| Seismology | EarthScope, NCEDC, SCEDC, read by Ni et al. 2025 | native miniSEED on S3 | more than 1.3 PB |
| Sentinel-2 | L2A Cloud-Optimized GeoTIFFs on AWS | cloud optimized | size not found |

Regridded stores can exceed the raw archive, and sources disagree on raw ERA5 (about 10 PB at ECMWF, about 5 PB in the ARCO-ERA5 README). A byte ratio is therefore not a coverage fraction. The earlier "ERA5 20%" compared a reformatted copy with curated subsets elsewhere and is withdrawn, as is the claim of six orders of magnitude between disciplines. GNSS, OOI, DAS, hydrology, InSAR and Sentinel-1 were not searched for this table.

Seismology has a small curated share and also a whole-archive inference run. Inference over an archive is not training on it. This note does not test whether packaging caused ML success in weather.

## Finding 4: solid-earth simulation papers mention ML surrogates less often, and little output is packaged

Articles naming an ML surrogate (physics-informed neural network, neural operator,
DeepONet, or a surrogate model or emulator with an ML term) per 100 articles naming
a numerical method, OpenAlex 2023 to 2025 (`simulation_counts.json`):

| Field or subfield | Index |
|---|---|
| Physics and Astronomy | 32.0 |
| Computer Science | 16.5 |
| Global and Planetary Change | 16.2 |
| Atmospheric Science | 13.5 |
| Earth and Planetary Sciences (field) | 6.4 |
| Geophysics | 5.3 |
| Engineering | 2.8 |
| Earth-Surface Processes | 1.9 |

This is a ratio of two keyword groups at one period, not a rate of adoption. ML-ready simulation corpora found in solid earth total 2.48 TB (OpenFWI 2.1 TB, HEMEW-3D 0.37 TB, two rupture sets), against 101 TB found in other physics and atmosphere (`simulation_corpora.json`). The lists are purposive. One CyberShake study (22.12) kept 75 TB and handled 2.5 PB during its run.

## Reproducibility

| Check | Command |
|---|---|
| Frozen snapshots | `pixi run -e report requery-offline` |
| Live re-query of every source, dated summary written here | `pixi run -e report requery-live` |
| Notebooks | `pixi run -e report notebooks` |
| HTML report | `pixi run -e report report` |

Results are in the newest `requery_<date>.md` and `requery_<date>_summary.json`, and in section 8 of the report. Web-researched volumes cannot be re-queried by a script; each row carries its source URL, date and a checked-in-text flag. The DAS labels are frozen in `data/semantic_screen/das_topic_2026-10-29/`, and checks on them are in `docs/das_screen_checks_2026-11-06/`.

## The archive figures in the request, checked

| Stated in the request | What the sources say |
|---|---|
| NASA about 200 PB of SAR | NASA Earth science holds 225.7 PB in all, cloud copies included (127.7 PB deduplicated, FY2024). The SAR part at ASF was more than 20 PB in 2023; NISAR is projected at about 40 PB per year. |
| EarthScope about 4 PB | Seismic archive more than 1 PB (2025); geodetic archive more than 300 TB (2020, no newer figure). No 4 PB figure found. |
| USGS hydroscience | NWIS publishes site counts (about 1.5 million), not bytes. The USGS Landsat archive is 13.8 PB (2025) or 20 PB (2023 slide); USGS has not reconciled the two. |
| NCAR reanalysis | NCAR GDEX (former RDA) migrated 9 PB at its 2025 relaunch, not stated as a total. ECMWF holds ERA5 at about 10 PB within a 718 PB archive. |

Other holdings for scale: NOAA NCEI more than 60 PB (late 2023), CMIP6 28 PB with
replicas.

## Caveats

- Volumes use different definitions (with or without replicas, online or tape).
  ECMWF's 718 PB slide does not say whether backups are counted.
- Weakest archive figures: ASF (secondary source, 2023), GAGE (2020), NCAR GDEX
  (migrated volume), NCEI (2023), Landsat (two USGS figures). Quotes not checked in
  the source text are marked `checked_in_text: false` in `archives.json`.
- The seismology denominator is the data used in one study, from a paper Marine Denolle
  co-authored, so it is a lower bound on holdings. CEED and SCEDC benchmarks overlap.
- Rows added on 2026-11-06 were read through page summaries and need reading in the
  source before citation.
- Platform counts depend on keyword clauses recorded in `platform_counts.json`.
  Hugging Face matching uses repository names only.
- All paper counts are keyword co-occurrence, not actual use.
