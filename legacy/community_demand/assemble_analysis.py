from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parent
primary=json.loads((R/'queries_primary.json').read_text()); secondary=json.loads((R/'queries_secondary.json').read_text()); sample=json.loads((R/'need_sample_20.json').read_text())
allcounts={int(x['key']):x['count'] for q in primary if q['id']=='all_article_review' for x in q['groups']}
rows=[]; metrics=[]
for q in primary+secondary:
 c={int(x['key']):x['count'] for x in q['groups']}
 for y in range(2020,2026):rows.append({'query_id':q['id'],'year':y,'count':c.get(y,0),'all_article_review_count':allcounts[y],'per_100000_all_article_reviews':round(c.get(y,0)/allcounts[y]*100000,6)})
 if q['id']!='all_article_review':
  a,b=c[2020],c[2025];metrics.append({'query_id':q['id'],'count_2020':a,'count_2025':b,'ratio_2025_over_2020':b/a,'cagr_5_intervals':(b/a)**.2-1,'ratio_normalized_to_all_article_review_count':(b/allcounts[2025])/(a/allcounts[2020]),'url':q['url']})
with (R/'annual_title_abstract_article_review_counts.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
(R/'growth_metrics.json').write_text(json.dumps(metrics,indent=2))
codes={
('das',1):('method_or_result_not_request','Curates an event benchmark and reports detection performance; no explicit request for shared AI-ready data in the abstract.'),
('das',2):('empirical_or_conditional_data_need','Says performance can improve as more training data are acquired; no demand for a common standard is established.'),
('das',3):('method_or_result_not_request','Tests domain shifts and amounts of labeled data for telecom sensing; no explicit community data request.'),
('das',4):('method_or_result_not_request','Proposes unsupervised denoising without labeled data; keyword hit is a method description rather than a request.'),
('das',5):('explicit_earth_data_or_benchmark_gap','Identifies small DAS training datasets as a limit on generalization; publisher introduction additionally identifies heterogeneity, confidentiality, and acquisition costs.'),
('das',6):('empirical_or_conditional_data_need','Conditionally motivates sufficiently large training data for DAS prediction, but does not establish a shared benchmark or standardization request.'),
('earthquake_simulation',1):('method_or_result_not_request','Uses available crustal-model data; data availability is a method input qualification, not an explicit data-standard need.'),
('earthquake_simulation',2):('empirical_or_conditional_data_need','Reports training on about300k2Dsimulations and degradation outside the fault-length/asperity training range; evidence for coverage/generalization tests, not a request for new simulations.'),
('geodesy_ml',1):('outside_target_earth_science_scope','NLOS navigation classification and automated data collection; outside targeted crustal/geodetic data holdings.'),
('geodesy_ml',2):('unassessable_abstract_missing','No abstract returned by OpenAlex. Do not infer need from title or keywords.'),
('geodesy_ml',3):('outside_target_earth_science_scope','Explicit annotation and sensor-fusion challenges, but for indoor/outdoor navigation, not the proposed Earth-science holdings.'),
('geodesy_ml',4):('method_or_result_not_request','Ionospheric prediction experiment describes its training data and forecast results; no explicit standardized data request.'),
('geodesy_ml',5):('outside_target_earth_science_scope','GNSS spoof detection identifies generalization limitations for security scenarios, outside targeted Earth-science holdings.'),
('geodesy_ml',6):('outside_target_earth_science_scope','Cooperative vehicle navigation uses data sharing as a technique; not a request for Earth-science shared datasets.'),
('hydrology_ml',1):('unassessable_abstract_missing','No abstract returned by OpenAlex. Do not infer need from title or keywords.'),
('hydrology_ml',2):('unassessable_abstract_missing','No abstract returned by OpenAlex. Do not infer need from title or keywords.'),
('hydrology_ml',3):('empirical_or_conditional_data_need','Reports beneficial scaling and generalization as training data increase; not an explicit request for a new community dataset or standard.'),
('hydrology_ml',4):('lexical_false_positive','Standardized Streamflow/Precipitation indices are scientific variables, not dataset standardization. Stemming causes a misleading hit.'),
('hydrology_ml',5):('explicit_earth_data_or_benchmark_gap','Explicitly identifies missing community tools for uncertainty estimation benchmarking; develops benchmarks itself, so do not imply the gap remains wholly unaddressed.'),
('hydrology_ml',6):('broader_integration_need_not_ai_standard','Calls for future spatial data integration, radar, precipitation, cloud computing, and AI in water research; broader need statement, not direct demand for this proposal’s specific holdings.')}
for x in sample:
 code,note=codes[(x['topic'],x['rank_within_topic'])];x['screen_code']=code;x['screen_note']=note;x['screened_text']='OpenAlex title/abstract; publisher confirmation additionally for DAS#5, earthquake_simulation#2, hydrology_ml#5';x['screening_date']='2026-10-21';x['screening_status']='preliminary_single_reviewer'
(R/'need_sample_20_coded.json').write_text(json.dumps(sample,indent=2))
with (R/'need_sample_20_coded.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=sample[0]);w.writeheader();w.writerows(sample)
summary={}
for x in sample:summary[x['screen_code']]=summary.get(x['screen_code'],0)+1
(R/'manual_screening_summary.json').write_text(json.dumps({'n':len(sample),'sampling':'Six most-cited matches per topic, except earthquake_simulation has onlytwo matches; not a random or prevalence sample. Ties sorted by API default. Citation counts are at query snapshot.','counts':summary,'interpretation':'Do not divide category counts by20 to estimate prevalence in the literature. Three abstracts are missing. No papers are manually confirmed to request this exact consortium’s holdings.','limitations':['Single reviewer preliminary coding','Search limited to indexed title/abstract','No systematic discussion-section/full-text search','No citation/reuse disambiguation','Topic and article-type classification/coverage may change']},indent=2))
# Hash the API responses used as provenance; failure diagnostics remain separately saved.
files=sorted(p for p in R.glob('*.json') if p.name not in ['growth_metrics.json','need_sample_20_coded.json','manual_screening_summary.json','provenance_manifest.json'])
(R/'provenance_manifest.json').write_text(json.dumps({'client_snapshot_date':'2026-10-21','provider':'OpenAlex publicRESTAPI, unauthenticated shared free budget; no key requested or created','files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]},indent=2))
print('CountsCSVrows',len(rows),'screenedworks',len(sample),'screening',summary)
