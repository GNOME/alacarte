# -*- coding: utf-8 -*-
#   Alacarte Menu Editor - Simple fd.o Compliant Menu Editor
#   Copyright (C) 2006  Travis Watkins
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

import gtk, gtk.glade, gmenu, gobject
import LaunchpadIntegration
import cgi, os
import gettext
gettext.bindtextdomain('alacarte')
gettext.textdomain('alacarte')
gtk.glade.bindtextdomain('alacarte')
gtk.glade.textdomain('alacarte')
_ = gettext.gettext
from Alacarte.MenuEditor import MenuEditor
from Alacarte.DialogHandler import DialogHandler
from Alacarte import util

class MainWindow:
	def __init__(self, datadir, version, argv):
		self.file_path = datadir
		self.version = version
		self.editor = MenuEditor()
		self.tree = gtk.glade.XML(os.path.join(self.file_path, 'alacarte.glade'), 'mainwindow')
		self.tree.get_widget('mainwindow').connect('destroy', lambda *a: gtk.main_quit())
		LaunchpadIntegration.set_sourcepackagename('alacarte')
		LaunchpadIntegration.add_items(self.tree.get_widget('help_menu_menu'), -1, False, True)
		signals = {}
		for attr in dir(self):
			signals[attr] = getattr(self, attr)
		self.tree.signal_autoconnect(signals)
		self.setupMenuTree()
		self.setupItemTree()
		self.tree.get_widget('mainwindow').set_icon_name('alacarte')
		self.dialogs = DialogHandler(self.editor, self.file_path)

	def run(self):
		self.loadMenus()
		self.tree.get_widget('mainwindow').show_all()
		gtk.main()

	def setupMenuTree(self):
		self.menu_store = gtk.TreeStore(gtk.gdk.Pixbuf, str, object)
		menus = self.tree.get_widget('menu_tree')
		column = gtk.TreeViewColumn(_('Name'))
		column.set_spacing(4)
		cell = gtk.CellRendererPixbuf()
		column.pack_start(cell, False)
		column.set_attributes(cell, pixbuf=0)
		cell = gtk.CellRendererText()
		cell.set_fixed_size(-1, 25)
		column.pack_start(cell, True)
		column.set_attributes(cell, markup=1)
		column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
		menus.append_column(column)

	def setupItemTree(self):
		items = self.tree.get_widget('item_tree')
		column = gtk.TreeViewColumn(_('Show'))
		cell = gtk.CellRendererToggle()
		cell.connect('toggled', self.on_item_tree_show_toggled)
		column.pack_start(cell, True)
		column.set_attributes(cell, active=0)
		#hide toggle for separators
		column.set_cell_data_func(cell, self._cell_data_toggle_func)
		items.append_column(column)
		column = gtk.TreeViewColumn(_('Item'))
		column.set_spacing(4)
		cell = gtk.CellRendererPixbuf()
		column.pack_start(cell, False)
		column.set_attributes(cell, pixbuf=1)
		cell = gtk.CellRendererText()
		cell.set_fixed_size(-1, 25)
		column.pack_start(cell, True)
		column.set_attributes(cell, markup=2)
		items.append_column(column)
		self.item_store = gtk.ListStore(bool, gtk.gdk.Pixbuf, str, object, str)
		items.set_model(self.item_store)

	def _cell_data_toggle_func(self, tree_column, renderer, model, treeiter):
		if not model[treeiter][3].get_type() == gmenu.TYPE_SEPARATOR:
			renderer.set_property('visible', True)

	def loadMenus(self):
		self.menu_store.clear()
		for menu in self.editor.getMenus():
			iters = [None]*20
			self.loadMenu(iters, menu)
		self.tree.get_widget('menu_tree').set_model(self.menu_store)
		for menu in self.menu_store:
			self.tree.get_widget('menu_tree').expand_to_path(menu.path)

	def loadMenu(self, iters, parent, depth=0):
		if depth == 0:
			icon = util.getIcon(parent)
			iters[depth] = self.menu_store.append(None, (icon, cgi.escape(parent.get_name()), parent))
		depth += 1
		for menu in self.editor.getMenus(parent):
			name = cgi.escape(menu.get_name())
			icon = util.getIcon(menu)
			iters[depth] = self.menu_store.append(iters[depth-1], (icon, name, menu))
			self.loadMenu(iters, menu, depth)
		depth -= 1

	def loadItems(self, menu, menu_path):
		self.item_store.clear()
		for item, show in self.editor.getItems(menu):
			if item.get_type() == gmenu.TYPE_SEPARATOR:
				name = '---'
				icon = None
			else:
				if show:
					name = cgi.escape(item.get_name())
				else:
					name = '<small><i>' + cgi.escape(item.get_name()) + '</i></small>'
				icon = util.getIcon(item)
			self.item_store.append((show, icon, name, item, menu_path))

	def reloadMenus(self):
		menu_tree = self.tree.get_widget('menu_tree')
		menus, iter = menu_tree.get_selection().get_selected()
		menu_path = menus.get_path(iter)
		self.loadMenus()
		menu_tree.get_selection().select_path(menu_path)
		return False

	def reloadItems(self):
		item_tree = self.tree.get_widget('item_tree')
		items, iter = item_tree.get_selection().get_selected()
		item_path = items.get_path(iter)
		menu_tree = self.tree.get_widget('menu_tree')
		self.on_menu_tree_cursor_changed(menu_tree)
		item_tree.get_selection().select_path(item_path)
		return False

	def on_menu_tree_cursor_changed(self, treeview):
		menus, iter = treeview.get_selection().get_selected()
		menu_path = menus.get_path(iter)
		items = self.tree.get_widget('item_tree')
		items.get_selection().unselect_all()
		self.loadItems(self.menu_store[menu_path][2], menu_path)

	def on_item_tree_show_toggled(self, cell, path):
		item = self.item_store[path][3]
		if item.get_type() == gmenu.TYPE_SEPARATOR:
			return
		if self.item_store[path][0]:
			self.editor.hideItem(item)
			self.item_store[path][2] = '<small><i>' + self.item_store[path][2] + '</i></small>'
		else:
			self.editor.showItem(item)
			self.item_store[path][2] = cgi.escape(item.get_name())
		self.item_store[path][0] = not self.item_store[path][0]

	def on_item_tree_row_activated(self, treeview, path, column):
		item = self.item_store[path][3]
		if item.get_type() == gmenu.TYPE_ENTRY:
			self.dialogs.editItemDialog(self.item_store[path])
		elif item.get_type() == gmenu.TYPE_DIRECTORY:
			self.dialogs.editMenuDialog(self.item_store[path])
		gobject.idle_add(self.reloadMenus)
		gobject.idle_add(self.reloadItems)

	def on_item_tree_popup_menu(self, item_tree, event=None):
		model, iter = item_tree.get_selection().get_selected()
		if event:
			#don't show if it's not the right mouse button
			if event.button != 3:
				return
			button = event.button
			event_time = event.time
			info = item_tree.get_path_at_pos(int(event.x), int(event.y))
			if info != None:
				path, col, cellx, celly = info
				item_tree.grab_focus()
				item_tree.set_cursor(path, col, 0)
		else:
			path = model.get_path(iter)
			button = 0
			event_time = 0
			item_tree.grab_focus()
			item_tree.set_cursor(path, item_tree.get_columns()[0], 0)
		popup = self.tree.get_widget('edit_menu_menu')
		popup.popup( None, None, None, button, event_time)

	def on_help_about_activate(self, menu):
		tree = gtk.glade.XML(os.path.join(self.file_path, 'alacarte.glade'), 'aboutdialog')
		dialog = tree.get_widget('aboutdialog')
		dialog.set_icon(self.icon)
		dialog.set_version(self.version)
		dialog.set_logo(self.logo)
		dialog.show()
