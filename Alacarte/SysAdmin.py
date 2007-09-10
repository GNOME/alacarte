# -*- coding: utf-8 -*-
#   Alacarte Menu Editor - Simple fd.o Compliant Menu Editor
#   Copyright (C) 2006  Novell.
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Library General Public
#   License as published by the Free Software Foundation; either
#   version 2 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import gtk, gconf

class SysAdmin:
	ab_max_newapps_prefix = '/desktop/gnome/applications/main-menu'
	ab_max_newapps_key = ab_max_newapps_prefix + '/ab_new_apps_max_items'

	#Fixme - how do I get this programatically - maybe gconftool-2 --get-default-source
	#sp1 -  DEFAULTS_SOURCE = 'xml::/etc/opt/gnome/gconf/gconf.xml.defaults'
	#10.3 - DEFAULTS_SOURCE = 'xml::/etc/gconf/gconf.xml.schemas'
	DEFAULTS_SOURCE = 'xml::/etc/gconf/gconf.xml.schemas'
	
	def __init__(self, system_view):
		print "SysAdmin::system_view = " + str(system_view)
		self.system_view = system_view
		if(self.system_view):
			engine = gconf.engine_get_for_address(self.DEFAULTS_SOURCE)
			self.gconf_client = gconf.client_get_for_engine(engine)
			#engine.unref()
		else:
			self.gconf_client = gconf.client_get_default()
		self.gconf_client.add_dir(self.ab_max_newapps_prefix, gconf.CLIENT_PRELOAD_NONE)
		print type(self.gconf_client)
		print "Leave SysAdmin::__init__"

	def getGConfValue (self, key):
		print "Enter getGConfValue"
		#if(self.system_view):
		#	value = self.gconf_client.get_default_from_schema(key);
		#	retval = value.get_int()
		#else:
		#	retval = self.gconf_client.get_int(key)

		retval = self.gconf_client.get_int(key)
		return retval

	def setGConfValue (self, key, value):
		print "Enter setGConfValue"
		#val = self.gconf_client.get_default_from_schema(key);
		#val.set_int(value)
		#self.gconf_client.set(key, val)

		self.gconf_client.set_int(key, value)

	def ab_key_changed (self, client, cnxn_id, entry, glade_tree):
		print "Enter " + __name__ + ":ab_key_changed"
		if entry.value and entry.value.type == gconf.VALUE_INT:
			glade_tree.get_widget('ab_newapps_max_spin').set_text(entry.value.to_string())
		
	def setup_ab (self, glade_tree):
		print "Enter setup_ab"
		glade_tree.get_widget('ab_newapps_max_spin').set_text(str(self.getGConfValue(SysAdmin.ab_max_newapps_key)))
		self.gconf_client.notify_add(self.ab_max_newapps_key, self.ab_key_changed, glade_tree)

	def setup_viewmode (self, glade_tree, systemview):
		print "Enter setup_viewmode"
		if systemview:
			label = glade_tree.get_widget('system_view_button').get_label()
			label = label + ':  ' + systemview
			print label
			glade_tree.get_widget('system_view_button').set_label(label)
		else:
			glade_tree.get_widget('system_view_button').set_active(False)
			glade_tree.get_widget('user_view_button').set_active(True)
			
