License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires: systemd, nginx
Summary: rpm


%description
Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc
%define __logdir    /var/log/otus
%define __bindir    /usr/local/ip2w/
%define __systemddir    /etc/systemd/system/
%define __nginxconf /etc/nginx/default.d

%prep

%setup -q -n otus-%{current_datetime}
%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}

%{__mkdir} -p %{buildroot}/%{__etcdir}
%{__mkdir} -p %{buildroot}/%{__logdir}
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__install} -pD -m 644  %{name}.service %{buildroot}/%{__systemddir}/%{name}.service
%{__install} -pD -m 644  %{name}/%{name}.py %{__bindir}/%{name}.py
%{__install} -pD -m 644  %{name}_proxy.conf %{__nginxconf}/%{name}_proxy.conf
%{__install} -pD -m 644  %{name}.conf %{__etcdir}/%{name}.conf
%{__install} -pD -m 644  %{name}.ini %{__etcdir}/%{name}.ini

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__logdir}
%{__bindir}
%{__systemddir}
