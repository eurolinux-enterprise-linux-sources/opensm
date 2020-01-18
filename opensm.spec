%define _hardened_build 1

Name: opensm
Version: 3.3.20
Release: 2%{?dist}
Summary: OpenIB InfiniBand Subnet Manager and management utilities
License: GPLv2 or BSD
Url: http://www.openfabrics.org/
Source0: http://www.openfabrics.org/downloads/management/%{name}-%{version}.tar.gz
Source2: opensm.logrotate
Source4: opensm.sysconfig
Source5: opensm.service
Source6: opensm.launch
Source7: opensm.rwtab
Patch0: opensm-3.3.13-prefix.patch
BuildRequires: libibmad-devel >= 1.3.12, libtool, bison, flex, byacc, systemd
Requires: %{name}-libs%{?_isa} = %{version}-%{release}, logrotate, rdma
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
OpenSM is the OpenIB project's Subnet Manager for Infiniband networks.
The subnet manager is run as a system daemon on one of the machines in
the infiniband fabric to manage the fabric's routing state.  This package
also contains various tools for diagnosing and testing Infiniband networks
that can be used from any machine and do not need to be run on a machine
running the opensm daemon.

%package libs
Summary: Libraries used by opensm and included utilities

%description libs
Shared libraries for Infiniband user space access

%package devel
Summary: Development files for the opensm-libs libraries
Requires: %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
Development environment for the opensm libraries

%package static
Summary: Static version of the opensm libraries
Requires: %{name}-devel%{?_isa} = %{version}-%{release}
%description static
Static version of opensm libraries

%prep
%setup -q
%patch0 -p1 -b .prefix

%build
%configure --with-opensm-conf-sub-dir=rdma CFLAGS="$CFLAGS -fno-strict-aliasing"
make %{?_smp_mflags}
cd opensm
./opensm -c ../opensm-%{version}.conf

%install
make install DESTDIR=%{buildroot}
# remove unpackaged files from the buildroot
rm -f %{buildroot}%{_libdir}/*.la
rm -fr %{buildroot}%{_sysconfdir}/init.d
install -D -m644 opensm-%{version}.conf %{buildroot}%{_sysconfdir}/rdma/opensm.conf
install -D -m644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/opensm
install -D -m644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/opensm
install -D -m644 %{SOURCE5} %{buildroot}%{_unitdir}/opensm.service
install -D -m755 %{SOURCE6} %{buildroot}%{_libexecdir}/opensm-launch
install -D -m644 %{SOURCE7} %{buildroot}%{_sysconfdir}/rwtab.d/opensm
mkdir -p ${RPM_BUILD_ROOT}/var/cache/opensm
install -m 755 scripts/sldd.sh %{buildroot}%{_sbindir}/sldd.sh

%post
%systemd_post opensm.service

%preun
%systemd_preun opensm.service

%postun
if [ -d /var/cache/opensm ]; then
	rm -fr /var/cache/opensm
fi
%systemd_postun_with_restart opensm.service

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files
%dir /var/cache/opensm
%{_sbindir}/*
%{_mandir}/*
%{_unitdir}/*
%{_libexecdir}/*
%config(noreplace) %{_sysconfdir}/logrotate.d/opensm
%config(noreplace) %{_sysconfdir}/rdma/opensm.conf
%config(noreplace) %{_sysconfdir}/sysconfig/opensm
%{_sysconfdir}/rwtab.d/opensm
%doc AUTHORS ChangeLog INSTALL README NEWS doc/performance-manager-HOWTO.txt doc/QoS_management_in_OpenSM.txt doc/partition-config.txt doc/opensm-sriov.txt doc/current-routing.txt doc/opensm_release_notes-3.3.txt
%license COPYING

%files libs
%{_libdir}/lib*.so.*

%files devel
%{_libdir}/lib*.so
%{_includedir}/infiniband

%files static
%{_libdir}/lib*.a

%changelog
* Wed Nov  1 2017 Honggang Li <honli@redhat.com> - 3.3.20-2
- Fix up preuninstall script
- Resolves: bz1508334

* Mon Oct 16 2017 Honggang Li <honli@redhat.com> - 3.3.20-1
- Cleanup the spec file
- Rebase to latest upstream release 3.3.20
- Resolves: bz1456524

* Fri Jun 05 2015 Doug Ledford <dledford@redhat.com> - 3.3.19-1
- Update to latest upstream release
- Build on s390
- Related: bz1186159

* Fri Oct 17 2014 Doug Ledford <dledford@redhat.com> - 3.3.18-2
- Fix an issue found by rpmdiff
- Related: bz1061587

* Thu Oct 09 2014 Doug Ledford <dledford@redhat.com> - 3.3.18-1
- Update to latest upstream release
- Resolves: bz1061587, bz1042745, bz884555, bz948475

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.3.15-7
- Mass rebuild 2013-12-27

* Mon Mar 25 2013 Doug Ledford <dledford@redhat.com> - 3.3.15-6
- Oops, forgot to remove the -B option to opensm when starting it

* Mon Mar 25 2013 Doug Ledford <dledford@redhat.com> - 3.3.15-5
- Drop the old sysv init script
- Fix opensm-launch to restart opensm in a loop.  This works around the
  fact that systemd starts opensm so early that we very well might not have
  sync on the link yet.  Without the physical link being up, opensm exits
  immediately.  This way opensm will get restarted every 30 seconds until
  sync is active on the link or until the opensm service is stopped.
- Always install the newly generated opensm-%%{version}.conf as opensm.conf
- Make the launch work properly in the event that no GUIDs are set and
  there are no numbered config files

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.15-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Dec 05 2012 Doug Ledford <dledford@redhat.com> - 3.3.15-3
- Fix startup on read only root
- Update default config file
- Resolves: bz817591

* Wed Dec 05 2012 Doug Ledford <dledford@redhat.com> - 3.3.15-2
- More tweaks to systemd setup (proper scriptlets now)
- More tweaks to old sysv init script support (fix Requires)

* Tue Nov 27 2012 Doug Ledford <dledford@redhat.com> - 3.3.15-1
- Update to latest upstream release
- Update to systemd startup

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.13-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Mar 13 2012 Doug Ledford <dledford@redhat.com> - 3.3.13-2
- Fix the config file comment in the opensm init script
- Resolves: bz802727

* Tue Feb 28 2012 Doug Ledford <dledford@redhat.com> - 3.3.13-1
- Update to latest upstream version
- Fix a minor issue in init scripts that would cause systemd to try and
  start/stop things in the wrong order
- Add a patch to allow us to specify the subnet prefix on the command line

* Tue Jan 03 2012 Doug Ledford <dledford@redhat.com> - 3.3.12-1
- Update to latest upstream version

* Mon Aug 15 2011 Kalev Lember <kalevlember@gmail.com> - 3.3.9-2
- Rebuilt for rpm bug #728707

* Wed Jul 20 2011 Doug Ledford <dledford@redhat.com> - 3.3.9-1
- Update to latest upstream version
- Add /etc/sysconfig/opensm for use by opensm init script
- Enable the ability to start more than one instance of opensm for multiple
  fabric support
- Enable the ability to start opensm with a priority other than default for
  support of backup opensm instances

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Mar 08 2010 Doug Ledford <dledford@redhat.com> - 3.3.5-1
- Update to latest upstream release.  We need various defines in ib_types.h
  for the latest ibutils package to build properly, and the latest ibutils
  package is needed because we found licensing problems in the older
  tarballs during review.

* Mon Jan 11 2010 Doug Ledford <dledford@redhat.com> - 3.3.3-2
- ExcludeArch s390(x) as there's no hardware support there

* Thu Dec 03 2009 Doug Ledford <dledford@redhat.com> - 3.3.3-1
- Update to latest upstream release
- Minor tweaks to init script for LSB compliance

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 20 2009 Doug Ledford <dledford@redhat.com> - 3.3.2-1
- Update to latest upstream version

* Wed Apr 22 2009 Doug Ledford <dledford@redhat.com> - 3.3.1-1
- Update to latest upstream version

* Fri Mar 06 2009 Caolán McNamara <caolanm@redhat.com> - 3.2.1-3
- fix bare elifs to rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jun 08 2008 Doug Ledford <dledford@redhat.com> - 3.2.1-1
- Initial package for Fedora review process
