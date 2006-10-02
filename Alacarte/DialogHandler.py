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
import gmenu, gtk, gtk.glade, gobject
import gettext
_ = gettext.gettext
from Alacarte import util

class DialogHandler:
	editor = None
	file_path = None
	timer = None
	in_revert = False
	first_change = False

	def __init__(self, parent, editor, file_path):
		self.parent = parent
		self.editor = editor
		self.file_path = file_path
		self.command_completion = gtk.EntryCompletion()
		self.command_completion.set_property('popup-completion', False)
		self.command_completion.set_inline_completion(True)
		self.completion_full = gtk.ListStore(str)
		self.completion_used = gtk.ListStore(str)
		self.command_completion.set_text_column(0)
		paths = os.getenv('PATH')
		for path in paths.split(os.pathsep):
			if os.path.isdir(path):
				try:
					for name in os.listdir(path):
						f = os.path.join(path, name)
						if os.path.isfile(f):
							if os.access(f, os.X_OK):
								self.completion_full.append([name,])
				except:
					pass
		self.command_completion.set_model(self.completion_used)

	def showError(self, message):
		dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE, None)
		dialog.set_title('')
		dialog.set_size_request(400, -1)
		dialog.set_markup('<b>' + cgi.escape(message) + '</b>')
		dialog.run()
		dialog.destroy()

	def showCommandDialog(self, command_entry):
		dialog = gtk.FileChooserDialog('Choose a Program', None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		if len(command_entry.get_text()) and '/' in command_entry.get_text():
			dialog.set_current_folder(command_entry.get_text().rsplit('/', 1)[0])
		else:
			dialog.set_current_folder('/usr/bin/')
		file_filter = gtk.FileFilter()
		file_filter.add_mime_type('application/x-executable')
		file_filter.add_mime_type('application/x-shellscript')
		dialog.set_filter(file_filter)
		dialog.show_all()
		if dialog.run() == gtk.RESPONSE_OK:
			command = dialog.get_filename()
			new_command = ''
			length, i = len(command), 0
			while i < length:
				char = command[i]
				if not (ord(char) >= ord('a') and ord(char) <= ord('z')):
					if not (ord(char) >= ord('A') and ord(char) <= ord('Z')):
						if char == '/':
							new_command += char
						else:
							new_command += '\\' + char
					else:
						new_command += char
				else:
					new_command += char
				i += 1
			command_entry.set_completion(None)
			command_entry.set_text(new_command)
			command_entry.set_completion(self.command_completion)
		dialog.destroy()

	def showIconDialog(self, button):
		dialog = gtk.FileChooserDialog('Choose an Icon', None, gtk.FILE_CHOOSER_ACTION_OPEN, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OK, gtk.RESPONSE_OK))
		if button.icon_path:
			dialog.set_current_folder(button.icon_path.rsplit('/', 1)[0])
		else:
			dialog.set_current_folder('/usr/share/icons/')
		preview = gtk.VBox()
		preview.set_spacing(8)
		preview.set_size_request(92, 92)
		preview_text = gtk.Label('Preview')
		preview.pack_start(preview_text, False, False)
		preview_image = gtk.Image()
		preview.pack_start(preview_image, False, False)
		preview.show()
		preview_text.show()
		preview_image.show()
		dialog.set_preview_widget(preview)
		dialog.set_preview_widget_active(False)
		dialog.set_use_preview_label(False)
		dialog.connect('selection-changed', self.on_icon_dialog_selection_changed, preview_image)
		file_filter = gtk.FileFilter()
		file_filter.add_mime_type('image/png')
		file_filter.add_mime_type('image/x-xpixmap')
		file_filter.add_mime_type('image/svg+xml')
		dialog.set_filter(file_filter)
		dialog.show_all()
		if dialog.run() == gtk.RESPONSE_OK:
			button.remove(button.get_children()[0])
			pixbuf = util.getIcon(dialog.get_filename())
			button.icon_path = dialog.get_filename()
			image = gtk.Image()
			image.set_from_pixbuf(pixbuf)
			image.show()
			button.add(image)
			dialog.destroy()
			return True
		dialog.destroy()
		return False

	def on_icon_button_clicked(self, button):
		self.showIconDialog(button)

	def on_icon_dialog_selection_changed(self, dialog, image):
		icon_file = dialog.get_preview_filename()
		try:
			pixbuf = gtk.gdk.pixbuf_new_from_file(icon_file)
		except:
			dialog.set_preview_widget_active(False)
			return
		if pixbuf.get_width() > 64 or pixbuf.get_height() > 64:
			pixbuf = pixbuf.scale_simple(32, 32, gtk.gdk.INTERP_HYPER)
		image.set_from_pixbuf(pixbuf)
		dialog.set_preview_widget_active(True)

	def newItemDialog(self):
		self.tree = gtk.glade.XML(os.path.join(self.file_path, 'alacarte.glade'), 'newitemproperties')
		signals = {}
		for attr in dir(self):
			signals[attr] = getattr(self, attr)
		self.tree.signal_autoconnect(signals)
		def responseChecker(response):
			if response == gtk.RESPONSE_OK:
				if len(self.tree.get_widget('newitem_name_entry').get_text()) == 0:
					self.showError(_('A name is required.'))
					return False
				if len(self.tree.get_widget('newitem_command_entry').get_text()) == 0:
					self.showError(_('A command is required.'))
					return False
				return 'save'
			return True
		command_entry = self.tree.get_widget('newitem_command_entry')
		command_entry.set_completion(self.command_completion)
		icon_button = self.tree.get_widget('newitem_icon_button')
		icon_button.remove(icon_button.get_children()[0])
		label = gtk.Label('No Icon')
		icon_button.add(label)
		icon_button.icon_path = None
		dialog = self.tree.get_widget('newitemproperties')
		dialog.set_transient_for(self.parent)
		dialog.show_all()
		can_close = False
		while can_close == False:
			response = dialog.run()
			can_close = responseChecker(response)
		if can_close == 'save':
			name_entry = self.tree.get_widget('newitem_name_entry')
			comment_entry = self.tree.get_widget('newitem_comment_entry')
			command_button = self.tree.get_widget('newitem_command_button')
			term_check = self.tree.get_widget('newitem_terminal_check')
			dialog.destroy()
			return (icon_button.icon_path, name_entry.get_text(), comment_entry.get_text(), command_entry.get_text(), term_check.get_active())
		dialog.destroy()

	def editItemDialog(self, item_row):
		def responseChecker(response):
			if response == gtk.RESPONSE_REJECT:
				self.revertItem()
				return False
			if response == gtk.RESPONSE_CLOSE or response == gtk.RESPONSE_DELETE_EVENT:
				if len(self.tree.get_widget('item_name_entry').get_text()) == 0:
					self.showError(_('A name is required.'))
					return False
				if len(self.tree.get_widget('item_command_entry').get_text()) == 0:
					self.showError(_('A command is required.'))
					return False
				return True
			return False
		self.in_dialog_setup = True
		self.item_row = item_row
		self.item = item_row[3]
		#item likes to lose it's parent
		self.item_parent = self.item.get_parent()
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

		dialog.set_transient_for(self.parent)
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
			icon_button.icon_path = None
		name_entry.set_text(cgi.escape(self.item.get_name()))
		if self.item.get_comment():
			comment_entry.set_text(self.item.get_comment())
		if self.item.get_exec():
			command = self.item.get_exec()
			#escape a few common things in commands
			command = command.replace('\r', '\\r')
			command = command.replace('\n', '\\n')
			command = command.replace('\t', '\\t')
			command_entry.set_text(cgi.escape(command))
		#hack to work around weird bug
		command_entry.set_completion(self.command_completion)
		if self.item.get_launch_in_terminal():
			term_check.set_active(True)
		dialog.show_all()
		self.item_original_values = (
			icon_button.icon_path,
			name_entry.get_text(),
			comment_entry.get_text(),
			command_entry.get_text(),
			term_check.get_active()
			)
		self.in_dialog_setup = False
		#hack to make undo work
		self.first_change = True
		can_close = False
		while can_close == False:
			response = dialog.run()
			can_close = responseChecker(response)
		dialog.destroy()
		self.first_change = False

	def on_item_contents_changed(self, garbage):
		self.item_row[1] = util.getIcon(self.tree.get_widget('item_icon_button').icon_path)
		self.item_row[2] = self.tree.get_widget('item_name_entry').get_text()
		if self.first_change:
			self.saveItem(self.item_original_values, True)
			self.first_change = False
		if self.in_revert:
			self.in_revert = False
			self.saveItem(self.item_original_values)
			return
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

	def on_item_icon_button_clicked(self, button):
		if self.showIconDialog(button):
			self.on_item_contents_changed(button)	

	def on_item_command_entry_key_press_event(self, entry, event):
		if event.keyval == gtk.keysyms.BackSpace:
			return
		if event.keyval == gtk.keysyms.Delete:
			start, end = entry.get_selection_bounds()
			entry.delete_text(start, end)
		if event.keyval == gtk.keysyms.Tab:
			start, end = entry.get_selection_bounds()
			if start != end and start != 1 and end == len(entry.get_text()):
				entry.select_region(end, end)
				entry.set_position(-1)
				return True
		elif len(entry.get_text()) == 2:
			chars = entry.get_text()[:2]
			self.completion_used.clear()
			for item in self.completion_full:
				gobject.idle_add(self.compareCommands, item[0], chars)

	def compareCommands(self, possible_command, typed_chars):
		if possible_command[:2] == typed_chars:
			self.completion_used.append((possible_command,))
		return False

	def on_item_command_button_clicked(self, button):
		self.showCommandDialog(self.tree.get_widget('item_command_entry'))

	def on_newitem_command_button_clicked(self, button):
		self.showCommandDialog(self.tree.get_widget('newitem_command_entry'))

	def saveItem(self, values, final=False):
		pixbuf, path = util.getIcon(self.item, True)
		#if the icon hasn't changed don't save the themed path
		if path == values[0]:
			self.editor.editItem(self.item, None, values[1], values[2], values[3], values[4], self.item_parent, final)
		else:
			self.editor.editItem(self.item, values[0], values[1], values[2], values[3], values[4], self.item_parent, final)

	def revertItem(self):
		self.in_revert = True
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
		self.tree.get_widget('item_name_entry').set_text(self.item_original_values[1])
		self.tree.get_widget('item_comment_entry').set_text(self.item_original_values[2])
		self.tree.get_widget('item_command_entry').set_text(self.item_original_values[3])
		self.tree.get_widget('item_terminal_check').set_active(self.item_original_values[4])
		self.tree.get_widget('item_revert_button').set_sensitive(False)

	def newMenuDialog(self):
		tree = gtk.glade.XML(os.path.join(self.file_path, 'alacarte.glade'), 'newmenuproperties')
		signals = {}
		for attr in dir(self):
			signals[attr] = getattr(self, attr)
		tree.signal_autoconnect(signals)
		def responseChecker(response):
			if response == gtk.RESPONSE_OK:
				if len(tree.get_widget('newmenu_name_entry').get_text()) == 0:
					self.showError(_('A name is required.'))
					return False
				return 'save'
			return True
		dialog = tree.get_widget('newmenuproperties')
		dialog.set_transient_for(self.parent)
		icon_button = tree.get_widget('newmenu_icon_button')
		icon_button.remove(icon_button.get_children()[0])
		label = gtk.Label('No Icon')
		icon_button.add(label)
		icon_button.icon_path = None
		dialog.show_all()
		can_close = False
		while can_close == False:
			response = dialog.run()
			can_close = responseChecker(response)
		if can_close == 'save':
			name_entry = tree.get_widget('newmenu_name_entry')
			comment_entry = tree.get_widget('newmenu_comment_entry')
			dialog.destroy()
			return (icon_button.icon_path, name_entry.get_text(), comment_entry.get_text())
		dialog.destroy()
		

	def editMenuDialog(self, menu_row):
		def responseChecker(response):
			if response == gtk.RESPONSE_REJECT:
				self.revertMenu()
				return False
			if response == gtk.RESPONSE_CLOSE or response == gtk.RESPONSE_DELETE_EVENT:
				if len(self.tree.get_widget('menu_name_entry').get_text()) == 0:
					self.showError(_('A name is required.'))
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

		dialog.set_transient_for(self.parent)
		icon_button.remove(icon_button.get_children()[0])
		pixbuf, path = util.getIcon(self.menu, True)
		icon_button.icon_path = None
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
		dialog.show_all()
		self.menu_original_values = (
			icon_button.icon_path,
			name_entry.get_text(),
			comment_entry.get_text()
			)
		#hack to make undo work
		self.first_change = True
		self.in_dialog_setup = False
		can_close = False
		while can_close == False:
			response = dialog.run()
			can_close = responseChecker(response)
		self.menu_original_values = ()
		dialog.destroy()

	def on_menu_contents_changed(self, garbage):
		self.menu_row[1] = util.getIcon(self.tree.get_widget('menu_icon_button').icon_path)
		self.menu_row[2] = self.tree.get_widget('menu_name_entry').get_text()
		if self.first_change:
			self.saveMenu(self.menu_original_values, True)
			self.first_change = False
		if self.in_revert:
			self.in_revert = False
			self.saveMenu(self.menu_original_values)
			return
		if not self.in_dialog_setup:
			self.tree.get_widget('menu_revert_button').set_sensitive(True)
			values = (
				self.tree.get_widget('menu_icon_button').icon_path,
				self.tree.get_widget('menu_name_entry').get_text(),
				self.tree.get_widget('menu_comment_entry').get_text()
				)
			self.saveMenu(values)

	def on_menu_icon_button_clicked(self, button):
		if self.showIconDialog(button):
			self.on_menu_contents_changed(button)

	def saveMenu(self, values, final=False):
		pixbuf, path = util.getIcon(self.menu, True)
		#if the icon hasn't changed don't save the themed path
		if path == values[0]:
			self.editor.editMenu(self.menu, None, values[1], values[2], final)
		else:
			self.editor.editMenu(self.menu, values[0], values[1], values[2], final)

	def revertMenu(self):
		self.in_revert = True
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
		self.tree.get_widget('menu_name_entry').set_text(self.menu_original_values[1])
		self.tree.get_widget('menu_comment_entry').set_text(self.menu_original_values[2])
