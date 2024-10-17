%define major 4

%define libname %mklibname amu %{major}
%define devname %mklibname amu -d

Summary:	Automount utilities including an updated version of Amd
Name:		am-utils
Version:	6.1.5
Release:	11
Epoch:		2
License:	BSD
Group:		System/Servers
Url:		https://www.am-utils.org/
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
Patch8:		am-utils-6.1.5-fix-configure.patch
Requires:	rpcbind
BuildRequires:	bison
BuildRequires:	byacc
BuildRequires:	flex
BuildRequires:	gdbm-devel
BuildRequires:	openldap-devel >= 2.0.0
BuildConflicts:	db2-devel
BuildConflicts:	db1-devel
%rename		amd

%description
Am-utils includes an updated version of Amd, the popular BSD
automounter.  An automounter is a program which maintains a cache of
mounted filesystems.  Filesystems are mounted when they are first
referenced by the user and unmounted after a certain period of inactivity.
Amd supports a variety of filesystems, including NFS, UFS, CD-ROMS and
local drives.

You should install am-utils if you need a program for automatically
mounting and unmounting filesystems.

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

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	Shared library files for am-utils
Group:		System/Servers
Conflicts:	%{_lib}amu2 < 2:6.1.5-10
Obsoletes:	%{_lib}amu2 < 2:6.1.5-10

%description -n %{libname}
Shared library files from the am-utils package.

%files -n %{libname}
%{_libdir}/libamu.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Development files for am-utils
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Obsoletes:	%{mklibname amu -d 2} < 2:6.1.5-9

%description -n %{devname}
Development headers, and files for development from the am-utils package.

%files -n %{devname}
%{_libdir}/libamu.so

#----------------------------------------------------------------------------

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
%patch8 -p1

%build
./bootstrap
autoconf
%configure2_5x \
	--enable-shared \
	--disable-static \
	--sysconfdir=%{_sysconfdir} \
	--enable-libs="-lnsl -lresolv" \
	--disable-amq-mount \
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

