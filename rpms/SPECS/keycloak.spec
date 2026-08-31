Name:           keycloak
Version:        26.3.2
Release:        1%{?dist}
Summary:        Keycloak IAM (native Quarkus distribution, no Docker)
License:        ASL 2.0
URL:            https://www.keycloak.org/
Source0:        https://github.com/keycloak/keycloak/releases/download/%{version}/keycloak-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  java-21-openjdk-devel
Requires:       java-21-openjdk-headless
Requires:       postgresql
Requires(pre):  shadow-utils

%global kchome /opt/keycloak

%description
Keycloak identity provider for Jitsi Meet OIDC/token authentication.
Installed from upstream tarball with kc.sh build; runs under systemd.

%prep
%autosetup -n keycloak-%{version}

%build
export KC_DB=postgres
./bin/kc.sh build

%install
install -d %{buildroot}%{kchome}
install -d %{buildroot}%{_sysconfdir}/keycloak
install -d %{buildroot}%{_unitdir}

cp -a bin conf lib providers quarkus %{buildroot}%{kchome}/
install -m 0644 rpms/config/keycloak.conf %{buildroot}%{_sysconfdir}/keycloak/keycloak.conf
install -m 0644 rpms/systemd/keycloak.service %{buildroot}%{_unitdir}/keycloak.service

%pre
getent group keycloak >/dev/null || groupadd -r keycloak
getent passwd keycloak >/dev/null || \
  useradd -r -g keycloak -d %{kchome} -s /sbin/nologin keycloak

%post
%systemd_post keycloak.service

%preun
%systemd_preun keycloak.service

%postun
%systemd_postun_with_restart keycloak.service

%files
%dir %attr(0755,keycloak,keycloak) %{kchome}
%dir %attr(0755,root,root) %{_sysconfdir}/keycloak
%config(noreplace) %{_sysconfdir}/keycloak/keycloak.conf
%{kchome}/bin/
%{kchome}/conf/
%{kchome}/lib/
%{kchome}/providers/
%{kchome}/quarkus/
%{_unitdir}/keycloak.service

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 26.3.2-1
- Native Keycloak tarball + systemd (Jitsi OIDC integration)
