#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_THEME_VERSION="${DOCS_THEME_VERSION:-1.0.2}"
DOCS_THEME_REPO_URL="${DOCS_THEME_REPO_URL:-https://github.com/productive-k3s/productive-k3s-docs-theme}"
DOCS_THEME_ARCHIVE_URL="${DOCS_THEME_ARCHIVE_URL:-${DOCS_THEME_REPO_URL}/archive/refs/tags/${DOCS_THEME_VERSION}.tar.gz}"
DOCS_THEME_CACHE_DIR="${DOCS_THEME_CACHE_DIR:-${ROOT_DIR}/.cache/productive-k3s-docs-theme}"
DOCS_THEME_ARCHIVE_PATH="${DOCS_THEME_ARCHIVE_PATH:-${DOCS_THEME_CACHE_DIR}/${DOCS_THEME_VERSION}.tar.gz}"
DOCS_THEME_EXTRACT_DIR="${DOCS_THEME_EXTRACT_DIR:-${DOCS_THEME_CACHE_DIR}/${DOCS_THEME_VERSION}}"
SHARED_THEME_DIR_OVERRIDE="${SHARED_THEME_DIR:-}"
DEFAULT_SHARED_THEME_DIR="${ROOT_DIR}/.shared/productive-k3s-docs-theme/material-overrides"
SHARED_THEME_DIR="${SHARED_THEME_DIR_OVERRIDE:-${DOCS_THEME_EXTRACT_DIR}/productive-k3s-docs-theme-${DOCS_THEME_VERSION}/material-overrides}"
PREPARE_ONLY=0

usage() {
  cat <<EOF
Usage:
  $(basename "$0") [--prepare-only]

Behavior:
  - uses SHARED_THEME_DIR when explicitly provided and present
  - otherwise downloads docs theme ${DOCS_THEME_VERSION} from ${DOCS_THEME_ARCHIVE_URL}
  - caches the extracted theme under ${DOCS_THEME_CACHE_DIR}
EOF
}

while (($# > 0)); do
  case "$1" in
    --prepare-only)
      PREPARE_ONLY=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf '[ERROR] Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

prepare_theme_cache() {
  if [[ -d "${DEFAULT_SHARED_THEME_DIR}" && -z "${SHARED_THEME_DIR_OVERRIDE}" ]]; then
    SHARED_THEME_DIR="${DEFAULT_SHARED_THEME_DIR}"
    return 0
  fi

  if [[ -d "${SHARED_THEME_DIR}" ]]; then
    return 0
  fi

  mkdir -p "${DOCS_THEME_CACHE_DIR}"
  if [[ ! -f "${DOCS_THEME_ARCHIVE_PATH}" ]]; then
    printf '[INFO] Downloading docs theme %s from %s\n' "${DOCS_THEME_VERSION}" "${DOCS_THEME_ARCHIVE_URL}"
    curl -fsSL "${DOCS_THEME_ARCHIVE_URL}" -o "${DOCS_THEME_ARCHIVE_PATH}"
  fi

  if [[ ! -d "${DOCS_THEME_EXTRACT_DIR}/productive-k3s-docs-theme-${DOCS_THEME_VERSION}/material-overrides" ]]; then
    rm -rf "${DOCS_THEME_EXTRACT_DIR}"
    mkdir -p "${DOCS_THEME_EXTRACT_DIR}"
    tar -xzf "${DOCS_THEME_ARCHIVE_PATH}" -C "${DOCS_THEME_EXTRACT_DIR}"
  fi

  SHARED_THEME_DIR="${DOCS_THEME_EXTRACT_DIR}/productive-k3s-docs-theme-${DOCS_THEME_VERSION}/material-overrides"
}

prepare_theme_cache

if [[ ! -d "${SHARED_THEME_DIR}" ]]; then
  printf '[ERROR] Shared theme directory not found after preparation: %s\n' "${SHARED_THEME_DIR}" >&2
  exit 1
fi

if [[ "${PREPARE_ONLY}" -eq 1 ]]; then
  printf '[INFO] Docs theme prepared at %s\n' "${SHARED_THEME_DIR}"
  exit 0
fi

install -d \
  "${ROOT_DIR}/docs/src/overrides/partials" \
  "${ROOT_DIR}/docs/src/assets/stylesheets" \
  "${ROOT_DIR}/docs/src/assets/images"

cp "${SHARED_THEME_DIR}/main.html" "${ROOT_DIR}/docs/src/overrides/main.html"
cp "${SHARED_THEME_DIR}/partials/logo.html" "${ROOT_DIR}/docs/src/overrides/partials/logo.html"
cp "${SHARED_THEME_DIR}/partials/header.html" "${ROOT_DIR}/docs/src/overrides/partials/header.html"
cp "${SHARED_THEME_DIR}/partials/footer.html" "${ROOT_DIR}/docs/src/overrides/partials/footer.html"
cp "${SHARED_THEME_DIR}/partials/toc.html" "${ROOT_DIR}/docs/src/overrides/partials/toc.html"
cp "${SHARED_THEME_DIR}/assets/stylesheets/extra.css" "${ROOT_DIR}/docs/src/assets/stylesheets/extra.css"
cp "${SHARED_THEME_DIR}/assets/images/argentina.png" "${ROOT_DIR}/docs/src/assets/images/argentina.png"
cp "${SHARED_THEME_DIR}/assets/images/productive-k3s-icon-square-0.3x.png" "${ROOT_DIR}/docs/src/assets/images/productive-k3s-icon-square-0.3x.png"
cp "${SHARED_THEME_DIR}/assets/images/favicon.ico" "${ROOT_DIR}/docs/src/assets/images/favicon.ico"
