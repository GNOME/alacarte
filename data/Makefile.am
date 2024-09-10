SUBDIRS = icons

%.desktop: %.desktop.in
	$(AM_V_GEN) $(MSGFMT) --desktop --template $< -o $@-t \
		-d $(top_srcdir)/po && mv $@-t $@

desktopdir = $(datadir)/applications
desktop_in_files = alacarte.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)

%.xml:	%.xml.in
	$(AM_V_GEN) $(MSGFMT) --xml --template $< -d $(top_srcdir)/po -o $@

metainfodir = $(datadir)/metainfo
metainfo_in_files = org.gnome.alacarte.metainfo.xml.in
metainfo_DATA = $(metainfo_in_files:.xml.in=.xml)

pkgdata_DATA = alacarte.ui launcher-editor.ui directory-editor.ui

CLEANFILES = \
	$(desktop_DATA) \
	$(metainfo_DATA) \
	$(NULL)

EXTRA_DIST = \
	$(desktop_in_files) \
	$(metainfo_in_files) \
	$(pkgdata_DATA) \
	$(NULL)

install-data-hook: $(UPDATE_DESKTOP)

uninstall-hook: $(UPDATE_DESKTOP)

-include $(top_srcdir)/git.mk
