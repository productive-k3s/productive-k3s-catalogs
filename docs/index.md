# Productive K3S Catalogs

Productive K3S Catalogs is the public discovery point for installable Productive K3S content.

It exposes a CLI-readable catalog and a marketplace-style web portal for:

- infrastructure scenarios;
- environment profiles;
- optional add-ons;
- public and protected/pro entries.

[Open marketplace](catalog.md){ .md-button .md-button--primary }

## How it fits

```mermaid
graph LR
  Ops[productive-k3s-ops] --> Catalogs[productive-k3s-catalogs]
  Infra[productive-k3s-infra] --> Ops
  InfraPro[productive-k3s-profiles-pro] --> Ops
  Addons[productive-k3s-addons] --> Ops
  AddonsPro[productive-k3s-addons-pro] --> Ops
  Catalogs --> CLI[productive-k3s-cli]
  Catalogs --> Web[GH Pages marketplace]
```

## Catalog responsibilities

This repository does not own the implementation of scenarios, profiles or add-ons. It publishes the index that points to them.

Public entries can point directly to downloadable artifacts. Protected entries can point to a purchase, contact, or authorization flow.
