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

import os, cgi
import gmenu, gtk, gtk.glade
import gettext
gettext.bindtextdomain('alacarte')
gettext.textdomain('alacarte')
gtk.glade.bindtextdomain('alacarte')
gtk.glade.textdomain('alacarte')
_ = gettext.gettext
from Alacarte import util

class DialogHandler:
	window_icon = None
	editor = None
	file_path = None

	def __init__(self, editor, file_path):
		self.editor = editor
		self.file_path = file_path

	def showError(self, message):
		dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, None)
		dialog.set_title('')
		dialog.set_size_request(400, -1)
		dialog.set_markup('<b>' + cgi.escape(message) + '</b>')
		dialog.run()
		dialog.destroy()

	def editItemDialog(self, item_row):
		self.in_dialog_setup = True
		self.item_row = item_row
		self.item = item_row[3]
		#load widgets
		self.tree = gtk.glade.XML(os.path.join(self.file_path, 'alacarte.glade'), 'itemproperties')
		signals = {}
		for attr in dir(self):
			signals[attr] = getattr(self, attr)
		self.tree.signal_autoconnect(signals)
		dialog = self.tree.get_widget('itemproperties')
		icon_button = self.tree.get_widget('item_icon_button')
		name_entry = self.tree.get_widget('item_name_entry')
		comment_entry = self.tree.get_widget('item_comment_entry')
		command_entry = self.tree.get_widget('item_command_entry')
		command_button = self.tree.get_widget('item_command_button')
		term_check = self.tree.get_widget('item_terminal_check')

		icon_button.remove(icon_button.get_children()[0])
		pixbuf, path = util.getIcon(self.item, True)
		if pixbuf:
			image = gtk.Image()
			image.set_from_pixbuf(pixbuf)
			icon_button.add(image)
			icon_button.icon_path = path
		else:
			label = gtk.Label('No Icon')
			icon_button.add(label)
		name_entry.set_text(self.item.get_name())
		if self.item.get_comment():
			comment_entry.set_text(self.item.get_comment())
		if self.item.get_exec():
			command_entry.set_text(self.item.get_exec())
		if self.item.get_terminal():
			term_check.set_active(True)
		dialog.set_icon(self.window_icon)
		dialog.show_all()
		self.item_original_values = (
			icon_button.icon_path,
			name_entry.get_text(),
			comment_entry.get_text(),
			command_entry.get_text(),
			term_check.get_active()
			)
		self.in_dialog_setup = False

	def saveItem(self, values):
		pixbuf, path = util.getIcon(self.item, True)
		#if the icon hasn't changed don't save the themed path
		if path == values[0]:
			self.editor.editItem(self.item, None, values[1], values[2], values[3], values[4])
		else:
			self.editor.editItem(self.item, values[0], values[1], values[2], values[3], values[4])

	def on_item_contents_changed(self, garbage):
		if not self.in_dialog_setup:
			self.tree.get_widget('item_revert_button').set_sensitive(True)
			values = (
				self.tree.get_widget('item_icon_button').icon_path,
				self.tree.get_widget('item_name_entry').get_text(),
				self.tree.get_widget('item_comment_entry').get_text(),
				self.tree.get_widget('item_command_entry').get_text(),
				self.tree.get_widget('item_terminal_check').get_active()
				)
			self.saveItem(values)
			self.item_row[1] = util.getIcon(values[0])
			self.item_row[2] = values[1]

	def on_item_revert_button_clicked(self, button):
		icon_button = self.tree.get_widget('item_icon_button')
		icon_button.remove(icon_button.get_children()[0])
		if self.item_original_values[0]:
			image = gtk.Image()
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.item_original_values[0], 24, 24)
			image.set_from_pixbuf(pixbuf)
			icon_button.add(image)
			image.show()
			icon_button.icon_path = self.item_original_values[0]
		else:
			label = gtk.Label('No Icon')
			icon_button.add(label)
		self.tree.get_widget('item_name_entry').set_text(self.item_original_values[1]),
		self.tree.get_widget('item_comment_entry').set_text(self.item_original_values[2]),
		self.tree.get_widget('item_command_entry').set_text(self.item_original_values[3]),
		self.tree.get_widget('item_terminal_check').set_active(self.item_original_values[4])
		self.tree.get_widget('item_revert_button').set_sensitive(False)

	def on_item_close_button_clicked(self, button):
		if len(self.tree.get_widget('item_name_entry').get_text()) == 0:
			self.showError(_('A name is required.'))
		elif len(self.tree.get_widget('item_command_entry').get_text()) == 0:
			self.showError(_('A command is required.'))
		else:
			self.tree.get_widget('itemproperties').destroy()

	def editMenuDialog(self, menu_row):
		def responseChecker(response):
			if response == gtk.RESPONSE_REJECT:
				self.revertMenu()
				return False
			if response == gtk.RESPONSE_CLOSE or response == gtk.RESPONSE_DELETE_EVENT:
				if len(self.tree.get_widget('menu_name_entry').get_text()) == 0:
					self.showError(_('A name is required.'))
					return False
				if self.tree.get_widget('menu_name_entry').get_text() == 'Other':
					self.showError(_('A menu cannot be named "Other".'))
					return False
				return True
			return False
		self.in_dialog_setup = True
		self.menu_row = menu_row
		self.menu = menu_row[3]
		#load widgets
		self.tree = gtk.glade.XML(os.path.join(self.file_path, 'alacarte.glade'), 'menuproperties')
		signals = {}
		for attr in dir(self):
			signals[attr] = getattr(self, attr)
		self.tree.signal_autoconnect(signals)
		dialog = self.tree.get_widget('menuproperties')
		icon_button = self.tree.get_widget('menu_icon_button')
		name_entry = self.tree.get_widget('menu_name_entry')
		comment_entry = self.tree.get_widget('menu_comment_entry')

		icon_button.remove(icon_button.get_children()[0])
		pixbuf, path = util.getIcon(self.menu, True)
		if pixbuf:
			image = gtk.Image()
			image.set_from_pixbuf(pixbuf)
			icon_button.add(image)
			icon_button.icon_path = path
		else:
			label = gtk.Label('No Icon')
			icon_button.add(label)
		name_entry.set_text(self.menu.get_name())
		if self.menu.get_comment():
			comment_entry.set_text(self.menu.get_comment())
		dialog.set_icon(self.window_icon)
		dialog.show_all()
		self.menu_original_values = (
			icon_button.icon_path,
			name_entry.get_text(),
			comment_entry.get_text()
			)
		self.in_dialog_setup = False
		can_close = False
		while can_close == False:
			response = dialog.run()
			can_close = responseChecker(response)
		dialog.destroy()

	def saveMenu(self, values):
		pixbuf, path = util.getIcon(self.menu, True)
		#if the icon hasn't changed don't save the themed path
		if path == values[0]:
			self.editor.editMenu(self.menu, None, values[1], values[2])
		else:
			self.editor.editMenu(self.menu, values[0], values[1], values[2])

	def on_menu_contents_changed(self, garbage):
		if not self.in_dialog_setup:
			self.tree.get_widget('menu_revert_button').set_sensitive(True)
			values = (
				self.tree.get_widget('menu_icon_button').icon_path,
				self.tree.get_widget('menu_name_entry').get_text(),
				self.tree.get_widget('menu_comment_entry').get_text()
				)
			self.saveMenu(values)
			self.menu_row[1] = util.getIcon(values[0])
			self.menu_row[2] = values[1]

	def revertMenu(self):
		icon_button = self.tree.get_widget('menu_icon_button')
		icon_button.remove(icon_button.get_children()[0])
		if self.menu_original_values[0]:
			image = gtk.Image()
			pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.menu_original_values[0], 24, 24)
			image.set_from_pixbuf(pixbuf)
			icon_button.add(image)
			image.show()
			icon_button.icon_path = self.menu_original_values[0]
		else:
			label = gtk.Label('No Icon')
			icon_button.add(label)
		self.tree.get_widget('menu_name_entry').set_text(self.menu_original_values[1]),
		self.tree.get_widget('menu_comment_entry').set_text(self.menu_original_values[2]),

	def on_menu_close_button_clicked(self, button):
		if len(self.tree.get_widget('menu_name_entry').get_text()) == 0:
			self.showError(_('A name is required.'))
		elif self.tree.get_widget('menu_name_entry').get_text() == 'Other':
			self.showError(_('A menu cannot be named "Other".'))
		else:
			return True
