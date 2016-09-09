Name:           dvdrip
Version:        0.98.11
Release:        10%{?dist}
Summary:        Graphical DVD ripping and encoding tool

Group:          Applications/Multimedia
License:        (GPL+ or Artistic) and CC-BY-SA
URL:            http://www.exit1.org/dvdrip/
Source0:        http://www.exit1.org/dvdrip/dist/dvdrip-%{version}.tar.gz
Patch3:         dvdrip-0.98.9-fix_locale.patch
Patch5:         dvdrip-0.98.9-rm-GUI_Pipe.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(Gtk2) >= 1.121
BuildRequires: perl(Gtk2::Ex::FormFactory) >= 0.65
BuildRequires: perl(Locale::TextDomain) >= 1.16
BuildRequires: perl(Event::ExecFlow) >= 0.64
BuildRequires: perl(Event::RPC) >= 0.89
BuildRequires: perl(AnyEvent) >= 1.02
BuildRequires: desktop-file-utils
BuildRequires: gettext
Requires: ImageMagick
#Needed for transcoding
Requires: transcode >= 0.6.13
Requires: %{name}-master = %{version}-%{release}
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

#Optionals
# subtitleripper, vcdimager, lsdvd, xvid4conf
# ogmtools is deprecated since ogm/ogg container (for video) is broken
# according to ffmpeg/MPlayer developers
# -master Requires: fping

#Filtering
%{?filter_setup:
%filter_from_requires /perl(Video::DVDRip::Task)/d
%filter_setup
}


%description
dvd::rip is a full featured DVD copy program. It provides an easy to use but
feature-rich Gtk+ GUI to control almost all aspects of the ripping and
transcoding process. It uses the widely known video processing swissknife
transcode and many other Open Source tools.

%package        master
Summary:        Master node controller for %{name}
Group:          Applications/Multimedia
Requires:       fping
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description    master
The %{name}-master package contains the master node controller for %{name}.


%prep
%setup -q
%patch3 -p1 -b .fix_locale
%patch5 -p1

# Fix encoding issues:
%define docfiles Changes Changes.0.46 COPYRIGHT Credits README TODO lib/Video/DVDRip/translators.txt
for txtfile in %docfiles ; do
    iconv -f iso-8859-1 -t UTF8 $txtfile -o $txtfile.utf8
    touch -r $txtfile $txtfile.utf8
    mv -f $txtfile.utf8 $txtfile
done

# Fix permission:
chmod -x lib/Video/DVDRip/Cluster/Webserver.pm

# Remove the included perl modules. The ones 
# installed in the system will be used instead:
rm -fr perl-modules

%build
# We first build dvdrip-progress.c dvdrip-splitpipe.c with our flags
# The compilation won't be done twince as the binaries are already here.
# Note that only theses two make the package arch dependant (not the perl side).
pushd src
make CFLAGS="$RPM_OPT_FLAGS" %{?_smp_mflags}
popd

%{__perl} Makefile.PL INSTALLDIRS=vendor
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make pure_install PERL_INSTALL_ROOT=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name '*.bs' -a -size 0 -exec rm -f {} ';'
find $RPM_BUILD_ROOT -depth -type d -exec rmdir {} 2>/dev/null ';'
chmod -R u+w $RPM_BUILD_ROOT/*

desktop-file-install --vendor "" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --mode 644 \
  --add-category="X-AudioVideoImport" \
  %{name}.desktop

#Install icon
mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps
install -pm 0644 dvdrip-icon-hq.svg $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

#Fix for locale
mkdir -p $RPM_BUILD_ROOT%{_datadir}/locale
mv $RPM_BUILD_ROOT%{perl_vendorlib}/LocaleData/* $RPM_BUILD_ROOT%{_datadir}/locale
rmdir $RPM_BUILD_ROOT%{perl_vendorlib}/LocaleData
%find_lang video.dvdrip

%clean
rm -rf $RPM_BUILD_ROOT

%check
%{?_with_test:make test}


%post
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files
%defattr(-,root,root,-)
%doc %docfiles lib/Video/DVDRip/license.txt
%exclude %{_bindir}/%{name}-master
%{_bindir}/%{name}*
%dir %{perl_vendorlib}/Video
%dir %{perl_vendorlib}/Video/DVDRip
%{perl_vendorlib}/Video/DVDRip/GUI
%{_datadir}/applications/*%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg
%{_mandir}/man1/*.1*
%{_mandir}/man3/*.3*

%files master -f video.dvdrip.lang
%defattr(-,root,root,-)
%{_bindir}/%{name}-master
%dir %{perl_vendorlib}/Video
%dir %{perl_vendorlib}/Video/DVDRip
%exclude %{perl_vendorlib}/Video/DVDRip/GUI
%{perl_vendorlib}/Video/DVDRip/
%{perl_vendorlib}/Video/DVDRip.pm


%changelog
* Fri Sep 09 2016 Sérgio Basto <sergio@serjux.com> - 0.98.11-10
- Rebuild for Perl-5.24

* Sun Aug 31 2014 Sérgio Basto <sergio@serjux.com> - 0.98.11-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Oct 08 2013 Nicolas Chauvet <kwizart@gmail.com> - 0.98.11-8
- Rebuilt

* Sun Oct 07 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.98.11-7
- Rebuilt for perl

* Wed Feb 08 2012 Nicolas Chauvet <kwizart@gmail.com> - 0.98.11-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Oct 03 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.98.11-5
- Filter perl(Video::DVDRip::Task)

* Tue Sep 27 2011 Nicolas Chauvet <kwizart@gmail.com> - 0.98.11-3
- Rebuilt for perl

* Tue Aug 24 2010 Nicolas Chauvet <kwizart@gmail.com> - 0.98.11-2
- rebuilt for new perl

* Tue May 11 2010 Orcan Ogetbil <oged[DOT]fedora[AT]gmail[DOT]com> - 0.98.11-1
- Update to 0.98.11
- No need to rebuild locale data as this is no longer required in the guidelines
- Update the post* scriptlets

* Wed Dec 30 2009 Nicolas Chauvet <kwizart@fedoraproject.org> - 0.98.10-4
- Rebuild for perl
- Do not produce weird file because of the patch command.

* Fri Oct 23 2009 Orcan Ogetbil <oged[DOT]fedora[AT]gmail[DOT]com> - 0.98.10-3
- Update desktop file according to F-12 FedoraStudio feature

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 0.98.10-2
- rebuild for new F11 features

* Mon Feb 23 2009 kwizart < kwizart at gmail.com > - 0.98.10-1
- Update to 0.98.10 -  Some of our patches got merged upstream.
  http://www.exit1.org/dvdrip/changes.cipp?version=0.98.10
* Wed Feb  4 2009 kwizart < kwizart at gmail.com > - 0.98.9-8
- Backport a patch for transcode110
* Mon Feb  2 2009 kwizart < kwizart at gmail.com > - 0.98.9-7
- Fix directory ownership (rpmfusion #354)
* Fri Dec 12 2008 kwizart < kwizart at gmail.com > - 0.98.9-6
- Split dvdrip-master
* Wed Dec 10 2008 kwizart < kwizart at gmail.com > - 0.98.9-5
- Update BuildRequirement as described in Makefile.PL
- Fix Make test
* Tue Dec  9 2008 Orcan Ogetbil < orcanbahri [AT] yahoo [DOT] com > - 0.98.9-4
- Fix encoding and permission issues
- Remove the packaged perl modules during %%prep.
- Minor SPEC file cleanup.
- Comment out unnecessary BR's.
- Comment out the nontplworkaround patch.
* Tue Dec  9 2008 kwizart < kwizart at gmail.com > - 0.98.9-3
- Fix DataLocale regenerated
- Fix the License
* Sat Nov 29 2008 kwizart < kwizart at gmail.com > - 0.98.9-2
- Fix fping path
* Thu Oct  9 2008 kwizart < kwizart at gmail.com > - 0.98.9-1
- Update to 0.98.9
* Mon Sep 29 2008 kwizart < kwizart at gmail.com > - 0.98.8-3
- Remove non-mandatory requirement.
* Thu Sep 11 2008 kwizart < kwizart at gmail.com > - 0.98.8-2
- Remove optionals tools
* Wed Apr 30 2008 kwizart < kwizart at gmail.com > - 0.98.8-1
- Initial package for RPM Fusion
