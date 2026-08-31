#!/usr/bin/env bash
# Клонирование upstream-репозиториев Jitsi для локальной сборки.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/src"
mkdir -p "$SRC"

JITSI_STABLE_TAG="${JITSI_STABLE_TAG:-stable/jitsi-meet_11146}"

clone_or_pull() {
  local name="$1"
  local url="$2"
  local ref="${3:-}"
  if [[ -d "$SRC/$name/.git" ]]; then
    echo "Updating $name..."
    if [[ -n "$ref" ]]; then
      git -C "$SRC/$name" fetch --depth 1 origin "refs/tags/${ref}:refs/tags/${ref}" 2>/dev/null \
        || git -C "$SRC/$name" fetch --depth 1 origin "$ref"
      git -C "$SRC/$name" checkout -f "$ref"
    else
      git -C "$SRC/$name" pull --ff-only
    fi
  else
    echo "Cloning $name..."
    if [[ -n "$ref" ]]; then
      git clone --depth 1 --branch "$ref" "$url" "$SRC/$name"
    else
      git clone --depth 1 "$url" "$SRC/$name"
    fi
  fi
}

# Core Jitsi stack — один stable-тег на все три репо
clone_or_pull jitsi-meet       "https://github.com/jitsi/jitsi-meet.git"                       "$JITSI_STABLE_TAG"
clone_or_pull jitsi-videobridge "https://github.com/jitsi/jitsi-videobridge.git"             "$JITSI_STABLE_TAG"
clone_or_pull jicofo           "https://github.com/jitsi/jicofo.git"                         "$JITSI_STABLE_TAG"

# File sharing (отдельный репо, пока без привязки к stable-тегу meet)
clone_or_pull jitsi-meet-file-sharing-service \
  "https://github.com/jitsi/jitsi-meet-file-sharing-service.git"

# Reservation REST API (Prosody mod_reservations → этот backend)
clone_or_pull jitsi-reservation-api \
  "https://github.com/grommunio/jitsi-reservation-api.git"

# Опционально, фаза 2 (тег может отсутствовать в репо)
for repo in jigasi jibri; do
  clone_or_pull "$repo" "https://github.com/jitsi/${repo}.git" "$JITSI_STABLE_TAG" || \
    echo "WARN: skip $repo (tag $JITSI_STABLE_TAG not found)"
done

echo "Done. Sources in $SRC"
