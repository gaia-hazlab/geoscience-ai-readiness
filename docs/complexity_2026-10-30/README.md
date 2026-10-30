# How complex are the geosciences? Scoping note, 30 October 2026

Four directions can be measured from published sources today, though with very different evidence behind each:

- **Heavy tails.** Heavy-tailed size distributions are the norm for the hazards tabulated. In 24 geoscience source-and-data-set rows that report an exponent, 13 were tested against alternative distributions, and only 4 of those 13 favored a pure power law.
- **Effective dimension.** Published estimates exist for only a few data types: climate fields, Global Navigation Satellite System (GNSS) common-mode error and small Interferometric Synthetic Aperture Radar (InSAR) stacks. None exists for seismogram archives, distributed acoustic sensing (DAS) or the ERA5 reanalysis of the European Centre for Medium-Range Weather Forecasts (ECMWF).
- **Coupled equations.** Minimal coupled models need between 1 and 17 scalar balance equations. That is not more than canonical physics systems (4 to 8). The complexity sits in the closures, not in the count.
- **Unobserved drivers.** Some of the drivers of hazard outcomes have sourced numbers, but no published percentage splits seismic loss variance among hazard, exposure and vulnerability.

No number in this folder was estimated. A value that could not be found in a source is recorded as "not found". The four directions are never added into one complexity score.

Section 5 sets each axis against sourced AI successes and limitations, and summarizes readiness per discipline as a profile of separate measures. The same material is section 6 of the HTML report `docs/report/ai_readiness_solid_earth.html` and notebook `notebooks/04_complexity_and_readiness.ipynb`.

## Files

| File | Content | Rows | Rows with a value | Read in source text |
|---|---|---|---|---|
| `power_laws.json` | exponents, conventions, tests against alternatives | 34 | 31 | 30 |
| `dimensionality.json` | nominal sizes and published effective dimensions | 41 | 36 | 36 |
| `coupled_pdes.json` | balance-equation and state-variable counts per coupled system | 20 | 19 | 18 |
| `unobserved_drivers.json` | sourced gaps in what drives hazard outcomes | 29 | 21 (+3 qualitative) | 20 |
| `ai_evidence.json` | AI successes and limitations along the four axes | 30 | 28 | 28 |
| `readiness_profile.json` | status per discipline and measure, citing row ids; no numbers of its own | 8 disciplines × 5 measures | | |
| `eos_guidelines.json` | Eos Opinion rules, read 2026-10-30 | 16 items | | 13 |
| `eos_evidence_brief.md` | sourced fact sheet for an Eos Opinion; not a draft (Eos bars AI-written text) | | | |
| `SUMMARY.md` | one-page summary: what is measurable, what needs data, headline | | | |

How the tables were made: five web-research subagents ran on 2026-10-30 under one sourcing protocol, and their output was reviewed in this session.
- Every Digital Object Identifier (DOI) was checked against the Crossref API.
- I re-read the following numbers in the downloaded text myself:
  - Pope et al. 2021, Table 1
  - Bretherton et al. 1999: 18.5 and 23.8
  - Gruszczynski et al. 2016: "nearly 40 %"
  - Faranda et al. 2017: D = 13
  - Issah & Martin: the singular-value remark
  - the Eos rule on AI tools, in the eos.org/submit page text
  - Dascher-Cousineau et al. 2023 and Stockman et al. 2023 abstracts (rows `ai-30`, `ai-31`)
- Everything else was read by a subagent and not re-read here.

Figures rebuild offline. Both scripts run with the standard library plus matplotlib, and the checks below run under `pixi run all`:

```bash
python scripts/complexity_tables.py
```

```bash
pixi run python scripts/complexity_figures.py
```

The first validates the five tables and the readiness profile against the sourcing rules. The second writes `build/complexity/fig1_power_law_exponents.{png,svg}`, `fig2_coupled_pde_counts.{png,svg}`, `fig3_readiness_profile.{png,svg}`, `power_law_pdf_exponents.csv` and `readiness_profile.csv`. The report and notebook rebuild with `pixi run -e report report` and `pixi run -e report notebooks`. `tests/test_complexity_tables.py` runs the validator inside `pixi run all`.

### Row conventions (all five tables)

Each row carries:
- `value`, or `value_min` and `value_max`, exactly as stated, plus `value_text` with the source's wording;
- `units`, `source`, `doi` or `url`, and `as_of` (publication year, or the data date the source gives);
- `quote`, a verbatim snippet of at most 25 words;
- `where_read`: full text, abstract, landing page, search snippet or not read;
- `checked_in_text`: true only when the number was seen in fetched text. Search snippets and memory count as false.

Other rules:
- A finding with no number starts its `value_text` with "qualitative:".
- Edits made after collection are logged in each table's `method` field or the row `notes`. One example: solar flares were moved to the comparison group because they are heliophysics.

## 1. Power laws: how many observables are heavy tailed, and has the power law been tested?

**Metric.** For each observable, record the stated exponent, its exact convention and whether that source compared the power law against alternatives. The usual alternatives are lognormal, stretched exponential and power law with exponential cut-off (truncated or tapered). Clauset, Shalizi & Newman (2009, doi 10.1137/070710111) set the standard test: maximum-likelihood fit, Kolmogorov-Smirnov (KS) goodness of fit, and likelihood-ratio tests.

**Caveat on conventions.** Exponents are comparable only within one convention:
- b-values are cumulative magnitude-frequency slopes.
- Kagan's beta is a survivor-function exponent on moment.
- Corral's beta and Clauset's alpha are density exponents.
- Hack's h is a geometric scaling exponent.
- The flood exponent a relates discharge to recurrence interval.

The table records each convention as stated and converts none. Figure 1 draws only the density-convention rows.

**What was found (24 geoscience rows with a value):**

| Test status in the source | Rows | Examples |
|---|---|---|
| Tested, power law favored | 4 | southern California seismic moment (Corral & González 2019); southern California b (Sornette et al. 1996); rockfall volumes (Dussauge et al. 2003); tropical cyclone power dissipation (Corral & González 2019) |
| Tested, mixed result | 4 | global Centroid Moment Tensor (CMT) moment, double power law; Omori-Utsu p (Utsu et al. 1995); landslide areas, double Pareto (Stark & Hovius 2001); Canadian wildfires |
| Tested, alternative favored or equally good | 5 | California earthquake amplitudes and US wildfires (Clauset 2009); global moment, tapered Pareto (Kagan 2010); global b with two regimes (Sornette 1996); Angola wildfires, truncated lognormal |
| Not tested in that source | 11 | landslide areas (Malamud 2004, Guzzetti 2002), Hack's law, drainage area, flood peaks, eruption sizes (Papale 2018, KS fit only), US and Australian wildfires (Malamud 1998), coastlines |

Selected values. All are in `power_laws.json`, with conventions.

| Observable | Exponent as stated | Source |
|---|---|---|
| Gutenberg-Richter b, southern California | 1.00 ± 0.02 up to moment magnitude about 7.5 | Sornette et al. 1996 |
| Omori-Utsu p, worldwide compilation | median about 1.1, range 0.6 to 2.5 | Utsu, Ogata & Matsu'ura 1995 |
| Seismic moment, survivor exponent beta | 0.63 to 0.67 | Kagan 2010 |
| Landslide area, density tail | 2.40 (written -2.40) | Malamud et al. 2004 |
| Hack's law h | 0.57 to 0.60 | Dodds & Rothman 1999, citing Maritan et al. 1996 |
| Explosive eruptions, VEI 3 and above | k = 1.95 | Papale 2018 |
| Coastline fractal dimension, west coast of Britain | 1.25 | Mandelbrot 1967 |

VEI is the Volcanic Explosivity Index.

**Comparison with other fields.** Clauset (2009) found 17 of 24 data sets consistent with a power law, and word frequency was the only one where no alternative was plausible. Its non-geoscience density exponents are word frequency 1.95, US city population 2.37, citations 3.16, web hits 1.81 and net worth 2.3, a span of 1.81 to 3.16. The geoscience density exponents in Figure 1 span 1.15 to 2.5. The two ranges overlap. On this evidence, heavy tails do not make geoscience unusual. They make it like other complex systems.

**What it can claim.**
- Heavy-tailed size distributions are documented for every hazard class in the table.
- Where the form was tested, a pure power law usually could not be distinguished from tapered or lognormal alternatives.
- Extrapolation to the largest events, where losses concentrate, therefore rests on a functional form the data do not pin down.

**What it cannot claim.**
- How many geoscience observables are heavy tailed in general. The table is a purposive sample, not a census.
- That the 11 untested rows would fail a test.
- Any comparison of exponents across conventions.

**Not found.**
- Fault-length exponent: the Bonnet et al. 2001 review was not readable.
- Holocene eruption tail: Deligne et al. 2010 uses an extreme-value model.
- Tsunami run-up exponents: Burroughs & Tebbens 2005 was seen in a snippet only.
- El-Isa & Eaton 2014, b from 0.3 to 2.5, is in the table but was seen in a search snippet only.

## 2. Dimensionality: nominal size versus effective dimension

**Metric.** There are two quantities, kept in separate rows:
- **Nominal dimension:** the named axes and their stated sizes, such as channels × time, grid × levels × variables, or pixels × acquisitions.
- **Effective dimension:** a published estimate by a named estimator. Examples are the number of empirical orthogonal functions (EOFs) or principal components needed for a stated variance fraction, the effective spatial degrees of freedom of Bretherton et al. (1999), a local attractor dimension, a maximum-likelihood estimate (MLE) of intrinsic dimension (Levina & Bickel), or a singular-value decomposition (SVD) rank.

**Caveat.** Effective dimension depends on region, variable, averaging period, variance threshold and estimator. The same Northern Hemisphere 500-hPa height field (Bretherton et al. 1999, December to February pentads, 672 grid points) gives:

| Estimator | Value |
|---|---|
| eigenvalue formula N*ef | 18.5 |
| moment matching N*mm | 23.8 |
| EOFs for 90% of variance | 27 |

**What was found.**

| Data set | Nominal (stated) | Effective (published) | Source |
|---|---|---|---|
| ERA5 reanalysis | 31 km native grid, 137 model levels, hourly; 0.25° and 37 pressure levels as distributed | not found | Hersbach et al. 2020; ECMWF and Copernicus Climate Data Store (CDS) pages |
| Northern Hemisphere 500-hPa height, winter | 672 grid points | 18.5 to 27 (estimator-dependent) | Bretherton et al. 1999 |
| Northern Hemisphere monthly surface temperature | 1002 grid points (5° × 5°) | about 60 (winter) to 90 (summer); annual global 45 | Wang & Shen 1999 |
| North Atlantic daily sea-level pressure | about 10^3 grid points | mean local attractor dimension 13, range 3 to 20 | Faranda, Messori & Yiou 2017 |
| GNSS, 87 Central European stations | 3 components × 87 stations | first principal component carries nearly 40% (North), over 50% (East, Up) of common-mode variance | Gruszczynski et al. 2016 |
| InSAR, Wolf volcano | 20 interferograms; 10^3 to 10^7 pixels per interferogram in general | 6 independent components (3 deformation) | Gaddes et al. 2018 |
| InSAR, Calbuco | 12 interferograms | reduced to 10 dimensions (authors' choice) | Ebmeier 2016 |
| DAS, Sacramento dark fiber | 12,000 channels at 500 Hz, about 0.3 PB in 7 months | not found | Ajo-Franklin et al. 2019 |
| DAS, Brady Hot Springs and urban fiber | about 8,000 channels at 1,000 samples/s | no rank given; singular values "close to uniform", lossy SVD compression tolerated to 100× for detection | Issah & Martin, Center for Wave Phenomena report CWP-1027 |
| Continuous seismic waveforms | 47,354 stations, 1.3 PB, 2002 to 2025 | not found | Ni et al. 2025 (Seismica; Marine Denolle is a co-author) |
| Volcanic tremor, Stromboli | single-station time series | embedding dimension "around five" (secondary) | Taylor et al. 2010, citing De Lauro et al. 2008 |
| CMIP6 output | 2068 requested variables; 20 to 40 PB projected | not found | Juckes et al. 2020; Eyring et al. 2016 |
| ImageNet, CIFAR-10, MNIST (comparison) | ImageNet tested at 224 × 224 × 3; the other image sizes were not read in the source | MLE 26 to 43; 13 to 26; 7 to 13 | Pope et al. 2021 |

CMIP6 is the Coupled Model Intercomparison Project phase 6.

**What it can claim.**
- Nominal sizes are large: about 8,000 to 12,000 channels per DAS array, and 47,354 seismic or 17,000 GNSS stations processed in single studies.
- Where effective dimension has been estimated for smooth climate fields, it is tens. That is the same order as natural-image benchmarks, not larger.
- The one DAS result points the other way: slow singular-value decay means DAS records are not obviously low rank.

**What it cannot claim.**
- That geoscience data are intrinsically higher-dimensional than other machine-learning (ML) data. The estimates are too few, cover different variables, and use estimators that give 18.5 to 27 on the same field.
- That the missing estimates are large.

**Needs new data.** This is the cheapest new measurement in the folder. Running one estimator (for example MLE intrinsic dimension with fixed k, plus EOF counts at 90%) on open samples would give the first comparable effective-dimension column for raw sensor data. Suitable samples include a public DAS record, a broadband waveform set already in SeisBench, an InSAR stack and an ERA5 subset.

## 3. Minimal coupled partial differential equations (PDEs): how many equations does a canonical coupled system need?

**What counts as "one PDE".** Every row uses the same rule, applied to the minimal model as written in one cited source:

1. Count each balance law (mass, momentum, energy, species) once. A vector equation counts as one (`balance_equations_vector`).
2. Expand vector equations into scalar components in the model's stated dimensionality. This gives `balance_equations_scalar_3d`, the plotted value: 3D momentum is 3, antiplane momentum is 1.
3. Count state variables evolved by ordinary differential equations (ODEs) at a point separately. Examples are rate-and-state theta and slip on a fault, or bubble radius.
4. List constitutive and closure relations (friction law, Darcy's law, equation of state, rheology, the three-equation melt closure) but do not count them.

The rule counts model size, not difficulty. Rate-and-state friction is one ODE plus one closure, yet it carries most of the earthquake-cycle problem.

**What was found** (Figure 2):

| System | Scalar balance equations + ODE states | Source |
|---|---|---|
| Rain infiltration and slope stability (factor of safety is algebraic) | 1, 1D vertical | Baum, Savage & Godt 2008, TRIGRS manual, following Iverson 2000 |
| Earthquake cycle, rate-and-state, quasi-dynamic or fully dynamic, 2D antiplane | 1 + 2 | Sequences of Earthquakes and Aseismic Slip (SEAS) benchmark BP1; Erickson et al. 2020 |
| Earthquake cycle with fluid injection | 2 + 2 | SEAS BP6 |
| Earthquake cycle, 3D | 3 + 3 | SEAS BP5; Jiang et al. 2022 |
| Biot poroelasticity, quasi-static | 4 | Merxhani 2016 (arXiv tutorial; Wang 2000 and Segall 2010 were not open) |
| Thermo-poro-elasticity | 5 | Brun et al. 2019 |
| Two-phase melt migration, simplified McKenzie | 5 | Rhebergen et al. 2014 |
| Ice sheet, full Stokes plus heat | 5 | Gagliardini et al. 2013 (Elmer/Ice) |
| Ice-shelf meltwater plume with three-equation melt, 1D steady | 4 | Jenkins 2011 |
| Volcanic conduit with bubble growth | 5 + 3 | Gonnermann & Manga 2007 |
| Atmosphere or ocean primitive equations | 6 each | MIT general circulation model (MITgcm) manual |
| Coupled atmosphere, ocean and sea ice | 17 (12 without sea ice) | MITgcm manual and sea-ice package |
| Comparison: incompressible Navier-Stokes, Maxwell, ideal magnetohydrodynamics | 4, 8, 8 | Fefferman (Clay problem); Goedbloed & Poedts notes |

TRIGRS is the US Geological Survey (USGS) Transient Rainfall Infiltration and Grid-based Regional Slope-stability program.

**What it can claim.**
- The minimal coupled models of solid-Earth hazards are small systems: 1 to 8 scalar equations plus 0 to 3 local state variables.
- Only the coupled climate core reaches 17.
- So the difficulty of these systems does not come from the number of coupled equations. It comes from:
  - closures that are empirical or poorly constrained (friction, permeability, rheology, melt-interface physics);
  - the span of time scales between rupture and interseismic loading, which the SEAS benchmarks are built to resolve;
  - parameters that are unobserved at depth.

**What it cannot claim.**
- A ranking of systems by difficulty.
- That the counts are unique. A different source or dimensionality changes them.

**Departures from the protocol** (see row notes):
- Full McKenzie 1984: equations not readable, so not found.
- Glacier-ocean: a composite of two sources, hatched in Figure 2.
- Iverson 2000: counted from the USGS implementation of it.
- Ideal magnetohydrodynamics: counts div B = 0 as an initial condition (8). Maxwell counts both divergence equations (8). Counted the way Maxwell is, ideal magnetohydrodynamics would be 9.

## 4. Unobserved drivers of outcomes

**Metric.** Sourced numbers on the parts of the risk chain that drive outcomes but are missing or poorly observed: fault inventories, the subsurface, exposure and building inventories, and the loss records themselves. Each row says what the number does not show.

**What was found:**

| Gap | Value | Source |
|---|---|---|
| Earthquake deaths in continental interiors vs plate boundaries, about 1890 to 2010 | at least 1,400,000 vs 800,000; often on faults not known beforehand (no fraction given) | England & Jackson 2011 |
| California moment rate off modeled faults, partly on unmodeled faults | 32% to 37% | Field et al. 2014 (UCERF3) |
| California smoothed seismicity inside modeled fault zones | 53% to 59% | Field et al. 2014 |
| UCERF2 faults with a measured slip rate | about 30% | Field et al. 2014 |
| 2016 Kaikōura rupture | at least 12 major faults, mapped and unmapped (no count of unmapped) | Hamling et al. 2017 |
| Seafloor mapped to modern resolution | 28.7% (GEBCO 2026 grid; trade-press reprint of the Seabed 2030 release) | Seabed 2030 announcement, April 2026 |
| Conterminous US with 1:24,000-scale geologic maps | 19.6% (1989 poll) | Soller & Berg 1997 |
| Urban population in cities with more than 80% complete OpenStreetMap (OSM) buildings | 16% (48% live in cities under 20% complete) | Herfort et al. 2023 |
| People exposed to the 100-year flood, 18 countries, by population layer alone | 101 to 134 million | Smith et al. 2019 |
| Emergency Events Database (EM-DAT) natural-hazard events missing total damage, 1990 to 2020 | 41.5% (insured damage 88.1%, deaths 1.3%) | Jones, Guha-Sapir & Tubeuf 2022 |
| EM-DAT entries without economic loss, 2000 to 2020, all disaster types | 80.38% | CRED Crunch No. 63, 2021 |
| EM-DAT undercount of fatal landslide events, 2004 to 2010 | about 2000% (fatalities 430%) | Froude & Petley 2018, citing Petley 2012 |

Definitions of the acronyms in the table:
- UCERF3: Uniform California Earthquake Rupture Forecast, version 3.
- GEBCO: General Bathymetric Chart of the Oceans.
- CRED: Centre for Research on the Epidemiology of Disasters.

Qualitative findings, with no number:
- Bouwer 2011: weather-loss trends are driven "primarily" by exposure growth.
- Crowley et al. 2005: vulnerability uncertainty exceeds ground-motion uncertainty for one scenario.
- Markhvida et al. 2020: a variance-based ranking of inputs to average annual loss puts building design level, an exposure attribute, first.

**What it can claim.**
- Outcome labels are sparse: EM-DAT lacks total damage for 41.5% of natural-hazard events.
- Exposure is weakly observed: 16% of the urban population lives where OSM buildings are more than 80% complete.
- A third to a half of California deformation and seismicity sits outside the modeled fault network.

**What it cannot claim.**
- A percentage of seismic loss variance due to exposure and vulnerability versus hazard. No peer-reviewed number was found (row `uo-05`), and the qualitative sources disagree on scope.
- A global fraction of the subsurface constrained by observation. Seafloor mapping is a surface quantity.
- The fraction of damaging earthquakes on unmapped faults. England & Jackson give no fraction, and the 2023 Türkiye ruptures were mainly on mapped faults (Reitman et al. 2023).

## 5. AI evidence along the four axes, and a readiness profile

**AI evidence.** `ai_evidence.json` holds 28 sourced results, each tagged with its axis and as a success or a limitation against a stated baseline. Both kinds were sought on purpose, so the counts describe what was collected, not how often AI succeeds.

| Axis | Successes | Limitations | Example success | Example limitation |
|---|---|---|---|---|
| Dimensionality | 8 | 2 | GraphCast beats the best operational deterministic system on 90% of 1,380 targets (Lam et al. 2023) | Pangu-Weather's effective resolution is 500 to 700 km on a 0.25° grid (Bonavita 2024) |
| Closures | 5 | 3 | a neural point process keeps forecast skill at M1.2 where ETAS degrades (Stockman et al. 2023) | neural convection and NeuralGCM fail at +4 K warming (Rasp et al. 2018; Kochkov et al. 2024) |
| Tails | 1 | 3 | probabilistic AI beats the IFS ensemble on record heat (Wessel et al. 2026, preprint) | the HRES physics model beats GraphCast, Pangu-Weather and FuXi (five configurations) on 2020 record extremes (Zhang et al. 2026) |
| Unobserved drivers | 3 | 3 | 1.4 billion building footprints from imagery (Microsoft) | building recall 70.9% in Africa against 85.9% in Europe |

ETAS is the epidemic-type aftershock sequence model; IFS and HRES are the ECMWF Integrated Forecasting System and its high-resolution configuration.

DeVries et al. (2018), the deep-learning aftershock study, was removed as a contested exemplar. On 2026-10-30, Nature and Crossref showed a Matters Arising (Mignan & Broccardo 2019) and a Reply, with no retraction notice. The Mignan & Broccardo limitation stays (`ai-22`).

**Readiness profile.** `readiness_profile.json` scores nothing. For 8 disciplines and 5 measures it records:
- a status: measured, partial, not found or not assessed;
- the row ids the cell rests on.

The measures are ML-ready share of the archive, published AI results, effective dimension, tail test, and unobserved drivers. The validator rejects:
- unknown row ids;
- statuses claimed without evidence;
- free-standing numbers in the notes.

Figure 12 of the report draws the profile.

**How the axes bear on AI readiness:**
- **Suited.** Native data are large over modestly sized measured structure, and the physics is few known laws plus empirical closures. Both are settings where learned representations and learned closures have documented gains.
- **Opportunity.** Small ML-ready shares of the archives (`docs/archive_readiness_2026-10-30`).
- **Work that remains.**
  - tails: the form is untested, and AI degrades on records;
  - labels: outcome and exposure data are missing;
  - transfer: regional models fail out of domain;
  - sensor data: no effective-dimension estimate for seismic, DAS or ERA5 archives.

## What this folder does not do

- It does not combine directions. Exponents, dimensions, equation counts and missing-data shares have different units and meanings, so there is no total.
- It does not claim geoscience is more complex than other fields. Where a comparison exists (directions 1 to 3), the geoscience values overlap the range of the comparison systems on these measures. The case for "hard to make AI-ready" rests on directions 1 and 4: tails that are heavy and poorly constrained, and outcomes and drivers that are unobserved. It does not rest on equation counts or intrinsic dimension.
