%global jitsi_root %{?_jitsi_root}%{!?_jitsi_root:%(echo $HOME)/Work/Jitsi}
%global java_home %{?_java_home}%{!?_java_home:%{jitsi_root}/tools/jdk-21.0.12.1+1}

Name:           keycloak
Version:        26.3.2
Release:        1%{?dist}
Summary:        Keycloak IAM (native Quarkus distribution, no Docker)
License:        ASL 2.0
URL:            https://www.keycloak.org/
Source0:        keycloak-%{version}.tar.gz
BuildArch:      noarch

# JDK 21 из tools/bootstrap.sh (_java_home), без системного java-21-openjdk-devel
Requires:       java-21-openjdk-headless
Requires:       postgresql
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%global kchome /opt/keycloak

%description
Keycloak identity provider for Jitsi Meet OIDC/token authentication.
Installed from upstream tarball with kc.sh build; runs under systemd.

%prep
%setup -q -n keycloak-%{version}

%build
export JAVA_HOME="%{java_home}"
export PATH="%{java_home}/bin:$PATH"
export KC_DB=postgres
./bin/kc.sh build

%install
install -d %{buildroot}%{kchome}
install -d %{buildroot}%{_sysconfdir}/keycloak
install -d %{buildroot}%{_unitdir}

cp -a bin conf lib providers themes %{buildroot}%{kchome}/
install -m 0644 "%{jitsi_root}/rpms/config/keycloak.conf" \
  %{buildroot}%{_sysconfdir}/keycloak/keycloak.conf
install -m 0644 "%{jitsi_root}/rpms/systemd/keycloak.service" \
  %{buildroot}%{_unitdir}/keycloak.service

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
%{kchome}/themes/
%{_unitdir}/keycloak.service

%changelog
* Tue Sep 01 2026 glstnd <build@local> - 26.3.2-1
- Native Keycloak tarball + kc.sh build + systemd
