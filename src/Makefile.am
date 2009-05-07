NULL = 

QUIET_GEN = $(Q:@=@echo ' GEN '$@;)

AM_CPPFLAGS = \
	$(ALACARTE_CFLAGS) \
	$(NULL)

bin_PROGRAMS = \
	alacarte \
	$(NULL)

BUILT_SOURCES = alacarte.vala.stamp

alacarte_VALASOURCES = \
	mainwindow.vala \
	config.vala \
	$(NULL)

alacarte_SOURCES = \
	alacarte.vala.stamp \
	$(alacarte_VALASOURCES:.vala=.c) \
	$(NULL)

alacarte.vala.stamp: $(alacarte_VALASOURCES)
	$(VALAC) -C --pkg gtk+-2.0 --pkg glib-2.0 --pkg gmodule-2.0 --vapidir=$(srcdir)/../vapi --pkg libxfce4menu-0.1 $^
	touch $@

alacarte_LDADD = \
	$(ALACARTE_LIBS) \
	$(NULL)

EXTRA_DIST = \
	$(alacarte_VALASOURCES) \
	alacarte.vala.stamp \
	config.vala.in \
	$(NULL)

MAINTAINERCLEANFILES = \
	$(alacarte_VALASOURCES:.vala=.c) \
	$(NULL)

config.vala: config.vala.in
	$(QUIET_GEN)sed						\
		-e s!\@prefix\@!$(prefix)!		\
		-e s!\@datadir\@!$(datadir)!		\
		-e s!\@pkgdatadir\@!$(pkgdatadir)!	\
		-e s!\@libexecdir\@!$(libexecdir)!	\
		-e s!\@libdir\@!$(libdir)!		\
		-e s!\@PACKAGE\@!$(PACKAGE)!		\
		-e s!\@VERSION\@!$(VERSION)!		\
		< $< > $@

CLEANFILES = \
	config.vala \
	$(NULL)

