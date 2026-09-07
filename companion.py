"""Static companion UI and reference packets; no accounts or application backend."""
import html, json, re

BOT = 'https://box.boodle.ai/a/@ColoradoWeedGuide'

def tutorial_examples(base, images):
    examples = [
        ('russian-thistle', '1. Russian thistle: recognize a tumbleweed',
         'A widespread introduced weed that dries into a tumbleweed. We will use it to practice searching, comparing the photographs with the Recognize section, and reading Plants & habitat to learn how it spreads.',
         'CSU Extension', 'https://extension.colostate.edu/resource/identification-and-management-of-kochia-and-russian-thistle/'),
        ('showy-milkweed', '2. Showy milkweed: check pet hazards',
         'Its pink flowers make an appealing second example. We will open Dogs & cats and follow its ASPCA source: milkweeds are toxic to dogs and cats. The warning covers milkweeds as a group. Flowering beauty and native status do not establish pet safety.',
         'ASPCA: Milkweed', 'https://www.aspca.org/pet-care/aspca-poison-control/toxic-and-non-toxic-plants/milkweed')]
    cards, mirror = [], []
    for pid, title, description, source, source_url in examples:
        photo = next(i for i in images if i['plant_id'] == pid)
        thumb = photo.get('thumbnail', photo)
        src, profile = base+'/'+thumb['path'], base+'/plants/'+pid+'/'
        cards.append(f'<section><h3>{html.escape(title)}</h3><figure><a href="{profile}"><img src="{src}" width="{thumb["width"]}" height="{thumb["height"]}" loading="lazy" alt="{html.escape(photo["alt"])}"></a><figcaption>Photo: <a href="{html.escape(photo["source_page"])}">{html.escape(photo["creator"])}</a> · <a href="{html.escape(photo["license_url"])}">{html.escape(photo["license"])}</a></figcaption></figure><p>{html.escape(description)} <a href="{source_url}">{html.escape(source)}</a>.</p><p><a href="{profile}">Open this example’s plant page →</a></p></section>')
        mirror.append(f'### {title}\n\n![{photo["alt"]}]({src})\n\nPhoto: [{photo["creator"]}]({photo["source_page"]}); [{photo["license"]}]({photo["license_url"]}).\n\n{description} [{source}]({source_url}).\n\n[Open this example’s plant page]({profile}).\n')
    return '<div class="tour-examples">'+''.join(cards)+'</div>', '\n'.join(mirror)

def panel(base, plants, script_url):
    options = ''.join(f'<option value="{html.escape(p["id"])}">{html.escape(p["name"])} — {html.escape(p["scientific"])}</option>' for p, _ in sorted(plants, key=lambda pair: pair[0]['name']))
    return f'''<section class="companion-workspace" data-weed-workspace data-base="{html.escape(base)}">
<details class="field-note-step" id="field-note-step"><summary>Later in the tour: prepare a note for BoodleBox</summary>
<div class="field-bot"><img src="{base}/assets/colorado-weed-guide-avatar-v1.png" width="80" height="80" alt="Colorado Weed Guide’s decorative thistle and hand-lens emblem"><p><strong><a href="{BOT}" target="_blank" rel="noopener">Colorado Weed Guide ↗</a></strong><br>The BoodleBox tutor that walks you through this website.</p></div>
<div class="field-grid"><form id="field-form">
<h2 id="field-form-heading">Write a note about a plant</h2>
<p id="field-form-intro">A note is a short message you prepare here and discuss with the bot. Choose a profile you have looked at, or leave it unselected, and describe your own observations below. If this is your first visit, begin with the plant library above.</p>
<label for="field-mode">What kind of note?</label><select id="field-mode"><option value="field">My plant observations</option><option value="practice">Tutorial practice — learning the website</option></select>
<label for="plant-one" id="plant-one-label">A possible match</label><select id="plant-one"><option value="">I’m not sure yet</option>{options}</select>
<div id="field-details">
<label for="plant-two">Compare with another plant <span>(optional)</span></label><select id="plant-two"><option value="">No comparison yet</option>{options}</select>
<label for="field-goal">What would you like help with?</label><select id="field-goal"><option>Compare identifying features</option><option>Understand risks to people or animals</option><option>Understand habitat and ecological effects</option><option>Prepare questions about removal or management</option></select>
<label for="field-place">General setting <span>(optional; no street address needed)</span></label><input id="field-place" maxlength="180" placeholder="For example: Pueblo County, beside a ditch">
</div>
<label for="field-observations" id="field-observations-label">What can you see?</label><textarea id="field-observations" rows="5" maxlength="900" placeholder="Leaves, stem, flower or fruit, height, season… Describe only what you actually observed."></textarea>
<p class="metadata" id="field-mode-help">A selected profile is a candidate, not a confirmed identification. Observe without tasting or handling an unfamiliar plant.</p>
<button type="submit">Prepare my field note →</button><p id="prepare-status" role="status"></p>
</form><section id="field-result" hidden aria-labelledby="note-heading">
<h2 id="note-heading" tabindex="-1">2. Take it to your guide</h2>
<p>Your note, selected profiles and reference links are ready below. Review them before sharing. The guide also has a reference book covering all the plants. Nothing has been sent to BoodleBox.</p>
<div class="field-note-heading"><label for="field-note">Your field note and references</label><button type="button" class="field-copy" id="copy-field-note" title="Copy field note" aria-label="Copy field note"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h3"/></svg></button></div>
<textarea id="field-note" rows="14" readonly></textarea>
<div data-fieldwork-share data-note-id="field-note" data-companion="ColoradoWeedGuide" hidden></div>
<p id="copy-status" role="status"></p>
<p><a class="field-open" href="{BOT}" target="_blank" rel="noopener">Open Colorado Weed Guide ↗</a></p>
<p>In BoodleBox, choose <strong>Start New Chat</strong>, or keep using your existing Colorado Weed Guide conversation. With the updated Fieldwork extension and both pages in Chrome split view, <strong>Put note in BoodleBox</strong> fills the empty chat draft. Review it and press <strong>Send</strong>.</p>
<p>Without that button, use the small copy icon, paste into the chat, and press Send. Ask the guide about what you noticed. Its links bring you back to a profile or comparison.</p>
<p><a id="field-return" href="{base}/companion/">Reopen these selected profiles</a> · <a href="{base}/">Browse all plants</a></p>
</section></div></details>
<noscript><p>To prepare a note here, enable JavaScript. You can also <a href="{BOT}">open Colorado Weed Guide</a> and paste a profile link and your observations directly into the chat.</p></noscript>
</section><script src="{html.escape(script_url)}" defer></script>'''

def reference_packet(meta, body, base, revised):
    # Preserve all article safety sections and evidence appendices, without photo markup.
    text = re.sub(r'## Three views of this plant\n.*?(?=\n## |\Z)', '', body, flags=re.S)
    match = re.search(r'## Recognize[^\n]*\n+(.*?)(?=\n## |\n# |\Z)',text,flags=re.S)
    recognition = match.group(1).strip().replace('{{BASE}}',base) if match else ''
    if len(recognition)>650: recognition=''  # Link to the complete section instead of cutting qualifications.
    return {'id': meta['id'], 'name': meta['name'], 'scientific': meta['scientific'], 'warning': meta['warning'],
            'recognition': recognition,
            'url': base+'/plants/'+meta['id']+'/', 'revised': revised,
            'text': text.replace('{{BASE}}', base).replace('{{GALLERY}}', '')}
