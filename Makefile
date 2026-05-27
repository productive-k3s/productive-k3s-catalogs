.PHONY: setup serve build validate clean

setup:
	python -m pip install -r requirements.txt

serve:
	mkdocs serve

build:
	mkdocs build --strict

validate:
	python scripts/validate_catalog.py catalogs/index.yaml

clean:
	rm -rf site
