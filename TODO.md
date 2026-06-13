# TODO

Simple, versioned backlog for `productive-k3s-catalogs` only.

Format:
- `Title`: short action-oriented label
- `Description`: one sentence, max 250 chars, easy to scan in reviews

Rules:
- Keep only repo-local responsibilities here.
- Do not track work owned by other repositories.
- Cross-repo dependencies can be mentioned only as context, never as the main ownership of an item.

## Catalog Contract

- `Document Stack Entries Publicly`
  `Update the public catalog docs so stack entries are explained alongside addon and profile artifacts, including their intended consumer flows.`

- `Review Catalog Schema Coverage`
  `Check whether the validator should enforce more entry-level fields or compatibility metadata as stack and package contracts grow richer.`

- `Clarify Source Repository Labels`
  `Keep catalog docs and examples aligned with the current split between source repositories, runtime engines, and published artifacts.`

## Site and Validation

- `Improve Marketplace Presentation`
  `Refine the website presentation so addon, stack, and profile entries remain easy to distinguish as the catalog grows.`

- `Add Catalog Fixture Coverage`
  `Expand validation fixtures so schema regressions for new kinds like stack are caught before publishing the generated catalog index.`

- `Review Generated vs Doc Copies`
  `Make sure generated catalog files and documentation mirrors stay intentionally synchronized and avoid drifting independently.`
