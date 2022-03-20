XSLTPROC_FLAGS = \
	--nonet \
	--stringparam man.output.quietly 1 \
	--stringparam funcsynopsis.style ansi \
	--stringparam man.th.extra1.suppress 1 \
	--stringparam man.authors.section.enabled 0 \
	--stringparam man.copyright.section.enabled 0

%.1: %.xml
	$(AM_V_GEN) $(XSLTPROC) $(XSLTPROC_FLAGS) http://docbook.sourceforge.net/release/xsl/current/manpages/docbook.xsl $<

man_MANS = alacarte.1

xml_files = ${patsubst %.1,%.xml,${patsubst %.7,%.xml,$(man_MANS)}}

EXTRA_DIST = $(xml_files)

CLEANFILES = $(man_MANS)

-include $(top_srcdir)/git.mk
