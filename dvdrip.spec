Name:           dvdrip
Version:        0.98.9
Release:        7%{?dist}
Summary:        Graphical DVD ripping and encoding tool

Group:          Applications/Multimedia
License:        (GPL+ or Artistic) and CC-BY-SA
URL:            http://www.exit1.org/dvdrip/
Source0:        http://www.exit1.org/dvdrip/dist/dvdrip-%{version}.tar.gz
Patch1:         dvdrip-0.98.8-default_config.patch
Patch2:         dvdrip-0.98.9-fping_path.patch
Patch3:         dvdrip-0.98.9-fix_locale.patch
Patch4:         dvdrip-0.98.9-test_Locale.patch
Patch5:         dvdrip-0.98.9-rm-GUI_Pipe.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: perl(ExtUtils::MakeMaker)
BuildRequires: perl(Gtk2) >= 1.121
BuildRequires: perl(Gtk2::Ex::FormFactory) >= 0.65
BuildRequires: perl(Locale::TextDomain) >= 1.16
BuildRequires: perl(Event::ExecFlow) >= 0.62
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

%description
dvd::rip is a full featured DVD copy program. It provides an easy to use but
feature-rich Gtk+ GUI to control almost all aspects of the ripping and
transcoding process. It uses the widely known video processing swissknife
transcode and many other Open Source tools.

%package        master
Summary:        Master node controler for %{name}
Group:          Applications/Multimedia
Requires:       fping
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))

%description    master
The %{name}-master package contains the master node controler for %{name}.


%prep
%setup -q
#%%patch0 -p1 -b .nontplworkaround
# OGM container is deprecated and shound't be used anymore
%patch1 -p1 -b .defaultconfig
%patch2 -p1 -b .path
%patch3 -p1 -b .fix_locale
%patch4 -p1 -b .test_locale
%patch5 -p1 -b .rm-GUI_Pipe

#Remove pre-built mo
find lib/LocaleData -name "*.mo" -exec rm -f {} ';'

#Fix the part that need an X screen at l10n regeneration.

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
#We make the LocaleData
pushd l10n
  make all
popd
#Compilation sometime fails with parallele make

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
# update icon themes
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi 

%postun
# update icon themes
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

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
