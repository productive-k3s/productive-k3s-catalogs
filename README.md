# Productive K3S Catalogs

Public catalog and marketplace website for the Productive K3S ecosystem.

This repository publishes the generated catalog indexes consumed by the Productive K3S CLI and renders them as a MkDocs-based web portal. The catalog exposes public and protected Productive K3S entries, including infrastructure scenarios, profiles, and add-ons packaged as downloadable artifacts.

## Purpose

`productive-k3s-catalogs` is the public discovery layer for Productive K3S.

It is designed to:

- publish catalog YAML files generated from `productive-k3s-ops`;
- expose installable public entries for the CLI;
- list protected or commercial entries with purchase/contact links;
- render a GitHub Pages marketplace-style website;
- keep the public catalog format stable and easy to consume from automation.

## Repository layout

```text
.
├── catalogs/                  # Generated catalog indexes consumed by the CLI and website
│   └── index.yaml
├── docs/                      # MkDocs website source
│   ├── index.md
│   ├── catalog.md
│   └── assets/
│       ├── javascripts/
│       │   └── marketplace.js
│       └── stylesheets/
│           └── marketplace.css
├── scripts/                   # Validation / generation helpers
│   └── validate_catalog.py
├── .github/workflows/         # GitHub Pages publishing workflow
│   └── docs.yml
├── mkdocs.yml
├── requirements.txt
├── Makefile
└── LICENSE
```

## Local development

```bash
make setup
make serve
```

The documentation site will be available at:

```text
http://127.0.0.1:8000
```

## Validate catalog

```bash
make validate
```

## Publish model

The expected flow is:

1. `productive-k3s-ops` reads public and protected source repositories.
2. It generates one or more normalized YAML catalog indexes.
3. This repository publishes those YAML files.
4. The CLI reads the catalog to discover available entries.
5. The MkDocs website renders the same catalog as a marketplace page.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
