"""Record content changes by hash. Run after editing Markdown or source data."""
import datetime as dt, hashlib, json, subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
f=R/'data/revisions.json'
records=json.loads(f.read_text(encoding='utf8')) if f.exists() else {}
now=dt.datetime.now(dt.timezone.utc).replace(second=0,microsecond=0).isoformat().replace('+00:00','Z')
changed=[]
paths=sorted((R/'content').rglob('*.md'))+[p for p in sorted((R/'data').glob('*.json')) if p.name!='revisions.json']
for p in paths:
    key=p.relative_to(R).as_posix();sha=hashlib.sha256(p.read_bytes()).hexdigest()
    if records.get(key,{}).get('sha256')==sha:continue
    previous=records.get(key)
    records[key]={'created':previous['created'] if previous else now,'modified':now,'sha256':sha,'time_basis':'UTC timestamp of the editorial revision-recording event; not source publication or expert validation'}
    changed.append(key)
if changed:
    project=records.get('_project',{})
    records['_project']={'created':project.get('created',now),'modified':now}
    f.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
    with (R/'data/change-log.jsonl').open('a',encoding='utf8',newline='\n') as log:log.write(json.dumps({'recorded_at':now,'changed_files':changed,'sha256':{p:records[p]['sha256'] for p in changed}},ensure_ascii=False)+'\n')
print(f'Recorded {len(changed)} content changes')
