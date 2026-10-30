# Figures for an Earth science opinion piece

The report uses a shared editorial style in `scripts/figure_style.py`, applied by
`archive_readiness_figures.py` and `explore_das_semantic.py`.

- Ocean teal is the main evidence color; burnt ochre distinguishes solid-earth
  subfields or a second series. Moss, gold and plum distinguish additional DAS
  categories; stone marks comparison fields or unresolved records. Read each
  panel's labels: colors do not identify a single discipline across all figures.
- Warm paper, dark mineral-colored text and serif headlines set an editorial
  tone. Sans-serif data labels and light grids support close reading.
- Linear comparisons use stems and dots, starting at zero. Log-volume charts
  use points: horizontal bar length on a logarithmic scale is misleading.
  Missing volumes remain written statements, never zero-valued points.
- Titles describe the available evidence. Keyword mentions are not measured
  adoption; the DAS semantic screen remains an explicitly unvalidated draft.
- Sources sit in a separate band beneath each plot. Tight export bounds retain
  long labels. PNGs are 300 dpi; SVG and PDF retain vector marks and text.

Rebuild all eleven report figures and the self-contained HTML report with:

```sh
pixi run -e report report
```

Exports are under `build/archive_readiness/` and `build/das_semantic/`. The report
is `docs/report/ai_readiness_solid_earth.html`. Historical reference exports and
frozen evidence snapshots are not restyled or modified.
