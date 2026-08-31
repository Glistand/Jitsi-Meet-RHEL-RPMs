Name:           jitsi-meet-auth-keycloak
Version:        2.0
Release:        1%{?dist}
Summary:        Keycloak OIDC configuration templates for Jitsi Meet
License:        ASL 2.0
URL:            https://jitsi.github.io/handbook/docs/devops-guide/authentication/
BuildArch:      noarch

Requires:       jitsi-meet-prosody
Requires:       jitsi-meet-web-config
Requires:       keycloak
Requires:       prosody
Requires:       nginx

%description
Prosody token-auth snippets, config.js SSO URLs, and nginx /realms/ proxy
for Keycloak integration. Run jitsi-meet-configure after install.

%install
install -d %{buildroot}%{_datadir}/jitsi-meet-auth-keycloak
install -d %{buildroot}%{_libexecdir}/jitsi-meet

install -m 0644 rpms/config/keycloak-prosody.lua.snippet \
  %{buildroot}%{_datadir}/jitsi-meet-auth-keycloak/prosody.lua.snippet
install -m 0644 rpms/config/keycloak-config.js.snippet \
  %{buildroot}%{_datadir}/jitsi-meet-auth-keycloak/config.js.snippet
install -m 0644 rpms/config/keycloak-nginx.conf.snippet \
  %{buildroot}%{_datadir}/jitsi-meet-auth-keycloak/nginx.conf.snippet
install -m 0755 rpms/config/jitsi-meet-configure \
  %{buildroot}%{_libexecdir}/jitsi-meet/configure

%files
%{_datadir}/jitsi-meet-auth-keycloak/
%{_libexecdir}/jitsi-meet/configure

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 2.0-1
- Keycloak auth templates per official Jitsi handbook
