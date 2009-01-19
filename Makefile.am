## Process this file with automake to produce Makefile.in

SUBDIRS = data po Alacarte

CLEANFILES=

bin_SCRIPTS = alacarte
CLEANFILES += alacarte

alacarte: alacarte.in
	sed -e s!\@PYTHON\@!@PYTHON@!		\
	    -e s!\@PYOPTIONS\@!-OOt!		\
	    < $< > $@
alacarte: Makefile

EXTRA_DIST = alacarte.in
