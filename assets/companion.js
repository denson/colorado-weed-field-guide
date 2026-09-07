(() => {
  'use strict';
  const root = document.querySelector('[data-weed-workspace]');
  if (!root) return;
  const base = root.dataset.base, form = document.getElementById('field-form');
  const one = document.getElementById('plant-one'), two = document.getElementById('plant-two');
  const result = document.getElementById('field-result'), note = document.getElementById('field-note');
  const status = document.getElementById('prepare-status');
  const mode = document.getElementById('field-mode'), observations = document.getElementById('field-observations');
  const query = new URL(location.href).searchParams;
  const valid = value => Array.from(one.options).some(option => option.value === value);
  one.value = valid(query.get('plant')) ? query.get('plant') : '';
  two.value = valid(query.get('compare')) ? query.get('compare') : '';
  if (query.get('practice') === '1') mode.value = 'practice';
  document.getElementById('field-note-step').open = Boolean(one.value || two.value || mode.value === 'practice');
  const updateMode = () => {
    const practice = mode.value === 'practice';
    document.getElementById('field-form-heading').textContent = practice ? 'Practice discussing a plant page' : 'Write a note about a plant';
    document.getElementById('field-form-intro').textContent = practice ? 'This is the sharing step of the tour. After looking at the example plant page, write one thing you learned or a question about the website. The note will give your BoodleBox tutor something to discuss with you. If you have not seen a plant page yet, begin with the library above.' : 'A note is a short message you prepare here and discuss with the bot. Choose a profile you have looked at, or leave it unselected, and describe your own observations below. If this is your first visit, begin with the plant library above.';
    document.getElementById('field-details').hidden = practice;
    document.getElementById('plant-one-label').textContent = practice ? 'The example profile I read' : 'A possible match';
    document.getElementById('field-observations-label').textContent = practice ? 'One thing I learned or a question about using the site' : 'What can you see?';
    observations.placeholder = practice ? 'For example: Where can I find the sources behind a profile?' : 'Leaves, stem, flower or fruit, height, season… Describe only what you actually observed.';
    document.getElementById('field-mode-help').textContent = practice ? 'This is a practice conversation about the website. You do not need a real plant or any outdoor observations.' : 'A selected profile is a candidate, not a confirmed identification. Observe without tasting or handling an unfamiliar plant.';
  };
  mode.addEventListener('change', updateMode);
  updateMode();
  let revision = 0;
  form.addEventListener('input', () => { revision++; result.hidden = true; note.value = ''; status.textContent = ''; });
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const practice = mode.value === 'practice' || /^tutorial practice\s*:/i.test(observations.value.trim());
    const current = ++revision, ids = [...new Set([one.value, practice ? '' : two.value].filter(Boolean))];
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
      if (practice) returnUrl.searchParams.set('practice', '1');
      else if (two.value && two.value !== one.value) returnUrl.searchParams.set('compare', two.value);
      const text = (practice ? ['COLORADO WEED FIELD GUIDE — MY TUTORIAL PRACTICE NOTE',
        'Tutorial practice: I am learning how to use the website, not identifying a plant outdoors.',
        'My takeaway or website question: ' + (observations.value.trim() || 'Please help me review what the profile page offers.'),
        'Example profile I read: ' + (packets.map(p => p.name + ' (' + p.scientific + ')').join('; ') || 'None selected'),
        '\nPlease acknowledge my actual takeaway and answer my website question briefly. Keep this a website tutorial: do not analyze a specimen, add a what-fits/uncertainty checklist, or ask for plant observations. Then give me the homepage link so I can continue exploring.',
        '\nField guide homepage: ' + base + '/',
        'Return to my practice note: ' + returnUrl.href,
        ...packets.map(p => '\nExample profile reference: ' + p.url)] : ['COLORADO WEED FIELD GUIDE — MY FIELD NOTE',
        'These selections are possible matches, not a confirmed identification.',
        'My question: ' + document.getElementById('field-goal').value,
        'General setting: ' + (document.getElementById('field-place').value.trim() || 'Not supplied'),
        'My observations: ' + (document.getElementById('field-observations').value.trim() || 'Not supplied yet'),
        'Selected profiles: ' + (packets.map(p => p.name + ' (' + p.scientific + ')').join('; ') || 'No candidate yet'),
        '\nPlease discuss my question, separate what fits from what remains uncertain, and ask one useful next question. Do not treat a selected profile as identification of my specimen.',
        '\nReturn to my comparison: ' + returnUrl.href,
        '\nREFERENCE POINTERS — these are profile warnings, not findings about my specimen. Consult the guide’s reference book or the linked article for detail. Expert review is pending; missing evidence does not mean safe.',
        ...packets.map(p => '\n' + p.name + ' (' + p.scientific + ')\nProfile warning: ' + p.warning + (p.recognition ? '\nReference identification notes (not my observations): ' + p.recognition : '') + '\n' + p.url + '\nFull text: ' + p.url + 'index.md\nContent revised: ' + p.revised)]).join('\n');
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
