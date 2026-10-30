# Evidence brief for an Eos Opinion, 30 October 2026

**Read first.** Eos does not accept proposals or articles written, in part or in full, with AI tools. The page eos.org/submit was read in the browser on 2026-10-30 and says: "Proposals (and articles) may not be written—in part or full—using artificial intelligence (AI) tools." This file is therefore a sourced fact sheet, not a draft, outline or proposal. The framing, structure and every sentence of the piece are yours to write.

Each fact below is copied from a row of the tables in this folder. The row id lets you open the quote, the as-of date and the read-in-text flag. Rows read only from an abstract, a preprint or a secondary source say so in their notes.

## Eos Opinion constraints

From the December 2025 author guidelines and eos.org/submit, retrieved 2026-10-30 (`eos_guidelines.json`):

| Item | Rule | Read in source text |
|---|---|---|
| Opinion maximum length | 1,500 words | yes |
| Opinion scope | identify a problem in the Earth and space science community (cultural or scientific) and offer solutions; move quickly to recommendations if the problem is widely known | yes |
| Number of references | no more than 12; hyperlinks to sources are an accepted and sometimes preferred alternative | yes |
| Hyperlinks vs reference list | in-line citations with a reference list at the end are allowed; linking text to outside sources is an alternative and 'in some cases ... the preferred and/or necessary approach'; the submit page says Eos prefers hyperlinks | yes |
| Number of figures | not found (no numeric cap; figures must be simple, non-technical and may be redesigned or declined) | yes |
| Lead image | required: an eye-catching landscape photograph, not a figure, collage or map; separate .jpg/.png files with caption and credit; permissions needed | yes |
| Headline length | up to 64 characters including spaces; no acronyms or abbreviations | yes |
| Teaser (dek) length | up to 200 characters including spaces; must not repeat the headline | yes |
| Author bio | not found (neither the guidelines PDF nor the submit page mentions a bio) | no (fetch summary only) |
| Maximum number of authors | 5; only people who write the manuscript; no project-team names | yes |
| Structure | narrative, not Abstract-Introduction-Methods; significance in first or second paragraph; subsections with subtitles; minimal lists | yes |
| Prior publication and preprints | must not have been published before, including as a preprint; posting drafts under Eos editing is not permitted | yes |
| Manuscript file format | .docx/.doc (or .txt); no PDF, no cloud links, no line numbers | yes |
| Submission route | proposal (outline, not a manuscript) via a Google Form linked from eos.org/submit; after acceptance, drafts go through Basecamp with the corresponding author only | no (fetch summary only) |
| Use of AI tools | proposals and articles may not be written, in part or full, with AI tools | yes |
| Timeline | proposal response within 4 weeks; manuscript due within 6 weeks of acceptance; about 8 weeks in queue; 14-18 weeks proposal to publication | no (fetch summary only) |

## Sourced facts by axis

### Dimensionality: large native data over modest measured structure

| Row | Fact as stated | Source | Link | Read in text |
|---|---|---|---|---|
| `dim-08` | 12000 channels sampled at 500 Hz; 2 m spatial sampling; 10 m gauge length | Ajo-Franklin et al. (2019), Scientific Reports | https://doi.org/10.1038/s41598-018-36675-8 | yes |
| `dim-14` | 47,354 stations spanning 2002-2025 | Ni et al. (2025), Seismica (arXiv 2505.18874) | https://doi.org/10.26443/seismica.v4i2.1738 | yes |
| `dim-26` | N*ef ≈ 19 (fitted 18.5); first N*ef EOFs explain about 82% of the variance | Bretherton et al. (1999), Journal of Climate | https://doi.org/10.1175/1520-0442(1999)012<1990:TENOSD>2.0.CO;2 | yes |
| `dim-31` | around 60 in the winter months and 90 in the summer months (NH); SH varies between 35 and 50 | Wang & Shen (1999), Journal of Climate | https://doi.org/10.1175/1520-0442(1999)012<1280:EOSDOF>2.0.CO;2 | yes |
| `dim-38` | between 26 and 43 (MLE k=3: 26; k=5: 38; k=10: 43; k=20: 43) | Pope et al. (2021), ICLR (arXiv 2104.08894) | https://arxiv.org/pdf/2104.08894 | yes |
| `dim-40` | MLE k=3: 7; k=5: 11; k=10: 12; k=20: 13 | Pope et al. (2021), ICLR (arXiv 2104.08894) | https://arxiv.org/pdf/2104.08894 | yes |
| `dim-13` | SVD compression tested at 5x to 100x; detection significance of mid-sized and large events preserved at 100x; error growth explained by a close to uniform distribution of singular values | Issah & Martin (n.d., CWP-1027), Center for Wave Phenomena Report, Colorado School of Mines | https://wpfiles.mines.edu/cwp/Website/Publications/Reports/CWP-1027_Issah.pdf | yes |
| `dim-18` | not found | none found in searches of 2026-10-30 |  | no |
| `ai-02` | AI success: two times more earthquakes using only a portion (less than 1/3) of seismic stations | Mousavi et al. (2020), Nature Communications | https://doi.org/10.1038/s41467-020-17591-w | yes |
| `ai-04` | AI success: outperforms the most accurate operational deterministic systems on 90% of 1380 verification targets | Lam et al. (2023), Science | https://doi.org/10.1126/science.adi2336 | yes |
| `ai-06` | AI success: greater skill than ENS on 97.2% of 1,320 targets | Price et al. (2025), Nature | https://doi.org/10.1038/s41586-024-08252-9 | yes |
| `ai-07` | AI success: PhaseNet-DAS v1 detects 2-5 times more events than PhaseNet across four DAS cables | Zhu et al. (2023), Nature Communications | https://doi.org/10.1038/s41467-023-43355-3 | yes |
| `ai-09` | AI limitation: effective resolution of Pangu-Weather forecasts is closer to 500-700 km than to the nominal 0.25 deg | Bonavita (2024), Geophysical Research Letters | https://doi.org/10.1029/2023GL107377 | yes |

### Coupled physics: few balance laws, empirical closures

| Row | Fact as stated | Source | Link | Read in text |
|---|---|---|---|---|
| `pde-01` | static equilibrium, antiplane (1 scalar) = 1 PDE; fault ODEs: slip delta (dδ/dt = V) and state theta = 2 | Erickson & Jiang (2018), SEAS Benchmark Problem BP1-QD description, SCEC; published in Erickson et al. (2020), Seismological Research Letters | https://doi.org/10.1785/0220190248 | yes |
| `pde-05` | equilibrium in displacements (3) + fluid mass balance / storage equation (1) = 4 | Merxhani (2016), An introduction to linear poroelasticity, arXiv:1607.04274 (follows Verruijt 1969 and Biot) | https://arxiv.org/pdf/1607.04274 | yes |
| `pde-17` | atmosphere 6 + ocean 6 + sea ice [momentum 2 (2D) + HEFF 1 + AREA 1 + HSNOW 1 = 5] = 17 | MITgcm User Manual: Section 1.3 and the SEAICE package chapter | https://mitgcm.readthedocs.io/en/latest/phys_pkgs/seaice.html | yes |
| `pde-18` | momentum (3) + incompressibility (1) = 4 | Fefferman (2006), Existence and smoothness of the Navier-Stokes equation, Clay Mathematics Institute Millennium Prize Problems | https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf | yes |
| `ai-13` | AI success: ensemble mean temperature RMSE for NeuralGCM stands at 0.16K ... climatology's RMSE of 0.45K | Kochkov et al. (2024), Nature | https://doi.org/10.1038/s41586-024-07744-y | yes |
| `ai-30` | AI success: improved fit and forecast accuracy compared to our benchmark when the training set is sufficiently long (>10^4 events) | Dascher-Cousineau et al. (2023), Geophysical Research Letters | https://doi.org/10.1029/2023gl103909 | yes |
| `ai-31` | AI success: both models perform similarly above M3; lowering the threshold to M1.2 reduces the performance of ETAS unlike the neural model | Stockman, Lawson & Werner (2023), Earth's Future | https://doi.org/10.1029/2023ef003777 | yes |
| `ai-15` | AI success: R2 value of 0.89 (naive periodicity model: 0.3) | Rouet-Leduc et al. (2017), Geophysical Research Letters | https://doi.org/10.1002/2017GL074677 | yes |
| `ai-12` | AI limitation: NNCAM trained on reference climate only is unable to generalize to much warmer climates (+4K SST) | Rasp, Pritchard & Gentine (2018), PNAS | https://doi.org/10.1073/pnas.1810286115 | yes |
| `ai-14` | AI limitation: for more substantial SST increases (+4K), NeuralGCM's response diverges from expectations | Kochkov et al. (2024), Nature | https://doi.org/10.1038/s41586-024-07744-y | yes |
| `ai-22` | AI limitation: AUC = 0.85 using 2 free parameters versus the 13,451 parameters ...; improved AUC = 0.86 | Mignan & Broccardo (2019), Nature | https://doi.org/10.1038/s41586-019-1582-8 | yes |

### Heavy tails: common, form rarely settled

| Row | Fact as stated | Source | Link | Read in text |
|---|---|---|---|---|
| `pl-summary-clauset` | 17 of the 24 data sets | Clauset, Shalizi & Newman (2009), SIAM Review | https://doi.org/10.1137/070710111 | yes |
| `pl-02` | 1.655 (bootstrap 1.65 +/- 0.04) | Corral & Gonzalez (2019), Earth and Space Science | https://doi.org/10.1029/2018EA000479 | yes |
| `pl-04` | 0.63–0.67 (catalog estimates); Table 2: 0.6820 global, mt = 5.8, 5450 events; proposed bias-corrected 0.52–0.56 | Kagan (2010), Tectonophysics | https://doi.org/10.1016/j.tecto.2010.04.034 | yes |
| `pl-22` | beta = 1.818 above 63 ha (p 0.22, n 1,294, 3.63 decades); bootstrap 1.79 ± 0.07 | Corral & Gonzalez (2019), Earth and Space Science | https://doi.org/10.1029/2018EA000479 | yes |
| `pl-12` | alpha+1 = 2.11 (Taiwan); alpha+1 = 2.46 ± 0.2 (New Zealand) | Stark & Hovius (2001), Geophysical Research Letters, as reported in Guzzetti (2006), PhD dissertation ch. 5 'Statistics of landslide size' | https://doi.org/10.1029/2000GL008527 | yes |
| `ai-17` | AI limitation: HRES still consistently outperforms state-of-the-art AI models ...; 162,751 heat, 32,991 cold, and 53,345 wind records | Zhang et al. (2026), Science Advances | https://doi.org/10.1126/sciadv.aec1433 | yes |
| `ai-18` | AI success: WeatherNext2 achieves Brier skill scores over the IFS of 23% at the 90th percentile and 24% (23-26%) for record-breaking extreme events | Wessel et al. (2026), arXiv preprint 2610.20519 | https://arxiv.org/pdf/2610.20519 | yes |
| `ai-19` | AI limitation: mslp barely reaches below 980 hPa | Sun et al. (2025), PNAS | https://doi.org/10.1073/pnas.2420914122 | yes |
| `ai-20` | AI limitation: saturation starts ... around 5.5 for Italy and 6.0 for Chile | Munchmeyer et al. (2021), Geophysical Journal International | https://doi.org/10.1093/gji/ggab139 | yes |

### Unobserved drivers and missing labels

| Row | Fact as stated | Source | Link | Read in text |
|---|---|---|---|---|
| `uo-23` | missing for 96.2% (reconstruction costs), 88.1% (insured damages), 41.5% (total estimated damages); total deaths 1.3% | Jones, Guha-Sapir & Tubeuf (2022), Scientific Data | https://doi.org/10.1038/s41597-022-01667-x | yes |
| `uo-19` | 1,848 urban centres (16% of the urban population) exceed 80%; 9,163 cities (48% of the urban population) below 20% | Herfort et al. (2023), Nature Communications | https://doi.org/10.1038/s41467-023-39698-6 | yes |
| `uo-10` | between 32% and 37% (UCERF2-implied: 27%) | Field et al. (2014), Bulletin of the Seismological Society of America 104(3) | https://doi.org/10.1785/0120130164 | yes |
| `uo-12` | Only about 30% | Field et al. (2014), Bulletin of the Seismological Society of America 104(3) | https://doi.org/10.1785/0120130164 | yes |
| `uo-06` | at least 1,400,000 deaths (continental interiors) vs 800,000 (plate boundaries) | England & Jackson (2011), Nature Geoscience | https://doi.org/10.1038/ngeo1168 | yes |
| `uo-05` | not found | not found |  | no |
| `ai-23` | AI success: 516M Africa-wide detected footprints | Sirko et al. (2021), arXiv preprint 2107.12283 | https://arxiv.org/pdf/2107.12283 | yes |
| `ai-24` | AI limitation: 19.4M km2, 64% of the land surface of the continent | Sirko et al. (2021), arXiv preprint 2107.12283 | https://arxiv.org/pdf/2107.12283 | yes |
| `ai-26` | AI limitation: Africa precision 94.4%, recall 70.9% (Europe 94.3% / 85.9%) | Microsoft (2026), GlobalMLBuildingFootprints repository README | https://github.com/microsoft/GlobalMLBuildingFootprints | yes |
| `ai-27` | AI success: catalog of ~900,000 earthquakes ... an order of magnitude more events than the catalog routinely produced | Tan et al. (2021), The Seismic Record | https://doi.org/10.1785/0320210001 | yes |
| `ai-28` | AI limitation: no model trained on a regional dataset reaches an AUC score above 0.75 for detection on GEOFON ... in-domain performance of 0.85 to 0.99 | Munchmeyer et al. (2022), JGR Solid Earth | https://doi.org/10.1029/2021JB023499 | yes |

## Statements the evidence does not support

- That AI handles higher-dimensional problems than physics-based methods. The sourced point is narrower: learning cost scales with intrinsic dimension (Pope et al. 2021), and the measured effective dimensions of climate fields are tens while native data are far larger. No estimate exists for seismic, distributed acoustic sensing (DAS) or ERA5 reanalysis data.
- That geoscience is more complex than other fields. Exponents, equation counts and effective dimensions overlap the comparison systems in these tables.
- Any single readiness or complexity score. The profile (`readiness_profile.json`, figure 12 of the report) is a set of separate measures.
- A percentage of seismic loss variance due to exposure and vulnerability (row `uo-05`: not found).
- That DeVries et al. (2018) was retracted. As of 2026-10-30, Nature and Crossref show a Matters Arising (Mignan & Broccardo 2019) and a Reply (Meade 2019), with no retraction notice. It was removed from the evidence table as a contested exemplar.

## Figures

Eos asks for simple, non-technical figures that its staff may redesign, and a landscape photograph as the lead image, not a figure. The report figures (`docs/report/ai_readiness_solid_earth.html`, figures 5 and 10 to 12) are technical; any Eos figure would be a simplified redraw from the same tables.
