dnl -*- Mode: autoconf -*-
dnl Process this file with autoconf to produce a configure script.
AC_PREREQ(2.53)
AC_INIT(alacarte, 0.9.2, https://launchpad.net/products/alacarte/+filebug)
AC_CONFIG_SRCDIR(alacarte.in)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE

m4_define(required_pygtk_version, 2.8.0)
m4_define(required_python_abi, 2.4)

dnl put the ACLOCAL flags in the makefile
ACLOCAL="$ACLOCAL $ACLOCAL_FLAGS"


GETTEXT_PACKAGE=alacarte
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

AM_PATH_PYTHON_VERSION(2.4, 2.4.0)

PKG_CHECK_MODULES(ALACARTE, libgnome-menu >= 2.14)

dnl Check for correctly installed pygtk
AC_MSG_CHECKING(for pygtk required_pygtk_version installed for python required_python_abi)
prog="
import pygtk; pygtk.require('2.0')
import gobject
assert gobject.pygtk_version >= tuple(map(int, 'required_pygtk_version'.split('.')))
"
if $PYTHON -c "$prog" 1>&AC_FD_CC 2>&AC_FD_CC; then
    AC_MSG_RESULT(found)
else
    AC_MSG_RESULT(not found)
    AC_MSG_ERROR(required pygtk version not found)
fi

dnl Check for correctly installed python-glade
dnl AC_MSG_CHECKING(for pyglade required_pygtk_version installed for python required_python_abi)
dnl prog="
dnl import pygtk; pygtk.require('2.0')
dnl import gtk.glade
dnl "
dnl if $PYTHON -c "$prog" 1>&AC_FD_CC 2>&AC_FD_CC; then
dnl    AC_MSG_RESULT(found)
dnl else
dnl    AC_MSG_RESULT(not found)
dnl    AC_MSG_ERROR(required pyglade version not found)
dnl fi

AC_CONFIG_FILES([
        Makefile
        po/Makefile.in
        Alacarte/Makefile
        ])

AC_OUTPUT

