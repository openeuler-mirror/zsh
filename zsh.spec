%define _bindir /bin

Name:                 zsh
Version:              5.7.1
Release:              6
Summary:              A shell designed for interactive use
License:              MIT
URL:                  http://zsh.sourceforge.net
Source0:              https://downloads.sourceforge.net/%{name}/%{name}-%{version}.tar.xz

# There are five startup files that zsh will read commands from
# http://zsh.sourceforge.net/Intro/intro_3.html
Source1:              zlogin
Source2:              zlogout
Source3:              zprofile
Source4:              zshrc
Source5:              zshenv
Source6:              dotzshrc

BuildRequires:        autoconf coreutils gawk gdbm-devel libcap-devel make
BuildRequires:        ncurses-devel pcre-devel sed texinfo hostname gcc

Requires(post):       info grep
Requires(preun):      info
Requires(postun):     coreutils grep

Provides:             /bin/zsh

Patch0000: 0225-44345-fix-wordcode-traversal-where-without-a-followi.patch
Patch0001: CVE-2019-20044.patch
Patch0002: backport-CVE-2021-45444-1.patch
Patch0003: backport-CVE-2021-45444-2.patch


%description
The zsh is a shell designed for interactive use, and it is also a powerful scripting language. Many of
the useful features of bash, ksh, and tcsh were incorporated into zsh. It can match files by file extension
without running an external program, share command history with any shell, and more.

%package              help
Summary:              zsh shell manual in html format
BuildArch:            noarch

Provides:             zsh-html
Obsoletes:            zsh-html

%description          help
This package contains the zsh manual in html format.

%prep
%autosetup -p1
autoreconf -fiv

sed -e 's|^\.NOTPARALLEL|#.NOTPARALLEL|' -i 'Config/defs.mk.in'

%build
%undefine _strict_symbol_defs_build

export LIBLDFLAGS='-z lazy'

%configure --enable-etcdir=%{_sysconfdir} --with-tcsetpgrp --enable-maildir-support --enable-pcre

make -C Src headers
make -C Src -f Makemod zsh{path,xmod}s.h version.h
%make_build all html

%check
make check

%install
%make_install install.info fndir=%{_datadir}/%{name}/%{version}/functions sitefndir=%{_datadir}/%{name}/site-functions \
                           scriptdir=%{_datadir}/%{name}/%{version}/scripts sitescriptdir=%{_datadir}/%{name}/scripts \
                           runhelpdir=%{_datadir}/%{name}/%{version}/help

rm -f $RPM_BUILD_ROOT%{_bindir}/zsh-%{version}
rm -f $RPM_BUILD_ROOT%{_infodir}/dir

install -d ${RPM_BUILD_ROOT}%{_sysconfdir}
for i in %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5}; do
    install -m 644 $i $RPM_BUILD_ROOT%{_sysconfdir}/"${i##*/}"
done

install -d $RPM_BUILD_ROOT%{_sysconfdir}/skel
install -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_sysconfdir}/skel/.zshrc

for i in checkmail harden run-help zcalc zkbd; do
    sed -i -e 's!/usr/local/bin/zsh!%{_bindir}/zsh!' $RPM_BUILD_ROOT%{_datadir}/zsh/%{version}/functions/$i
    chmod +x $RPM_BUILD_ROOT%{_datadir}/zsh/%{version}/functions/$i
done

%post
if [ "$1" = 1 ]; then
  if [ ! -f %{_sysconfdir}/shells ] ; then
    echo "%{_bindir}/%{name}" > %{_sysconfdir}/shells
    echo "/bin/%{name}" >> %{_sysconfdir}/shells
  else
    grep -q "^%{_bindir}/%{name}$" %{_sysconfdir}/shells || echo "%{_bindir}/%{name}" >> %{_sysconfdir}/shells
    grep -q "^/bin/%{name}$" %{_sysconfdir}/shells || echo "/bin/%{name}" >> %{_sysconfdir}/shells
  fi
fi

if [ -f %{_infodir}/zsh.info.gz ]; then
/sbin/install-info %{_infodir}/zsh.info.gz %{_infodir}/dir \
  --entry="* zsh: (zsh).                        An enhanced bourne shell."
fi

%preun
if [ "$1" = 0 ] ; then
    if [ -f %{_infodir}/zsh.info.gz ]; then
    /sbin/install-info --delete %{_infodir}/zsh.info.gz %{_infodir}/dir \
      --entry="* zsh: (zsh).                    An enhanced bourne shell."
    fi
fi

%postun
if [ "$1" = 0 ] && [ -f %{_sysconfdir}/shells ] ; then
  sed -i '\!^%{_bindir}/%{name}$!d' %{_sysconfdir}/shells
  sed -i '\!^/bin/%{name}$!d' %{_sysconfdir}/shells
fi

%files
%doc README LICENCE Etc/* FEATURES MACHINES NEWS
%attr(755,root,root) %{_bindir}/zsh

%{_libdir}/zsh

%config(noreplace) %{_sysconfdir}/skel/.z*
%config(noreplace) %{_sysconfdir}/z*
%{_datadir}/zsh

%files help
%doc Doc/*.html
%{_mandir}/*/*
%{_infodir}/*

%changelog
* Tue Mar 1 2022 wangjie <wangjie375@h-partners.com> - 5.7.1-6
- Type: CVE
- ID: CVE-2021-45444
- SUG: NA
- DESC: fix CVE-2021-45444

* Wed Jun 24 2020 xuping <xuping21@huawei.com> - 5.7.1-5
- Type:cves
- ID:CVE-2019-20044
- SUG:NA
- DESC:fix CVE-2019-20044

* Thu Feb 6 2020 openEuler Buildteam <buildteam@openeuler.org> - 5.7.1-4
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:add buildrequires of gcc and make

* Mon Feb 3 2020 openEuler Buildteam <buildteam@openeuler.org> - 5.7.1-3
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:fix missing files 

* Wed Jan 15 2020 openEuler Buildteam <buildteam@openeuler.org> - 5.7.1-2
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:revise buildrequires

* Wed Jan 8 2020 openEuler Buildteam <buildteam@openeuler.org> - 5.7.1-1
- Type:enhancement
- ID:NA
- SUG:NA
- DESC:update version to 5.7.1

* Wed Dec 18 2019 jiangchuangang <jiangchuangang@huawei.com> - 5.6.2-3
- Type:enhancement
- ID:NA
- SUG:restart
- DESC:Synchronize a patch

* Wed Sep 18 2019 dongjian <dongjian13@huawei.com> - 5.6.2-2
- modify summary
