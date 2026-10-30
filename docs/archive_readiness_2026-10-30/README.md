# AI readiness of the geosciences as a domain, 30 October 2026

This note compares three measures: how often geoscience papers mention ML, how
geoscience datasets show up on data platforms, and how much of each raw archive has
been packaged as ML-ready benchmarks. Everything here is keyword or metadata
evidence. None of it measures actual use or reuse.

Files in this folder:

| File | Content | How it was produced |
|---|---|---|
| `archives.json` | 16 raw-archive volumes with source, date and quote | subagent web research, 2026-10-30 |
| `benchmarks.json` | 30 ML-ready benchmarks, 24 with a stated byte size | subagent web research, 2026-10-30 |
| `platform_counts.json` | DataCite, Hugging Face and OpenAlex counts | `scripts/platform_readiness_counts.py`, 93 keyless requests, 2026-10-30 |
| `platform_receipts.json` | URL, status and SHA256 of every response | same run; raw responses in gitignored `runs/platform_counts_2026-10-30/raw/` |
| `simulation_counts.json`, `simulation_receipts.json` | simulation and ML-surrogate article counts by field, subfield, year | same script, simulation block, 9 requests |
| `simulation_corpora.json` | 16 simulation archives and ML-ready simulation corpora | subagent web research, 2026-10-30 |
| `requery_2026-10-30.md`, `requery_2026-10-30_summary.json` | live re-query against the frozen counts | `scripts/requery_check.py` |

Figures and `archive_pairs.csv` rebuild offline with
`python scripts/archive_readiness_figures.py` into `build/archive_readiness/`.

## Finding 1: geoscience papers adopt ML methods at or above the average field

Share of OpenAlex articles whose title or abstract mentions "machine learning",
"deep learning" or "neural network" (Earth and environmental sciences are OpenAlex
fields 19 and 23 by primary topic):

| Year | All fields | Earth and environmental sciences |
|---|---|---|
| 2016 | 0.35% | 0.42% |
| 2020 | 1.42% | 1.56% |
| 2025 | 3.89% | 5.11% |

For 2023 to 2025 the all-field rate is 3.4%. Atmospheric science (6.9%),
oceanography (6.1%) and geophysics (4.8%) sit above it; geology (3.0%),
geochemistry (2.6%) and paleontology (0.4%) sit below. Remote sensing papers are
mostly filed outside these two fields, so they are not in the subfield split.

## Finding 2: "AI-ready" is a rare label everywhere, not a geoscience deficit

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

The AI-ready label is new: DataCite datasets using it number 5 in 2020, 27 in 2023
and 156 in 2025. OpenAlex articles using it number 165 in 2025 across all fields,
7 of them in Earth and environmental sciences. The subject tag undercounts Earth
datasets badly (PANGAEA and most agency archives do not use it), which is why the
tagged row shows 3.

On Hugging Face, dataset repositories whose names contain geoscience terms total
about 4,000 across six disciplines, against 4,624 for three biomedical terms. These
are upper bounds from name matching ("flood" dominates hydrology); the geodesy count
keeps only "insar" and "gnss" matches, 25 repositories. The most downloaded
geoscience item is an ERA5 copy (456,702 downloads in 30 days).

These counts do not support the proposal sentence that geoscience datasets on
AI-native hubs lag general repositories. I found no local script or data behind
that sentence; it should be sourced or reworded.

## Finding 3: the gap is volume, and the packaged share differs by up to six orders of magnitude between disciplines

ML-ready benchmarks against the archive they were drawn from (`fig1_archive_vs_ml_ready`):

| Discipline | Raw archive | ML-ready packaged | Share |
|---|---|---|---|
| Reanalysis: ERA5 | 10 PB (ECMWF, Sep 2026) | 2.05 PB (ARCO-ERA5) | 20% |
| Seismology | more than 1 PB (EarthScope seismic, 2025) | 2.66 TB (7 benchmarks) | 0.27%, upper bound |
| SAR: Sentinel-1 | more than 20 PB (ASF DAAC, 2023) | 16 TB (Major TOM S1, Sen1Floods11) | 0.08% |
| Optical: Sentinel-2 | 91 PB (Copernicus Data Space, end 2025) | 25.1 TB (Major TOM S2 L2A, SSL4EO, SEN12MS, BigEarthNet) | 0.03% |
| Climate projections: CMIP6 | more than 16 PB distinct (ESGF, 2025) | 2.39 GB (ClimateBench) | below 0.001% |
| Geodesy: GNSS | more than 300 TB (EarthScope GAGE, 2020) | none found | none |
| Ocean observatory: OOI | 2.8 PB raw (2025) | none found | none |
| DAS | no published archive volume | 680 GB (4 datasets) | not computable |
| Hydrology: gauges | USGS NWIS publishes no byte total | 54 GB (CAMELS, Caravan, LamaH) | not computable |

Reanalysis is the one discipline where a large fraction of the archive exists in an
analysis-ready cloud format. It is also the discipline where ML weather models are
trained on decades of the full record; this note does not test whether the
packaging caused that. Elsewhere the packaged data are a fraction of a percent
of the archive, and for GNSS and ocean observatories I found no ML-ready benchmark
at all. A benchmark is a designed subsample, so a small share is not by itself a
deficit. It does bound what can be trained without new curation, and it is the
quantity a pretraining effort would have to raise.

## Finding 4: solid-earth simulation communities adopt ML surrogates more slowly, and package almost no simulation output

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

The Earth and environmental index rose from 0.45 (2016) to 10.9 (2025), ahead of
all fields (7.2), carried by climate and atmosphere. ML-ready simulation corpora in
solid earth total 2.48 TB (OpenFWI 2.1 TB, HEMEW-3D 0.37 TB, two rupture sets),
against 101 TB in other physics and atmosphere (DrivAerNet++, The Well, ClimSim,
PDEBench, BLASTNet). One CyberShake study (22.12) kept 75 TB and handled 2.5 PB
during its run (`simulation_corpora.json`).

## Reproducibility

| Check | Command | Result on 2026-10-30 |
|---|---|---|
| Frozen snapshots | `pixi run -e report requery-offline` | 12 of 12 hashes match |
| Live re-query, no key | `pixi run -e report requery-live` | OpenAlex 90/90, simulation 148/148, DataCite 36/36 numbers within 1%; DAS series identical for 2020-2023, +1 in 2024 and 2025 |
| Notebooks | `pixi run -e report notebooks` | `notebooks/01`-`03` execute offline without errors |
| HTML report | `pixi run -e report report` | `docs/report/ai_readiness_solid_earth.html`, every number computed from tracked inputs |

The live receipt is `requery_2026-10-30.md` (summary in
`requery_2026-10-30_summary.json`). Web-researched volumes cannot be re-queried by a
script; each row carries its source URL, date and a checked-in-text flag. The DAS
semantic labels are frozen in `data/semantic_screen/das_topic_2026-10-29/`; rerunning
the screen needs an OpenAlex key, Claude credentials and about $4.50.

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
- Seismology's share uses only the EarthScope archive as denominator, though the
  benchmarks also draw on SCEDC, NCEDC, INGV and Swiss archives.
- Platform counts depend on keyword clauses recorded in `platform_counts.json`.
  Hugging Face matching uses repository names only.
- All paper counts are keyword co-occurrence, not actual use.
