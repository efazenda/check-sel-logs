# Specfile
Summary:       Check SEL Logs
Name:          check-sel-logs
Version:       14.11.4
Release:       1%{?dist}
License:       GPL
Group:         System Environment/Base
BuildRoot:     %{_tmppath}/%{name}-root
BuildArch:     noarch
Source:        %{name}-%{version}.tar.gz
BuildRequires: python >= 2.6
Requires:      python >= 2.6
Requires:      logrotate

%description
This package contains the python script check_sel_logs.py that check the SEL logs of the BMC and dump the content in the logs when the threshold is raised


%prep
%setup -n %{name}-%{version}


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/bin/
mkdir -p $RPM_BUILD_ROOT/usr/share/doc/check_sel_logs/
mkdir -p $RPM_BUILD_ROOT/etc/logrotate.d/

install -m 644 COPYING $RPM_BUILD_ROOT/usr/share/doc/check_sel_logs/
install -m 644 AUTHORS $RPM_BUILD_ROOT/usr/share/doc/check_sel_logs/
install -m 644 ChangeLog $RPM_BUILD_ROOT/usr/share/doc/check_sel_logs/
install -m 644 checksellogs $RPM_BUILD_ROOT/etc/logrotate.d/checksellogs
install -m 755 check_sel_logs.py $RPM_BUILD_ROOT/usr/bin/check_sel_logs.py

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_DIR/%{name}-%{version}

%post
echo "30 8 * * * /usr/bin/check_sel_logs.py >/dev/null 2> /var/log/check_sel_logs_error.log" > /etc/cron.d/check_sel_logs 
 

%files
%defattr(-,root,root)
/usr/bin/check_sel_logs.py
/etc/logrotate.d/checksellogs
/usr/share/doc/check_sel_logs/COPYING
/usr/share/doc/check_sel_logs/AUTHORS
/usr/share/doc/check_sel_logs/ChangeLog

%changelog
* Mon Nov 26 2014 - Edouard Fazenda <Edouard.Fazenda@gmail.com>
- Initial release
