#!/usr/bin/env bash
# Сборка release-архива: RPM + офлайн-репозиторий зависимостей + конфиги + INSTALL-RHEL.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-dev}"
RPM_DIR="${2:-$ROOT/build/rpms/noarch}"
OUT_DIR="${3:-$ROOT/dist}"

BUNDLE_NAME="jitsi-meet-rhel-${VERSION#v}"
STAGING="$OUT_DIR/$BUNDLE_NAME"

rm -rf "$STAGING"
mkdir -p "$STAGING/rpms/el9" "$STAGING/rpms/fc44" "$STAGING/repo/el9" "$STAGING/config-examples"

# RPM Jitsi
shopt -s nullglob
el9=( "$RPM_DIR"/*el9*.rpm )
fc44=( "$RPM_DIR"/*fc44*.rpm )
if ((${#el9[@]} == 0)); then
  echo "ERROR: no *el9*.rpm in $RPM_DIR" >&2
  exit 1
fi
cp -a "${el9[@]}" "$STAGING/rpms/el9/"
cp -a "${el9[@]}" "$STAGING/repo/el9/"
((${#fc44[@]})) && cp -a "${fc44[@]}" "$STAGING/rpms/fc44/" || true

# Офлайн-зависимости EL9 (dnf download + createrepo)
if [[ "${SKIP_OFFLINE_DEPS:-0}" != "1" ]]; then
  echo "==> Downloading EL9 dependency RPMs for offline install..."
  "$ROOT/scripts/download-offline-deps.sh" "$STAGING/repo/el9" el9
  echo "==> Creating local DNF repo metadata..."
  "$ROOT/scripts/createrepo-el9.sh" "$STAGING/repo/el9"
else
  echo "SKIP_OFFLINE_DEPS=1 — repo/el9/ contains only Jitsi RPMs"
  "$ROOT/scripts/createrepo-el9.sh" "$STAGING/repo/el9"
fi

# Prosody-плагины из исходников jitsi-meet
PLUGINS_SRC="$ROOT/src/jitsi-meet/resources/prosody-plugins"
if [[ -d "$PLUGINS_SRC" ]]; then
  cp -a "$PLUGINS_SRC" "$STAGING/prosody-plugins"
else
  echo "WARN: $PLUGINS_SRC not found — run ./scripts/clone-sources.sh before bundle" >&2
fi

# Документация и конфиги
cp "$ROOT/release/INSTALL-RHEL.md" "$STAGING/"
cp "$ROOT/release/install-offline.sh" "$STAGING/"
chmod +x "$STAGING/install-offline.sh"
cp -a "$ROOT/rpms/config/examples/." "$STAGING/config-examples/"
cp -a "$ROOT/rpms/config/jicofo-config" "$STAGING/config-examples/jicofo/config.env.example"
cp -a "$ROOT/rpms/config/videobridge-config" "$STAGING/config-examples/jvb/config.env.example"
mkdir -p "$STAGING/config-examples/systemd"
cp -a "$ROOT/rpms/systemd/." "$STAGING/config-examples/systemd/"

# Контрольные суммы (Jitsi RPM + полный офлайн-репозиторий)
(
  cd "$STAGING"
  sha256sum rpms/el9/*.rpm rpms/fc44/*.rpm 2>/dev/null || true
  find repo/el9 -maxdepth 1 -name '*.rpm' | sort | xargs sha256sum 2>/dev/null || true
) > "$STAGING/CHECKSUMS.sha256"

ARCHIVE="$OUT_DIR/${BUNDLE_NAME}.tar.gz"
tar -C "$OUT_DIR" -czf "$ARCHIVE" "$BUNDLE_NAME"

RPM_COUNT="$(find "$STAGING/repo/el9" -maxdepth 1 -name '*.rpm' | wc -l)"
echo "Created: $ARCHIVE"
echo "RPM in offline repo/el9: $RPM_COUNT"
echo "Archive size: $(du -h "$ARCHIVE" | cut -f1)"
