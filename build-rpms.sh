#!/usr/bin/env bash
# Сборка RPM-пакетов Jitsi Meet для RHEL/Fedora из локальных исходников.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$ROOT/src"
RPMS="$ROOT/rpms"
TOOLS="$ROOT/tools"
OUT="$ROOT/build/rpms"

JAVA_HOME="${JAVA_HOME:-$TOOLS/jdk-21.0.12.1+1}"
MAVEN_HOME="${MAVEN_HOME:-$TOOLS/apache-maven-3.9.9}"
export JAVA_HOME PATH="$JAVA_HOME/bin:$MAVEN_HOME/bin:$PATH"

PREBUILT="${PREBUILT:-1}"
TARGET_DIST="${TARGET_DIST:-}"

mkdir -p "$OUT" "$ROOT/build/logs"

log() { echo "[build-rpms] $*"; }

ensure_tools() {
  if [[ ! -x "$JAVA_HOME/bin/java" ]]; then
    log "JDK 21 не найден в $JAVA_HOME. Запустите: tools/bootstrap.sh"
    exit 1
  fi
  if [[ ! -x "$MAVEN_HOME/bin/mvn" ]]; then
    log "Maven не найден в $MAVEN_HOME. Запустите: tools/bootstrap.sh"
    exit 1
  fi
}

build_java_components() {
  if [[ "$PREBUILT" == "1" ]]; then
    log "PREBUILT=1 — пропуск Maven (ожидаются готовые archive.zip)"
    return
  fi
  log "Сборка jicofo..."
  (cd "$SRC/jicofo" && mvn -DskipTests package) | tee "$ROOT/build/logs/jicofo-maven.log"
  log "Сборка jitsi-videobridge..."
  (cd "$SRC/jitsi-videobridge" && mvn -DskipTests package) | tee "$ROOT/build/logs/jvb-maven.log"
}

build_web() {
  if [[ "$PREBUILT" == "1" && -d "$SRC/jitsi-meet/libs" ]]; then
    log "jitsi-meet web уже собран (libs/)"
    return
  fi
  log "Сборка jitsi-meet web (npm + make)..."
  (cd "$SRC/jitsi-meet" && npm ci && NODE_OPTIONS=--max-old-space-size=8192 make) \
    | tee "$ROOT/build/logs/jitsi-meet-make.log"
}

rpmbuild_all() {
  local defines=(
    --define "_topdir $ROOT/build/rpmbuild"
    --define "_rpmdir $OUT"
    --define "_srcrpmdir $OUT"
    --define "_jitsi_root $ROOT"
    --define "_java_home $JAVA_HOME"
    --define "_maven_home $MAVEN_HOME"
    --define "_prebuilt $PREBUILT"
  )
  if [[ -n "$TARGET_DIST" ]]; then
    defines+=(--define "dist .$TARGET_DIST")
  fi

  mkdir -p "$ROOT/build/rpmbuild"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

  for spec in jicofo jitsi-videobridge jitsi-meet-web jitsi; do
    log "rpmbuild: $spec"
    rpmbuild -bb "${defines[@]}" "$RPMS/SPECS/$spec.spec"
  done
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [all|java|web|rpm]

  all   — полная сборка (по умолчанию)
  java  — только Maven (jicofo + videobridge)
  web   — только jitsi-meet web
  rpm   — только rpmbuild (PREBUILT=1)

Переменные окружения:
  PREBUILT=1     использовать уже собранные артефакты (по умолчанию)
  TARGET_DIST=el9  суффикс дистрибутива RPM (.el9)
  JAVA_HOME      путь к JDK 21 (по умолчанию tools/jdk-21.0.12.1+1)

Пример для RHEL 9:
  TARGET_DIST=el9 PREBUILT=1 ./build-rpms.sh rpm
EOF
}

main() {
  local step="${1:-all}"
  ensure_tools
  case "$step" in
    all)
      build_java_components
      build_web
      rpmbuild_all
      ;;
    java) build_java_components ;;
    web)  build_web ;;
    rpm)  rpmbuild_all ;;
    -h|--help) usage ;;
    *) usage; exit 1 ;;
  esac
  log "Готово. RPM: $OUT"
  find "$OUT" -name '*.rpm' -printf '%p\n' 2>/dev/null || find "$OUT" -name '*.rpm'
}

main "$@"
