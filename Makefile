SHELL := /bin/bash

.PHONY: setup \
	docs-build docs-serve docs-up docs-down docs-clean \
	serve build clean \
	validate sync-catalog sync-theme

setup:
	python3 -m pip install -r requirements.txt

docs-serve:
	$(MAKE) sync-theme
	$(MAKE) sync-catalog
	mkdocs serve

docs-build:
	$(MAKE) sync-theme
	$(MAKE) sync-catalog
	mkdocs build --strict

docs-up:
	$(MAKE) docs-serve

docs-down:
	$(MAKE) docs-clean

docs-clean:
	rm -rf site

serve: docs-serve

build: docs-build

validate:
	python3 scripts/validate_catalog.py catalogs/index.yaml

sync-catalog:
	python3 scripts/sync_catalog_docs.py

sync-theme:
	bash ./sync-shared-theme.sh

clean: docs-clean
