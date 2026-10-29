import urllib.request, urllib.error, urllib.parse, pathlib, json, csv, time
ROOT=pathlib.Path(__file__).resolve().parent
BASE='from_publication_date:2020-01-01,to_publication_date:2025-12-31,type:article|review'
TOPICS={
'das':'"distributed acoustic sensing"',
'earthquake_simulation':'earthquake AND ("rupture simulation" OR "wavefield simulation" OR "synthetic seismograms")',
'geodesy_ml':'(geodesy OR geodetic OR GNSS) AND ("machine learning" OR "deep learning")',
'hydrology_ml':'(hydrology OR hydrological) AND ("machine learning" OR "deep learning")'}
NEED='("data scarcity" OR "data availability" OR "data sharing" OR "open dataset" OR "benchmark dataset" OR interoperability OR standardization OR standardisation OR "training data")'
manifest=[]; sample=[]
def abstract(ii):
 if not ii:return ''
 out={p:w for w,ps in ii.items() for p in ps}
 return ' '.join(out[p] for p in sorted(out))
for topic,q in TOPICS.items():
 filt=BASE+',title_and_abstract.search:('+q+') AND '+NEED
 for mode in ['need_annual','need_sample']:
  p={'filter':filt,'per_page':200} if mode=='need_annual' else {'filter':filt,'per_page':6,'sort':'cited_by_count:desc','select':'id,doi,title,publication_year,cited_by_count,abstract_inverted_index,primary_location,type'}
  if mode=='need_annual':p['group_by']='publication_year'
  url='https://api.openalex.org/works?'+urllib.parse.urlencode(p)
  filename=topic+'_'+mode+'.json'
  try:
   with urllib.request.urlopen(url,timeout=30) as r:raw=r.read().decode()
   (ROOT/filename).write_text(raw); data=json.loads(raw)
   manifest.append({'id':topic+'_'+mode,'url':url,'filter':filt,'raw_file':filename,'count':data.get('meta',{}).get('count'),'x_query':data.get('meta',{}).get('x_query'),'groups':data.get('group_by')})
   print(topic,mode,data.get('meta',{}).get('count'))
   if mode=='need_sample':
    for rank,w in enumerate(data.get('results',[]),1):sample.append({'topic':topic,'rank_within_topic':rank,'openalex_id':w['id'],'doi':w.get('doi'),'title':w['title'],'year':w['publication_year'],'citations_at_snapshot':w['cited_by_count'],'abstract':abstract(w.get('abstract_inverted_index')),'landing_page':w.get('primary_location',{}).get('landing_page_url')})
  except urllib.error.HTTPError as e:
   raw=e.read().decode();(ROOT/(filename+'.error.txt')).write_text(str(e)+'\n'+raw);print('ERROR',topic,mode,str(e),raw[:500])
  time.sleep(1.3)
(ROOT/'queries_need_and_sample.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'need_sample_20.json').write_text(json.dumps(sample,indent=2))
with (ROOT/'need_sample_20.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(sample[0]) if sample else ['topic']);writer.writeheader();writer.writerows(sample)
with (ROOT/'need_sample_20_for_review.txt').open('w') as f:
 for x in sample:
  f.write(f"[{x['topic']} #{x['rank_within_topic']}] {x['year']} {x['title']}\n{x['doi']}\n{x['abstract']}\n\n")
