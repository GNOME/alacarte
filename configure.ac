dnl -*- Mode: autoconf -*-
dnl Process this file with autoconf to produce a configure script.
AC_PREREQ(2.53)
AC_INIT(alacarte, 3.7.90, http://bugzilla.gnome.org/enter_bug.cgi?product=alacarte)
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])
AC_CONFIG_SRCDIR(alacarte.in)
AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE([1.7 no-dist-gzip dist-xz])
AM_MAINTAINER_MODE

dnl put the ACLOCAL flags in the makefile
ACLOCAL="$ACLOCAL $ACLOCAL_FLAGS"


GETTEXT_PACKAGE=alacarte
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.40.0])

AM_PATH_PYTHON_VERSION(2.7, 2.7.0, 2.6, 2.6.0, 2.5, 2.5.0, 2.4, 2.4.0)

PKG_CHECK_MODULES(ALACARTE, libgnome-menu-3.0 >= 3.5.3 pygobject-3.0)

AC_CONFIG_FILES([
        Makefile
        po/Makefile.in
        Alacarte/Makefile
        data/alacarte.desktop.in
	data/Makefile
	data/icons/Makefile
        ])

AC_OUTPUT

