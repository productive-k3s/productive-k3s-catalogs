(function () {
  const state = {
    entries: [],
    search: '',
    visibility: 'all',
    kind: 'all',
    category: 'all',
  };

  const byId = (id) => document.getElementById(id);

  function normalizeEntry(entry) {
    return {
      id: entry.id || entry.name,
      name: entry.name || entry.id,
      kind: entry.kind || 'unknown',
      visibility: entry.visibility || 'public',
      category: entry.category || 'uncategorized',
      description: entry.description || '',
      version: entry.version || '',
      sourceRepository: entry.sourceRepository || '',
      tags: entry.tags || [],
      artifact: entry.artifact || {},
      commercial: entry.commercial || {},
      install: entry.install || { requiresLocalOverrides: false, inputs: [] },
    };
  }

  async function loadCatalog(container) {
    const catalogUrl = container.dataset.catalogUrl || '../catalogs/index.yaml';
    const response = await fetch(catalogUrl);
    if (!response.ok) {
      throw new Error(`Unable to load catalog: ${response.status}`);
    }
    const raw = await response.text();
    const data = jsyaml.load(raw);
    state.entries = (data.entries || []).map(normalizeEntry);
  }

  function fillSelect(select, values) {
    const current = select.value;
    const options = ['all', ...Array.from(new Set(values)).sort()];
    select.innerHTML = options
      .map((value) => `<option value="${value}">${value === 'all' ? 'All' : escapeHtml(value)}</option>`)
      .join('');
    select.value = options.includes(current) ? current : 'all';
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function matches(entry) {
    const q = state.search.trim().toLowerCase();
    const searchable = [
      entry.name,
      entry.description,
      entry.kind,
      entry.category,
      entry.visibility,
      entry.sourceRepository,
      ...entry.tags,
    ].join(' ').toLowerCase();

    return (!q || searchable.includes(q)) &&
      (state.visibility === 'all' || entry.visibility === state.visibility) &&
      (state.kind === 'all' || entry.kind === state.kind) &&
      (state.category === 'all' || entry.category === state.category);
  }

  function renderCard(entry) {
    const artifactUrl = entry.artifact && entry.artifact.url;
    const commercialUrl = entry.commercial && entry.commercial.url;
    const commercialLabel = (entry.commercial && entry.commercial.label) || 'Request access';

    const action = artifactUrl
      ? `<a class="pk3s-action" href="${escapeHtml(artifactUrl)}">Download TGZ</a>`
      : commercialUrl
        ? `<a class="pk3s-action" href="${escapeHtml(commercialUrl)}">${escapeHtml(commercialLabel)}</a>`
        : `<span class="pk3s-action secondary">Coming soon</span>`;

    const install = entry.install || { requiresLocalOverrides: false, inputs: [] };
    const localOverrideBadge = entry.kind === 'profile' && install.requiresLocalOverrides
      ? `<span class="pk3s-badge">local overrides required</span>`
      : '';
    const inputsBlock = entry.kind === 'profile' && Array.isArray(install.inputs) && install.inputs.length
      ? `
        <div class="pk3s-install-meta">
          <strong>Install inputs</strong>
          <ul>
            ${install.inputs.map((input) => `<li><code>${escapeHtml(input.name)}</code> · ${escapeHtml(input.source || 'either')}${input.required ? ' · required' : ''}${input.sensitive ? ' · sensitive' : ''}</li>`).join('')}
          </ul>
        </div>
      `
      : '';

    return `
      <article class="pk3s-card" data-kind="${escapeHtml(entry.kind)}" data-visibility="${escapeHtml(entry.visibility)}">
        <div class="pk3s-badges">
          <span class="pk3s-badge">${escapeHtml(entry.kind)}</span>
          <span class="pk3s-badge">${escapeHtml(entry.visibility)}</span>
          <span class="pk3s-badge">${escapeHtml(entry.category)}</span>
          ${localOverrideBadge}
        </div>
        <h3>${escapeHtml(entry.name)}</h3>
        <p>${escapeHtml(entry.description)}</p>
        ${inputsBlock}
        <div class="pk3s-tags">
          ${entry.tags.map((tag) => `<span class="pk3s-tag">${escapeHtml(tag)}</span>`).join('')}
        </div>
        <small>${entry.version ? `Version ${escapeHtml(entry.version)}` : ''}${entry.sourceRepository ? ` · ${escapeHtml(entry.sourceRepository)}` : ''}</small>
        <div class="pk3s-actions">${action}</div>
      </article>
    `;
  }

  function render() {
    const cards = byId('pk3s-cards');
    const summary = byId('pk3s-summary');
    const filtered = state.entries.filter(matches);

    fillSelect(byId('pk3s-kind'), state.entries.map((entry) => entry.kind));
    fillSelect(byId('pk3s-category'), state.entries.map((entry) => entry.category));

    summary.textContent = `${filtered.length} entries shown from ${state.entries.length} catalog entries.`;
    cards.innerHTML = filtered.length
      ? filtered.map(renderCard).join('')
      : '<p>No catalog entries match the selected filters.</p>';
  }

  function wireEvents() {
    byId('pk3s-search').addEventListener('input', (event) => {
      state.search = event.target.value;
      render();
    });

    byId('pk3s-visibility').addEventListener('change', (event) => {
      state.visibility = event.target.value;
      render();
    });

    byId('pk3s-kind').addEventListener('change', (event) => {
      state.kind = event.target.value;
      render();
    });

    byId('pk3s-category').addEventListener('change', (event) => {
      state.category = event.target.value;
      render();
    });
  }

  document.addEventListener('DOMContentLoaded', async () => {
    const container = document.querySelector('.pk3s-marketplace');
    if (!container) return;

    try {
      wireEvents();
      await loadCatalog(container);
      render();
    } catch (error) {
      const cards = byId('pk3s-cards');
      cards.innerHTML = `<p>${escapeHtml(error.message)}</p>`;
    }
  });
})();
