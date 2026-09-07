"""Structural, evidence and asset checks before publication; no browser required."""
import hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlparse,unquote
from collections import Counter
from bs4 import BeautifulSoup
from PIL import Image
R=Path(__file__).resolve().parent;O=R/'_site';errors=[]
def check(ok,message):
    if not ok:errors.append(message)
def digest(f):return hashlib.sha256(f.read_bytes()).hexdigest()
catalog=json.loads((O/'catalog.json').read_text(encoding='utf8'))
prov=json.loads((O/'provenance.json').read_text(encoding='utf8'))
base=catalog['base_url'];plants=catalog['plants'];images=prov['images'];sources=prov['sources'];revisions=prov['revisions']
def check_public_paths(value,location='provenance'):
    if isinstance(value,dict):
        for k,v in value.items():check_public_paths(v,location+'.'+k)
    elif isinstance(value,list):
        for i,v in enumerate(value):check_public_paths(v,location+'['+str(i)+']')
    elif isinstance(value,str):check(not re.match(r'^[A-Za-z]:[\\/]',value),location+' exposes an unavailable local path')
check_public_paths(prov)
canonical={p.stem for p in (R/'content/plants').glob('*.md')}
plant_ids={p['id'] for p in plants}
check(len(plants)==len(plant_ids) and plant_ids==canonical,'Catalog must represent every canonical profile exactly once')
check(set(p['category'] for p in plants)=={'native','xeriscape','invasive'},'Unexpected or missing category')
check(len(images)==3*len(plants),'Expected three image records per canonical profile')
# Distinct embedded photographs can share a PDF URL; an exact figure/object locator is required.
check(len({(i['original_url'],i.get('original_locator','')) for i in images})==len(images),'Duplicate photograph source and locator')
check(len({i['sha256'] for i in images})==len(images),'Duplicate photograph bytes')
check(len({i['id'] for i in images})==len(images),'Duplicate image IDs')
check(all(i['plant_id'] in plant_ids for i in images),'Image points to an unknown plant')
check({i['path'] for i in images}=={p.relative_to(R).as_posix() for p in (R/'assets/photos').iterdir() if p.is_file()},'Missing or orphan photograph files')
coverage=json.loads((O/'coverage.json').read_text(encoding='utf8'))
check(coverage==prov['coverage'],'Coverage differs from provenance')
check(coverage['profile_count']==len(plants),'Coverage profile count is stale')
check(len(coverage['entries'])==82,'Expected all 82 entries in the reviewed 2025 state rule')
check(Counter(e['noxious_class'] for e in coverage['entries'])=={'A':27,'B':37,'C':18},'State-list baseline counts differ')
check(len({e['listed_taxon'] for e in coverage['entries']})==82,'Duplicate state-list taxon')
by_id={p['id']:p for p in plants}
for e in coverage['entries']:
    check(e.get('profile_id') in plant_ids,'Uncovered listing: '+e['name'])
    check(e['source_id'] in sources and bool(e.get('locator')),'Listing source/locator missing')
    p=by_id.get(e.get('profile_id'),{})
    check(p.get('noxious_class')==e['noxious_class'],'Listing/profile class mismatch: '+e['name'])
    check(bool(e.get('mapping_note')),'Missing taxon mapping note: '+e['name'])
concerns=json.loads((O/'concerns.json').read_text(encoding='utf8'))
check(concerns==prov['concern_groups'],'Concern routes differ from provenance')
for g in concerns['groups']:
    check(bool(g['plant_ids']) and len(g['plant_ids'])==len(set(g['plant_ids'])),'Empty or duplicate concern group')
    check(all(pid in plant_ids for pid in g['plant_ids']),'Unknown plant in concern group')
for i in images:
    for k in ['creator','license','license_url','source_page','original_url','identification_note','caption','alt','accessed','sha256']:
        check(bool(i.get(k)),i['id']+': missing '+k)
    f=R/i['path'];check(f.is_file(),str(f)+' missing')
    if f.is_file():
        check(digest(f)==i['sha256'],i['id']+' image hash mismatch')
        with Image.open(f) as im:check(im.size==(i['width'],i['height']),i['id']+' dimensions mismatch');im.verify()
    if 'thumbnail' in i:
        t=i['thumbnail'];check(t['parent_sha256']==i['sha256'],'Wrong thumbnail parent');check(digest(R/t['path'])==t['sha256'],'Wrong thumbnail hash')
    check(not re.search(r'NC\b|ND\b',i['license']),'Unexpected restrictive photo license: '+i['id'])
for p in plants:
    check(sum(i['plant_id']==p['id'] for i in images)==3,p['id']+' needs 3 photos')
    path=O/'plants'/p['id'];doc=BeautifulSoup((path/'index.html').read_text(encoding='utf8'),'html.parser');mirror=(path/'index.md').read_text(encoding='utf8')
    check(len(doc.select('.gallery figure img'))==3,p['id']+' missing gallery photos')
    check(p['name'] in doc.get_text() and p['scientific'] in doc.get_text(),p['id']+' missing identity')
    check(p['warning'] in doc.get_text() and p['warning'] in mirror,p['id']+' missing warning')
    research=p.get('research',{})
    check(research.get('status')=='researching' and research.get('open_questions'),p['id']+' missing research status or open questions')
    check(doc.select_one('#research-status') is not None and 'Still researching this plant' in mirror,p['id']+' research status must appear in HTML and Markdown')
    for question in research.get('open_questions',[]):
        check(question['question'] in mirror,p['id']+' missing agent research question')
    for label in ['People','Dogs & cats','Other animals','Plants & habitat']:
        check(any(h.get_text()==label for h in doc.select('h2')),p['id']+' missing '+label)
    check('# Appendix for agents' in mirror,p['id']+' missing agent appendix')
    check('Appendix for agents' not in doc.get_text(),p['id']+' exposes full appendix instead of article')
    for s in p['source_ids']:check(s in sources,p['id']+' unknown source '+s)
    check(len({c['id'] for c in p['claim_evidence']})==len(p['claim_evidence']),p['id']+' duplicate claim IDs')
    for c in p['claim_evidence']:
        check(c['sources'] or c['scope'] in ['Review limitation','Evidence gap','Not assessed'],p['id']+' unsourced factual claim '+c['id'])
        for sid in c['sources']:check(sid in sources,'Unknown claim source '+sid)
        check(all(sid in p['source_ids'] for sid in c['sources']),p['id']+' claim omitted from profile reference list')
    src=R/p['source'];check(digest(src)==revisions[p['source']]['sha256'],p['id']+' unrecorded source change; run record_revisions.py')
for sid,s in sources.items():
    for k in ['url','title','publisher','accessed','locator']:check(bool(s.get(k)),sid+' missing '+k)
    check(s['url'].startswith('https://'),sid+' non-HTTPS reference')
for src,record in revisions.items():
    if src=='_project':continue
    check((R/src).exists(),'Missing revision source '+src)
    check(digest(R/src)==record['sha256'],'Unrecorded edit: '+src)
pages=list(O.rglob('index.html'))
for file in pages:
    text=file.read_text(encoding='utf8');doc=BeautifulSoup(text,'html.parser');rel=file.relative_to(O).as_posix()
    check('{{' not in text and 'chatgpt.site' not in text,rel+' unresolved template or old host')
    check(doc.find('h1') is not None and doc.find('main') is not None,rel+' missing static body')
    md=file.with_suffix('.md');fallback=Path(str(md)+'.txt');check(md.read_bytes()==fallback.read_bytes(),rel+' Markdown/text mismatch')
    check(doc.select_one('main .agent-links a[href$="index.md"]') is not None,rel+' agent link missing from main body')
    for a in doc.select('[href],[src]'):
        value=a.get('href') or a.get('src')
        if not value.startswith(base+'/'):continue
        path=value[len(base)+1:].split('#')[0].split('?')[0];f=O/unquote(path)
        if not path or path.endswith('/'):f=f/'index.html'
        check(f.is_file(),rel+' broken local URL '+value)
    for i in doc.select('img'):check(bool(i.get('alt')),rel+' image without alt text')
full=(O/'llms-full.txt').read_text(encoding='utf8')
comparison=json.loads((O/'coverage.json').read_text(encoding='utf8')).get('source_comparison',{})
check(comparison.get('profile_count')==len(plants),'Source comparison has a stale profile count')
for publication in comparison.get('publications',[]):
    check(publication['topic_count']==len(publication['rows']),'Comparison topic count mismatch')
    for status in ['full','partial','none']:
        check(publication['counts'][status]==sum(row['status']==status for row in publication['rows']),'Comparison status count mismatch')
    for row in publication['rows']:
        check(all(any(p['id']==pid for p in plants) for pid in row['profile_ids']),'Comparison points to a missing profile')
check(full.count('# FILE: ')==len(pages),'Full corpus page count differs')
check((O/'start.md').read_bytes()==(O/'start.md.txt').read_bytes(),'Start mirror fallback differs')
check(all('localhost' not in u for u in [base]) or '--allow-local' in sys.argv,'Production base URL is local')
manifest=json.loads((O/'build-manifest.json').read_text(encoding='utf8'))
for path,sha in manifest['files'].items():check(digest(O/path)==sha,'Generated artifact hash mismatch: '+path)
if errors:
    print('\n'.join(errors));raise SystemExit(f'FAILED: {len(errors)} checks')
print(f'PASS: {len(plants)} profiles, {len(images)} distinct photos, {len(sources)} sources, {len(pages)} static pages; mirrors, citations, revisions, links and hashes verified.')
