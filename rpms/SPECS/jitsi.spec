Name:           jitsi
Version:        2.0
Release:        1%{?dist}
Summary:        Jitsi Meet stack (meta package)
License:        ASL 2.0
URL:            https://jitsi.org/meet
BuildArch:      noarch

Requires:       jicofo >= 1.1
Requires:       jitsi-videobridge >= 2.3
Requires:       jitsi-meet-web >= 2.0
Requires:       prosody
Recommends:     nginx
Recommends:     java-21-openjdk-headless

%description
Метапакет: основные компоненты Jitsi Meet для RHEL/Fedora.
После установки настройте Prosody, config.js и сертификаты TLS.

%files

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 2.0-1
- Meta package for single-server deployment
