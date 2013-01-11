SUBDIRS = icons

@INTLTOOL_DESKTOP_RULE@

desktopdir = $(datadir)/applications
ndesktop_in_files = alacarte.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)

pkgdata_DATA = alacarte.ui launcher-editor.ui

CLEANFILES = $(desktop_DATA)

EXTRA_DIST = $(pkgdata_DATA)

install-data-hook: $(UPDATE_DESKTOP)

uninstall-hook: $(UPDATE_DESKTOP)

