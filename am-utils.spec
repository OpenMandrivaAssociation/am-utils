%define major	2

%define libname %mklibname amu %{major}
%define develname %mklibname amu -d

Summary:	Automount utilities including an updated version of Amd
Name:		am-utils
Version:	6.1.5
Release:	9
Epoch:		2
License:	BSD
Group:		System/Servers
URL:		http://www.am-utils.org/
Source0:	ftp://ftp.am-utils.org/pub/am-utils/%{name}/%{name}-%{version}.tar.bz2
Source1:	am-utils.init
Source2:	am-utils.conf
Source3:	am-utils.sysconf
Source4:	am-utils.net.map
Patch0:		am-utils-6.0.4-nfs3.patch
# RH/Fedora #203193, MDV #45007 - tmpfile usage
Patch1:		am-utils-6.1.5-rmtab-temp.patch
# RH/Fedora #202180, MDV #45007 - amd service doesn't work
Patch2:		am-utils-6.1.5-nfs-version.patch
# MDV #45007, from RH: UTS_RELEASE macro has been removed from the latest kernel
Patch3:		am-utils-6.1.5-UTS_RELEASE.patch
# MDV #45007, Fedora build system bugfixes
Patch4:		am-utils-6.1.5-buildsys.patch
# RH/Fedora #435420, MDV #45007 - CVE-2008-1078 am-utils: insecure usage of
# temporary files
Patch5:		am-utils-6.1.5-expn-temp.patch
# RH/Fedora #450754, MDV #45007 - Amd does not work with 2.6.25
Patch6:		am-utils-6.1.5-nolock-toplvl.patch
# RH/Fedora #566711 - am-utils: incorrect use of tcp_wrapper
Patch7:		am-utils-6.1.5-libwarp.patch
Requires(pre): grep
Requires(post): rpm-helper chkconfig
Requires(preun): rpm-helper chkconfig
Requires:	rpcbind
BuildRequires:	bison 
BuildRequires:	byacc 
BuildRequires:	flex 
BuildRequires:	gdbm-devel 
BuildRequires:	openldap-devel >= 2.0.0
BuildConflicts: db2-devel db1-devel
%rename	amd

%description
Am-utils includes an updated version of Amd, the popular BSD
automounter.  An automounter is a program which maintains a cache of
mounted filesystems.  Filesystems are mounted when they are first
referenced by the user and unmounted after a certain period of inactivity.
Amd supports a variety of filesystems, including NFS, UFS, CD-ROMS and
local drives.  

You should install am-utils if you need a program for automatically
mounting and unmounting filesystems.

%package -n %{libname}
Group:          System/Servers
Summary:        Shared library files for am-utils

%description -n %{libname}
Shared library files from the am-utils package.

%package -n %{develname}
Group:          Development/C
Summary:        Development files for am-utils
Requires:       %{libname} = %{EVRD}
Obsoletes:      %{mklibname amu -d 2} < 2:6.1.5-9

%description -n %{develname}
Development headers, and files for development from the am-utils package.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
./bootstrap
%configure2_5x \
	--enable-shared				\
    --disable-static				\
	--sysconfdir=%{_sysconfdir}		\
	--enable-libs="-lnsl -lresolv"		\
	--disable-amq-mount                     \
	--without-ldap

%make

%install
%makeinstall_std

mkdir -p %{buildroot}%{_sysconfdir}/{sysconfig,rc.d/init.d}
install -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/amd
install -m 755 %{SOURCE1} %{buildroot}%{_sysconfdir}/rc.d/init.d/amd

mkdir -p %{buildroot}/.automount
rm -f %{buildroot}%{_sbindir}/ctl-amd

# install the default config and map files
install -m 600 %{SOURCE2} %{buildroot}%{_sysconfdir}/amd.conf
install -m 640 %{SOURCE4} %{buildroot}%{_sysconfdir}/amd.net

rm -f %{buildroot}/amd.conf
rm -f %{buildroot}/%{_sysconfdir}/*-sample
rm -f %{buildroot}/amd

%pre
# Check if we have an old fashioned amd.conf and rename if to amd.net
if [ "$1" = "0" ] ; then
    if grep -q "auto_dir" %{_sysconfdir}/amd.conf 2>/dev/null > /dev/null ; then
	# this is okay
	exit 0
    else
	# this needs to be renamed. Still, if %{_sysconfdir}/amd.net exists, then
	# don't bother renamig it. RPM will handle it better than us here.
	if [ -e %{_sysconfdir}/amd.net ] ; then
	    exit 0
	else
	    mv -f %{_sysconfdir}/amd.conf /etc/amd.net
	fi
    fi
fi
exit 0

%post
%_post_service amd

%preun
%_preun_service amd

%files
%doc doc/*.ps AUTHORS BUGS ChangeLog NEWS README* scripts/*-sample INSTALL COPYING
%dir /.automount
%{_bindir}/pawd
%{_bindir}/expn
%{_sbindir}/*
%{_mandir}/man[58]/*
%{_mandir}/man1/pawd.1*
%{_mandir}/man1/expn.1*
%config(noreplace) %verify(not md5) %{_sysconfdir}/amd.conf
%config(noreplace) %verify(not md5) %{_sysconfdir}/amd.net
%config(noreplace) %{_sysconfdir}/sysconfig/amd
%config(noreplace) %{_sysconfdir}/rc.d/init.d/amd
%{_infodir}/*.info*

%files -n %{libname}
%{_libdir}/*.so.*

%files -n %{develname}
%{_libdir}/*.so

%changelog
* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 2:6.1.5-8mdv2011.0
+ Revision: 609973
- rebuild

* Mon Mar 08 2010 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 2:6.1.5-7mdv2010.1
+ Revision: 515618
- Include fixes from am-utils Fedora package, also handling
  Mandriva bug #45007:
  * RH/Fedora #203193, MDV #45007 - tmpfile usage
  * RH/Fedora #202180, MDV #45007 - amd service doesn't work
  * MDV #45007, from RH: UTS_RELEASE macro has been removed from the
    latest kernel (replaces am-utils-6.1.5-fix-configure.patch)
  * MDV #45007, Fedora build system bugfixes
  * RH/Fedora #435420, MDV #45007 - CVE-2008-1078 am-utils: insecure
    usage of temporary files
  * RH/Fedora #450754, MDV #45007 - Amd does not work with 2.6.25
  * RH/Fedora #566711 - am-utils: incorrect use of tcp_wrapper
- Add LSB header to amd initscript.

* Sun Jul 26 2009 Guillaume Rousse <guillomovitch@mandriva.org> 2:6.1.5-6mdv2010.0
+ Revision: 400423
- new devel policy
- uncompress additional sources
- patch1: fix configure script
- fix dependencies

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild
    - use std info-install macros
    - kill re-definition of %%buildroot on Pixel's request

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Thu Aug 23 2007 Thierry Vignaud <tv@mandriva.org> 2:6.1.5-3mdv2008.0
+ Revision: 69949
- kill file require on chkconfig
- kill file require on info-install


* Sun Jan 07 2007 Crispin Boylan <crisb@mandriva.org> 6.1.5-2mdv2007.0
+ Revision: 105188
- Kill db1 dep

* Sat Aug 05 2006 Olivier Thauvin <nanardon@mandriva.org> 2:6.1.5-1mdv2007.0
+ Revision: 51689
- 6.1.5
- Import am-utils

* Sun Dec 11 2005 Olivier Thauvin <nanardon@mandriva.org> 6.1.3-1mdk
- 6.1.3

* Wed Sep 28 2005 Olivier Thauvin <nanardon@mandriva.org> 6.1.2.1-1mdk
- 6.1.2.1

* Thu May 05 2005 Olivier Thauvin <nanardon@mandriva.org> 6.0.9-9mdk
- fix build on amd64 (autotools)

* Thu Nov 18 2004 Olivier Thauvin <thauvin@aerov.jussieu.fr> 6.0.9-8mdk
- clean dep, update for 64bits

* Tue Mar 02 2004 Pascal Terjan <pterjan@mandrake.org> 6.0.9-7mdk
- Fix one more DEP

* Sun Feb 29 2004 Pascal Terjan <pterjan@mandrake.org> 6.0.9-6mdk
- Fix DEP due to Epoch

* Thu Feb 26 2004 Olivier Thauvin <thauvin@aerov.jussieu.fr> 6.0.9-5mdk
- Fix DEP
- disabling ldap (won't build on klama)

