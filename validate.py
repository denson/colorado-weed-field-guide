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
check(len(plants)==40,'Expected 40 plant profiles')
check(Counter(p['category'] for p in plants)=={'native':10,'xeriscape':10,'invasive':20},'Category counts differ')
check(len(images)==120,'Expected 120 image records')
check(len({i['original_url'] for i in images})==120,'Photographs must have distinct original image URLs')
check(len({i['sha256'] for i in images})==120,'Duplicate photograph bytes')
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
    for label in ['People','Dogs & cats','Other animals','Plants & habitat']:
        check(any(h.get_text()==label for h in doc.select('h2')),p['id']+' missing '+label)
    check('# Appendix for agents' in mirror,p['id']+' missing agent appendix')
    check('Appendix for agents' not in doc.get_text(),p['id']+' exposes full appendix instead of article')
    for s in p['source_ids']:check(s in sources,p['id']+' unknown source '+s)
    for c in p['claim_evidence']:
        check(c['sources'] or c['scope'] in ['Review limitation','Evidence gap','Not assessed'],p['id']+' unsourced factual claim '+c['id'])
        for sid in c['sources']:check(sid in sources,'Unknown claim source '+sid)
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
check(full.count('# FILE: ')==len(pages),'Full corpus page count differs')
check((O/'start.md').read_bytes()==(O/'start.md.txt').read_bytes(),'Start mirror fallback differs')
check(all('localhost' not in u for u in [base]) or '--allow-local' in sys.argv,'Production base URL is local')
manifest=json.loads((O/'build-manifest.json').read_text(encoding='utf8'))
for path,sha in manifest['files'].items():check(digest(O/path)==sha,'Generated artifact hash mismatch: '+path)
if errors:
    print('\n'.join(errors));raise SystemExit(f'FAILED: {len(errors)} checks')
print(f'PASS: {len(plants)} profiles, {len(images)} distinct photos, {len(sources)} sources, {len(pages)} static pages; mirrors, citations, revisions, links and hashes verified.')
