#Module-Specific definitions
%define mod_name mod_ftp
%define mod_conf B41_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Apache module for FTP support
Name:		apache-%{mod_name}
Version:	0.9.4
Release: 	%mkrel 2
Group:		System/Servers
License:	Apache License
URL:		http://httpd.apache.org/mod_ftp/
Source0:	http://httpd.apache.org/dev/dist/mod_ftp/httpd-%{mod_name}-%{version}.tar.gz
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file
BuildRequires:	libtool
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
mod_ftp is a FTP Protocol module to serve httpd content over the FTP protocol
(whereever the HTTP protocol could also be used). It provides both RETR/REST
retrieval and STOR/APPE upload, using the same user/permissions model as httpd
(so it shares the same security considerations as mod_dav plus mod_dav_fs).

%prep

%setup -q -n httpd-%{mod_name}-%{version}

for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

cp %{SOURCE1} %{mod_conf}

# fix defaults
perl -pi -e "s|\@\@FTPPort\@\@|2121|g" %{mod_conf}
perl -pi -e "s|\@exp_ftpdocsdir\@|/var/www/ftp|g" %{mod_conf}
perl -pi -e "s|\@rel_logfiledir\@|/var/log/httpd|g" %{mod_conf}
perl -pi -e "s|\@exp_runtimedir\@/ssl_scache|/var/cache/httpd/mod_ssl/ssl_scache|g" %{mod_conf}
perl -pi -e "s|\@exp_runtimedir\@/ssl_mutex|/var/cache/httpd/mod_ssl/mod_ssl_mutex|g" %{mod_conf}
perl -pi -e "s|\@exp_sysconfdir\@/htpasswd\.users|%{_sysconfdir}/httpd/conf/htpasswd\.ftpusers|g" %{mod_conf}
perl -pi -e "s|\@exp_sysconfdir\@/server\.crt|/etc/pki/tls/certs/localhost\.crt|g" %{mod_conf}
perl -pi -e "s|\@exp_sysconfdir\@/server\.key|/etc/pki/tls/private/localhost\.key|g" %{mod_conf}


# fix the manual
for i in `find docs -name "*.html.en"`; do
    new_name=`echo $i | sed -e "s/.html.en/.html/g"`
    mv -f $i $new_name
done

find docs -name "*.xml*" | xargs rm -f

# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build
export APXS=%{_sbindir}/apxs

sh ./configure.apxs

%make

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}/var/www/ftp

libtool --mode=install %{_bindir}/install modules/ftp/mod_ftp.la %{buildroot}%{_libdir}/apache-extramodules/mod_ftp.la
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

# cleanup
rm -f %{buildroot}%{_libdir}/apache-extramodules/*.*a

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CHANGES-FTP LICENSE-FTP NOTICE-FTP README-FTP STATUS-FTP docs/manual/ftp docs/manual/mod
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/*.so
%dir /var/www/ftp
