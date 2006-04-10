# -*- coding: utf-8 -*-
#   Alacarte Menu Editor - Simple fd.o Compliant Menu Editor
#   Copyright (C) 2006  Travis Watkins, Heinrich Wendel
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

import os, re, xml.dom.minidom, locale
import gmenu
from Alacarte import util

class Menu:
	tree = None
	visible_tree = None
	path = None
	dom = None

class MenuEditor:
	def __init__(self):
		self.locale = locale.getdefaultlocale()[0]
		self.__loadMenus()

	def __loadMenus(self):
		self.applications = Menu()
		self.applications.tree = gmenu.lookup_tree('applications.menu', gmenu.FLAGS_SHOW_EMPTY|gmenu.FLAGS_INCLUDE_EXCLUDED|gmenu.FLAGS_INCLUDE_NODISPLAY)
		self.applications.visible_tree = gmenu.lookup_tree('applications.menu')
		self.applications.path = os.path.join(util.getUserMenuPath(), self.applications.tree.get_menu_file())
		if not os.path.isfile(self.applications.path):
			self.applications.dom = xml.dom.minidom.parseString(util.getUserMenuXml(self.applications.tree))
		else:
			self.applications.dom = xml.dom.minidom.parse(self.applications.path)
		self.__remove_whilespace_nodes(self.applications.dom)

		self.settings = Menu()
		self.settings.tree = gmenu.lookup_tree('settings.menu', gmenu.FLAGS_SHOW_EMPTY|gmenu.FLAGS_INCLUDE_EXCLUDED|gmenu.FLAGS_INCLUDE_NODISPLAY)
		self.settings.visible_tree = gmenu.lookup_tree('settings.menu')
		self.settings.path = os.path.join(util.getUserMenuPath(), self.settings.tree.get_menu_file())
		if not os.path.isfile(self.settings.path):
			self.settings.dom = xml.dom.minidom.parseString(util.getUserMenuXml(self.settings.tree))
		else:
			self.settings.dom = xml.dom.minidom.parse(self.settings.path)
		self.__remove_whilespace_nodes(self.settings.dom)

	def save(self):
		for menu in ('applications', 'settings'):
			fd = open(getattr(self, menu).path, 'w')
			fd.write(re.sub("\n[\s]*([^\n<]*)\n[\s]*</", "\\1</", getattr(self, menu).dom.toprettyxml().replace('<?xml version="1.0" ?>\n', '')))
			fd.close()
		self.__loadMenus()

	def getMenus(self, parent=None):
		if parent == None:
			return (self.applications.tree.root, self.settings.tree.root)
		temp = []
		for menu in parent.get_contents():
			if menu.get_type() == gmenu.TYPE_DIRECTORY:
				if menu.menu_id == 'Other' and len(menu.get_contents()) == 0:
					continue
				temp.append(menu)
		return temp

	def getItems(self, menu):
		temp = []
		for item in menu.get_contents():
			if item.get_type() == gmenu.TYPE_SEPARATOR:
				temp.append((item, True))
			else:
				if item.get_type() == gmenu.TYPE_ENTRY and item.get_desktop_file_id()[-19:] == '-usercustom.desktop':
					continue
				temp.append((item, self.__isVisible(item)))
		return temp

	def setVisible(self, item, visible):
		dom = self.__getMenu(item).dom
		if item.get_type() == gmenu.TYPE_ENTRY:
			menu_xml = self.__getXmlMenu(self.__getPath(item.get_parent()), dom, dom)
			if visible:
				self.__addXmlFilename(menu_xml, dom, item.get_desktop_file_id(), 'Include')
				self.__writeItem(item, no_display=False)
			else:
				self.__addXmlFilename(menu_xml, dom, item.get_desktop_file_id(), 'Exclude')
		elif item.get_type() == gmenu.TYPE_DIRECTORY:
			menu_xml = self.__getXmlMenu(self.__getPath(item), dom, dom)
			if visible:
				for node in self.__getXmlNodesByName(['Deleted', 'NotDeleted'], menu_xml):
					node.parentNode.removeChild(node)
				self.__writeMenu(item, no_display=False)
			else:
				self.__writeMenu(item, no_display=True)
		self.save()

	def hideItem(self, item):
		self.setVisible(item, False)

	def showItem(self, item):
		self.setVisible(item, True)

	def editItem(self, item, icon, name, comment, command, use_term):
		#if nothing changed don't make a user copy
		if icon == item.get_icon() and name == item.get_name() and \
			comment == item.get_comment() and command == item.get_exec() and \
			use_term == item.get_terminal():
			return
		self.__writeItem(item, icon, name, comment, command, use_term)
		self.save()

	def editMenu(self, menu, icon, name, comment):
		#if nothing changed don't make a user copy
		if icon == menu.get_icon() and name == menu.get_name() and comment == menu.get_comment():
			return
		#we don't use this, we just need to make sure the <Menu> exists
		#otherwise changes won't show up
		dom = self.__getMenu(menu).dom
		menu_xml = self.__getXmlMenu(self.__getPath(menu), dom, dom)
		self.__writeMenu(menu, icon, name, comment)
		self.save()

	def moveItem(self, item, after=None):
		pass

	#private stuff
	def __getMenu(self, item):
		root = item.get_parent()
		while True:
			if root.get_parent():
				root = root.get_parent()
			else:
				break
		if root.menu_id == self.applications.tree.root.menu_id:
			return self.applications
		return self.settings

	def __isVisible(self, item):
		if item.get_type() == gmenu.TYPE_ENTRY:
			return not (item.get_is_excluded() or item.get_is_nodisplay())
		def loop_for_menu(parent, menu):
			for item in parent.get_contents():
				if item.get_type() == gmenu.TYPE_DIRECTORY:
					if item.menu_id == menu.menu_id:
						return True
					temp = loop_for_menu(item, menu)
					if temp:
						return True
			return False
		menu = self.__getMenu(item)
		if menu == self.applications:
			root = self.applications.visible_tree.root
		elif menu == self.settings:
			root = self.settings.visible_tree.root
		if item.get_type() == gmenu.TYPE_DIRECTORY:
			return loop_for_menu(root, item)
		return True

	def __getPath(self, menu, path=None):
		if not path:
			path = 'Applications'
		if menu.get_parent():
			self.__getPath(menu.get_parent(), path)
			path += '/'
			path += menu.menu_id
		return path

	def __getXmlMenu(self, path, element, dom):
		if '/' in path:
			(name, path) = path.split('/', 1)
		else:
			name = path
			path = ''

		found = None
		for node in self.__getXmlNodesByName('Menu', element):
			for child in self.__getXmlNodesByName('Name', node):
				if child.childNodes[0].nodeValue == name:
					if path:
						found = self.__getXmlMenu(path, node, dom)
					else:
						found = node
					break
			if found:
				break
		if not found:
			node = self.__addXmlMenuElement(element, name, dom)
			if path:
				found = self.__getXmlMenu(path, node, dom)
			else:
				found = node

		return found

	def __addXmlMenuElement(self, element, name, dom):
		node = dom.createElement('Menu')
		self.__addXmlTextElement(node, 'Name', name, dom)
		return element.appendChild(node)

	def __addXmlTextElement(self, element, name, text, dom):
		node = dom.createElement(name)
		text = dom.createTextNode(text)
		node.appendChild(text)
		return element.appendChild(node)

	def __addXmlFilename(self, element, dom, filename, type = 'Include'):
		# remove old filenames
		for node in self.__getXmlNodesByName(['Include', 'Exclude'], element):
			if node.childNodes[0].nodeName == 'Filename' and node.childNodes[0].childNodes[0].nodeValue == filename:
				element.removeChild(node)

		# add new filename
		node = dom.createElement(type)
		node.appendChild(self.__addXmlTextElement(node, 'Filename', filename, dom))
		return element.appendChild(node)

	def __addDeleted(self, element, dom):
		node = dom.createElement('Deleted')
		return element.appendChild(node)

	def __writeItem(self, item, icon=None, name=None, comment=None, command=None, use_term=None, no_display=None, startup_notify=None):
		file_path = item.get_desktop_file_path()
		file_id = item.get_desktop_file_id()
		keyfile = util.DesktopParser(file_path)
		if icon:
			keyfile.set('Icon', icon)
			keyfile.set('Icon', icon, self.locale)
		if name:
			print name
			keyfile.set('Name', name)
			keyfile.set('Name', name, self.locale)
		if comment:
			keyfile.set('Comment', comment)
			keyfile.set('Comment', comment, self.locale)
		if command:
			keyfile.set('Exec', command)
		if use_term != None:
			keyfile.set('Terminal', use_term)
		if no_display != None:
			keyfile.set('NoDisplay', no_display)
		if startup_notify != None:
			keyfile.set('StartupNotify', startup_notify)
		out_path = os.path.join(util.getUserItemPath(), file_id)
		keyfile.write(open(out_path, 'w'))

	def __writeMenu(self, menu, icon=None, name=None, comment=None, no_display=None):
		file_id = menu.get_menu_id() + '.directory'
		file_path = util.getDirectoryPath(file_id)
		keyfile = util.DesktopParser(file_path)
		if icon:
			keyfile.set('Icon', icon)
		if name:
			keyfile.set('Name', name)
			keyfile.set('Name', name, self.locale)
		if comment:
			keyfile.set('Comment', comment)
			keyfile.set('Comment', comment, self.locale)
		if no_display != None:
			keyfile.set('NoDisplay', no_display)
		out_path = os.path.join(util.getUserDirectoryPath(), file_id)
		keyfile.write(open(out_path, 'w'))
		return out_path

	def __getXmlNodesByName(self, name, element):
		for	child in element.childNodes:
			if child.nodeType == xml.dom.Node.ELEMENT_NODE and child.nodeName in name:
				yield child

	def __remove_whilespace_nodes(self, node):
		remove_list = []
		for child in node.childNodes:
			if child.nodeType == xml.dom.minidom.Node.TEXT_NODE:
				child.data = child.data.strip()
				if not child.data.strip():
					remove_list.append(child)
			elif child.hasChildNodes():
				self.__remove_whilespace_nodes(child)
		for node in remove_list:
			node.parentNode.removeChild(node)

	#AFTER THIS STILL NOT PORTED
	def __addXmlMove(self, element, old, new):
		node = self.doc.createElement("Move")
		node.appendChild(self.__addXmlTextElement(node, 'Old', old))
		node.appendChild(self.__addXmlTextElement(node, 'New', new))
		return element.appendChild(node)

	def __addXmlLayout(self, element, layout):
		# remove old layout
		for node in self.__getXmlNodesByName("Layout", element):
			element.removeChild(node)

		# add new layout
		node = self.doc.createElement("Layout")
		for order in layout.order:
			if order[0] == "Separator":
				child = self.doc.createElement("Separator")
				node.appendChild(child)
			elif order[0] == "Filename":
				child = self.__addXmlTextElement(node, "Filename", order[1])
			elif order[0] == "Menuname":
				child = self.__addXmlTextElement(node, "Menuname", order[1])
			elif order[0] == "Merge":
				child = self.doc.createElement("Merge")
				child.setAttribute("type", order[1])
				node.appendChild(child)
		return element.appendChild(node)

	def __addLayout(self, parent):
		layout = Layout()
		layout.order = []
		layout.show_empty = parent.Layout.show_empty
		layout.inline = parent.Layout.inline
		layout.inline_header = parent.Layout.inline_header
		layout.inline_alias = parent.Layout.inline_alias
		layout.inline_limit = parent.Layout.inline_limit

		layout.order.append(["Merge", "menus"])
		for entry in parent.Entries:
			if isinstance(entry, Menu):
				layout.parseMenuname(entry.Name)
			elif isinstance(entry, MenuEntry):
				layout.parseFilename(entry.DesktopFileID)
			elif isinstance(entry, Separator):
				layout.parseSeparator()
		layout.order.append(["Merge", "files"])

		parent.Layout = layout

		return layout

	def __addEntry(self, parent, entry, after=None, before=None):
		if after or before:
			if after:
				index = parent.Entries.index(after) + 1
			elif before:
				index = parent.Entries.index(before)
			parent.Entries.insert(index, entry)
		else:
			parent.Entries.append(entry)

		xml_parent = self.__getXmlMenu(parent.getPath(True, True))

		if isinstance(entry, MenuEntry):
			parent.MenuEntries.append(entry)
			entry.Parents.append(parent)
			self.__addXmlFilename(xml_parent, entry.DesktopFileID, "Include")
		elif isinstance(entry, Menu):
			parent.addSubmenu(entry)

		if after or before:
			self.__addLayout(parent)
			self.__addXmlLayout(xml_parent, parent.Layout)

	def __deleteEntry(self, parent, entry, after=None, before=None):
		parent.Entries.remove(entry)

		xml_parent = self.__getXmlMenu(parent.getPath(True, True))

		if isinstance(entry, MenuEntry):
			entry.Parents.remove(parent)
			parent.MenuEntries.remove(entry)
			self.__addXmlFilename(xml_parent, entry.DesktopFileID, "Exclude")
		elif isinstance(entry, Menu):
			parent.Submenus.remove(entry)

		if after or before:
			self.__addLayout(parent)
			self.__addXmlLayout(xml_parent, parent.Layout)

	def __deleteFile(self, filename):
		try:
			os.remove(filename)
		except OSError:
			pass
		try:
			self.filenames.remove(filename)
		except ValueError:
			pass
