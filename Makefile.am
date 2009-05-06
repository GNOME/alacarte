NULL = 

#Build in these directories:

SUBDIRS = \
	data \
	src \
	po \
	vapi \
	$(NULL)

CLEANFILES=

alacartedocdir = ${prefix}/doc/alacarte
alacartedoc_DATA = \
	ChangeLog.pre-git \
	ChangeLog \
	README \
	COPYING \
	AUTHORS \
	INSTALL \
	NEWS \
	$(NULL)

EXTRA_DIST = \
	$(alacartedoc_DATA) \
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
	ChangeLog \
	$(NULL)

ChangeLog:
	@echo Creating $@
	@if test -d "$(srcdir)/.git"; then \
	  (GIT_DIR=$(top_srcdir)/.git ./missing --run git log git-migration.. --stat -M -C --name-status  --date=short --no-color) | fmt --split-only > $@.tmp \
	  && mv -f $@.tmp $@ \
	  || ($(RM) $@.tmp; \
	      echo Failed to generate ChangeLog, your ChangeLog may be outdated >&2; \
	      (test -f $@ || echo git-log is required to generate this file >> $@)); \
	else \
	  test -f $@ || \
	  (echo A git checkout and git-log is required to generate ChangeLog >&2 && \
	   echo A git checkout and git-log is required to generate this file >> $@); \
	fi

.PHONY: ChangeLog

