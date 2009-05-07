NULL = 

SUBDIRS = \
	data \
	src \
	po \
	vapi \
	$(NULL)

alacartedocdir = ${prefix}/doc/alacarte
alacartedoc_DATA = \
	README \
	COPYING \
	AUTHORS \
	INSTALL \
	NEWS \
	$(NULL)

EXTRA_DIST = \
	$(alacartedoc_DATA) \
	gitlog-to-changelog \
	intltool-extract.in \
	intltool-merge.in \
	intltool-update.in \
	MAINTAINERS \
	$(NULL)

DISTCLEANFILES = \
	intltool-extract \
	intltool-merge \
	intltool-update
	po/.intltool-merge-cache \
	$(NULL)

dist-hook: gen-ChangeLog

gen_start_date = 2009-05-04
.PHONY: gen-ChangeLog
gen-ChangeLog:
	if test -d .git; then						\
	  $(top_srcdir)/gitlog-to-changelog				\
	    --since=$(gen_start_date) > $(distdir)/cl-t;		\
	  rm -f $(distdir)/ChangeLog;					\
	  mv $(distdir)/cl-t $(distdir)/ChangeLog;			\
	fi

