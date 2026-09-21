SHELL := /bin/bash
PID_FILE := .mkdocs.pid
LOG_FILE := .mkdocs.log

.PHONY: setup \
	docs-prepare \
	docs-build docs-serve docs-up docs-down docs-clean \
	serve build clean \
	validate sync-catalog sync-theme

setup:
	python3 -m pip install -r requirements.txt

docs-prepare:
	bash ./sync-shared-theme.sh --prepare-only

docs-serve:
	$(MAKE) docs-prepare
	$(MAKE) sync-theme
	$(MAKE) sync-catalog
	mkdocs serve --config-file mkdocs.yml --dev-addr 127.0.0.1:8000

docs-build:
	$(MAKE) docs-prepare
	$(MAKE) sync-theme
	$(MAKE) sync-catalog
	mkdocs build --strict

docs-up:
	$(MAKE) docs-prepare
	$(MAKE) sync-theme
	$(MAKE) sync-catalog
	@if [[ -f "$(PID_FILE)" ]]; then \
		existing_pid="$$(cat "$(PID_FILE)")"; \
		if kill -0 "$${existing_pid}" >/dev/null 2>&1; then \
			printf '[INFO] MkDocs is already running on http://127.0.0.1:8000 (pid %s)\n' "$${existing_pid}"; \
			exit 0; \
		fi; \
		rm -f "$(PID_FILE)"; \
	fi; \
	nohup mkdocs serve --config-file mkdocs.yml --dev-addr 127.0.0.1:8000 >"$(LOG_FILE)" 2>&1 & \
	server_pid="$$!"; \
	printf '%s\n' "$${server_pid}" > "$(PID_FILE)"; \
	printf '[INFO] MkDocs started on http://127.0.0.1:8000 (pid %s)\n' "$${server_pid}"; \
	printf '[INFO] Log file: %s\n' "$(LOG_FILE)"

docs-down:
	@if [[ -f "$(PID_FILE)" ]]; then \
		existing_pid="$$(cat "$(PID_FILE)")"; \
		if kill -0 "$${existing_pid}" >/dev/null 2>&1; then \
			kill "$${existing_pid}" >/dev/null 2>&1 || true; \
		fi; \
		rm -f "$(PID_FILE)"; \
	fi
	rm -f "$(LOG_FILE)"

docs-clean:
	rm -rf site
	rm -f "$(PID_FILE)" "$(LOG_FILE)"

serve: docs-serve

build: docs-build

validate:
	python3 scripts/validate_catalog.py catalogs/index.yaml

sync-catalog:
	python3 scripts/sync_catalog_docs.py

sync-theme:
	bash ./sync-shared-theme.sh

clean: docs-clean
