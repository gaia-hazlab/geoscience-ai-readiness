# Historical exploratory sources — not the current inference workflow

Unchanged October 21 sources, frozen for audit:

- `community_demand/collect_openalex.py` makes requests at top level on execution
  **or import**. Do not import it. Its historical API syntax may be obsolete.
  The standalone harvester has a guarded, explicit opt-in interface.
- `community_demand/assemble_analysis.py` reads neighboring frozen inputs. Its
  preliminary judgments are **hard-coded by topic and rank**. Never apply those
  labels to refreshed results, changed rankings or another corpus. New review
  must bind stable paper IDs and evidence using `tools/ai_readiness/`.
- The twenty-paper sample is most-cited, single-reviewer preliminary screening,
  with three missing abstracts. It is not random and gives no population
  prevalence, demand or adoption estimate. Do not turn its category counts into
  percentages of a field. The separate frozen DAS keyword series measures activity.
- `targeted_evidence/build_need_evidence.py` assembles hand-curated public-source
  evidence and reference suggestions, not a systematic review. It writes files
  beside itself at top level, including a historical proposed text insert;
  it never edits a live proposal.

Use separate copies when auditing these scripts. Default checks never execute
collectors or this targeted assembler. Private holdings, mixed private/public
manifests and live-proposal revision builders were excluded. Rerunning the ranked
screening assembler against a refreshed search is scientifically invalid.
