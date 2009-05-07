#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME="alacarte"

#automake requires ChangeLog to exist
touch ChangeLog

. gnome-autogen.sh
