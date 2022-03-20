## Process this file with automake to produce Makefile.in

NULL =

SUBDIRS = data po Alacarte

if BUILD_DOCUMENTATION
SUBDIRS += man
endif

CLEANFILES=

bin_SCRIPTS = alacarte
CLEANFILES += alacarte

DISTCLEANFILES = ChangeLog

alacarte: alacarte.in
	$(AM_V_GEN)sed -e s!\@PYTHON\@!@PYTHON@!	\
	    -e s!\@PYOPTIONS\@!-OOt!			\
	    < $< > $@
alacarte: Makefile

EXTRA_DIST = \
	alacarte.in \
	MAINTAINERS \
	ChangeLog.pre-git

MAINTAINERCLEANFILES = \
	$(GITIGNORE_MAINTAINERCLEANFILES_TOPLEVEL) \
	$(GITIGNORE_MAINTAINERCLEANFILES_MAKEFILE_IN) \
	$(GITIGNORE_MAINTAINERCLEANFILES_M4_LIBTOOL) \
	$(GITIGNORE_MAINTAINERCLEANFILES_M4_GETTEXT) \
	$(srcdir)/ABOUT-NLS \
	$(srcdir)/INSTALL \
	$(srcdir)/config.h.in~ \
	$(srcdir)/configure \
	$(srcdir)/po/.intltool-merge-cache.lock \
	$(srcdir)/py-compile \
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

-include $(top_srcdir)/git.mk
