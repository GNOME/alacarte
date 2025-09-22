dnl -*- Mode: autoconf -*-
dnl Process this file with autoconf to produce a configure script.
AC_PREREQ(2.53)
AC_INIT(alacarte, 3.58.0, https://gitlab.gnome.org/GNOME/alacarte/-/issues)
m4_ifdef([AM_SILENT_RULES],[AM_SILENT_RULES([yes])])
AC_CONFIG_SRCDIR(alacarte.in)
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_AUX_DIR([build-aux])
AM_INIT_AUTOMAKE([1.16.4 no-dist-gzip dist-xz tar-ustar -Wno-portability])
AM_MAINTAINER_MODE

AM_GNU_GETTEXT([external])
AM_GNU_GETTEXT_VERSION([0.19.8])
AM_GNU_GETTEXT_REQUIRE_VERSION([0.19.8])

GETTEXT_PACKAGE=alacarte
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], ["$GETTEXT_PACKAGE"], [Gettext package])

AM_PATH_PYTHON(3.7)

PKG_CHECK_MODULES(ALACARTE, libgnome-menu-3.0 >= 3.5.3 pygobject-3.0)

AC_ARG_ENABLE(documentation,
              AS_HELP_STRING([--enable-documentation],
                             [build documentation]),,
              enable_documentation=yes)
if test x$enable_documentation = xyes; then
   AC_PATH_PROG([XSLTPROC], [xsltproc])
   if test x$XSLTPROC = x; then
      AC_MSG_ERROR([xsltproc is required to build documentation])
   fi
fi
AM_CONDITIONAL(BUILD_DOCUMENTATION, test x$enable_documentation = xyes)

AC_CONFIG_FILES([
        Makefile
        po/Makefile.in
        Alacarte/Makefile
	data/Makefile
	data/icons/Makefile
	man/Makefile
        ])

AC_OUTPUT

