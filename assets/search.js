const search = document.querySelector('[data-search]');
if (search) {
  const cards = [...document.querySelectorAll('[data-plant]')];
  const result = document.querySelector('[data-result]');
  const catalog = document.querySelector('[data-catalog]');
  function filter() {
    const q = search.value.trim().toLocaleLowerCase();
    catalog.classList.toggle('grid', Boolean(q));
    catalog.classList.toggle('search-results', Boolean(q));
    let visible = 0;
    for (const card of cards) { card.hidden = !card.dataset.plant.includes(q); if (!card.hidden) visible++; }
    for (const section of document.querySelectorAll('[data-category]')) section.hidden = !section.querySelector('[data-plant]:not([hidden])');
    result.textContent = `${visible} of ${cards.length} plants`;
  }
  search.addEventListener('input', filter);
  document.querySelector('[data-clear]').addEventListener('click', () => {search.value='';filter();search.focus();});
  filter();
}
