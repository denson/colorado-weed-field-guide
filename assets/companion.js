(() => {
  'use strict';
  const root = document.querySelector('[data-weed-workspace]');
  if (!root) return;
  const base = root.dataset.base, form = document.getElementById('field-form');
  const one = document.getElementById('plant-one'), two = document.getElementById('plant-two');
  const result = document.getElementById('field-result'), note = document.getElementById('field-note');
  const status = document.getElementById('prepare-status');
  const query = new URL(location.href).searchParams;
  const valid = value => Array.from(one.options).some(option => option.value === value);
  one.value = valid(query.get('plant')) ? query.get('plant') : '';
  two.value = valid(query.get('compare')) ? query.get('compare') : '';
  let revision = 0;
  form.addEventListener('input', () => { revision++; result.hidden = true; note.value = ''; status.textContent = ''; });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const current = ++revision, ids = [...new Set([one.value, two.value].filter(Boolean))];
    result.hidden = true; note.value = ''; status.textContent = 'Preparing your note and its references…';
    try {
      const packets = await Promise.all(ids.map(async id => {
        if (!valid(id)) throw new Error('selection');
        const response = await fetch(base + '/companion/plants/' + encodeURIComponent(id) + '.json');
        if (!response.ok) throw new Error('reference');
        const packet = await response.json();
        if (packet.id !== id || typeof packet.text !== 'string' || typeof packet.warning !== 'string') throw new Error('reference');
        return packet;
      }));
      if (current !== revision) return;
      const returnUrl = new URL(base + '/companion/');
      if (one.value) returnUrl.searchParams.set('plant', one.value);
      if (two.value && two.value !== one.value) returnUrl.searchParams.set('compare', two.value);
      const text = ['COLORADO WEED FIELD GUIDE — MY FIELD NOTE',
        'These selections are possible matches, not a confirmed identification.',
        'My question: ' + document.getElementById('field-goal').value,
        'General setting: ' + (document.getElementById('field-place').value.trim() || 'Not supplied'),
        'My observations: ' + (document.getElementById('field-observations').value.trim() || 'Not supplied yet'),
        'Selected profiles: ' + (packets.map(p => p.name + ' (' + p.scientific + ')').join('; ') || 'No candidate yet'),
        '\nPlease discuss my question, separate what fits from what remains uncertain, and ask one useful next question. Do not treat a selected profile as identification of my specimen.',
        '\nReturn to my comparison: ' + returnUrl.href,
        '\nREFERENCE POINTERS — these are profile warnings, not findings about my specimen. Consult the guide’s reference book or the linked article for detail. Expert review is pending; missing evidence does not mean safe.',
        ...packets.map(p => '\n' + p.name + ' (' + p.scientific + ')\nProfile warning: ' + p.warning + (p.recognition ? '\nReference identification notes (not my observations): ' + p.recognition : '') + '\n' + p.url + '\nFull text: ' + p.url + 'index.md\nContent revised: ' + p.revised)].join('\n');
      if (text.length > 3800) throw new Error('length');
      note.value = text;
      document.getElementById('field-return').href = returnUrl.href;
      document.getElementById('copy-status').textContent = '';
      result.hidden = false; status.textContent = '';
      document.getElementById('note-heading').focus();
    } catch (error) {
      if (current !== revision) return;
      status.textContent = error.message === 'length' ? 'These profiles make a long note. Select one plant at a time and prepare it again.' : 'The reference text could not load. Your observations are still here; please try again.';
    }
  });
  document.getElementById('copy-field-note').addEventListener('click', async () => {
    const status = document.getElementById('copy-status');
    try { await navigator.clipboard.writeText(note.value); status.textContent = 'Copied. Paste into Colorado Weed Guide, review, and press Send.'; }
    catch { note.focus(); note.select(); status.textContent = 'Select and copy the note with Ctrl+C (Command+C on Mac), then paste it into the chat.'; }
  });
})();
