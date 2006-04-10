## Process this file with automake to produce Makefile.in

SUBDIRS = po Alacarte

CLEANFILES=

bin_SCRIPTS = alacarte
CLEANFILES += alacarte alacarte-dbg

EXTRA_DIST = $(bin_SCRIPTS)
EXTRA_DIST += intltool-extract.in intltool-merge.in intltool-update.in
DISTCLEANFILES = intltool-extract intltool-merge intltool-update

install-data-local:

@INTLTOOL_DESKTOP_RULE@

desktopdir = $(datadir)/applications
desktop_in_files = alacarte.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
EXTRA_DIST += $(desktop_in_files)
CLEANFILES += $(desktop_DATA)

alacarte: alacarte.in
	sed -e s!\@PYTHON\@!@PYTHON@!		\
	    -e s!\@PYOPTIONS\@!-OOt!		\
	    < $< > $@
alacarte: Makefile

BUILT_SOURCES = alacarte-dbg
alacarte-dbg: alacarte.in
	sed -e s!\@PYTHON\@!@PYTHON@!		\
	    -e s!\@PYOPTIONS\@!!		\
	    < $< > $@
	chmod a+x $@
alacarte: Makefile

EXTRA_DIST += alacarte.in

pkgdata_DATA = alacarte.glade alacarte.svg
EXTRA_DIST += $(pkgdata_DATA)
