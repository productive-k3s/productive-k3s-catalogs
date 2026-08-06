# Marketplace

<div class="pk3s-marketplace" data-catalog-url="/catalogs/index.yaml">
  <aside class="pk3s-filters">
    <label>
      Buscar
      <input id="pk3s-search" type="search" placeholder="Buscar en el catálogo..." />
    </label>

    <label>
      Visibilidad
      <select id="pk3s-visibility">
        <option value="all">Todas</option>
        <option value="public">Pública</option>
        <option value="protected">Protegida</option>
        <option value="private">Privada</option>
      </select>
    </label>

    <label>
      Tipo
      <select id="pk3s-kind">
        <option value="all">Todos</option>
      </select>
    </label>

    <label>
      Categoría
      <select id="pk3s-category">
        <option value="all">Todas</option>
      </select>
    </label>
  </aside>

  <section class="pk3s-results">
    <div id="pk3s-summary" class="pk3s-summary"></div>
    <div id="pk3s-cards" class="pk3s-card-grid"></div>
  </section>
</div>
