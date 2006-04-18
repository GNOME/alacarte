## Process this file with automake to produce Makefile.in

SUBDIRS = po Alacarte

CLEANFILES=

bin_SCRIPTS = alacarte
CLEANFILES += alacarte

EXTRA_DIST = intltool-extract.in intltool-merge.in intltool-update.in
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

EXTRA_DIST += alacarte.in

pkgdata_DATA = alacarte.glade logo.svg
EXTRA_DIST += $(pkgdata_DATA)

icondir = $(datadir)/icons/hicolor/22x22/apps
icon_DATA = alacarte.png
EXTRA_DIST += $(icon_DATA)
svgicondir = $(datadir)/icons/hicolor/scalable/apps
svgicon_DATA = alacarte.svg
EXTRA_DIST += $(svgicon_DATA)

gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

install-data-hook:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating Gtk icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated. After install, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi
