Name:           jitsi-reservation-api
Version:        1.0
Release:        1%{?dist}
Summary:        REST reservation backend for Jitsi Meet mod_reservations
License:        GPL-3.0-or-later
URL:            https://github.com/grommunio/jitsi-reservation-api
Source0:        jitsi-reservation-api-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3-pip
Requires:       python3
Requires:       python3-flask
Requires:       python3-sqlalchemy

%description
Flask API implementing Jitsi Prosody mod_reservations contract:
POST/GET/DELETE /conference plus CRUD /reservation for advance booking.

%prep
%autosetup -n jitsi-reservation-api-%{version}

%build
# vendored deps optional; prefer distro python3-flask on EL9/Fedora

%install
install -d %{buildroot}%{_libexecdir}/jitsi-reservation-api
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_sysconfdir}/jitsi-reservation-api
install -d %{buildroot}%{_localstatedir}/lib/jitsi-reservation-api

cp -a *.py templates static 2>/dev/null %{buildroot}%{_libexecdir}/jitsi-reservation-api/ || cp -a . %{buildroot}%{_libexecdir}/jitsi-reservation-api/
install -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/jitsi-reservation-api.service
install -m 0644 rpms/config/jitsi-reservation-api.conf %{buildroot}%{_sysconfdir}/jitsi-reservation-api/config.py

%pre
getent group jitsi >/dev/null || groupadd -r jitsi
getent passwd jitsi >/dev/null || \
  useradd -r -g jitsi -d %{_localstatedir}/lib/jitsi -s /sbin/nologin jitsi

%post
%systemd_post jitsi-reservation-api.service

%preun
%systemd_preun jitsi-reservation-api.service

%postun
%systemd_postun_with_restart jitsi-reservation-api.service

%files
%dir %attr(0750,jitsi,jitsi) %{_localstatedir}/lib/jitsi-reservation-api
%dir %attr(0755,root,root) %{_sysconfdir}/jitsi-reservation-api
%config(noreplace) %{_sysconfdir}/jitsi-reservation-api/config.py
%{_libexecdir}/jitsi-reservation-api/
%{_unitdir}/jitsi-reservation-api.service

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 1.0-1
- grommunio jitsi-reservation-api wrapper for native deployment
