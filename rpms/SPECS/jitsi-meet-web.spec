%global jitsi_root %{?_jitsi_root}%{!?_jitsi_root:%(echo $HOME)/Work/Jitsi}
%global prebuilt %{?_prebuilt:1}%{!?_prebuilt:0}

Name:           jitsi-meet-web
Version:        2.0
Release:        1%{?dist}
Summary:        Jitsi Meet web client (static files)
License:        ASL 2.0
URL:            https://github.com/jitsi/jitsi-meet
BuildArch:      noarch

%if %{prebuilt} == 0
BuildRequires:  nodejs
BuildRequires:  npm
BuildRequires:  make
%endif

Requires:       nginx or httpd

%description
Веб-интерфейс Jitsi Meet — статические файлы для nginx/httpd.
Требует отдельной настройки Prosody, jicofo и jitsi-videobridge.

%prep
# Сборка из %{jitsi_root}/src/jitsi-meet

%build
%if %{prebuilt} == 0
cd "%{jitsi_root}/src/jitsi-meet"
npm ci
NODE_OPTIONS=--max-old-space-size=8192 make
%endif

%install
rm -rf %{buildroot}
MEET="%{jitsi_root}/src/jitsi-meet"

install -d %{buildroot}/usr/share/jitsi-meet
install -m 644 $MEET/*.html %{buildroot}/usr/share/jitsi-meet/ 2>/dev/null || true
install -m 644 $MEET/interface_config.js $MEET/manifest.json $MEET/pwa-worker.js %{buildroot}/usr/share/jitsi-meet/ 2>/dev/null || true

for dir in libs static css sounds fonts images lang; do
    if [ -d "$MEET/$dir" ]; then
        cp -a "$MEET/$dir" %{buildroot}/usr/share/jitsi-meet/
    fi
done

install -d %{buildroot}/usr/share/jitsi-meet/scripts
install -m 755 $MEET/resources/*.sh %{buildroot}/usr/share/jitsi-meet/scripts/ 2>/dev/null || true
install -m 644 $MEET/resources/robots.txt %{buildroot}/usr/share/jitsi-meet/ 2>/dev/null || true

install -d %{buildroot}/etc/jitsi/meet
install -m 644 $MEET/config.js %{buildroot}/etc/jitsi/meet/config.js.example 2>/dev/null || true

%files
%defattr(-,root,root,-)
/usr/share/jitsi-meet/
%config(noreplace) /etc/jitsi/meet/config.js.example

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 2.0-1
- Initial RHEL/Fedora RPM from upstream source
