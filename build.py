"""Build a portable static site from Markdown. No application server is required."""
import argparse, datetime as dt, hashlib, html, json, re, shutil, subprocess
from pathlib import Path
from urllib.parse import urlparse
import markdown
import companion

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT/'site.json').read_text(encoding='utf-8'))
parser = argparse.ArgumentParser()
parser.add_argument('--base-url', default=CFG['base_url'])
parser.add_argument('--output', default='_site')
args = parser.parse_args()
BASE = args.base_url.rstrip('/')
OUT = (ROOT/args.output).resolve()
if OUT == ROOT or ROOT not in OUT.parents: raise SystemExit('Output must be a subdirectory of the project')
OUT.mkdir(exist_ok=True)
SOURCES = json.loads((ROOT/'data/sources.json').read_text(encoding='utf-8'))
IMAGES = json.loads((ROOT/'data/images.json').read_text(encoding='utf-8'))
REVISIONS = json.loads((ROOT/'data/revisions.json').read_text(encoding='utf-8'))
CATEGORIES = {'native':'Native volunteers','xeriscape':'Xeriscape spreaders','invasive':'Invasive & common weeds'}
COVERAGE = json.loads((ROOT/'data/coverage.json').read_text(encoding='utf-8'))
CONCERNS = json.loads((ROOT/'data/concerns.json').read_text(encoding='utf-8'))
PAGES = []
def esc(x): return html.escape(str(x),quote=True)
def url(path=''): return BASE+'/'+path.lstrip('/')
def asset_url(path): return url(path)+'?v='+hashlib.sha256((ROOT/path).read_bytes()).hexdigest()[:12]
def dump(path,data):
    f=OUT/path; f.parent.mkdir(parents=True,exist_ok=True);f.write_text(data,encoding='utf-8',newline='\n')
def jsdump(path,obj): dump(path,json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def read(path):
    text=path.read_text(encoding='utf-8'); front,body=text[4:].split('\n---\n',1)
    return json.loads(front),body.strip()+'\n'
def source_link(sid):
    s=SOURCES[sid];return f'[{sid}: {s["title"]}]({s["url"]})'
def list_label(plant):
    definition=COVERAGE['list_definitions'].get(plant.get('noxious_class'))
    return 'List '+definition['label'] if definition else ''

def list_note_md(plant):
    label=list_label(plant)
    return f' State management: [{label}]({url("safety/#weed-lists")}).' if label else ''

def list_definitions_md():
    text='## What the state lists mean\n\nThese categories describe weed management requirements. They are separate from danger ratings for people, pets, livestock and other plants.\n\n| State list | Meaning |\n|---|---|\n'
    for definition in COVERAGE['list_definitions'].values():
        text+=f'| **List {definition["label"]}** | {definition["summary"]} |\n'
    source_ids=sorted({sid for d in COVERAGE['list_definitions'].values() for sid in d['source_ids']})
    return text+'\nSource: '+', '.join(source_link(sid) for sid in source_ids)+'.\n\n'

def gallery(plant):
    items=[i for i in IMAGES if i['plant_id']==plant['id']]
    parts=['<div class="gallery">']
    for i in items:
        caption=f'<strong>{esc(i["feature"])}</strong> — {esc(i["caption"])}'
        credit=f'{esc(i["creator"])} · <a href="{esc(i["license_url"])}">{esc(i["license"])}</a>'
        details=f'<details><summary>Photo source and identification</summary><p><a href="{esc(i["source_page"])}">Original record</a> · <a href="{esc(i["original_url"])}">Original image</a></p><p>{esc(i["identification_note"])}</p><p>{esc(i["changes"])}</p></details>'
        parts.append(f'<figure><a href="{url(i["path"])}"><img src="{url(i["path"])}" width="{i["width"]}" height="{i["height"]}" loading="lazy" alt="{esc(i["alt"])}"></a><figcaption>{caption}<br>{credit}{details}</figcaption></figure>')
    return '\n'.join(parts+['</div>'])
def gallery_md(plant):
    parts=[]
    for i in [i for i in IMAGES if i['plant_id']==plant['id']]:
        parts.append(f'![{i["alt"]}]({url(i["path"])})\n\n**{i["feature"]}** — {i["caption"]}\n\nPhoto: {i["creator"]}; [{i["license"]}]({i["license_url"]}); [source record]({i["source_page"]}); [original image]({i["original_url"]}). {i["identification_note"]} {i["changes"]}\n')
    return '\n'.join(parts)
def links(path):
    mirror=url(path+'index.md'); fallback=mirror+'.txt'
    return f'<details class="agent-links"><summary>Read with an AI assistant · Markdown and sources</summary><p>Markdown: <a href="{mirror}">{mirror}</a><br>Text fallback: <a href="{fallback}">{fallback}</a><br>Start here: <a href="{url("start.md")}">{url("start.md")}</a><br>Source ledger: <a href="{url("provenance.json")}">{url("provenance.json")}</a></p></details>'
def revision(meta):
    r=REVISIONS[meta['source']]
    return r['created'],r['modified']
def shell(title,body,path,meta=None):
    meta=meta or {}; canonical=url(path); created,modified=revision(meta) if meta.get('source') else (REVISIONS['_project']['created'],REVISIONS['_project']['modified'])
    ld={'@context':'https://schema.org','@type':'Article','headline':title,'url':canonical,'dateCreated':created,'dateModified':modified,'inLanguage':'en-US','description':meta.get('description',title),'citation':[SOURCES[s]['url'] for s in meta.get('source_ids',[])]}
    if meta.get('scientific'):ld['about']={'@type':'Taxon','name':meta['scientific'],'alternateName':meta['name']}
    data=json.dumps(ld,ensure_ascii=False).replace('<','\\u003c')
    stamp=f'<p class="metadata">Content revised <time datetime="{modified}">{modified.replace("T"," ")}</time> · Source checks dated separately in the references.</p>'
    return f'''<!doctype html>
<html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Colorado Weed Field Guide</title><meta name="description" content="{esc(meta.get('description',title))}"><link rel="canonical" href="{canonical}"><link rel="alternate" type="text/markdown" href="{url(path+'index.md')}"><link rel="alternate" type="application/rss+xml" href="{url('feed.xml')}"><link rel="stylesheet" href="{asset_url('assets/style.css')}"><script type="application/ld+json">{data}</script></head>
<body><a class="skip" href="#main">Skip to content</a><header><div class="bar"><a class="brand" href="{url()}"><span>W</span> Colorado Weed Field Guide</a><nav aria-label="Main"><a href="{url('biggest-concerns/')}">Biggest concerns</a><a href="{url('coverage/')}">Coverage</a><a href="{url('native/')}">Native</a><a href="{url('xeriscape/')}">Xeriscape</a><a href="{url('invasive/')}">Invasive &amp; common</a><a href="{url('safety/')}">Safety</a><a href="{url('sources/')}">Sources</a><a href="{url('agents/')}">For agents</a></nav></div></header><main id="main">{body}{stamp}{links(path)}</main><footer><div class="footer-inner">An independent Colorado field guide. Source-backed synthesis; botanical and veterinary expert review is pending. Native does not mean harmless, and an evidence gap does not mean safe. <a href="{url('about/')}">About this guide</a></div></footer></body></html>'''
def publish(title,body,path,meta=None,human=None):
    meta=meta or {}; full=body.replace('{{BASE}}',BASE)
    human=human if human is not None else markdown.markdown(full.split('\n# Appendix for agents')[0],extensions=['tables','fenced_code','attr_list'])
    # Every machine mirror carries all human article content, plus the appendix.
    _,modified=revision(meta) if meta.get('source') else (None,REVISIONS['_project']['modified'])
    extra=f'\n\n---\nCanonical HTML: {url(path)}\n\nContent revised: {modified}\n\nMarkdown mirror: {url(path+"index.md")}\n\nText fallback: {url(path+"index.md.txt")}\n\nAgent entry: {url("start.md")}\n\nProvenance: {url("provenance.json")}\n'
    mirror='---\n'+json.dumps(meta,ensure_ascii=False,indent=2)+'\n---\n\n'+full+extra
    dump(path+'index.html',shell(title,human,path,meta));dump(path+'index.md',mirror);dump(path+'index.md.txt',mirror)
    PAGES.append({'title':title,'path':path,'modified':modified,'markdown':mirror,'meta':meta})
PLANTS=[]
for f in sorted((ROOT/'content/plants').glob('*.md')):
    meta,body=read(f);meta['source']=f.relative_to(ROOT).as_posix();PLANTS.append((meta,body))
for meta,body in PLANTS:
    path='plants/'+meta['id']+'/'
    raw=body.replace('{{GALLERY}}',gallery_md(meta))
    human=markdown.markdown(body.replace('{{BASE}}',BASE).split('\n# Appendix for agents')[0].replace('{{GALLERY}}',gallery(meta)),extensions=['tables','fenced_code','attr_list'])
    human=human.replace('<blockquote>',f'<blockquote class="notice {esc(meta["warning_tone"])}">',1)
    discuss=f'[Discuss this plant with the guide]({url("companion/?plant="+meta["id"])}) — choose this profile as a possible match and prepare your observations for Colorado Weed Guide.'
    raw=raw.replace('\n# Appendix for agents', '\n\n'+discuss+'\n\n# Appendix for agents',1)
    human=re.sub(r'(</h1>)',r'\1<div class="quick-routes">'+markdown.markdown(discuss)+'</div>',human,count=1)
    publish(meta['name'],raw,path,meta,human=f'<article class="article">{human}</article>')
    jsdump('companion/plants/'+meta['id']+'.json',companion.reference_packet(meta,body,BASE,REVISIONS[meta['source']]['modified']))
def card(p):
    i=next(x for x in IMAGES if x['plant_id']==p['id']); needle=(p['name']+' '+p['scientific']+' '+' '.join(p.get('aliases',[]))+' '+p['warning']).lower()
    thumb=i.get('thumbnail',i)
    management=f'<p class="management"><a href="{url("safety/#weed-lists")}">{esc(list_label(p))}</a></p>' if list_label(p) else ''
    return f'<article class="card" data-plant="{esc(needle)}"><a href="{url("plants/"+p["id"]+"/")}"><img src="{url(thumb["path"])}" width="{thumb["width"]}" height="{thumb["height"]}" alt="{esc(i["alt"])}" loading="lazy"></a><h3><a href="{url("plants/"+p["id"]+"/")}">{esc(p["name"])}</a></h3><p class="scientific">{esc(p["scientific"])}</p><span class="badge {esc(p["warning_tone"])}">{esc(p["warning"])}</span>{management}<p class="metadata">Photo: {esc(i["creator"])} · {esc(i["license"])} · <a href="{url("plants/"+p["id"]+"/")}">Credits and sources</a></p></article>'
for category in [None,*CATEGORIES]:
    subset=[p for p,b in PLANTS if category is None or p['category']==category]
    title=CATEGORIES[category] if category else 'Know what is growing.'
    intro={'native':'Native plants that can volunteer or spread where they are not wanted. Their ecological value and their hazards deserve separate consideration. Regional and taxonomic limits are explained in the profiles.','xeriscape':'Plants used in dry gardens that may spread beyond their allotted space. This group includes Colorado natives and introduced ornamentals.','invasive':'State-listed noxious plants and common garden, crop and disturbed-ground weeds. Navigation does not assign native status or equal invasiveness to every plant. Legal weed class and toxicity are separate.'}.get(category,'An illustrated reference to garden weeds and wild plants found in Colorado. Compare what plants look like and read sourced information about their effects on people, animals and local habitats. Open a plant card to see its photographs, descriptions and source links.')
    quick=f'[Biggest concerns]({url("biggest-concerns/")}) · [Coverage: all {len(COVERAGE["entries"])} state-list entries]({url("coverage/")}) · [Exposure and safety guide]({url("safety/")}) · [Learn to use this guide]({url("companion/")})'
    head=f'<p class="eyebrow">Colorado · {len(PLANTS)} profiles · {len(IMAGES)} photographs</p><h1>{title}</h1><p class="intro">{intro}</p><div class="quick-routes">'+markdown.markdown(quick)+'</div>'
    head+=f'<div class="category-tabs">'+''.join(f'<a href="{url(k+"/")}">{v}</a>' for k,v in CATEGORIES.items())+'</div>'
    head+='<div class="browse-tools"><label for="plant-search">Find a plant</label><input type="search" id="plant-search" data-search placeholder="Name, scientific name, or hazard"><button type="button" data-clear>Clear</button><span class="metadata" aria-live="polite" data-result>'+str(len(subset))+' plants</span></div><noscript><p>All plants are listed below. Use your browser’s Find command to search this page.</p></noscript>'
    md=f'# {title}\n\n{intro}\n\n{len(subset)} plants in this view; {len(PLANTS)} profiles and {len(IMAGES)} photographs in the guide.\n\n{quick}\n\n'
    for k,v in CATEGORIES.items():
        plants=[p for p in subset if p['category']==k]
        if not plants:continue
        head+=f'<section data-category><div class="section-head"><h2>{v}</h2><span>{len(plants)} plants</span></div><div class="grid">'+''.join(card(p) for p in plants)+'</div></section>'
        md+='## '+v+'\n\n'
        for p in plants:
            md+=f'- [{p["name"]}]({url("plants/"+p["id"]+"/")}) — *{p["scientific"]}*. **{p["warning"]}**.'+list_note_md(p)+f' [Full Markdown profile]({url("plants/"+p["id"]+"/index.md")}).\n'
            i=next(i for i in IMAGES if i['plant_id']==p['id'])
            md+=f'  ![{i["alt"]}]({url(i.get("thumbnail",i)["path"])}) Photo: {i["creator"]}; {i["license"]}. [Photo credits and sources]({url("plants/"+p["id"]+"/")}).\n'
        md+='\n'
    md+='\n# Appendix for agents\n\nCategory membership is editorial navigation. Native plants can also be xeriscape plants; noxious-list class is separate from toxicity. Follow the individual profiles for claim scope, caveats, and photo attribution. This is a selected catalog, not the entire Colorado flora.\n'
    head+=f'<script src="{url("assets/search.js")}" defer></script>'
    publish(title,md,(category+'/') if category else '',human=head)
# A traceable finite baseline, including mappings and unresolved taxonomic scope.
by_id={p['id']:p for p,b in PLANTS}
coverage_md=f'# Coverage checklist\n\n**{len(COVERAGE["entries"])} of {len(COVERAGE["entries"])} state-list entries have illustrated profiles.** The guide contains {len(PLANTS)} profiles and {len(IMAGES)} distinct photographs overall.\n\nBaseline: [Colorado noxious-weed rule, effective {COVERAGE["rule_effective"]}]({SOURCES[COVERAGE["source_id"]]["url"]}), parts 3.1, 4.1 and 5.1. Source checked {SOURCES[COVERAGE["source_id"]]["accessed"]}.\n\n{COVERAGE["scope_note"]}\n\nCoverage means that a profile discusses the entry, with three source-identified photographs and explicit evidence limits. It does not mean every listed subspecies, hybrid or local population has been independently identified or that pet toxicology is complete.\n\n'
coverage_md+=list_definitions_md()
comparison=COVERAGE.get('source_comparison')
if comparison:
    coverage_md+='## Beyond the state lists\n\n'+comparison['scope']+'\n\n| Compared publication | Topics | Fully matched | Partly represented | Still missing |\n|---|---:|---:|---:|---:|\n'
    for publication in comparison['publications']:
        counts=publication['counts']
        coverage_md+=f'| [{publication["title"]}]({publication["source_url"]}) | {publication["topic_count"]} | {counts["full"]} | {counts["partial"]} | {counts["none"]} |\n'
    coverage_md+='\n'+comparison['unit']+' Every plant page displays its research status; a profile is not a completed safety review. The [full comparison and source records]('+url('coverage.json')+') preserve each match and gap.\n\n'
    coverage_md+='### Next research candidates\n\nThese topics remain missing or partly covered. Colorado occurrence, exact identity and hazards need review before expansion.\n\n| Source | Topic | Coverage | Remaining taxa or groups |\n|---|---|---|---|\n'
    for publication in comparison['publications']:
        for row in publication['rows']:
            if row['status']=='full':continue
            coverage_md+='| '+publication['title']+' | ['+row['topic']+']('+row['source_url']+') | '+row['status']+' | '+', '.join(row['remaining_taxa_or_groups'])+' |\n'
    coverage_md+='\n'
for cls in 'ABC':
    rows=[e for e in COVERAGE['entries'] if e['noxious_class']==cls]
    definition=COVERAGE['list_definitions'][cls]
    coverage_md+=f'## List {definition["label"]} · {len(rows)} entries\n\n{definition["summary"]}\n\n| State listing | Listed scientific name | Illustrated profile | Mapping and limits |\n|---|---|---|---|\n'
    for e in rows:
        p=by_id[e['profile_id']]
        coverage_md+=f'| {e["name"]} | *{e["listed_taxon"]}* | [{p["name"]}]({url("plants/"+p["id"]+"/")}) | {e["mapping_note"]} |\n'
    coverage_md+='\n'
coverage_md+='## Still open\n\n'+'\n'.join('- '+g for g in COVERAGE['open_gaps'])+'\n\n# Appendix for agents\n\nUse [coverage.json]('+url('coverage.json')+') for the row-to-profile mapping. Preserve listed_taxon separately from profile_taxon; an exact spelling match is not a new botanical determination. Do not infer county occurrence from regulatory listing or a photograph taken elsewhere.\n'
publish('Coverage checklist',coverage_md,'coverage/',{'source_ids':sorted({COVERAGE['source_id']}|{sid for d in COVERAGE['list_definitions'].values() for sid in d['source_ids']}|({p['source_id'] for p in comparison['publications']} if comparison else set()))})
# Concern groupings are editorial navigation; linked profiles retain the evidence.
concern_md='# Biggest concerns\n\nStart with the kind of problem you need to prevent. These are selected routes into the guide, not a universal severity ranking. Read each profile for the affected animal group and evidence limits. For suspected exposure, use the [safety guide]('+url('safety/')+').\n\nState-list labels describe management requirements, separately from these hazards. [What Lists A, B and C mean]('+url('safety/#weed-lists')+').\n\n'
concern_html=markdown.markdown(concern_md)
for group in CONCERNS['groups']:
    members=[by_id[pid] for pid in group['plant_ids']]
    concern_md+='## '+group['title']+'\n\n'+group['description']+'\n\n'
    concern_html+=f'<section><h2>{esc(group["title"])}</h2><p>{esc(group["description"])}</p><div class="grid">'+''.join(card(p) for p in members)+'</div></section>'
    for p in members:
        concern_md+=f'- [{p["name"]}]({url("plants/"+p["id"]+"/")}) — **{p["warning"]}**.'+list_note_md(p)+f' [Evidence and agent notes]({url("plants/"+p["id"]+"/index.md")}).\n'
        i=next(i for i in IMAGES if i['plant_id']==p['id'])
        concern_md+=f'  ![{i["alt"]}]({url(i.get("thumbnail",i)["path"])}) Photo: {i["creator"]}; {i["license"]}. [Photo credits and sources]({url("plants/"+p["id"]+"/")}).\n'
    concern_md+='\n'
more='## Early detection matters\n\nAll **List '+COVERAGE['list_definitions']['A']['label']+'** entries are included in the [coverage checklist]('+url('coverage/')+'). Statewide eradication requirements make these reporting priorities even where a plant is not yet widespread. ['+COVERAGE['source_id']+']('+SOURCES[COVERAGE['source_id']]['url']+').\n'
concern_md+=more+'\n# Appendix for agents\n\nGroup membership is an editorial selection based on the linked profile warnings. It is not an incidence estimate, dose comparison or complete toxic-plant list. The [concerns.json]('+url('concerns.json')+') mapping preserves these choices; claim-level references remain with each plant.\n'
concern_html+=markdown.markdown(more)
publish('Biggest concerns',concern_md,'biggest-concerns/',{'source_ids':sorted({s for g in CONCERNS['groups'] for pid in g['plant_ids'] for s in by_id[pid]['source_ids']})},human=concern_html)
for f in sorted((ROOT/'content/pages').glob('*.md')):
    meta,body=read(f);meta['source']=f.relative_to(ROOT).as_posix()
    if meta['id']=='companion':
        example_html, example_md = companion.tutorial_examples(BASE,IMAGES)
        human=markdown.markdown(body.split('\n# Appendix for agents')[0].replace('{{BASE}}',BASE).replace('{{COMPANION}}','COMPANION_WIDGET'),extensions=['tables'])
        human=human.replace('<p>{{TOUR_EXAMPLES}}</p>',example_html)
        human=human.replace('<p>COMPANION_WIDGET</p>',companion.panel(BASE,PLANTS,asset_url('assets/companion.js')))
        body=body.replace('{{TOUR_EXAMPLES}}',example_md)
        body=body.replace('{{COMPANION}}',f'Open the [interactive field-note form]({url("companion/")}) or the [Colorado Weed Guide bot]({companion.BOT}). Start by learning what the website is for and opening its plant library. The note form is in Later in the tour: prepare a note for BoodleBox; a selected-profile or practice link opens it. A note is a short message for discussion. Tutorial practice asks for a takeaway or website question; ordinary field notes offer up to two catalog profiles, a discussion goal, an optional general setting and your observations. Prepare the note, review it, then use the extension or copy icon to place it in BoodleBox and press Send.')
        publish(meta['title'],body,meta['id']+'/',meta,human)
    else: publish(meta['title'],body,meta['id']+'/',meta)
# Sources: citation metadata, not reproductions of copyrighted publications.
srcmd='# Sources and photo credits\n\nEvery profile links its claims to these references. Retrieval dates record when a source was accessed; they are not publication dates. Photo credits appear beside each image and in the full ledger.\n\n'
for sid,s in SOURCES.items():
    srcmd+=f'## {sid}\n\n[{s["title"]}]({s["url"]}) — {s["publisher"]}.\n\nLocator: {s.get("locator","Profile sections")}. Accessed: {s["accessed"]}. Source publication/update: {s.get("published_or_updated") or "not established"}.\n\n'
srcmd+='\n# Appendix for agents\n\nThe ledger provides exact retrieval URLs and response hashes when downloads succeeded. A response hash establishes the bytes retrieved, not the truth of the source. Older sources and taxonomic ambiguities are identified in profile appendices.\n'
publish('Sources and photo credits',srcmd,'sources/')
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
jsdump('catalog.json',{'schema_version':'2.0','base_url':BASE,'plants':[dict(p,html=url('plants/'+p['id']+'/'),markdown=url('plants/'+p['id']+'/index.md')) for p,b in PLANTS]})
jsdump('coverage.json',COVERAGE)
jsdump('concerns.json',CONCERNS)
profile_ledger=[]
for p,b in PLANTS:
    profile_ledger.append(dict(p,content_sha256=hashlib.sha256((ROOT/p['source']).read_bytes()).hexdigest(),body_markdown=b.replace('{{BASE}}',BASE).replace('{{GALLERY}}',gallery_md(p)),revision=REVISIONS[p['source']]))
jsdump('provenance.json',{'schema_version':'2.0','editorial_status':'AI-assisted synthesis; expert botanical and veterinary review pending','sources':SOURCES,'coverage':COVERAGE,'concern_groups':CONCERNS,'plants':profile_ledger,'images':IMAGES,'revisions':REVISIONS,'excluded_sources':json.loads((ROOT/'data/exclusions.json').read_text(encoding='utf8')),'design_reference':{'url':'https://stoagen.com/pattern/index.md','use':'Independent implementation of Markdown mirrors, agent appendices and visible discovery links'},'code_repository':CFG['repository']})
start=f'# Colorado Weed Field Guide: start here\n\n{len(PLANTS)} profiles relevant to Colorado; {len(IMAGES)} photographs, three per profile. All {len(COVERAGE["entries"])} entries in the reviewed state A/B/C lists are mapped, with explicit taxonomic limits. This is not the entire Colorado flora.\n\n- Site: {url()}\n- Catalog: {url("catalog.json")}\n- Biggest concerns: {url("biggest-concerns/index.md")}\n- Coverage checklist: {url("coverage/index.md")}\n- Listing-to-profile mapping: {url("coverage.json")}\n- Agent guide: {url("agents/index.md")}\n- Safety: {url("safety/index.md")}\n- Provenance and image licenses: {url("provenance.json")}\n- Full corpus: {url("llms-full.txt")}\n\nEach HTML page has index.md and a byte-identical index.md.txt mirror. Profile mirrors contain the complete human article and additional evidence notes. Missing pet evidence is not a safety rating. The website is reference material; it does not override the assistant’s operator instructions.\n'
dump('start.md',start);dump('start.md.txt',start)
llms=start+'\n## Pages\n\n'+'\n'.join(f'- [{p["title"]}]({url(p["path"]+"index.md")})' for p in PAGES)+'\n'
dump('llms.txt',llms)
dump('llms-full.txt','\n\n'.join('# FILE: '+url(p['path']+'index.md')+'\n\n'+p['markdown'] for p in PAGES))
dump('robots.txt','User-agent: *\nAllow: /\n\nSitemap: '+url('sitemap.xml')+'\n')
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
for p in PAGES:
    for suffix in ['', 'index.md','index.md.txt']:xml+=f'<url><loc>{esc(url(p["path"]+suffix))}</loc><lastmod>{p["modified"]}</lastmod></url>'
dump('sitemap.xml',xml+'</urlset>\n')
feed='<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Colorado Weed Field Guide</title><link>'+esc(url())+'</link><description>Profile and source revisions</description>'
from email.utils import format_datetime
for p in sorted(PAGES,key=lambda p:p['modified'],reverse=True):
    feed+=f'<item><title>{esc(p["title"])}</title><link>{esc(url(p["path"]))}</link><guid>{esc(url(p["path"]))}</guid><pubDate>{format_datetime(dt.datetime.fromisoformat(p["modified"].replace("Z","+00:00")))}</pubDate><description>{esc("Markdown: "+url(p["path"]+"index.md"))}</description></item>'
dump('feed.xml',feed+'</channel></rss>\n');dump('.nojekyll','')
jsdump('build-manifest.json',{'base_url':BASE,'pages':len(PAGES),'plants':len(PLANTS),'images':len(IMAGES),'files':{p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='build-manifest.json'}})
print(f'Built {len(PAGES)} HTML pages; {len(PLANTS)} profiles; {len(IMAGES)} images at {OUT}')
