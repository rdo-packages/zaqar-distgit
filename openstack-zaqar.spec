%global project zaqar
%global milestone .0rc2

%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

Name:           openstack-%{project}
# Liberty semver reset
# https://review.openstack.org/#/q/I6a35fa0dda798fad93b804d00a46af80f08d475c,n,z
Epoch:          1
Version:        1.0.0
Release:        0.1%{milestone}%{?dist}.1
Summary:        Message queuing service for OpenStack

License:        ASL 2.0
URL:            https://wiki.openstack.org/wiki/Zaqar
Source0:        http://tarballs.openstack.org/zaqar/%{project}-%{upstream_version}.tar.gz
Source1:        %{project}-dist.conf
# generated configuration file w/ oslo-config-generator
Source2:        %{project}.conf.sample

#
# patches_base=1.0.0.0rc2
#

Source10:       %{name}.service
Source11:       %{name}.logrotate

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  python-pbr
BuildRequires:  openstack-utils
BuildRequires:  systemd
BuildRequires:  git

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
Requires:         python-pbr

%description
Zaqar is a new OpenStack project to create a multi-tenant cloud queuing 
service.The project will define a clean, RESTful API, use a modular 
architecture, and will support both eventing and job-queuing semantics.
Users will be able to customize Zaqar to achieve a wide range of performance,
durability, availability,and efficiency goals

%prep
%autosetup -n %{project}-%{upstream_version} -S git

# Remove the requirements file so that pbr hooks don't add it
# to distutils requires_dist config
rm -rf {test-,}requirements.txt

%build
%{__python2} setup.py build

install -p -D -m 640 %{SOURCE2} etc/%{project}.conf.sample

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
%{__python2} setup.py install -O1 --skip-build --root %{buildroot}

 
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
%{!?_licensedir: %global license %%doc}
%license LICENSE
%doc README.rst

%dir %{_sysconfdir}/%{project}
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/%{project}.conf
%config(noreplace) %attr(0640, root, %{project}) %{_sysconfdir}/%{project}/logging.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%dir %attr(0755, %{project}, root) %{_localstatedir}/log/%{project}

%{_bindir}/%{project}-server
%{_bindir}/%{project}-bench
%{_bindir}/%{project}-gc

%{_datarootdir}/%{project}

%defattr(-, %{project}, %{project}, -)
%dir %{_sharedstatedir}/%{project}

%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{python2_sitelib}/%{project}
%{python2_sitelib}/%{project}-%{version}*.egg-info

%changelog
* Wed Oct 07 2015 Haikel Guemar <hguemar@fedoraproject.org> 1:1.0.0-0.1.0rc2
- Update to upstream 1.0.0.0rc2
- Drop compat binary marconi-server

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2015.1.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 12 2015 Haikel Guemar <hguemar@fedoraproject.org> 2015.1.0-1
- Update to upstream 2015.1.0
- Dropping pbr patch
- Spec cleanups

* Sun Oct 19 2014 Haïkel Guémar <hguemar@fedoraproject.org> 2014.2-1
- Update to upstream 2014.2

* Sun Sep 07 2014 Eduardo Echeverria <echevemaster@gmail.com> 2014.2-0.3.b3
- Adding missing requires

* Sun Sep 07 2014 Eduardo Echeverria <echevemaster@gmail.com> 2014.2-0.2.b3
- Adding obsoletes to the spec.

* Fri Aug 22 2014 Eduardo Echeverria <echevemaster@gmail.com> 2014.2-0.1.b3
- Initial commit
