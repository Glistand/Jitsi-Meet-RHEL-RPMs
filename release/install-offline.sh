#!/usr/bin/env bash
# Офлайн-установка Jitsi Meet на RHEL 9 из распакованного release-архива.
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$BUNDLE_DIR/repo/el9"
DOMAIN="${1:-}"

if [[ ! -d "$REPO_DIR/repodata" ]]; then
  echo "ERROR: local repo not found: $REPO_DIR/repodata" >&2
  echo "Use a full offline release archive (with repo/el9/)." >&2
  exit 1
fi

if [[ $EUID -ne 0 ]]; then
  echo "Run as root: sudo $0 [meet.example.com]" >&2
  exit 1
fi

REPO_FILE=/etc/yum.repos.d/jitsi-meet-offline.repo
cat >"$REPO_FILE" <<EOF
[jitsi-meet-offline]
name=Jitsi Meet offline (bundled)
baseurl=file://${REPO_DIR}
enabled=1
gpgcheck=0
module_hotfixes=1
EOF

echo "==> Installing packages from local repo (no internet)..."
dnf clean all
dnf install -y --disablerepo='*' --enablerepo=jitsi-meet-offline \
  java-21-openjdk-headless prosody nginx firewalld nodejs \
  postgresql-server postgresql \
  jicofo jitsi-videobridge jitsi-meet-web \
  keycloak jitsi-meet-file-sharing-service

if [[ -d "$BUNDLE_DIR/prosody-plugins" ]]; then
  echo "==> Installing Prosody plugins..."
  install -d /usr/share/jitsi-meet
  cp -a "$BUNDLE_DIR/prosody-plugins" /usr/share/jitsi-meet/
fi

echo "==> Firewall (http, https, media)..."
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --permanent --add-port=10000/udp
firewall-cmd --reload

if [[ -n "$DOMAIN" && "$DOMAIN" != "meet.example.com" ]]; then
  echo "==> Substituting domain: $DOMAIN"
  find "$BUNDLE_DIR/config-examples" -type f -print0 |
    xargs -0 sed -i "s/meet.example.com/${DOMAIN}/g" 2>/dev/null || true
fi

cat <<'EOF'

Packages installed. Next steps (manual, see INSTALL-RHEL.md):

  1. TLS: use self-signed cert or your internal CA (certbot needs internet).
     Example:
       openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
         -keyout /etc/nginx/ssl/meet.key -out /etc/nginx/ssl/meet.crt

  2. Copy configs from config-examples/ (prosody, nginx, jicofo, jvb, meet).

  3. prosodyctl register focus auth.<domain> <password>
     prosodyctl register jvb auth.<domain> <password>

  4. systemctl enable --now prosody jicofo jitsi-videobridge nginx

EOF
