# Установка Jitsi Meet на RHEL 9 / Rocky Linux 9 / AlmaLinux 9

Неофициальная сборка RPM из [Jitsi-Meet-RHEL-RPMs](https://github.com/Glistand/Jitsi-Meet-RHEL-RPMs).  
Без Docker — только systemd-сервисы.

## Содержимое архива

```
jitsi-meet-rhel-<версия>/
├── INSTALL-RHEL.md          # этот файл
├── install-offline.sh       # быстрая офлайн-установка пакетов
├── CHECKSUMS.sha256         # контрольные суммы RPM
├── repo/el9/                # локальный DNF-репозиторий (Jitsi + зависимости, repodata/)
├── rpms/el9/                # только пакеты Jitsi (для обновления)
│   ├── jicofo-*.rpm
│   ├── jitsi-videobridge-*.rpm
│   ├── jitsi-meet-web-*.rpm
│   └── jitsi-*.rpm          # метапакет (опционально)
├── rpms/fc44/               # Fedora 44 (если есть в релизе)
├── prosody-plugins/         # Lua-модули Prosody из jitsi-meet
└── config-examples/         # примеры конфигурации (замените meet.example.com)
    ├── prosody/
    ├── nginx/
    ├── jitsi-meet/
    ├── jicofo/
    ├── jvb/
    ├── keycloak/
    ├── file-sharing/
    └── reservation/
```

## Офлайн-установка (без интернета)

Архив содержит **все RPM для базового стека** на RHEL 9: Java 21, Prosody, nginx, Lua-модули и пакеты Jitsi. Интернет на целевой ВМ не нужен.

```bash
tar xzf jitsi-meet-rhel-*.tar.gz
cd jitsi-meet-rhel-*

# Проверка (опционально)
sha256sum -c CHECKSUMS.sha256

# Установка пакетов из локального репозитория
sudo ./install-offline.sh meet.example.com   # подставьте свой домен
```

Скрипт `install-offline.sh`:

1. Подключает `file://.../repo/el9` как локальный DNF-репозиторий
2. Ставит Java, Prosody, nginx, jicofo, jitsi-videobridge, jitsi-meet-web
3. Копирует Prosody-плагины в `/usr/share/jitsi-meet/prosody-plugins/`
4. Открывает порты в firewalld

**После установки пакетов** вручную настройте конфиги из `config-examples/` (см. разделы 3–5 ниже).

> **TLS:** `certbot` для Let's Encrypt требует интернет. На изолированной ВМ используйте самоподписанный сертификат или внутренний CA:
>
> ```bash
> sudo mkdir -p /etc/nginx/ssl
> sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
>   -keyout /etc/nginx/ssl/meet.key -out /etc/nginx/ssl/meet.crt \
>   -subj "/CN=meet.example.com"
> ```
>
> Укажите пути к сертификату в `config-examples/nginx/meet.example.com.conf`.

---

## Требования

| Компонент | Пакет dnf | Назначение |
|-----------|-----------|------------|
| Java 21 | `java-21-openjdk-headless` | jicofo, jitsi-videobridge |
| XMPP | `prosody` (≥ 0.12, EPEL) | сигнализация |
| Web | `nginx` | HTTPS + статика Meet |
| TLS | `certbot` + `python3-certbot-nginx` | Let's Encrypt (рекомендуется) |
| Firewall | `firewalld` | порты 80, 443, 10000/udp |

DNS: A-запись `meet.example.com` → публичный IP сервера.

Открытые порты:

- `80/tcp`, `443/tcp` — HTTP/HTTPS
- `10000/udp` — медиа (Jitsi Videobridge)
- `3478/udp`, `5349/tcp` — coturn (опционально, NAT)

## 1. Подготовка системы

**Если есть интернет** — установите зависимости из репозиториев:

```bash
sudo dnf install -y epel-release
sudo /usr/bin/crb enable    # CodeReady Builder — нужен для части зависимостей EPEL
sudo dnf install -y java-21-openjdk-headless prosody nginx firewalld certbot python3-certbot-nginx

sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-port=10000/udp
sudo firewall-cmd --reload
```

**Если интернета нет** — используйте `./install-offline.sh` (см. раздел «Офлайн-установка» выше), затем переходите к разделу 3.

## 2. Установка RPM

**С интернетом** (только пакеты Jitsi из архива):

```bash
tar xzf jitsi-meet-rhel-*.tar.gz
cd jitsi-meet-rhel-*

sha256sum -c CHECKSUMS.sha256

cd rpms/el9
sudo dnf install -y ./*.rpm
```

**Без интернета** — пакеты уже установлены через `install-offline.sh`; этот шаг можно пропустить.

Или по отдельности (при наличии сети и уже установленных зависимостях):

```bash
sudo dnf install -y jicofo-*.rpm jitsi-videobridge-*.rpm jitsi-meet-web-*.rpm
```

## 3. Prosody

```bash
sudo cp config-examples/prosody/meet.example.com.cfg.lua \
        /etc/prosody/conf.avail/meet.example.com.cfg.lua
sudo sed -i 's/meet.example.com/ВАШ_ДОМЕН/g' /etc/prosody/conf.avail/meet.example.com.cfg.lua

sudo ln -sf /etc/prosody/conf.avail/meet.example.com.cfg.lua \
            /etc/prosody/conf.d/meet.example.com.cfg.lua

# Секреты и пользователи (замените пароли)
sudo prosodyctl register focus auth.ВАШ_ДОМЕН focuspassword
sudo prosodyctl register jvb auth.ВАШ_ДОМЕН jvbpassword

sudo systemctl enable --now prosody
```

## 4. Jicofo и Videobridge

```bash
sudo cp config-examples/jicofo/jicofo.conf.example /etc/jitsi/jicofo/jicofo.conf
sudo cp config-examples/jvb/jvb.conf.example /etc/jitsi/videobridge/jvb.conf
sudo sed -i 's/meet.example.com/ВАШ_ДОМЕН/g' /etc/jitsi/jicofo/jicofo.conf /etc/jitsi/videobridge/jvb.conf
# Подставьте пароли focus/jvb из шага Prosody

sudo systemctl enable --now jicofo jitsi-videobridge
```

## 5. Jitsi Meet (web + nginx)

```bash
sudo cp config-examples/jitsi-meet/config.js.example \
        /etc/jitsi/meet/ВАШ_ДОМЕН-config.js

sudo cp config-examples/nginx/meet.example.com.conf \
        /etc/nginx/conf.d/meet.example.com.conf
sudo sed -i 's/meet.example.com/ВАШ_ДОМЕН/g' \
        /etc/jitsi/meet/ВАШ_ДОМЕН-config.js \
        /etc/nginx/conf.d/meet.example.com.conf

sudo certbot --nginx -d ВАШ_ДОМЕН
sudo nginx -t && sudo systemctl reload nginx
```

## 6. Проверка

```bash
sudo systemctl status prosody jicofo jitsi-videobridge nginx
curl -I https://ВАШ_ДОМЕН
```

Откройте `https://ВАШ_ДОМЕН` в браузере и создайте тестовую комнату.

Логи:

```bash
sudo tail -f /var/log/jitsi/jicofo.log
sudo tail -f /var/log/jitsi/jvb.log
sudo tail -f /var/log/prosody/prosody.log
```

## 7. Опционально: Keycloak (SSO)

Примеры фрагментов — в `config-examples/keycloak/` и `config-examples/prosody/token-auth.snippet`.

1. Установите Keycloak нативно (tarball + PostgreSQL) или из будущего RPM этого репозитория.
2. Создайте realm `jitsi-realm`, client `jitsi`.
3. В Prosody включите `authentication = "token"` и `cache_keys_url` на JWKS Keycloak.
4. В `config.js` добавьте `tokenAuthUrl`, `anonymousdomain` для гостей.
5. В nginx проксируйте `/realms/` на Keycloak (см. `nginx-realms.snippet`).

Документация: https://jitsi.github.io/handbook/docs/devops-guide/authentication/

## 8. Опционально: отправка файлов

После установки `jitsi-meet-file-sharing-service` (когда RPM будет в составе релиза):

1. Настройте Prosody `short_lived_token` — см. `config-examples/file-sharing/prosody.snippet`
2. Добавьте в nginx `location /file-service/` — `config-examples/file-sharing/nginx.snippet`
3. В `config.js`: `config.fileSharing = { enabled: true, apiUrl: '...' }`

Документация: https://jitsi.github.io/handbook/docs/devops-guide/file-sharing/

## 9. Опционально: reservation system

1. Запустите REST API бронирования (`jitsi-reservation-api`).
2. В Prosody включите модуль `reservations` — `config-examples/reservation/prosody.snippet`
3. Укажите `reservations_api_prefix = "http://127.0.0.1:8088"`

Документация: https://jitsi.github.io/handbook/docs/devops-guide/reservation/

## NAT / за NAT

Если сервер за NAT, в `/etc/jitsi/videobridge/jvb.conf` укажите public/private IP (см. комментарии в example).

## Обновление

```bash
sudo systemctl stop jicofo jitsi-videobridge
sudo dnf install ./rpms/el9/*.rpm
sudo systemctl start prosody jicofo jitsi-videobridge nginx
```

## Удаление

```bash
sudo systemctl disable --now jicofo jitsi-videobridge
sudo dnf remove jitsi jitsi-meet-web jitsi-videobridge jicofo
```

## Ссылки

- [Jitsi handbook — quickstart](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-quickstart/)
- [Исходники packaging](https://github.com/Glistand/Jitsi-Meet-RHEL-RPMs)
