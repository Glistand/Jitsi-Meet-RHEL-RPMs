#!/usr/bin/env bash
# Клонирование upstream-репозиториев Jitsi для локальной сборки.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$ROOT/src"
mkdir -p "$SRC"

clone_or_pull() {
  local name="$1"
  local url="https://github.com/jitsi/${name}.git"
  if [[ -d "$SRC/$name/.git" ]]; then
    echo "Updating $name..."
    git -C "$SRC/$name" pull --ff-only
  else
    echo "Cloning $name..."
    git clone --depth 1 "$url" "$SRC/$name"
  fi
}

for repo in jitsi-meet jitsi-videobridge jicofo jigasi jibri; do
  clone_or_pull "$repo"
done

echo "Done. Sources in $SRC"
