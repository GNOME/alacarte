SUBDIRS = icons

desktopdir = $(datadir)/applications
desktop_in_files = alacarte.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

pkgdata_DATA = alacarte.ui

CLEANFILES = $(desktop_DATA)

EXTRA_DIST = $(pkgdata_DATA)

install-data-hook: $(UPDATE_DESKTOP)

uninstall-hook: $(UPDATE_DESKTOP)

