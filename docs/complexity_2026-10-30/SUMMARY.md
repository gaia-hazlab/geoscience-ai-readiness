# Geoscience complexity: summary for Marine, 30 October 2026

**Recommended headline: the tail problem.** In the 24 geoscience power-law rows that report an exponent:
- 13 were tested against alternatives, and only 4 of those 13 favored a pure power law;
- the other 11 were never tested in the cited source.

So extreme-event statistics, where losses concentrate, rest on a functional form the data do not pin down. That is a defensible, sourced statement about why learning from geoscience data is hard. Its companion for AI readiness is the label gap: EM-DAT, the Emergency Events Database, has no total-damage estimate for 41.5% of natural-hazard events from 1990 to 2020 (Jones, Guha-Sapir & Tubeuf 2022).

**Not recommended as a headline:**
- **Equation counts.** Minimal coupled geoscience models need 1 to 17 scalar balance equations, against 4 to 8 for Navier-Stokes, Maxwell and magnetohydrodynamics. Equation count does not separate geoscience from physics; closures and scale span do.
- **Intrinsic dimension.** Published estimates for smooth climate fields are tens: 18.5 to 27 for Northern Hemisphere 500-hPa height, and 27 to 90 for surface temperature, depending on hemisphere and averaging (Wang & Shen 1999). Natural-image benchmarks give 7 to 43 (Pope et al. 2021). There is no estimate for seismic, distributed acoustic sensing (DAS) or ERA5 reanalysis data. The evidence does not show geoscience data to be intrinsically higher-dimensional.

## What is measurable now (sourced, in this folder)

| Direction | Measured | Table |
|---|---|---|
| Power laws | exponent, convention, test verdict for 24 geoscience and 6 comparison rows | `power_laws.json` |
| Dimensionality | 20 nominal sizes; 16 published effective-dimension values, 4 of them comparisons | `dimensionality.json` |
| Coupled partial differential equations (PDEs) | balance-equation and state counts for 16 geoscience and 3 physics systems under one counting rule | `coupled_pdes.json` |
| Unobserved drivers | 21 sourced gaps: faults, seafloor, geologic maps, building completeness, loss records, gauges | `unobserved_drivers.json` |

## What needs new data or analysis

| Gap | What would close it | Cost |
|---|---|---|
| Power law: 11 untested rows | Refit with the Clauset et al. (2009) tests on open catalogs: ComCat earthquakes, a landslide inventory, a wildfire perimeter database, USGS peak flows | days; keyless public data |
| Effective dimension of sensor data | One estimator (maximum-likelihood intrinsic dimension at fixed k, plus EOF count for 90% of variance) on an open DAS record, a SeisBench waveform set, an InSAR stack and an ERA5 subset, compared with the image benchmarks | days to a week; laptop or one GPU |
| Loss variance split (hazard vs exposure vs vulnerability) | No peer-reviewed percentage found. It needs a variance decomposition with an open risk engine (for example GEM OpenQuake) on a published exposure model | weeks; a study in itself |
| Fraction of damaging earthquakes on unmapped faults | No sourced fraction. It needs a catalog of damaging events matched against pre-event fault databases | weeks |
| Full McKenzie 1984 equation count; Wang 2000 and Segall 2010 Biot | Library access to the closed texts | hours |

ComCat is the USGS Comprehensive Earthquake Catalog; GEM is the Global Earthquake Model foundation; EOF is empirical orthogonal function.

## Caveats

- The tables are purposive samples of the literature, not a census.
- Most rows were read by subagents. I re-read five key numbers myself, listed in `README.md`.
- Several rows were read from the abstract only, and `where_read` marks them.
- Ni et al. (2025), the source of the 47,354-station figure, has you as a co-author.
- The Seabed 2030 figure of 28.7% comes from a trade-press reprint of the release.
