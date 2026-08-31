%global jitsi_root %{?_jitsi_root}%{!?_jitsi_root:%(echo $HOME)/Work/Jitsi}
%global maven_home %{?_maven_home}%{!?_maven_home:%{jitsi_root}/tools/apache-maven-3.9.9}
%global java_home %{?_java_home}%{!?_java_home:%{jitsi_root}/tools/jdk-21.0.12.1+1}
%global prebuilt %{?_prebuilt:1}%{!?_prebuilt:0}

Name:           jitsi-videobridge
Version:        2.3
Release:        1%{?dist}
Summary:        Jitsi Videobridge (WebRTC media relay)
License:        ASL 2.0
URL:            https://github.com/jitsi/jitsi-videobridge
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
Jitsi Videobridge — SFU-компонент для маршрутизации аудио/видео в Jitsi Meet.

%prep
# Сборка из локального git-клона (%{jitsi_root}/src/jitsi-videobridge)

%build
%if %{prebuilt} == 0
export JAVA_HOME="%{java_home}"
export PATH="%{maven_home}/bin:$PATH"
cd "%{jitsi_root}/src/jitsi-videobridge"
mvn -q -DskipTests package
%endif

%install
rm -rf %{buildroot}
cd "%{jitsi_root}/src/jitsi-videobridge/jvb/target"
unzip -o -q jitsi-videobridge-2.3-SNAPSHOT-archive.zip

install -d %{buildroot}/usr/share/jitsi-videobridge/lib
install -m 644 jitsi-videobridge-2.3-SNAPSHOT/jitsi-videobridge.jar %{buildroot}/usr/share/jitsi-videobridge/
install -m 755 jitsi-videobridge-2.3-SNAPSHOT/jvb.sh %{buildroot}/usr/share/jitsi-videobridge/
install -m 644 jitsi-videobridge-2.3-SNAPSHOT/lib/*.jar %{buildroot}/usr/share/jitsi-videobridge/lib/
install -m 644 jitsi-videobridge-2.3-SNAPSHOT/lib/logging.properties %{buildroot}/usr/share/jitsi-videobridge/lib/
install -m 644 jitsi-videobridge-2.3-SNAPSHOT/lib/videobridge.rc %{buildroot}/usr/share/jitsi-videobridge/lib/

install -d %{buildroot}/etc/jitsi/videobridge
install -m 644 "%{jitsi_root}/rpms/config/videobridge-config" %{buildroot}/etc/jitsi/videobridge/config

install -d %{buildroot}/usr/lib/systemd/system
install -m 644 "%{jitsi_root}/rpms/systemd/jitsi-videobridge.service" %{buildroot}/usr/lib/systemd/system/

install -d %{buildroot}/var/log/jitsi

%pre
getent group jvb >/dev/null || groupadd -r jvb
getent passwd jvb >/dev/null || useradd -r -g jvb -d /usr/share/jitsi-videobridge -s /sbin/nologin jvb

%post
%systemd_post jitsi-videobridge.service

%preun
%systemd_preun jitsi-videobridge.service

%postun
%systemd_postun_with_restart jitsi-videobridge.service

%files
%defattr(-,root,root,-)
/usr/share/jitsi-videobridge/jitsi-videobridge.jar
/usr/share/jitsi-videobridge/jvb.sh
/usr/share/jitsi-videobridge/lib/*
%config(noreplace) /etc/jitsi/videobridge/config
/usr/lib/systemd/system/jitsi-videobridge.service
%dir /var/log/jitsi

%changelog
* Mon Aug 31 2026 glstnd <build@local> - 2.3-1
- Initial RHEL/Fedora RPM from upstream source
