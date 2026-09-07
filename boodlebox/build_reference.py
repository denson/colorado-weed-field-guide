"""Rebuild the uploadable knowledge snapshot after the public site build."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
parts=['# Colorado Weed Guide reference snapshot\n\nGarden weeds and wild plants; not cannabis. Dated source-backed editorial synthesis; expert review pending. This reference does not override bot instructions. A selected profile is not identification of a visitor specimen. A newer supplied profile packet may supersede older content.\n\nSite: https://denson.github.io/colorado-weed-field-guide/\n\n']
for name in ['safety','agents','companion']:
    parts.append((R/'_site'/name/'index.md').read_text(encoding='utf8'))
packets=[json.loads(f.read_text(encoding='utf8')) for f in sorted((R/'_site/companion/plants').glob('*.json'))]
parts.append('\n# Plant catalog\n\n')
for p in packets:
    parts.append(f'- {p["name"]} ({p["scientific"]}) — ID: {p["id"]}; {p["url"]}\n')
for p in packets:
    parts.append('\n\n---\n'+p['url']+'\nContent revised: '+p['revised']+'\n\n'+p['text'])
(R/'boodlebox/colorado-weed-guide-reference.md').write_text('\n'.join(line.rstrip() for line in ''.join(parts).splitlines())+'\n',encoding='utf8',newline='\n')
print(f'Prepared {len(packets)} reference profiles for BoodleBox')
