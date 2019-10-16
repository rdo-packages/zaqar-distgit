# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%global service zaqar
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global common_desc \
Zaqar is a new OpenStack project to create a multi-tenant cloud queuing \
service.The project will define a clean, RESTful API, use a modular \
architecture, and will support both eventing and job-queuing semantics. \
Users will be able to customize Zaqar to achieve a wide range of performance, \
durability, availability,and efficiency goals

Name:           openstack-%{service}
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:          1
Version:        9.0.0
Release:        1%{?dist}
Summary:        Message queuing service for OpenStack

License:        ASL 2.0
URL:            https://wiki.openstack.org/wiki/Zaqar
Source0:        https://tarballs.openstack.org/zaqar/%{service}-%{upstream_version}.tar.gz
#

Source1:        %{service}-dist.conf

Source10:       %{name}.service
Source11:       %{name}.logrotate
Source12:       %{name}@.service

BuildArch:      noarch
BuildRequires:  openstack-macros
BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-pbr >= 1.6
BuildRequires:  systemd
BuildRequires:  git
# Required for config file generation
BuildRequires:  python%{pyver}-oslo-cache >= 1.26.0
BuildRequires:  python%{pyver}-oslo-config >= 2:5.2.0
BuildRequires:  python%{pyver}-oslo-db >= 4.27.0
BuildRequires:  python%{pyver}-oslo-log >= 3.36.0
BuildRequires:  python%{pyver}-oslo-policy >= 1.30.0
BuildRequires:  python%{pyver}-oslo-upgradecheck >= 0.1.0
BuildRequires:  python%{pyver}-keystonemiddleware >= 4.17.0
BuildRequires:  python%{pyver}-falcon
BuildRequires:  python%{pyver}-jsonschema
BuildRequires:  python%{pyver}-sqlalchemy >= 1.0.10
BuildRequires:  python%{pyver}-osprofiler
BuildRequires:  python%{pyver}-oslo-messaging
BuildRequires:  python%{pyver}-autobahn
# Required to compile translation files
BuildRequires:  python%{pyver}-babel
BuildRequires:  openstack-macros

# Handle python2 exception
%if %{pyver} == 2
BuildRequires:  python-enum34
BuildRequires:  python-pymongo
BuildRequires:  python-trollius
BuildRequires:  python-redis
%else
BuildRequires:  python%{pyver}-pymongo
BuildRequires:  python%{pyver}-trollius
BuildRequires:  python%{pyver}-redis
%endif

Obsoletes:      openstack-marconi < 2014.1-2.2

Requires(pre):  shadow-utils
%{?systemd_requires}

Requires:         python%{pyver}-six
Requires:         python%{pyver}-stevedore
Requires:         python%{pyver}-jsonschema
Requires:         python%{pyver}-oslo-cache >= 1.26.0
Requires:         python%{pyver}-oslo-config >= 2:5.2.0
Requires:         python%{pyver}-oslo-context >= 2.19.2
Requires:         python%{pyver}-oslo-db >= 4.27.0
Requires:         python%{pyver}-oslo-log >= 3.36.0
Requires:         python%{pyver}-oslo-messaging >= 5.29.0
Requires:         python%{pyver}-oslo-policy >= 1.30.0
Requires:         python%{pyver}-oslo-serialization >= 2.18.0
Requires:         python%{pyver}-oslo-utils >= 3.33.0
Requires:         python%{pyver}-oslo-i18n >= 3.15.3
Requires:         python%{pyver}-oslo-reports >= 1.18.0
Requires:         python%{pyver}-oslo-upgradecheck >= 0.1.0
Requires:         python%{pyver}-keystonemiddleware >= 4.17.0
Requires:         python%{pyver}-falcon
Requires:         python%{pyver}-futurist
Requires:         python%{pyver}-babel
Requires:         python%{pyver}-sqlalchemy >= 1.0.10
Requires:         python%{pyver}-keystoneclient
Requires:         python%{pyver}-requests
Requires:         python%{pyver}-iso8601
Requires:         python%{pyver}-webob >= 1.7.1
Requires:         python%{pyver}-pbr >= 2.0.0
Requires:         python%{pyver}-autobahn
Requires:         python%{pyver}-osprofiler >= 1.4.0
Requires:         python%{pyver}-alembic

# Handle python2 exception
%if %{pyver} == 2
Requires:         python-enum34
Requires:         python-pymongo
Requires:         python-memcached
Requires:         python-bson
Requires:         python-trollius
Requires:         python-msgpack >= 0.5.1
Requires:         python-redis
%else
Requires:         python%{pyver}-pymongo
Requires:         python%{pyver}-memcached
Requires:         python%{pyver}-bson
Requires:         python%{pyver}-trollius
Requires:         python%{pyver}-msgpack >= 0.5.1
Requires:         python%{pyver}-redis
%endif

%description
%{common_desc}

%package -n python%{pyver}-%{service}-tests
Summary:        Zaqar tests
%{?python_provide:%python_provide python%{pyver}-%{service}-tests}
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description -n python%{pyver}-%{service}-tests
%{common_desc}

This package contains the Zaqar test files.

%prep
%autosetup -n %{service}-%{upstream_version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
# Generate config file
PYTHONPATH=. oslo-config-generator-%{pyver} --config-file=etc/oslo-config-generator/zaqar.conf

%{pyver_build}
# Generate i18n files
%{pyver_bin} setup.py compile_catalog -d build/lib/%{service}/locale

# Programmatically update defaults in sample configs

#  First we ensure all values are commented in appropriate format.
#  Since icehouse, there was an uncommented keystone_authtoken section
#  at the end of the file which mimics but also conflicted with our
#  distro editing that had been done for many releases.
sed -i '/^[^#[]/{s/^/#/; s/ //g}; /^#[^ ]/s/ = /=/' etc/%{service}.conf.sample etc/logging.conf.sample

#  TODO: Make this more robust
#  Note it only edits the first occurrence, so assumes a section ordering in sample
#  and also doesn't support multi-valued variables like dhcpbridge_flagfile.
while read name eq value; do
  test "$name" && test "$value" || continue
  sed -i "0,/^# *$name=/{s!^# *$name=.*!#$name=$value!}" etc/%{service}.conf.sample
done < %{SOURCE1}

%install
%{pyver_install}

# Setup directories
install -d -m 755 %{buildroot}%{_unitdir}
install -d -m 755 %{buildroot}%{_datadir}/%{service}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{service}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{service}

# Install config files
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_datadir}/%{service}/%{service}-dist.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/%{service}

install -p -D -m 640 etc/%{service}.conf.sample %{buildroot}%{_sysconfdir}/%{service}/%{service}.conf
install -p -D -m 640 etc/logging.conf.sample    %{buildroot}%{_sysconfdir}/%{service}/logging.conf

# Install logrotate
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Install initscripts
install -p -m 644 %{SOURCE10} %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE12} %{buildroot}%{_unitdir}

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{pyver_sitelib}/%{service}/locale/*/LC_*/%{service}*po
rm -f %{buildroot}%{pyver_sitelib}/%{service}/locale/*pot
mv %{buildroot}%{pyver_sitelib}/%{service}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{service} --all-name

%pre
USERNAME=%{service}
GROUPNAME=$USERNAME
HOMEDIR=%{_sharedstatedir}/$USERNAME
getent group $GROUPNAME >/dev/null || groupadd -r $GROUPNAME
getent passwd $USERNAME >/dev/null || \
  useradd -r -g $GROUPNAME -G $GROUPNAME -d $HOMEDIR -s /sbin/nologin \
    -c "OpenStack Zaqar Daemon" $USERNAME
exit 0

%post
%systemd_post openstack-zaqar.service

%preun
%systemd_preun openstack-zaqar.service

%postun
%systemd_postun_with_restart openstack-zaqar.service

%files -f %{service}.lang
%{!?_licensedir: %global license %%doc}
%license LICENSE
%doc README.rst

%dir %{_sysconfdir}/%{service}
%config(noreplace) %attr(0640, root, %{service}) %{_sysconfdir}/%{service}/%{service}.conf
%config(noreplace) %attr(0640, root, %{service}) %{_sysconfdir}/%{service}/logging.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%dir %attr(0750, %{service}, root) %{_localstatedir}/log/%{service}

#%{_bindir}/marconi-server
%{_bindir}/%{service}-server
%{_bindir}/%{service}-status
%{_bindir}/%{service}-bench
%{_bindir}/%{service}-gc
%{_bindir}/%{service}-sql-db-manage

%{_datarootdir}/%{service}

%defattr(-, %{service}, %{service}, -)
%dir %{_sharedstatedir}/%{service}

%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%{pyver_sitelib}/%{service}
%{pyver_sitelib}/%{service}-%{version}*.egg-info
%exclude %{pyver_sitelib}/%{service}/tests

%files -n python%{pyver}-%{service}-tests
%license LICENSE
%{pyver_sitelib}/%{service}/tests

%changelog
* Wed Oct 16 2019 RDO <dev@lists.rdoproject.org> 1:9.0.0-1
- Update to 9.0.0

* Mon Sep 30 2019 RDO <dev@lists.rdoproject.org> 1:9.0.0-0.1.0rc1
- Update to 9.0.0.0rc1

