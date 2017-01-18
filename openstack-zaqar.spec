%global project zaqar
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-%{project}
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:          1
Version:        XXX
Release:        XXX
Summary:        Message queuing service for OpenStack

License:        ASL 2.0
URL:            https://wiki.openstack.org/wiki/Zaqar
Source0:        https://tarballs.openstack.org/zaqar/%{project}-%{upstream_version}.tar.gz
Source1:        %{project}-dist.conf

Source10:       %{name}.service
Source11:       %{name}.logrotate
Source12:       %{name}@.service

BuildArch:      noarch
BuildRequires:  openstack-macros
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-pbr >= 1.6
BuildRequires:  systemd
BuildRequires:  git
# Required for config file generation
BuildRequires:  python-oslo-cache >= 1.5.0
BuildRequires:  python-oslo-config >= 2:3.7.0
BuildRequires:  python-oslo-log >= 1.14.0
BuildRequires:  python-oslo-policy >= 0.5.0
BuildRequires:  python-keystonemiddleware >= 4.0.0
BuildRequires:  python-enum34
BuildRequires:  python-falcon
BuildRequires:  python-jsonschema
BuildRequires:  python-pymongo
BuildRequires:  python-sqlalchemy >= 1.0.10
BuildRequires:  python-osprofiler
BuildRequires:  python-oslo-messaging
# Required to compile translation files
BuildRequires:  python-babel

Obsoletes:      openstack-marconi < 2014.1-2.2

Requires(pre):  shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

Requires:         python-six
Requires:         python-stevedore
Requires:         python-jsonschema
Requires:         python-oslo-cache >= 1.5.0
Requires:         python-oslo-config >= 2:3.7.0
Requires:         python-oslo-context >= 0.2.0
Requires:         python-oslo-log >= 1.14.0
Requires:         python-oslo-policy >= 0.5.0
Requires:         python-oslo-serialization >= 1.10.0
Requires:         python-oslo-utils
Requires:         python-oslo-i18n
Requires:         python-keystonemiddleware >= 4.0.0
Requires:         python-falcon
Requires:         python-futurist
Requires:         python-pymongo
Requires:         python-sqlite3dbm
Requires:         python-memcached
Requires:         python-babel
Requires:         python-enum34
Requires:         python-bson
Requires:         python-sqlalchemy >= 1.0.10
Requires:         python-keystoneclient
Requires:         python-netaddr
Requires:         python-requests
Requires:         python-trollius
Requires:         python-iso8601
Requires:         python-msgpack >= 0.4.0
Requires:         python-webob >= 1.2.3
Requires:         python-posix_ipc
Requires:         python-pbr >= 1.6
Requires:         python-autobahn
Requires:         python-osprofiler >= 1.4.0
Requires:         python-alembic

%description
Zaqar is a new OpenStack project to create a multi-tenant cloud queuing 
service.The project will define a clean, RESTful API, use a modular 
architecture, and will support both eventing and job-queuing semantics.
Users will be able to customize Zaqar to achieve a wide range of performance,
durability, availability,and efficiency goals

%package -n python-%{project}-tests
Summary:        Zaqar tests
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description -n python-%{project}-tests
This package contains the Zaqar test files.

%prep
%autosetup -n %{project}-%{upstream_version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt

%build
# Generate config file
PYTHONPATH=. oslo-config-generator --config-file=etc/oslo-config-generator/zaqar.conf

%{__python2} setup.py build
# Generate i18n files
%{__python2} setup.py compile_catalog -d build/lib/%{project}/locale

# Programmatically update defaults in sample configs

#  First we ensure all values are commented in appropriate format.
#  Since icehouse, there was an uncommented keystone_authtoken section
#  at the end of the file which mimics but also conflicted with our
#  distro editing that had been done for many releases.
sed -i '/^[^#[]/{s/^/#/; s/ //g}; /^#[^ ]/s/ = /=/' etc/%{project}.conf.sample etc/logging.conf.sample

#  TODO: Make this more robust
#  Note it only edits the first occurrence, so assumes a section ordering in sample
#  and also doesn't support multi-valued variables like dhcpbridge_flagfile.
while read name eq value; do
  test "$name" && test "$value" || continue
  sed -i "0,/^# *$name=/{s!^# *$name=.*!#$name=$value!}" etc/%{project}.conf.sample
done < %{SOURCE1}']'


%install
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

# Create fake egg-info for the tempest plugin
# TODO switch to %{service} everywhere as in openstack-example.spec
%global service zaqar
%py2_entrypoint %{service} %{service}

# Setup directories
install -d -m 755 %{buildroot}%{_unitdir}
install -d -m 755 %{buildroot}%{_datadir}/%{project}
install -d -m 755 %{buildroot}%{_sharedstatedir}/%{project}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{project}

# Install config files
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_datadir}/%{project}/%{project}-dist.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/%{project}

install -p -D -m 640 etc/%{project}.conf.sample %{buildroot}%{_sysconfdir}/%{project}/%{project}.conf
install -p -D -m 640 etc/logging.conf.sample    %{buildroot}%{_sysconfdir}/%{project}/logging.conf
install -p -D -m 640 etc/policy.json.sample    %{buildroot}%{_sysconfdir}/%{project}/policy.json

# Install logrotate
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Install initscripts
install -p -m 644 %{SOURCE10} %{buildroot}%{_unitdir}
install -p -m 644 %{SOURCE12} %{buildroot}%{_unitdir}

# Install i18n .mo files (.po and .pot are not required)
install -d -m 755 %{buildroot}%{_datadir}
rm -f %{buildroot}%{python2_sitelib}/%{project}/locale/*/LC_*/%{project}*po
rm -f %{buildroot}%{python2_sitelib}/%{project}/locale/*pot
mv %{buildroot}%{python2_sitelib}/%{project}/locale %{buildroot}%{_datadir}/locale

# Find language files
%find_lang %{project} --all-name

%pre
USERNAME=%{project}
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

%files -f %{project}.lang
%{!?_licensedir: %global license %%doc}
%license LICENSE
%doc README.rst

%dir %{_sysconfdir}/%{project}
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}.conf
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/logging.conf
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/policy.json
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%dir %attr(0755, %{project}, root) %{_localstatedir}/log/%{project}

#%{_bindir}/marconi-server
%{_bindir}/%{project}-server
%{_bindir}/%{project}-bench
%{_bindir}/%{project}-gc
%{_bindir}/%{project}-sql-db-manage

%{_datarootdir}/%{project}

%defattr(-, %{project}, %{project}, -)
%dir %{_sharedstatedir}/%{project}

%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}@.service
%{python2_sitelib}/%{project}
%{python2_sitelib}/%{project}-%{version}*.egg-info
%exclude %{python2_sitelib}/%{project}/tests

%files -n python-%{project}-tests
%license LICENSE
%{python2_sitelib}/%{project}/tests
%{python2_sitelib}/%{service}_tests.egg-info

%changelog
