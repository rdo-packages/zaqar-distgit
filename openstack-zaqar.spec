%{!?sources_gpg: %{!?dlrn:%global sources_gpg 1} }
%global sources_gpg_sign 0x2426b928085a020d8a90d0d879ab7008d0896c8a
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
Version:        XXX
Release:        XXX
Summary:        Message queuing service for OpenStack

License:        ASL 2.0
URL:            https://wiki.openstack.org/wiki/Zaqar
Source0:        https://tarballs.openstack.org/zaqar/%{service}-%{upstream_version}.tar.gz
Source1:        %{service}-dist.conf

Source10:       %{name}.service
Source11:       %{name}.logrotate
Source12:       %{name}@.service
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
Source101:        https://tarballs.openstack.org/zaqar/%{service}-%{upstream_version}.tar.gz.asc
Source102:        https://releases.openstack.org/_static/%{sources_gpg_sign}.txt
%endif

BuildArch:      noarch

# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
BuildRequires:  /usr/bin/gpgv2
%endif
BuildRequires:  openstack-macros
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pbr >= 1.6
BuildRequires:  systemd
BuildRequires:  git-core
# Required for config file generation
BuildRequires:  python3-oslo-cache >= 1.26.0
BuildRequires:  python3-oslo-config >= 2:6.8.0
BuildRequires:  python3-oslo-db >= 4.27.0
BuildRequires:  python3-oslo-log >= 3.36.0
BuildRequires:  python3-oslo-policy >= 1.30.0
BuildRequires:  python3-oslo-upgradecheck >= 0.1.0
BuildRequires:  python3-keystonemiddleware >= 4.17.0
BuildRequires:  python3-falcon
BuildRequires:  python3-jsonschema
BuildRequires:  python3-sqlalchemy >= 1.3.2
BuildRequires:  python3-osprofiler
BuildRequires:  python3-oslo-messaging
BuildRequires:  python3-autobahn
# Required to compile translation files
BuildRequires:  python3-babel
BuildRequires:  openstack-macros

BuildRequires:  python3-trollius
BuildRequires:  python3-redis

Obsoletes:      openstack-marconi < 2014.1-2.2

Requires(pre):  shadow-utils
%{?systemd_requires}

Requires:         python3-stevedore >= 3.2.2
Requires:         python3-jsonschema >= 3.2.0
Requires:         python3-oslo-cache >= 1.26.0
Requires:         python3-oslo-config >= 2:8.3.2
Requires:         python3-oslo-context >= 2.19.2
Requires:         python3-oslo-db >= 11.0.0
Requires:         python3-oslo-log >= 4.6.1
Requires:         python3-oslo-messaging >= 12.5.0
Requires:         python3-oslo-policy >= 3.8.1
Requires:         python3-oslo-serialization >= 4.2.0
Requires:         python3-oslo-utils >= 4.12.1
Requires:         python3-oslo-i18n >= 3.15.3
Requires:         python3-oslo-reports >= 2.2.0
Requires:         python3-oslo-upgradecheck >= 1.3.0
Requires:         python3-keystonemiddleware >= 9.1.0
Requires:         python3-falcon >= 3.0.0
Requires:         python3-futurist >= 1.2.0
Requires:         python3-babel >= 2.3.4
Requires:         python3-sqlalchemy >= 1.3.19
Requires:         python3-keystoneclient
Requires:         python3-requests >= 2.25.0
Requires:         python3-iso8601 >= 0.1.11
Requires:         python3-webob >= 1.7.1
Requires:         python3-pbr >= 2.0.0
Requires:         python3-autobahn >= 21.2.2
Requires:         python3-osprofiler >= 1.4.0
Requires:         python3-alembic >= 0.9.6

Requires:         python3-memcached >= 1.56
Requires:         python3-bson
Requires:         python3-msgpack >= 1.0.0
Requires:         python3-redis
Requires:         python3-swiftclient >= 3.10.1
Requires:         python3-cryptography >= 2.7

%description
%{common_desc}

%package -n python3-%{service}-tests
Summary:        Zaqar tests
%{?python_provide:%python_provide python3-%{service}-tests}
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description -n python3-%{service}-tests
%{common_desc}

This package contains the Zaqar test files.

%prep
# Required for tarball sources verification
%if 0%{?sources_gpg} == 1
%{gpgverify}  --keyring=%{SOURCE102} --signature=%{SOURCE101} --data=%{SOURCE0}
%endif
%autosetup -n %{service}-%{upstream_version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
%py_req_cleanup

%build
# Generate config file
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/zaqar.conf

%{py3_build}
# Generate i18n files
%{__python3} setup.py compile_catalog -d build/lib/%{service}/locale --domain zaqar

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
%{py3_install}

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
rm -f %{buildroot}%{python3_sitelib}/%{service}/locale/*/LC_*/%{service}*po
rm -f %{buildroot}%{python3_sitelib}/%{service}/locale/*pot
mv %{buildroot}%{python3_sitelib}/%{service}/locale %{buildroot}%{_datadir}/locale

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
%{_bindir}/%{service}-wsgi

%{_datarootdir}/%{service}

%defattr(-, %{service}, %{service}, -)
%dir %{_sharedstatedir}/%{service}

%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%{python3_sitelib}/%{service}
%{python3_sitelib}/%{service}-%{version}*.egg-info
%exclude %{python3_sitelib}/%{service}/tests

%files -n python3-%{service}-tests
%license LICENSE
%{python3_sitelib}/%{service}/tests

%changelog
