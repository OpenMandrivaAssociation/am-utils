%define name	am-utils
%define version	6.1.5
%define release	%mkrel 2
%define epoch	2
%define major	2

%define libname %mklibname amu %major
%define libnamedevel %mklibname amu %major -d

Summary:	Automount utilities including an updated version of Amd
Name:		%{name}
Version:	%{version}
Release:	%{release}
Epoch:		%{epoch}
License:	BSD
Group:		System/Servers
Source:		ftp://ftp.am-utils.org/pub/am-utils/%{name}/%{name}-%{version}.tar.bz2
Source1:	am-utils.init.bz2
Source2:	am-utils.conf.bz2
Source3:	am-utils.sysconf.bz2
Source4:	am-utils.net.map.bz2
Requires(pre): grep
Requires(post): rpm-helper chkconfig info-install
Requires(preun): info-install rpm-helper chkconfig
Requires:	portmap
BuildRoot:	%{_tmppath}/%{name}-root
Obsoletes:	amd
Provides:	amd
BuildRequires:	bison byacc flex gdbm-devel openldap-devel >= 2.0.0
BuildRequires:  automake1.4
BuildConflicts: db2-devel db1-devel
Patch:		am-utils-6.0.4-nfs3.patch
URL:		http://www.am-utils.org/

%description
Am-utils includes an updated version of Amd, the popular BSD
automounter.  An automounter is a program which maintains a cache of
mounted filesystems.  Filesystems are mounted when they are first
referenced by the user and unmounted after a certain period of inactivity.
Amd supports a variety of filesystems, including NFS, UFS, CD-ROMS and
local drives.  

You should install am-utils if you need a program for automatically
mounting and unmounting filesystems.

%package -n %libname
Group:          System/Servers
Summary:        Shared library files for am-utils
Provides:	lib%name = %version-%release

%description -n %libname
Shared library files from the am-utils package.

%package -n %libnamedevel
Group:          Development/C
Summary:        Development files for am-utils
Requires:       %libname = %{epoch}:%version-%release
Provides:       libamu-devel

%description -n %libnamedevel
Development headers, and files for development from the am-utils package.

%prep
%setup -q
%patch -p1

%build

aclocal-1.4
automake-1.4 -a || :
autoconf

%serverbuild
%configure \
	--enable-shared				\
	--sysconfdir=%{_sysconfdir}		\
	--enable-libs="-lnsl -lresolv"		\
	--disable-amq-mount                     \
        --without-ldap

%make

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/{sysconfig,rc.d/init.d}

bzcat  %{SOURCE3} > $RPM_BUILD_ROOT/amd
install -m 755 $RPM_BUILD_ROOT/amd $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/amd

bzcat  %{SOURCE1} > $RPM_BUILD_ROOT/amd
install -m 755 $RPM_BUILD_ROOT/amd $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/amd

mkdir -p $RPM_BUILD_ROOT/.automount
rm -f $RPM_BUILD_ROOT%{_sbindir}/ctl-amd

# install the default config and map files

bzcat %{SOURCE2} > $RPM_BUILD_ROOT/amd.conf
install -m 600 $RPM_BUILD_ROOT/amd.conf $RPM_BUILD_ROOT%{_sysconfdir}/amd.conf

bzcat %{SOURCE4} > $RPM_BUILD_ROOT/amd
install -m 640 $RPM_BUILD_ROOT/amd $RPM_BUILD_ROOT%{_sysconfdir}/amd.net

rm -f $RPM_BUILD_ROOT/amd.conf
rm -f $RPM_BUILD_ROOT/%{_sysconfdir}/*-sample
rm -f $RPM_BUILD_ROOT/amd

%clean
rm -rf $RPM_BUILD_ROOT

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
/sbin/install-info %{_infodir}/am-utils.info.bz2 %{_infodir}/dir

%preun
%_preun_service amd
if [ $1 = 0 ]; then
   /sbin/install-info --delete %{_infodir}/am-utils.info.bz2 %{_infodir}/dir
fi

%post -n %libname -p /sbin/ldconfig

%postun -n %libname -p /sbin/ldconfig

%files
%defattr(-,root,root)
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

%files -n %libname
%defattr(-,root,root)
%_libdir/*.so.*

%files -n %libnamedevel
%defattr(-,root,root)
%_libdir/*.a
%_libdir/*.so
%_libdir/*.la



