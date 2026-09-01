#!/usr/bin/env bash
# createrepo_c для EL9-репозитория (локально или через rockylinux:9 container).
set -euo pipefail

REPO_DIR="${1:?usage: createrepo-el9.sh <repo-dir>}"

run_createrepo() {
  createrepo_c --update "$REPO_DIR" 2>/dev/null || createrepo_c "$REPO_DIR"
}

if command -v createrepo_c >/dev/null 2>&1; then
  run_createrepo
  exit 0
fi

if command -v podman >/dev/null 2>&1; then
  CONTAINER=podman
elif command -v docker >/dev/null 2>&1; then
  CONTAINER=docker
else
  echo "ERROR: createrepo_c not found and no podman/docker" >&2
  exit 1
fi

REPO_PARENT="$(cd "$(dirname "$REPO_DIR")" && pwd)"
REPO_BASE="$(basename "$REPO_DIR")"

$CONTAINER run --rm -i -v "${REPO_PARENT}:/repos:Z" rockylinux:9 \
  bash -c "dnf install -y -q createrepo_c && createrepo_c --update /repos/${REPO_BASE} 2>/dev/null || createrepo_c /repos/${REPO_BASE}"
