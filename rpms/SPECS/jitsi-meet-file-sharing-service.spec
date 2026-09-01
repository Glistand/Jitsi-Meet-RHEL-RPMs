%global jitsi_root %{?_jitsi_root}%{!?_jitsi_root:%(echo $HOME)/Work/Jitsi}
%global prebuilt %{?_prebuilt:1}%{!?_prebuilt:0}

Name:           jitsi-meet-file-sharing-service
Version:        1.0
Release:        2%{?dist}
Summary:        Jitsi Meet file upload REST service
License:        ASL 2.0
URL:            https://github.com/jitsi/jitsi-meet-file-sharing-service
BuildArch:      noarch

%if %{prebuilt} == 0
BuildRequires:  nodejs >= 22
BuildRequires:  npm >= 10
%endif
Requires:       nodejs >= 22
Requires:       openssl
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
TypeScript REST service for sharing files inside Jitsi Meet conferences.
Uses Prosody short_lived_token JWT; proxied via nginx at /file-service/.

%prep
# Сборка из %{jitsi_root}/src/jitsi-meet-file-sharing-service

%build
%if %{prebuilt} == 0
cd "%{jitsi_root}/src/jitsi-meet-file-sharing-service"
npm ci
npm run build
npm prune --omit=dev
%endif

%install
FS="%{jitsi_root}/src/jitsi-meet-file-sharing-service"

install -d %{buildroot}/usr/libexec/jitsi-meet-file-sharing-service
install -d %{buildroot}/usr/lib/systemd/system
install -d %{buildroot}/etc/jitsi/file-sharing-service
install -d %{buildroot}/var/lib/jitsi/file-sharing/uploads

cp -a "$FS/dist" "$FS/package.json" "$FS/node_modules" \
  %{buildroot}/usr/libexec/jitsi-meet-file-sharing-service/

install -m 0644 "%{jitsi_root}/rpms/systemd/jitsi-meet-file-sharing-service.service" \
  %{buildroot}/usr/lib/systemd/system/
install -m 0640 "%{jitsi_root}/rpms/config/file-sharing-service.env" \
  %{buildroot}/etc/jitsi/file-sharing-service/env

%pre
getent group jitsi >/dev/null || groupadd -r jitsi
getent passwd jitsi >/dev/null || \
  useradd -r -g jitsi -d /var/lib/jitsi -s /sbin/nologin jitsi

%post
%systemd_post jitsi-meet-file-sharing-service.service
KEYDIR="/etc/jitsi/file-sharing-service"
if [ ! -f "$KEYDIR/short_lived_token.key" ]; then
  openssl genrsa -out "$KEYDIR/short_lived_token.key" 2048
  chmod 0640 "$KEYDIR/short_lived_token.key"
  chown root:jitsi "$KEYDIR/short_lived_token.key"
  openssl rsa -in "$KEYDIR/short_lived_token.key" -pubout -out "$KEYDIR/short_lived_token.pub"
  chmod 0644 "$KEYDIR/short_lived_token.pub"
fi

%preun
%systemd_preun jitsi-meet-file-sharing-service.service

%postun
%systemd_postun_with_restart jitsi-meet-file-sharing-service.service

%files
%dir %attr(0750,jitsi,jitsi) /var/lib/jitsi/file-sharing
%dir %attr(0750,jitsi,jitsi) /var/lib/jitsi/file-sharing/uploads
%dir %attr(0750,root,jitsi) /etc/jitsi/file-sharing-service
%config(noreplace) %attr(0640,root,jitsi) /etc/jitsi/file-sharing-service/env
%ghost %attr(0640,root,jitsi) /etc/jitsi/file-sharing-service/short_lived_token.key
%ghost %attr(0644,root,jitsi) /etc/jitsi/file-sharing-service/short_lived_token.pub
/usr/libexec/jitsi-meet-file-sharing-service/
/usr/lib/systemd/system/jitsi-meet-file-sharing-service.service

%changelog
* Tue Sep 01 2026 glstnd <build@local> - 1.0-2
- Fix systemd unit path for rpmbuild (%{_unitdir} not expanded in CI)

* Tue Sep 01 2026 glstnd <build@local> - 1.0-1
- Build from upstream git; systemd + short_lived_token key generation
