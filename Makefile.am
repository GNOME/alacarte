## Process this file with automake to produce Makefile.in

SUBDIRS = data po Alacarte

CLEANFILES=

bin_SCRIPTS = alacarte
CLEANFILES += alacarte

EXTRA_DIST = intltool-extract.in intltool-merge.in intltool-update.in
DISTCLEANFILES = intltool-extract intltool-merge intltool-update

install-data-local:

alacarte: alacarte.in
	sed -e s!\@PYTHON\@!@PYTHON@!		\
	    -e s!\@PYOPTIONS\@!-OOt!		\
	    < $< > $@
alacarte: Makefile

EXTRA_DIST += alacarte.in
