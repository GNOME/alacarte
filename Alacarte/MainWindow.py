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
import time

class MainWindow:
	timer = None
	#hack to make editing menu properties work
	allow_update = True
	#drag-and-drop stuff
	dnd_items = [('ALACARTE_ITEM_ROW', gtk.TARGET_SAME_APP, 0)]
	dnd_menus = [('ALACARTE_MENU_ROW', gtk.TARGET_SAME_APP, 0)]
	dnd_both = dnd_items + dnd_menus
	drag_data = None

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

	def menuChanged(self, *a):
		if self.timer:
			gobject.source_remove(self.timer)
			self.timer = None
		self.timer = gobject.timeout_add(3, self.loadUpdates)

	def loadUpdates(self):
		if not self.allow_update:
			return
		menu_tree = self.tree.get_widget('menu_tree')
		item_tree = self.tree.get_widget('item_tree')
		items, iter = item_tree.get_selection().get_selected()
		update_items = False
		if iter:
			if items[iter][3].get_type() == gmenu.TYPE_DIRECTORY:
				item_id = items[iter][3].get_menu_id()
				update_items = True
			elif items[iter][3].get_type() == gmenu.TYPE_ENTRY:
				item_id = items[iter][3].get_desktop_file_id()
				update_items = True
		menus, iter = menu_tree.get_selection().get_selected()
		update_menus = False
		menu_id = None
		if iter:
			menu_id = menus[iter][2].get_menu_id()
			update_menus = True
		self.loadMenus()
		#find current menu in new tree
		if update_menus:
			menu_tree.get_model().foreach(self.findMenu, menu_id)
		self.on_menu_tree_cursor_changed(menu_tree)
		#find current item in new list
		if update_items:
			i = 0
			for item in item_tree.get_model():
				if item_id:
					if item[3].get_type() == gmenu.TYPE_ENTRY and item[3].get_desktop_file_id() == item_id:
						item_tree.get_selection().select_path((i,))
				else:
					if item[3].get_type() == gmenu.TYPE_DIRECTORY and item[3].get_menu_id() == item_id:
						item_tree.get_selection().select_path((i,))
				i += 1

	def findMenu(self, menus, path, iter, menu_id):
		 if menus[path][2].get_menu_id() == menu_id:
			menu_tree = self.tree.get_widget('menu_tree')
			menu_tree.expand_to_path(path)
			menu_tree.get_selection().select_path(path)
			return True

	def run(self):
		self.loadMenus()
		self.editor.applications.tree.add_monitor(self.menuChanged)
		self.editor.settings.tree.add_monitor(self.menuChanged)
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
		menus.enable_model_drag_dest(self.dnd_both, gtk.gdk.ACTION_PRIVATE)

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
		self.item_store = gtk.ListStore(bool, gtk.gdk.Pixbuf, str, object)
		items.set_model(self.item_store)
		items.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, self.dnd_items, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)

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
		for menu, show in self.editor.getMenus(parent):
			if show:
				name = cgi.escape(menu.get_name())
			else:
				name = '<small><i>' + cgi.escape(menu.get_name()) + '</i></small>'
			icon = util.getIcon(menu)
			iters[depth] = self.menu_store.append(iters[depth-1], (icon, name, menu))
			self.loadMenu(iters, menu, depth)
		depth -= 1

	def loadItems(self, menu, menu_path):
		self.item_store.clear()
		for item, show in self.editor.getItems(menu):
			menu_icon = None
			if item.get_type() == gmenu.TYPE_SEPARATOR:
				name = '---'
				icon = None
			else:
				if show:
					name = cgi.escape(item.get_name())
				else:
					name = '<small><i>' + cgi.escape(item.get_name()) + '</i></small>'
				icon = util.getIcon(item)
			self.item_store.append((show, icon, name, item))

	def on_file_new_menu_activate(self, menu):
		menu_tree = self.tree.get_widget('menu_tree')
		menus, iter = menu_tree.get_selection().get_selected()
		parent = menus[iter][2]
		values = self.dialogs.newMenuDialog()
		if values:
			self.editor.createMenu(parent, values[0], values[1], values[2])
		#FIXME: make gnome-menus update monitors when menus are added
		gobject.timeout_add(500, self.loadUpdates)

	def on_file_new_item_activate(self, menu):
		menu_tree = self.tree.get_widget('menu_tree')
		menus, iter = menu_tree.get_selection().get_selected()
		parent = menus[iter][2]
		values = self.dialogs.newItemDialog()
		if values:
			self.editor.createItem(parent, values[0], values[1], values[2], values[3], values[4])

	def on_edit_properties_activate(self, menu):
		item_tree = self.tree.get_widget('item_tree')
		items, iter = item_tree.get_selection().get_selected()
		item = self.item_store[iter][3]
		if item.get_type() == gmenu.TYPE_ENTRY:
			self.dialogs.editItemDialog(self.item_store[iter][3])
		elif item.get_type() == gmenu.TYPE_DIRECTORY:
			self.allow_update = False
			self.dialogs.editMenuDialog(self.item_store[iter])
			self.allow_update = True
			self.loadUpdates()

	def on_help_about_activate(self, menu):
		tree = gtk.glade.XML(os.path.join(self.file_path, 'alacarte.glade'), 'aboutdialog')
		dialog = tree.get_widget('aboutdialog')
		dialog.set_icon(self.icon)
		dialog.set_version(self.version)
		dialog.set_logo(self.logo)
		dialog.show()

	def on_menu_tree_cursor_changed(self, treeview):
		menus, iter = treeview.get_selection().get_selected()
		menu_path = menus.get_path(iter)
		item_tree = self.tree.get_widget('item_tree')
		item_tree.get_selection().unselect_all()
		self.loadItems(self.menu_store[menu_path][2], menu_path)

	def on_menu_tree_drag_data_received(self, treeview, context, x, y, selection, info, etime):
		menus = treeview.get_model()
		if selection.target == 'ALACARTE_ITEM_ROW':
			drop_info = treeview.get_dest_row_at_pos(x, y)
			if drop_info:
				path, position = drop_info
				types = (gtk.TREE_VIEW_DROP_INTO_OR_BEFORE, gtk.TREE_VIEW_DROP_INTO_OR_AFTER
					)
				if position not in types:
					context.finish(False, False, etime)
					return False
				item = self.drag_data
				old_parent = item.get_parent()
				new_parent = menus[path][2]
				if item.get_type() == gmenu.TYPE_ENTRY:
					self.editor.copyItem(item, new_parent)
				elif item.get_type() == gmenu.TYPE_DIRECTORY:
					self.editor.moveMenu(item, old_parent, new_parent)
				else:
					context.finish(False, False, etime) 
				context.finish(True, True, etime)

	def on_item_tree_show_toggled(self, cell, path):
		item = self.item_store[path][3]
		if item.get_type() == gmenu.TYPE_SEPARATOR:
			return
		if self.item_store[path][0]:
			self.editor.hideItem(item)
		else:
			self.editor.showItem(item)

	def on_item_tree_row_activated(self, treeview, path, column):
		self.on_edit_properties_activate(None)

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
		#without this shift-f10 won't work
		return True

	def on_item_tree_drag_data_get(self, treeview, context, selection, target_id, etime):
		items, iter = treeview.get_selection().get_selected()
		self.drag_data = items[iter][3]
		selection.set(selection.target, 8, 'items')

	def on_move_up_button_clicked(self, button):
		item_tree = self.tree.get_widget('item_tree')
		items, iter = item_tree.get_selection().get_selected()
		path = items.get_path(iter)
		#at top, can't move up
		if path[0] == 0:
			return
		item = items[path][3]
		before = items[(path[0] - 1,)][3]
		self.editor.moveItem(item, item.get_parent(), item.get_parent(), before=before)

	def on_move_down_button_clicked(self, button):
		item_tree = self.tree.get_widget('item_tree')
		items, iter = item_tree.get_selection().get_selected()
		path = items.get_path(iter)
		#at bottom, can't move down
		if path[0] == (len(items) - 1):
			return
		item = items[path][3]
		after = items[path][3]
		self.editor.moveItem(item, item.get_parent(), item.get_parent(), after=after)

	def on_close_button_clicked(self, button):
		gtk.main_quit()
