NULL = 

AM_CPPFLAGS = \
	$(ALACARTE_CFLAGS) \
	$(NULL)

BUILT_SOURCES = alacarte.vala.stamp

bin_PROGRAMS = alacarte

alacarte_VALASOURCES = \
	mainwindow.vala \
	config.vala \
	$(NULL)

alacarte_SOURCES = \
	$(alacarte_VALASOURCES:.vala=.c) \
	$(alacarte_VALASOURCES:.vala=.h) \
	$(NULL)

alacarte.vala.stamp: $(alacarte_VALASOURCES)
	$(VALAC) -C --pkg gtk+-2.0 --pkg glib-2.0 --pkg gmodule-2.0 --vapidir=$(top_srcdir)/vapi --pkg libxfce4menu-0.1 --basedir $(top_srcdir)/src $^
	touch $@

alacarte_LDADD = \
	$(ALACARTE_LIBS) \
	$(NULL)

config.vala: config.vala.in
	sed						\
		-e s!\@prefix\@!$(prefix)!		\
		-e s!\@datadir\@!$(datadir)!		\
		-e s!\@pkgdatadir\@!$(pkgdatadir)!	\
		-e s!\@libexecdir\@!$(libexecdir)!	\
		-e s!\@libdir\@!$(libdir)!		\
		-e s!\@PACKAGE\@!$(PACKAGE)!		\
		-e s!\@VERSION\@!$(VERSION)!		\
		< $< > $@
config.vala: Makefile

EXTRA_DIST = \
	$(alacarte_VALASOURCES) \
	alacarte.vala.stamp \
	config.vala.in \
	$(NULL)

CLEANFILES = config.vala

all-local: config.vala

DISTCLEANFILES = \
	$(NULL)

