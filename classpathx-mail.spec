# Copyright (c) 2000-2005, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define jmailver 1.3.1
%define inetlibver 1.1.1

Name:           classpathx-mail
Version:        1.1.1
Release:        9.4%{?dist}
Epoch:          0
Summary:        GNU JavaMail(tm)

Group:          System Environment/Libraries
# Classpath library exception
License:        GPLv2+ with exceptions
URL:            http://www.gnu.org/software/classpathx/
Source0:        http://ftp.gnu.org/gnu/classpathx/mail-%{version}.tar.gz
Source1:        http://ftp.gnu.org/gnu/classpath/inetlib-1.1.1.tar.gz
# see bz157685
Patch1:         %{name}-docbuild.patch
Patch2:         %{name}-add-inetlib.patch
Patch3:         %{name}-remove-inetlib.patch
# see bz157685
Patch4:         classpath-inetlib-docbuild.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
BuildRequires:  jpackage-utils >= 0:1.5
BuildRequires:  ant
BuildRequires:  jaf >= 0:1.0
BuildRequires:  %{_bindir}/perl
BuildRequires:  jce
#BuildRequires:  java-sasl
Requires:       jaf >= 0:1.0
Requires:       jce
Requires:       java-sasl
Requires(preun):  %{_sbindir}/update-alternatives
Requires(post):  %{_sbindir}/update-alternatives
Provides:       javamail = 0:%{jmailver}
# For backward compatibility with former monolithic subpackages
Provides:       javamail-monolithic = 0:%{jmailver}
Obsoletes:      classpathx-mail-monolithic <= 0:1.1.1_2jpp_6rh

%description
GNU JavaMail(tm) is a free implementation of the JavaMail API.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Provides:       javamail-javadoc = 0:%{jmailver}
BuildRequires:  java-javadoc, jaf-javadoc

%description    javadoc
%{summary}.


%prep
%setup -q -n mail-%{version}
%patch1 -p0
%patch2 -p0
%patch3 -p0
rm -f libmail.so
gzip -dc %{SOURCE1} | tar -xf -
pushd inetlib-%{inetlibver}
%patch4 -p0
  mkdir -p source/org/jpackage/mail
  mv source/gnu/inet source/org/jpackage/mail
popd
# assume no filename contains spaces
perl -p -i -e 's/gnu(.)inet/org${1}jpackage${1}mail${1}inet/' `grep gnu.inet -lr *`


%build
# build inetlib
pushd inetlib-%{inetlibver}
  export CLASSPATH=%(build-classpath jce sasl)
  ant -Dj2se.apidoc=%{_javadocdir}/java inetlib.jar doc
popd
mkdir classes
cp -r inetlib-%{inetlibver}/classes/org classes
# build mail
export CLASSPATH=%(build-classpath activation)
ant \
  -Dj2se.apidoc=%{_javadocdir}/java \
  -Djaf.apidoc=%{_javadocdir}/jaf \
  dist javadoc

# build monolithic
mkdir monolithic
pushd monolithic
for jar in gnumail gnumail-providers ; do jar xf ../$jar.jar; done
rm -f META-INF/MANIFEST.MF
jar cf ../monolithic.jar *
popd
rm -Rf monolithic


%install
rm -rf $RPM_BUILD_ROOT

install -dm 755 $RPM_BUILD_ROOT%{_javadir}/classpathx-mail

# API
install -pm 644 gnumail.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-api-%{version}.jar
ln -s mail-%{jmailver}-api-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-api.jar
ln -s mail-%{jmailver}-api.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mailapi.jar

# Providers
install -pm 644 gnumail-providers.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-providers-%{version}.jar
ln -s mail-%{jmailver}-providers-%{version}.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/mail-%{jmailver}-providers.jar
ln -s mail-%{jmailver}-providers.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/providers.jar
for prov in imap nntp pop3 smtp ; do
  ln -s mail-%{jmailver}-providers.jar \
    $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/$prov-%{jmailver}.jar
  ln -s providers.jar $RPM_BUILD_ROOT%{_javadir}/classpathx-mail/$prov.jar
done

install -pm 644 monolithic.jar \
  $RPM_BUILD_ROOT%{_javadir}/classpathx-mail-%{jmailver}-monolithic-%{version}.jar
ln -s classpathx-mail-%{jmailver}-monolithic-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar
touch $RPM_BUILD_ROOT%{_javadir}/javamail.jar # for %ghost

install -dm 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{jmailver}
cp -pR docs/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{jmailver}
ln -s %{name}-%{jmailver} $RPM_BUILD_ROOT%{_javadocdir}/%{name} # ghost symlink

%clean
rm -rf $RPM_BUILD_ROOT


%triggerpostun -- classpathx-mail-monolithic <= 0:1.1.1-1jpp
# Remove file from old monolithic subpackage
rm -f %{_javadir}/javamail.jar
# Recreate the link as update-alternatives could not do it
ln -s %{_sysconfdir}/alternatives/javamail %{_javadir}/javamail.jar

%post
%{_sbindir}/update-alternatives --install %{_javadir}/javamail.jar javamail %{_javadir}/classpathx-mail-1.3.1-monolithic.jar 010301

%preun
if [ "$1" = "0" ]; then
    %{_sbindir}/update-alternatives --remove javamail %{_javadir}/classpathx-mail-1.3.1-monolithic.jar
fi

%files
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog COPYING
%dir %{_javadir}/classpathx-mail
%{_javadir}/classpathx-mail/mail-%{jmailver}-api-%{version}.jar
%{_javadir}/classpathx-mail/mail-%{jmailver}-api.jar
%{_javadir}/classpathx-mail/mailapi.jar
%{_javadir}/classpathx-mail/mail-%{jmailver}-providers-%{version}.jar
%{_javadir}/classpathx-mail/mail-%{jmailver}-providers.jar
%{_javadir}/classpathx-mail/providers.jar
%{_javadir}/classpathx-mail/imap-%{jmailver}.jar
%{_javadir}/classpathx-mail/imap.jar
%{_javadir}/classpathx-mail/nntp-%{jmailver}.jar
%{_javadir}/classpathx-mail/nntp.jar
%{_javadir}/classpathx-mail/pop3-%{jmailver}.jar
%{_javadir}/classpathx-mail/pop3.jar
%{_javadir}/classpathx-mail/smtp-%{jmailver}.jar
%{_javadir}/classpathx-mail/smtp.jar
# Monolithic jar
%{_javadir}/classpathx-mail-%{jmailver}-monolithic-%{version}.jar
%{_javadir}/classpathx-mail-%{jmailver}-monolithic.jar
%ghost %{_javadir}/javamail.jar

%files javadoc
%defattr(644,root,root,755)
%{_javadocdir}/%{name}-%{jmailver}
%{_javadocdir}/%{name}

%changelog
* Mon Jan 25 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.1.1-9.4
- Fix non-standard group usage.
- Fix macro in changelog usage.

* Thu Jan 7 2010 Alexander Kurtakov <akurtako@redhat.com> 0:1.1.1-9.3
- Drop gcj_support. 
- Replace inetlib tarball with the upstream one.

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 0:1.1.1-9.2
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.1.1-9.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0:1.1.1-8.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 23 2008 David Walluck <dwalluck@redhat.com> 0:1.1.1-7.1
- reintroduce release numbering scheme that has been missing since -5

* Thu Oct 23 2008 David Walluck <dwalluck@redhat.com> 0:1.1.1-7
- remove javadoc scriptlets (Resolves: #205191)
- replace /usr/sbin with %%{_sbindir}

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0:1.1.1-6
- drop repotag
- fix license tag

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0:1.1.1-5jpp.3
- Autorebuild for GCC 4.3

* Fri Mar 16 2007 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:1.1.1-4jpp.3
- Remove gnu-crypto build requirement.

* Mon Sep 11 2006 Fernando Nasser <fnasser@redhat.com> 0:1.1.1-4jpp.2
- Add missing Requires for commands used in javadoc post/postun scripts

* Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> 0:1.1.1-4jpp.1
- Merge with upstream

* Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> 0:1.1.1-4jpp
- Add postun
- Fix javadoc unversioned link handling

* Tue Jul 25 2006 Fernando Nasser <fnasser@redhat.com> 0:1.1.1-3jpp_1fc
- Merge with upstream

* Tue Jul 25 2006 Fernando Nasser <fnasser@redhat.com> 0:1.1.1-3jpp
- Add trigger to remove old javamail.jar file from monolithic subpackage
- Fold -monolithic subpackage into main package to simplify dependency
  specifications in other packages
- Require update-alternatives to be present during install/uninstall
- Fix versioned providers jar file name
- Install/remove alternatives in the monolithic subpackage
- Fix providers jar names
- Add AOT bits

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:1.0-4jpp_7fc
- Rebuilt

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com>
- rebuild

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:1.0-4jpp_5fc
- stop the scriptlet spew

* Wed Dec 21 2005 Jesse Keating <jkeating@redhat.com> - 0:1.0-4jpp_4fc
- rebuilt

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Mon Nov 14 2005 Fernando Nasser <fnasser@redhat.com> 0:1.1.1-2jpp
- Change handling of alternatives to 6-digit scheme
- Change handling of javadocs to new %%{_netsharedpath} and 
  "/usr/share mounted read only" friendly scheme

* Fri Nov 11 2005 Vadim Nasardinov <vadimn@redhat.com> - 0:1.0-4jpp_3fc
- BZ 157685

* Thu Jul 28 2005 Fernando Nasser <fnasser@redhat.com> 0:1.1.1-1jpp
- Upgrade to Classpathx-Mail 1.1.1

* Fri Jun 17 2005 Fernando Nasser <fnasser@redhat.com> 0:1.1-1jpp
- Upgrade to Classpathx-Mail 1.1
- Add fix for handling of Mime multipart messages from Archit Shah
  From Gary Benson <gbenson@redhat.com>:
- Add a javamail-monolithic equivalent.

* Wed Jun  1 2005 Gary Benson <gbenson@redhat.com> 0:1.0-4jpp_2fc
- Fix location of monolithic jarfile.

* Tue May 31 2005 Gary Benson <gbenson@redhat.com> 0:1.0-4jpp_1fc
- Remove now-unnecessary workaround for #132524.
- Upgrade to 1.0-4jpp.
- Add a javamail-monolithic equivalent.

* Mon May 02 2005 Jason Corley <jason.corley@gmail.com> 0:1.0-4jpp
- Rebuild

* Tue Jan 11 2005 Gary Benson <gbenson@redhat.com> 0:1.0-3jpp_1fc
- Sync with RHAPS.

* Fri Nov 12 2004 Fernando Nasser <fnasser@redhat.com> 0:1.0-3jpp_1rh
- Merge with upstream to get version that does not require inetlib.

* Thu Nov  4 2004 Gary Benson <gbenson@redhat.com> 0:1.0-2jpp_1fc
- Build into Fedora.

* Thu Oct 28 2004 Thomas Fitzsimmons <fitzsim@redhat.com> 0:1.0-3jpp
- Don't require classpath-inetlib.
- Require java-sasl and jce.
- Replace gnu.inet references with org.jpackage.mail.inet.
- Build inetlib.
- Include inetlib in providers.jar.

* Sat Jul  3 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-2jpp
- Require classpath-inetlib and jaf.

* Tue Jun 15 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.0-1jpp
- First build.
