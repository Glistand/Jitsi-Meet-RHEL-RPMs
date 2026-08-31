Name:           jitsi-meet-prosody
Version:        2.0
Release:        1%{?dist}
Summary:        Prosody plugins and config for Jitsi Meet
License:        ASL 2.0
URL:            https://github.com/jitsi/jitsi-meet
BuildArch:      noarch

Requires:       prosody >= 0.12
Requires:       lua-sec
Requires:       lua-cjson

%description
Prosody Lua modules from jitsi-meet: reservations, file sharing,
short_lived_token, muc lobby, token auth hooks.

%install
install -d %{buildroot}%{_datadir}/jitsi-meet/prosody-plugins
install -d %{buildroot}%{_datadir}/jitsi-meet/prosody-templates

# Populated at build time from src/jitsi-meet/resources/prosody-plugins/
install -m 0644 rpms/config/prosody-jitsi-meet.cfg.lua.template \
  %{buildroot}%{_datadir}/jitsi-meet/prosody-templates/jitsi-meet.cfg.lua.template

%files
%{_datadir}/jitsi-meet/prosody-plugins/
%{_datadir}/jitsi-meet/prosody-templates/

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 2.0-1
- Prosody plugins including mod_reservations and file sharing
