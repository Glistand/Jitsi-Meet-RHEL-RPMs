#!/usr/bin/env bash
# Скачивание RPM-зависимостей для офлайн-установки на RHEL 9 / Rocky / Alma.
# Запускать на машине с интернетом (или через Docker rockylinux:9).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:-$ROOT/build/offline-repo/el9}"
DIST="${2:-el9}"

if [[ "$DIST" != "el9" ]]; then
  echo "ERROR: only el9 is supported (got: $DIST)" >&2
  exit 1
fi

mkdir -p "$DEST"

# Пакеты для базового стека Jitsi Meet (без certbot — для LE нужен интернет).
EL9_PACKAGES=(
  java-21-openjdk-headless
  prosody
  nginx
  firewalld
  lua-sec
  lua-basexx
  lua-luaossl
  lua-expat
  lua-filesystem
  lua-socket
  openssl
  ca-certificates
  createrepo_c
)

download_el9() {
  local dest="$1"
  dnf install -y epel-release dnf-plugins-core createrepo_c
  if [[ -x /usr/bin/crb ]]; then
    /usr/bin/crb enable
  elif command -v dnf >/dev/null; then
    dnf config-manager --set-enabled crb 2>/dev/null || true
  fi
  dnf makecache -y
  dnf download --resolve --destdir="$dest" "${EL9_PACKAGES[@]}"
}

run_in_docker() {
  local dest="$1"
  local dest_parent dest_base
  dest_parent="$(cd "$(dirname "$dest")" && pwd)"
  dest_base="$(basename "$dest")"

  if command -v podman >/dev/null 2>&1; then
    CONTAINER=podman
  elif command -v docker >/dev/null 2>&1; then
    CONTAINER=docker
  else
    echo "ERROR: need Rocky/EL9 host or podman/docker for offline deps download" >&2
    exit 1
  fi

  echo "Downloading EL9 deps via $CONTAINER (rockylinux:9) -> $dest"
  $CONTAINER run --rm -i \
    -v "${dest_parent}:/out:Z" \
    rockylinux:9 \
    bash -s "$dest_base" <<'DOCKEREOF'
set -euo pipefail
dest="/out/$1"
mkdir -p "$dest"
dnf install -y epel-release dnf-plugins-core createrepo_c
/usr/bin/crb enable || true
dnf makecache -y
dnf download --resolve --destdir="$dest" \
  java-21-openjdk-headless prosody nginx firewalld \
  lua-sec lua-basexx lua-luaossl lua-expat lua-filesystem lua-socket \
  openssl ca-certificates createrepo_c
DOCKEREOF
}

is_el9_host() {
  [[ -r /etc/os-release ]] || return 1
  # shellcheck disable=SC1091
  source /etc/os-release
  [[ "${VERSION_ID:-}" == "9" ]] || return 1
  case "${ID:-}" in
    rhel|rocky|almalinux|centos|ol) return 0 ;;
    *) return 1 ;;
  esac
}

if is_el9_host; then
  # RHEL 9 / Rocky / Alma — нативный dnf
  download_el9 "$DEST"
else
  run_in_docker "$DEST"
fi

count="$(find "$DEST" -maxdepth 1 -name '*.rpm' | wc -l)"
echo "Total RPM(s) in $DEST: $count"
