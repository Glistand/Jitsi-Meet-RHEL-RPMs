#!/usr/bin/env bash
# Загрузка portable JDK 21 и Maven (без root).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS="$ROOT/tools"
mkdir -p "$TOOLS"

if [[ ! -x "$TOOLS/jdk-21.0.12.1+1/bin/java" ]]; then
  echo "Downloading Temurin JDK 21..."
  curl -sL -o "$TOOLS/temurin21.tar.gz" \
    "https://api.adoptium.net/v3/binary/latest/21/ga/linux/x64/jdk/hotspot/normal/eclipse?project=jdk"
  tar xzf "$TOOLS/temurin21.tar.gz" -C "$TOOLS"
fi

if [[ ! -x "$TOOLS/apache-maven-3.9.9/bin/mvn" ]]; then
  echo "Downloading Maven 3.9.9..."
  curl -sL -o "$TOOLS/apache-maven.tar.gz" \
    "https://archive.apache.org/dist/maven/maven-3/3.9.9/binaries/apache-maven-3.9.9-bin.tar.gz"
  tar xzf "$TOOLS/apache-maven.tar.gz" -C "$TOOLS"
fi

echo "JAVA_HOME=$TOOLS/jdk-21.0.12.1+1"
echo "MAVEN_HOME=$TOOLS/apache-maven-3.9.9"
