from pathlib import Path
import csv, json

OUT = Path(__file__).resolve().parent
date = '2026-10-21'
rows = []
def add(id, title, year, doi, url, section, quote, evidence_type, interpretation, caveat, existing_resources, quantitative, access_note):
    assert len(quote.split()) <= 25, (id, len(quote.split()))
    rows.append(dict(id=id, title=title, year=year, doi=doi, source_url=url,
      source_section=section, short_exact_quote=quote, quote_word_count=len(quote.split()),
      evidence_type=evidence_type, interpretation=interpretation, limitation=caveat,
      existing_or_competing_resources=existing_resources, quantitative_evidence=quantitative,
      access_note=access_note, checked_on=date))

add('D01', 'Distributed Acoustic Sensing Community Resources', 2022, None,
 'https://web-archive-2022.iris.edu/hq/files/initiatives/das_rcn/Distributed_Acoustic_Sensing_Community_Resources_White_Paper.pdf',
 'Discussion and Recommendations, PDF page 5; survey methods/results pages 1–4',
 'the importance of developing a standard data and metadata format for DAS as well as supporting data handling, management, and distribution.',
 'Community survey and open community discussion; organizational white paper',
 'Direct evidence that some surveyed DAS users asked for common data/metadata and handling support. Prospective technology use establishes a user pool; data comments specify the interoperability problem.',
 'Anonymous, self-selected 10-question survey distributed through RCN mailing list/working groups; seismology overrepresented and authors note uncertainty in data-resource responses. Neither 90% nor 75% measures demand for AI-ready data. Number of respondents making the standards request is not reported. Authors call sample representative, but no probability sampling supports a population estimate.',
 'PASSCAL and CTEMPs instrument/training models already existed; respondents with their own resources also expressed interest in shared resources.',
 '95 respondents; contemporaneous mailing list 468 subscribers; 90% interested in DAS research/teaching within next five years; ~75% anticipated using instrument lending plus training at least once in five years; about half lacked one or more instrument/training/data-handling resources. These percentages are rounded source values, not counts derived here.',
 'Open six-page primary PDF read in full through web tool; page/line evidence verified. No DOI shown in the document.')

add('D02', 'Distributed Acoustic Sensing Research Coordination Network (DAS RCN) Final Report', 2025,
 '10.5281/zenodo.16924687', 'https://zenodo.org/records/16924687',
 'Depositor description; report §2.3 Community Surveys, printed page 8, indexed PDF passage',
 'Respondents also indicated that training and support of experimental design and data processing and storage continue to be needed.',
 'Community coordination report / capstone workshop synthesis; repeats the D01 survey',
 'Records multi-community needs and continuity of access, storage and processing priorities through the RCN; useful Flagship stewardship and support rationale.',
 'Not an independent second survey. Report rounds 95 responses to ~100. Do not add D01/D02 respondent counts. Published record describes June 2023 capstone process, but a capstone participant/institution count was not verified. No AI-ready-data preference percentage was measured.',
 'Approximately a dozen working groups, community forums, training activities and a DAS instrument collaborative; these are infrastructure/community foundations, not commitments to this proposal.',
 'Report says mailing list eventually exceeded 500; ~100 survey responses, 60% early-career, 90% considering DAS within five years. Prefer original D01 N=95 when quoting the survey. Verified participation breadth includes geomorphology, cryosphere, hydrology and volcanology.',
 'Zenodo primary depositor description read directly. Main PDF could not be opened by the web parser; §2.3 full indexed passage retrieved through primary-URL search. Do not claim entire report was read.')

add('D03', 'Toward a Metadata Standard for Distributed Acoustic Sensing (DAS) Data Collection', 2024,
 '10.1785/0220230325', 'https://doi.org/10.1785/0220230325', 'Abstract',
 'a need to implement a metadata standard specifically for DAS to facilitate the integration of DAS measurements across experiments and increase reusability.',
 'Peer-reviewed research article; explicit problem statement and proposed metadata solution',
 'Direct cross-deployment interoperability/reusability need; test project learning-record descriptions against this existing domain metadata effort rather than claiming no DAS standard exists.',
 'Abstract inspected; full article unavailable at publisher. This establishes a domain-metadata need and existing solution, not demand for our particular release or proof a metadata standard alone enables foundation models.',
 'Existing hierarchical experiment metadata describes interrogator, acquisition, channels, cable and fiber, demonstrated on four common and two hypothetical scenarios. FDSN DAS-metadata development is an additional current implementation to consider.',
 'Five experiment components; four common deployment scenarios and two hypothetical scenarios in the paper abstract.',
 'Primary publisher abstract retrieved in full; publication date and DOI verified. No discussion-section inference.')

add('D04', 'SeisBench: A Toolbox for Machine Learning in Seismology', 2022,
 '10.1785/0220210324', 'https://publikationen.bibliothek.kit.edu/1000146886',
 'Abstract of author-deposited preprint linked from published-paper repository record',
 'quality controlled benchmark datasets that contain representative class distributions are vital.',
 'Peer-reviewed software/framework paper; primary author preprint abstract used for passage',
 'Direct need for representative benchmarks and common model/data access. Supports measuring class coverage, distributions and loading burden as readiness dimensions.',
 'Passage verified in author preprint abstract, not re-read in publisher version. Existing SeisBench already standardizes model/data access: proposal must complement it, not erase it.',
 'SeisBench common API, models, datasets, preprocessing and augmentation. Published journal record DOI verified separately.',
 'No quantitative user-demand estimate extracted. Repository citation counts intentionally not used as adoption evidence.',
 'KIT primary institutional records: preprint https://publikationen.bibliothek.kit.edu/1000146910 and published article https://publikationen.bibliothek.kit.edu/1000146886.')

add('D05', 'Comprehensive Dataset for Event Classification Using Distributed Acoustic Sensing (DAS) Systems', 2025,
 '10.1038/s41597-025-05088-4', 'https://www.nature.com/articles/s41597-025-05088-4.pdf',
 'Abstract, PDF page 1; scope verified in Methods/Data Records',
 'the lack of large, high-quality datasets has hindered progress.',
 'Peer-reviewed data descriptor; explicit dataset-availability gap plus delivered dataset',
 'Direct data-quality and label-availability gap in DAS event classification; surrounding methods specify where existing coverage is concentrated.',
 'One campus acquisition, predominantly sunny April 2023 conditions, labeled anthropogenic/security events. This does not represent all DAS environments or establish absence of open DAS datasets. High within-dataset CNN accuracy is not proof of cross-site generalization.',
 'Published labeled campus DAS dataset in HDF5 with JSON annotation and NumPy masks, data loading code, nine table labels.',
 'Paper Table 1 lists 14 raw HDF5 files totaling 47.0 GB (sum of nine rounded row sizes); 324,465 labeled windows (sum of table counts), not 324,465 independent physical events. Do not compare window counts to earthquakes or simulations without a sample-unit definition.',
 'Open publisher PDF read through Methods/Data Records/Technical Validation; DOI, authors, acquisition scope and table values verified. Local sums explicitly labeled calculations.')

add('D06', 'Caravan - A global community dataset for large-sample hydrology', 2023,
 '10.1038/s41597-023-01975-w', 'https://www.nature.com/articles/s41597-023-01975-w', 'Abstract',
 'these datasets lack standardization, which makes global studies difficult.',
 'Peer-reviewed community data descriptor; explicit standardization need plus implemented solution',
 'Shows both demand for harmonization and feasibility of extensible community curation. Useful analogue for cross-holding physical alignment, provenance and licensing.',
 'This 2023 paper documents the then-current baseline, not current 2026 archive size or user count. Need must be articulated as added modalities/native-resolution support/physically justified joins; standard hydrologic datasets already exist.',
 'Caravan aggregates seven prior regional collections, harmonizes forcing/flow/attributes and provides cloud software for community extension.',
 'Initial release: 6,830 catchments, seven regional datasets, daily records 1981–2020, median record 31 years. These are data coverage counts, not demand counts.',
 'Open primary full text read including Abstract, Background & Summary, Methods and Data Records. Paper DOI distinct from data release DOI 10.5281/zenodo.7540792.')

add('D07', 'OpenFWI: Large-scale Multi-structural Benchmark Datasets for Full Waveform Inversion', 2022,
 '10.52202/068431-0435', 'https://papers.neurips.cc/paper_files/paper/2022/file/27d3ef263c7cb8d542c4f9815a49b69b-Paper-Datasets_and_Benchmarks.pdf',
 '§6.1 Future Challenges, printed page 10; Abstract/Table 1 for scope',
 'We expect more robust methods to handle data from different domains.',
 'Peer-reviewed benchmark dataset paper; empirical generalization tests plus explicit remaining challenge',
 'Direct evidence that standardized simulation benchmarks do not remove domain-transfer failures. Dataset heterogeneity, physical coverage and held-out domains should therefore be documented and evaluated.',
 'Primarily acoustic controlled-source FWI, not a proxy inventory for Alice Gabriel’s dynamic rupture archive. It already supplies large public simulation data; cannot support a blanket no-simulation-data claim. A call for robust methods does not by itself require more raw volume.',
 'OpenFWI provides 12 datasets, 2.1 TB, multiple geology configurations, 11 two-dimensional sets and one three-dimensional set, with supervised/unsupervised baselines.',
 '12 datasets / 2.1 TB; individual reported sizes 2K–67K in abstract; 3D subset 1.4 TB. Existing availability and technical scale, not community adoption counts.',
 'Primary conference PDF and official abstract both read. Discussion explicitly identifies generalization degradation, efficiency and passive-seismic work as future challenges.')

add('D08', 'Supervised Machine Learning of High Rate GNSS Velocities for Earthquake Strong Motion Signals', 2022,
 '10.1029/2022JB024854', 'https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2022JB024854',
 '§2.1 Signals of Interest',
 "Inclusion of this extended, real-world noise data set in training and validating will improve the model's generalization, or performance on unseen data.",
 'Peer-reviewed empirical method and data-construction study',
 'Specific methodological evidence for noise-diverse event-aligned geodetic samples and event-level partitions; supports evaluating more than signal-only counts.',
 'Authors describe expected generalization contribution of noise data. This is not a survey or independent community request; no inference that simply increasing total bytes guarantees improved models.',
 'UNAVCO/EarthScope GNSS archive and COMCAT already used together; source observables processed to TDCP velocities and manually labeled.',
 '1,701 station–event pairs from 77 earthquakes; 1,507 noise time series from 904 stations. Event-split nested cross-validation avoids event-waveform leakage.',
 'Open primary full text read: Abstract, Introduction, §2.1, feature engineering, nested cross-validation and Results/Discussion.')

add('D09', 'Research priorities for global food security under extreme events', 2022,
 '10.1016/j.oneear.2022.06.008', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC9307291/', 'Discussion',
 'both scientists and practitioners have a need for more granular data and better maps, and improved predictive capacity.',
 'Peer-reviewed expert elicitation / community research-priority exercise',
 'Direct evidence of need from a diverse expert process for granular validated impact data, mapping and prediction across hazards and food systems; connects directly to intended impact holdings.',
 'Purposefully assembled panel, not a representative prevalence survey. Priorities are for food-system research broadly; do not describe 69 people as endorsing this project or requesting a common AI format. Existing public data and services are not absent; ground validation, governance and effective use are substantive needs.',
 'Existing forecasting, monitoring, humanitarian-response tools and acute food-insecurity classifications; identified data/governance constraints remain.',
 '69 experts; 179 submitted research questions prioritized into 50; 32 threats. Counts reflect the elicitation exercise, not dataset users or platform adoption.',
 'Open primary full text on PMC read including Introduction, Research priorities, Better maps and predictions, Discussion; existing bibliography already includes this paper.')

add('D10', 'EarthSE: A Benchmark Evaluating Earth Scientific Exploration Capability for Large Language Models', 2026,
 None, 'https://proceedings.iclr.cc/paper_files/paper/2026/hash/d4ce6738e84876aa79f13c8bc8b7c5eb-Abstract-Conference.html', 'Abstract',
 "current benchmarks typically neglect the assessment of LLMs' capabilities in open-ended scientific exploration.",
 'Peer-reviewed ICLR benchmark paper; explicit evaluation-gap claim plus new benchmark',
 'Shows existing domain-specific scientific-exploration evaluation and remaining performance gaps. Compare our executable, held-out physical workflows rather than claiming no Earth-science benchmarks exist.',
 'The quoted historical motivation is addressed in part by EarthSE itself. Open-ended dialogue/QA does not establish complete executable-agent reliability. No DOI displayed by official proceedings; use official stable paper URL, not an invented DOI.',
 'Earth-Iron, Earth-Silver and Earth-Gold; paper-derived QA and multi-turn exploration dialogues with new metrics.',
 '100,000-paper construction corpus; five spheres, 114 disciplines, 11 task categories; 11 LLMs evaluated. These are coverage/evaluation counts, not community demand or users.',
 'Official proceedings abstract read; official PDF inspected for construction, expert dimensions and evaluation limitations.')

add('D11', 'EarthVerse: Benchmarking Scientific Agents Across Dynamic Earth Systems and Natural Hazards', 2026,
 '10.48550/arXiv.2608.23525', 'https://arxiv.org/abs/2608.23525v1', 'Abstract, version 1 dated August 24, 2026',
 'current agents often complete individual steps without maintaining a consistent chain across evidence, scales, units, calculations, and physical interpretation.',
 'Primary research preprint; existing executable Earth-science agent benchmark and reported empirical failures',
 'Direct competing benchmark evidence; supports reliability across evidence/scale/units as a measurable remaining problem and a reason to specify distinct project tasks/holdouts.',
 'Preprint, not peer-reviewed publication as of checked version. Performance is authors’ evaluation, not independently replicated here. Does not establish that project benchmarks are unique or that there is community demand for this specific platform.',
 'EarthVerse already provides heterogeneous event packages, executable ground truth and fine-grained scoring.',
 '405 tasks, 199 documented events, 19 hazard families, 25 model/agent systems; best mean answer-unit accuracy 84.65%, highest Strict@95 34.81%. Metrics are different aggregations and must not be treated as matched performance from one model unless tables verify.',
 'Primary arXiv versioned abstract read. Version and DOI verified; do not treat current GitHub mutable state as versioned paper evidence.')

doc = {
 'date': date, 'purpose': 'Targeted auditable evidence sample for Section 1.2; not a systematic review or representative prevalence estimate',
 'method': 'Targeted primary-source searches across DAS metadata/data management, ML seismology benchmarks, hydrology, geodetic event/noise records, food-system expert priorities and Earth-science agent evaluation. Need statements screened and surrounding scope checked. Discussion quoted only where open full text was directly read. RCN report passage transparently labeled indexed primary-PDF retrieval.',
 'independence': 'D01 and D02 are the same 2022 DAS survey process; do not count as two independent samples.',
 'sources': rows
}
(OUT/'Community_Need_Evidence_2026-10-21.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2)+'\n')
with (OUT/'Community_Need_Evidence_2026-10-21.csv').open('w', newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

refs = [
 dict(key='Aderhold2022',authors=['Kasey Aderhold','Scott Tyler','Danica Roth'],year=2022,
 title='Distributed Acoustic Sensing Community Resources',venue='DAS Research Coordination Network white paper',date='May 5, 2022',doi=None,
 url=rows[0]['source_url'],verified_full_author_list=True,citation='Kasey Aderhold, Scott Tyler, and Danica Roth (2022). Distributed Acoustic Sensing Community Resources. DAS Research Coordination Network white paper, May 5, 2022. '),
 dict(key='Lai2024',authors=['Voon Hui Lai','Kathleen M. Hodgkinson','Robert W. Porritt','Robert Mellors'],year=2024,
 title='Toward a Metadata Standard for Distributed Acoustic Sensing (DAS) Data Collection',venue='Seismological Research Letters',volume='95',issue='3',pages='1986–1999',doi='10.1785/0220230325',url='https://doi.org/10.1785/0220230325',
 verified_full_author_list=True,citation='Voon Hui Lai, Kathleen M. Hodgkinson, Robert W. Porritt, and Robert Mellors (2024). Toward a Metadata Standard for Distributed Acoustic Sensing (DAS) Data Collection. Seismological Research Letters, 95(3), 1986–1999. '),
 dict(key='Kratzert2023',authors=['Frederik Kratzert','Grey Nearing','Nans Addor','Tyler Erickson','Martin Gauch','Oren Gilon','Lukas Gudmundsson','Avinatan Hassidim','Daniel Klotz','Sella Nevo','Guy Shalev','Yossi Matias'],year=2023,
 title='Caravan - A global community dataset for large-sample hydrology',venue='Scientific Data',volume='10',article_number='61',doi='10.1038/s41597-023-01975-w',url='https://doi.org/10.1038/s41597-023-01975-w',
 verified_full_author_list=True,citation='Frederik Kratzert, Grey Nearing, Nans Addor, Tyler Erickson, Martin Gauch, Oren Gilon, Lukas Gudmundsson, Avinatan Hassidim, Daniel Klotz, Sella Nevo, Guy Shalev, and Yossi Matias (2023). Caravan - A global community dataset for large-sample hydrology. Scientific Data, 10, 61. '),
 dict(key='Deng2022',authors=['Chengyuan Deng','Shihang Feng','Hanchen Wang','Xitong Zhang','Peng Jin','Yinan Feng','Qili Zeng','Yinpeng Chen','Youzuo Lin'],year=2022,
 title='OpenFWI: Large-scale Multi-structural Benchmark Datasets for Full Waveform Inversion',venue='Advances in Neural Information Processing Systems',volume='35',doi='10.52202/068431-0435',url='https://doi.org/10.52202/068431-0435',
 verified_full_author_list=True,citation='Chengyuan Deng, Shihang Feng, Hanchen Wang, Xitong Zhang, Peng Jin, Yinan Feng, Qili Zeng, Yinpeng Chen, and Youzuo Lin (2022). OpenFWI: Large-scale Multi-structural Benchmark Datasets for Full Waveform Inversion. Advances in Neural Information Processing Systems, 35, Datasets and Benchmarks Track. ')
]
(OUT/'Community_Need_Recommended_New_References_2026-10-21.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')

summary = '''Community need: verified evidence and proposed short insert — October 21, 2026

The strongest quantitative evidence is an existing DAS community survey, not keyword-publication growth. Aderhold, Tyler and Roth (May 2022) report 95 responses to a ten-question anonymous survey; 90% anticipated DAS use for research or teaching within five years. This is prospective adoption of a sensing technology, not a percentage asking for AI-ready datasets. The useful direct need evidence is the discussion: some open comments requested common data/metadata and handling/distribution support. No count of such comments is reported. Seismology is overrepresented, data-resource questions may have confused some participants, and this self-selected sample cannot estimate global demand. The 2025 RCN final report recaps the same survey; never add the two response counts.

A second independent community process is already in our bibliography: Mehrabi et al. (2022), 69 food-system experts, 179 submitted questions prioritized to 50. Discussion explicitly calls for granular data, improved maps/predictions, stronger ground validation and governance. This supports the impact-data rationale, not an endorsement of this proposal or of a particular AI standard.

Suggested ~120-word Section 1.2 insert (all claims traceable; adjust length to available space):

Community need extends beyond archive growth. A 2022 DAS RCN survey received 95 responses; 90% anticipated using DAS for research or teaching within five years, while open comments requested common data/metadata and data-handling support (Aderhold et al., 2022). This self-selected survey measures prospective DAS use, not demand for our release. Cross-experiment integration and reuse motivate the existing DAS metadata standard (Lai et al., 2024). Hydrology offers a successful precedent: Caravan standardized seven regional collections spanning 6,830 catchments (Kratzert et al., 2023). In impact science, a 69-expert exercise identified needs for granular data, better maps and prediction (Mehrabi et al., 2022). Our contribution tests which enhancements make linked holdings useful for these communities and transferable to new scientific settings.

Dimensions warranted by the evidence:
1. Independent physical units and effective sample counts, not bytes or overlapping-window totals alone.
2. Modality, units, native temporal/spatial support, sampling rate and sensor response/calibration.
3. Coverage/diversity of sites, events, climates, geology, noise regimes and simulated parameters; missingness and imbalance.
4. Paired/partially paired modalities; physically defensible alignment and provenance of joins.
5. Rights to access, redistribute, train and evaluate; public development versus controlled tests.
6. Existing archival formats plus candidate AI access views, checksums/versioning, DOI and data/paper relationship.
7. Label/reference-answer provenance, uncertainty and independent holdout grouping; pretraining/public exposure risks.
8. Direct user and extended communities with evidence type: documented user, survey, paper use, recommendation, prospective pilot, or proposed outreach. Separate these explicitly.
9. Reproducible access/loader performance and cost; data actually read versus source archive size.
10. Outcome metrics: independent user task completion, qualified use/reuse, contributions and scientific generalization, not downloads alone.

Existing resources that must stay visible: SeisBench; FDSN/DAS-RCN metadata; the campus DAS event dataset; Caravan/CAMELS; OpenFWI; GNSS archives/COMCAT; EarthSE and EarthVerse. These sources delimit what is genuinely missing. OpenFWI’s controlled-source acoustic simulations are complementary evidence, not proof of need for every proposed rupture/wavefield release. EarthVerse already has executable heterogeneous Earth-event agent tasks; our distinction must be linked project holdings, fresh protected simulations, controlled physical workflow tests and independently reproducible scoring.

Not established in this audit: a population percentage demanding AI-ready Earth datasets; a growth rate for use of a named holding; unique users; committed adopters; a verified current volume/sample count for proposed holdings. A separate bibliometric analysis must distinguish subject growth, citations, and independently validated dataset usage, exclude incomplete 2026 from full-year growth estimates, and document denominators, query versions, abstract coverage and full-text eligibility. No endorsement inferred from a paper or citation.
'''
(OUT/'Community_Need_Synthesis_and_PD_Insert_2026-10-21.txt').write_text(summary)
print(json.dumps({'sources':len(rows),'max_quote_words':max(r['quote_word_count'] for r in rows),'new_references':len(refs),'files':[p.name for p in OUT.glob('*') if p.is_file()]},indent=2))
