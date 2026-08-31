%global jitsi_root %{?_jitsi_root}%{!?_jitsi_root:%(echo $HOME)/Work/Jitsi}
%global maven_home %{?_maven_home}%{!?_maven_home:%{jitsi_root}/tools/apache-maven-3.9.9}
%global java_home %{?_java_home}%{!?_java_home:%{jitsi_root}/tools/jdk-21.0.12.1+1}
%global prebuilt %{?_prebuilt:1}%{!?_prebuilt:0}

Name:           jicofo
Version:        1.1
Release:        1%{?dist}
Summary:        Jitsi Meet conference focus (signaling)
License:        ASL 2.0
URL:            https://github.com/jitsi/jicofo
BuildArch:      noarch

BuildRequires:  unzip
%if %{prebuilt} == 0
BuildRequires:  java-21-openjdk-devel
BuildRequires:  maven
%endif

Requires:       java-21-openjdk-headless
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
JItsi COnference FOcus — серверный компонент сигнализации для Jitsi Meet.
Управляет Jingle-сессиями и выбором Jitsi Videobridge для участников.

%prep
# Сборка из локального git-клона (%{jitsi_root}/src/jicofo)

%build
%if %{prebuilt} == 0
export JAVA_HOME="%{java_home}"
export PATH="%{maven_home}/bin:$PATH"
cd "%{jitsi_root}/src/jicofo"
mvn -q -DskipTests package
%endif

%install
rm -rf %{buildroot}
cd "%{jitsi_root}/src/jicofo/jicofo/target"
unzip -o -q jicofo-1.1-SNAPSHOT-archive.zip

install -d %{buildroot}/usr/share/jicofo/lib
install -m 644 jicofo-1.1-SNAPSHOT/jicofo.jar %{buildroot}/usr/share/jicofo/
install -m 755 jicofo-1.1-SNAPSHOT/jicofo.sh %{buildroot}/usr/share/jicofo/
install -m 644 jicofo-1.1-SNAPSHOT/lib/*.jar %{buildroot}/usr/share/jicofo/lib/

install -d %{buildroot}/etc/jitsi/jicofo
install -m 644 "%{jitsi_root}/src/jicofo/lib/logging.properties" %{buildroot}/etc/jitsi/jicofo/
install -m 644 "%{jitsi_root}/rpms/config/jicofo-config" %{buildroot}/etc/jitsi/jicofo/config

install -d %{buildroot}/usr/lib/systemd/system
install -m 644 "%{jitsi_root}/rpms/systemd/jicofo.service" %{buildroot}/usr/lib/systemd/system/

install -d %{buildroot}/var/log/jitsi

%pre
getent group jicofo >/dev/null || groupadd -r jicofo
getent passwd jicofo >/dev/null || useradd -r -g jicofo -d /usr/share/jicofo -s /sbin/nologin jicofo

%post
%systemd_post jicofo.service

%preun
%systemd_preun jicofo.service

%postun
%systemd_postun_with_restart jicofo.service

%files
%defattr(-,root,root,-)
/usr/share/jicofo/jicofo.jar
/usr/share/jicofo/jicofo.sh
/usr/share/jicofo/lib/*.jar
/etc/jitsi/jicofo/logging.properties
%config(noreplace) /etc/jitsi/jicofo/config
/usr/lib/systemd/system/jicofo.service
%dir /var/log/jitsi

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 1.1-1
- Initial RHEL/Fedora RPM from upstream source
