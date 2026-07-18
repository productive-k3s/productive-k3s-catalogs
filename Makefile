.PHONY: setup serve build validate sync-catalog sync-theme clean

setup:
	python3 -m pip install -r requirements.txt

serve:
	$(MAKE) sync-theme
	$(MAKE) sync-catalog
	mkdocs serve

build:
	$(MAKE) sync-theme
	$(MAKE) sync-catalog
	mkdocs build --strict

validate:
	python3 scripts/validate_catalog.py catalogs/index.yaml

sync-catalog:
	python3 scripts/sync_catalog_docs.py

sync-theme:
	bash ./sync-shared-theme.sh

clean:
	rm -rf site
