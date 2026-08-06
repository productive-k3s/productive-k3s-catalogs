# Formato del catálogo

El catálogo es un índice YAML normalizado generado por `productive-k3s-ops`.

El sitio actualmente espera, como mínimo, esta forma:

```yaml
apiVersion: catalogs.productive-k3s.io/v1alpha1
kind: ProductiveK3SCatalog
metadata:
  name: productive-k3s-catalog
  generatedAt: "2026-05-27T00:00:00Z"
entries:
  - id: core-rancher
    name: Rancher
    kind: addon
    visibility: public
    category: management
    description: Rancher dashboard for Productive K3S clusters.
    version: 0.1.0
    sourceRepository: productive-k3s-addons
    artifact:
      type: tgz
      url: https://example.com/rancher-0.1.0.tgz
    tags:
      - rancher
      - dashboard
      - management
```

Los profiles también pueden exponer metadatos de instalación derivados del repositorio fuente:

```yaml
install:
  requiresLocalOverrides: true
  inputs:
    - name: AWS_REGION
      required: true
      sensitive: false
      source: package-default
      description: Default AWS region used for provisioning
    - name: AWS_KEY_PAIR_NAME
      required: true
      sensitive: false
      source: local-override
      description: Existing AWS EC2 key pair name
```

Este resumen lo genera `productive-k3s-ops` a partir de metadata de profiles que vive junto a los `*.env` fuente en los repositorios de Infra. Está pensado para discovery y UX, no como reemplazo del manifiesto del paquete.

Las entradas protegidas pueden omitir la URL directa del artifact y exponer en cambio una acción comercial:

```yaml
artifact:
  type: tgz
  url: null
commercial:
  label: Request access
  url: https://productive-k3s.io/contact/
```
