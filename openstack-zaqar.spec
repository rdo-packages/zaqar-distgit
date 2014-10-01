%global project zaqar
Name:           openstack-%{project}
Version:        2014.2
Release:        0.3.b3%{?dist}
Summary:        Message queuing service for OpenStack

Group:          Applications/System
License:        ASL 2.0
URL:            https://wiki.openstack.org/wiki/Zaqar
Source0:        http://tarballs.openstack.org/zaqar/%{project}-%{version}.b3.tar.gz
Source1:        %{project}-dist.conf

Source10:       %{name}.service
Source11:       %{name}.logrotate

Patch0001: 0001-Remove-runtime-dependency-on-PBR.patch

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  systemd
BuildRequires:  python-setuptools
BuildRequires:  python-pbr
BuildRequires:  openstack-utils

Obsoletes:      openstack-marconi < 2014.1-2.2

Requires(pre):  shadow-utils
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

Requires:         python-six
Requires:         python-stevedore
Requires:         python-jsonschema
Requires:         python-oslo-config
Requires:         python-oslo-utils
Requires:         python-oslo-i18n
Requires:         python-falcon
Requires:         python-pymongo
Requires:         python-sqlite3dbm
Requires:         python-memcached
Requires:         python-babel
Requires:         python-bson
Requires:         python-sqlalchemy
Requires:         python-keystoneclient
Requires:         python-netaddr
Requires:         python-iso8601
Requires:         python-msgpack
Requires:         python-webob
Requires:         python-posix_ipc

%description
Zaqar is a new OpenStack project to create a multi-tenant cloud queuing 
service.The project will define a clean, RESTful API, use a modular 
architecture, and will support both eventing and job-queuing semantics.
Users will be able to customize Zaqar to achieve a wide range of performance,
durability, availability,and efficiency goals

%prep
%setup -q -n %{project}-%{version}.b3
%patch0001 -p1
sed -i 's/REDHATVERSION/%{version}/; s/REDHATRELEASE/%{release}/' %{project}/version.py

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt

%build
%{__python2} setup.py build

# Programmatically update defaults in sample configs

#  First we ensure all values are commented in appropriate format.
#  Since icehouse, there was an uncommented keystone_authtoken section
#  at the end of the file which mimics but also conflicted with our
#  distro editing that had been done for many releases.
sed -i '/^[^#[]/{s/^/#/; s/ //g}; /^#[^ ]/s/ = /=/' etc/%{project}.conf.sample etc/logging.conf.sample

#  TODO: Make this more robust
#  Note it only edits the first occurance, so assumes a section ordering in sample
#  and also doesn't support multi-valued variables like dhcpbridge_flagfile.
while read name eq value; do
  test "$name" && test "$value" || continue
  sed -i "0,/^# *$name=/{s!^# *$name=.*!#$name=$value!}" etc/%{project}.conf.sample
done < %{SOURCE1}']'


%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}

 
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

# Install logrotate
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Install initscripts
install -p -m 644 %{SOURCE10} %{buildroot}%{_unitdir}

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

%files
%doc LICENSE README.rst

%dir %{_sysconfdir}/%{project}
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}.conf
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/logging.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%dir %attr(0755, %{project}, root) %{_localstatedir}/log/%{project}

%{_bindir}/marconi-server
%{_bindir}/%{project}-server
%{_bindir}/%{project}-bench
%{_bindir}/%{project}-gc

%{_datarootdir}/%{project}

%defattr(-, %{project}, %{project}, -)
%dir %{_sharedstatedir}/%{project}

%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{python_sitelib}/%{project}
%{python_sitelib}/%{project}-%{version}*.egg-info

%changelog
* Sun Sep 10 2014 Eduardo Echeverria <echevemaster@gmail.com> 2014.2-0.3.b3
- Adding missing requires

* Sun Sep 07 2014 Eduardo Echeverria <echevemaster@gmail.com> 2014.2-0.2.b3
- Adding obsoletes to the spec.

* Fri Aug 22 2014 Eduardo Echeverria <echevemaster@gmail.com> 2014.2-0.1.b3
- Initial commit
