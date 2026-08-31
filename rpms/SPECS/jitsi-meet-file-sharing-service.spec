Name:           jitsi-meet-file-sharing-service
Version:        1.0
Release:        1%{?dist}
Summary:        Jitsi Meet file upload REST service
License:        ASL 2.0
URL:            https://github.com/jitsi/jitsi-meet-file-sharing-service
Source0:        jitsi-meet-file-sharing-service-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  nodejs >= 22
BuildRequires:  npm >= 10
Requires:       nodejs >= 22
Requires:       prosody
Requires(pre):  shadow-utils

%description
TypeScript REST service for sharing files inside Jitsi Meet conferences.
Uses Prosody short_lived_token JWT; proxied via nginx at /file-service/.

%prep
%autosetup -n jitsi-meet-file-sharing-service-%{version}

%build
export NODE_ENV=production
npm ci
npm run build

%install
install -d %{buildroot}%{_libexecdir}/jitsi-meet-file-sharing-service
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_sysconfdir}/jitsi/file-sharing-service
install -d %{buildroot}%{_localstatedir}/lib/jitsi/file-sharing/uploads

cp -a dist package.json node_modules %{buildroot}%{_libexecdir}/jitsi-meet-file-sharing-service/
install -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/jitsi-meet-file-sharing-service.service
install -m 0640 rpms/config/file-sharing-service.env %{buildroot}%{_sysconfdir}/jitsi/file-sharing-service/env

%pre
getent group prosody >/dev/null || groupadd -r prosody
getent group jitsi >/dev/null || groupadd -r jitsi
getent passwd jitsi >/dev/null || \
  useradd -r -g jitsi -d %{_localstatedir}/lib/jitsi -s /sbin/nologin jitsi

%post
%systemd_post jitsi-meet-file-sharing-service.service

%preun
%systemd_preun jitsi-meet-file-sharing-service.service

%postun
%systemd_postun_with_restart jitsi-meet-file-sharing-service.service

%files
%dir %attr(0750,jitsi,jitsi) %{_localstatedir}/lib/jitsi/file-sharing
%dir %attr(0750,jitsi,jitsi) %{_localstatedir}/lib/jitsi/file-sharing/uploads
%dir %attr(0750,root,jitsi) %{_sysconfdir}/jitsi/file-sharing-service
%config(noreplace) %attr(0640,root,jitsi) %{_sysconfdir}/jitsi/file-sharing-service/env
%{_libexecdir}/jitsi-meet-file-sharing-service/
%{_unitdir}/jitsi-meet-file-sharing-service.service

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 1.0-1
- Initial file sharing service package (native systemd, no pm2)
