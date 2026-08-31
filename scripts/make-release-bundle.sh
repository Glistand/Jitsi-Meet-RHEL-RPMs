#!/usr/bin/env bash
# Сборка release-архива: RPM (el9/fc44) + примеры конфигов + INSTALL-RHEL.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-dev}"
RPM_DIR="${2:-$ROOT/build/rpms/noarch}"
OUT_DIR="${3:-$ROOT/dist}"

BUNDLE_NAME="jitsi-meet-rhel-${VERSION#v}"
STAGING="$OUT_DIR/$BUNDLE_NAME"

rm -rf "$STAGING"
mkdir -p "$STAGING/rpms/el9" "$STAGING/rpms/fc44" "$STAGING/config-examples"

# RPM
shopt -s nullglob
el9=( "$RPM_DIR"/*el9*.rpm )
fc44=( "$RPM_DIR"/*fc44*.rpm )
if ((${#el9[@]} == 0)); then
  echo "ERROR: no *el9*.rpm in $RPM_DIR" >&2
  exit 1
fi
cp -a "${el9[@]}" "$STAGING/rpms/el9/"
((${#fc44[@]})) && cp -a "${fc44[@]}" "$STAGING/rpms/fc44/" || true

# Документация и конфиги
cp "$ROOT/release/INSTALL-RHEL.md" "$STAGING/"
cp -a "$ROOT/rpms/config/examples/." "$STAGING/config-examples/"
cp -a "$ROOT/rpms/config/jicofo-config" "$STAGING/config-examples/jicofo/config.env.example"
cp -a "$ROOT/rpms/config/videobridge-config" "$STAGING/config-examples/jvb/config.env.example"
mkdir -p "$STAGING/config-examples/systemd"
cp -a "$ROOT/rpms/systemd/." "$STAGING/config-examples/systemd/"

# Контрольные суммы
(
  cd "$STAGING"
  sha256sum rpms/el9/*.rpm rpms/fc44/*.rpm 2>/dev/null | sed 's| rpms/|  rpms/|'
) > "$STAGING/CHECKSUMS.sha256"

ARCHIVE="$OUT_DIR/${BUNDLE_NAME}.tar.gz"
tar -C "$OUT_DIR" -czf "$ARCHIVE" "$BUNDLE_NAME"

echo "Created: $ARCHIVE"
echo "File count: $(tar -tzf "$ARCHIVE" | wc -l)"
