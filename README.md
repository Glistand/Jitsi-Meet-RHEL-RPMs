# Jitsi Meet RHEL RPMs

> **Unofficial** community RPM packaging for Jitsi Meet on RHEL / Rocky Linux / AlmaLinux / Fedora.  
> Not affiliated with [8x8](https://www.8x8.com/) or [jitsi.org](https://jitsi.org/).

Сборка основных компонентов Jitsi Meet из upstream-репозиториев в `.rpm` с systemd-юнитами.

## Пакеты

| RPM | Описание |
|-----|----------|
| `jicofo` | Conference focus (сигнализация) |
| `jitsi-videobridge` | Videobridge (медиа) |
| `jitsi-meet-web` | Веб-клиент (статика) |
| `jitsi-meet-prosody` | Lua-плагины Prosody (reservations, file sharing, tokens) |
| `jitsi-meet-web-config` | nginx + config.js + TLS |
| `jitsi-meet-file-sharing-service` | REST API отправки файлов в конференции |
| `jitsi-reservation-api` | REST API бронирования комнат |
| `keycloak` | OIDC/SSO (нативный tarball + systemd, без Docker) |
| `jitsi-meet-auth-keycloak` | Шаблоны Prosody/config.js/nginx для Keycloak |
| `jitsi` | Метапакет полного стека |

Подробный план: [PLAN.md](PLAN.md).

## Быстрый старт

```bash
git clone https://github.com/Glistand/Jitsi-Meet-RHEL-RPMs.git
cd Jitsi-Meet-RHEL-RPMs

chmod +x build-rpms.sh tools/bootstrap.sh scripts/clone-sources.sh

# 1. Upstream-исходники
./scripts/clone-sources.sh

# 2. Portable JDK 21 + Maven (нужны для сборки Java-компонентов)
./tools/bootstrap.sh

# 3. Полная сборка
./build-rpms.sh all

# Или только RPM из уже собранных артефактов
TARGET_DIST=el9 PREBUILT=1 ./build-rpms.sh rpm
```

## Требования

- Fedora или RHEL 9+ (для сборки)
- `rpmbuild`, `git`, `nodejs`, `npm`, `unzip`
- **JDK 21** для Maven (системная Java 25 несовместима с Kotlin в jicofo)
- На целевом сервере: `java-21-openjdk-headless`, `prosody`, `nginx` или `httpd`

## Структура репозитория

```
├── rpms/SPECS/           # RPM spec-файлы
├── rpms/systemd/         # systemd units
├── rpms/config/          # примеры конфигурации
├── scripts/              # clone-sources.sh
├── tools/bootstrap.sh    # скачивание JDK 21 + Maven
└── build-rpms.sh
```

Исходники upstream, JDK/Maven и готовые RPM **не** хранятся в git — создаются локально при сборке.

## Установка на RHEL 9

```bash
sudo dnf install java-21-openjdk-headless prosody nginx
sudo dnf install ./build/rpms/noarch/jicofo-*.rpm \
                 ./build/rpms/noarch/jitsi-videobridge-*.rpm \
                 ./build/rpms/noarch/jitsi-meet-web-*.rpm
```

После установки настройте Prosody, `jicofo.conf`, `jvb.conf`, `config.js` и nginx с TLS.  
Подробнее: [Jitsi handbook](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-quickstart).

## Upstream

- [jitsi/jitsi-meet](https://github.com/jitsi/jitsi-meet)
- [jitsi/jitsi-videobridge](https://github.com/jitsi/jitsi-videobridge)
- [jitsi/jicofo](https://github.com/jitsi/jicofo)

## Лицензия

RPM-обёртка и скрипты — Apache 2.0 (см. [LICENSE](LICENSE)).  
Jitsi upstream — Apache 2.0 (см. [NOTICE](NOTICE)).
