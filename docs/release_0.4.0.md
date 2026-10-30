# Version 0.4.0 release preparation

Prepared October 30, 2026. No tag, GitHub release, PyPI upload or Zenodo deposit
has been published by this preparation.

This version adds the domain-level solid-earth report, frozen platform and
simulation evidence, DAS screening tools and eleven editorial-style report
figures. Figures have larger text and PNG/SVG/PDF exports. Figure 9 uses `n =`,
defined as the count of metadata records saying AI-ready or ML-ready.

The DAS model screen remains unvalidated. Keyword counts do not measure actual
adoption, and the software supplies no universal AI-readiness score. Frozen
inputs and historical reference figures retain their original provenance.

## Rebuild and package

```sh
pixi run all
pixi run -e report report
pixi run python scripts/build_release.py
```

The package builder verifies repository checksums and stages only version-controlled
files. It creates a source ZIP, Python source distribution, wheel, separate report
figure ZIP and checksums under `dist/0.4.0/`. Build the report first: its generated
figures are included separately; they are not needed by the installed library.
The wheel installs the analysis and figure libraries and packaged DAS snapshots;
the source archives additionally contain the report, notebooks and protocols.
The optional figure ZIP requires all eleven PNG/SVG/PDF exports to be present.

Before publication, merge the reviewed PR, rerun validation and packaging from
that commit, and tag it `v0.4.0`. Attach the prepared archives and checksums to the
GitHub release. Register a DOI only after a real archival deposit; no DOI is
invented in the citation files. Historical validation receipts remain dated
records for earlier versions.
