/* MIT License · Copyright (c) 2026 Long Ngo */
'use strict';
document.documentElement.classList.add('js');
const menuToggle = document.querySelector('.menu-toggle');
menuToggle.hidden = false;
menuToggle.addEventListener('click', () => {
  const open = document.querySelector('.sidebar').classList.toggle('menu-open');
  menuToggle.setAttribute('aria-expanded', String(open));
});
const tabs = [...document.querySelectorAll('[data-tab]')];
const panels = [...document.querySelectorAll('.guide-panel')];
const tablist = document.querySelector('.guide-tabs');
tablist.hidden = false;
function selectGuide(name, focus = false) {
  if (!tabs.some(tab => tab.dataset.tab === name)) return;
  tabs.forEach(tab => {
    const selected = tab.dataset.tab === name;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected && focus) tab.focus();
  });
  panels.forEach(panel => { panel.hidden = panel.id !== name; });
}
selectGuide(['plugin', 'mcp', 'api'].includes(location.hash.slice(1)) ? location.hash.slice(1) : 'plugin');
panels.forEach(panel => {
  panel.setAttribute('role', 'tabpanel');
  panel.setAttribute('aria-labelledby', 'tab-' + panel.id);
});
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => {
    selectGuide(tab.dataset.tab);
    history.replaceState(null, '', '#' + tab.dataset.tab);
  });
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) {
      event.preventDefault();
      selectGuide(tabs[next].dataset.tab, true);
      history.replaceState(null, '', '#' + tabs[next].dataset.tab);
    }
  });
});
document.querySelectorAll('[data-guide-link]').forEach(link => {
  link.addEventListener('click', () => selectGuide(link.dataset.guideLink));
});
window.addEventListener('hashchange', () => selectGuide(location.hash.slice(1)));
const search = document.querySelector('#knowledge-search');
const topics = [...document.querySelectorAll('[data-topic]')];
const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D').toLowerCase();
search.addEventListener('input', () => {
  const query = normalize(search.value.trim());
  let count = 0;
  topics.forEach(topic => {
    topic.hidden = !normalize(topic.textContent).includes(query);
    if (!topic.hidden) count++;
  });
  document.querySelector('#search-status').textContent = `${count} chủ đề · khung tri thức bản nháp`;
  document.querySelector('#no-results').hidden = count !== 0;
});
document.addEventListener('keydown', event => {
  if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName) && !document.activeElement.isContentEditable) {
    event.preventDefault();
    search.focus();
  }
});
let noticeTimer;
function notice(message) {
  const status = document.querySelector('#copy-status');
  status.textContent = message;
  status.classList.add('visible');
  clearTimeout(noticeTimer);
  noticeTimer = setTimeout(() => status.classList.remove('visible'), 2600);
}
document.querySelectorAll('.copy').forEach(button => {
  button.addEventListener('click', async () => {
    const code = button.parentElement.querySelector('code');
    try {
      await navigator.clipboard.writeText(code.textContent);
      notice('Đã sao chép.');
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      notice('Đã chọn nội dung. Nhấn Ctrl+C hoặc Command+C để sao chép.');
    }
  });
});
if ('IntersectionObserver' in window) {
  const links = [...document.querySelectorAll('.sidebar nav a')];
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      links.forEach(link => {
        if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, { rootMargin: '-10% 0px -65% 0px' });
  links.forEach(link => {
    const section = document.querySelector(link.hash);
    if (section) observer.observe(section);
  });
}
