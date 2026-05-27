# Marketplace

<div class="pk3s-marketplace" data-catalog-url="../catalogs/index.yaml">
  <aside class="pk3s-filters">
    <label>
      Search
      <input id="pk3s-search" type="search" placeholder="Search catalog..." />
    </label>

    <label>
      Visibility
      <select id="pk3s-visibility">
        <option value="all">All</option>
        <option value="public">Public</option>
        <option value="protected">Protected</option>
        <option value="private">Private</option>
      </select>
    </label>

    <label>
      Type
      <select id="pk3s-kind">
        <option value="all">All</option>
      </select>
    </label>

    <label>
      Category
      <select id="pk3s-category">
        <option value="all">All</option>
      </select>
    </label>
  </aside>

  <section class="pk3s-results">
    <div id="pk3s-summary" class="pk3s-summary"></div>
    <div id="pk3s-cards" class="pk3s-card-grid"></div>
  </section>
</div>
