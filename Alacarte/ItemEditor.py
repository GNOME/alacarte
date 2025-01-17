# -*- coding: utf-8 -*-
#   Alacarte Menu Editor - Simple fd.o Compliant Menu Editor
#   Copyright (C) 2013  Red Hat, Inc.
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

import cairo
import gettext
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk, Gdk, GdkPixbuf
from Alacarte import config, util

_ = gettext.gettext

EXTENSIONS = (".png", ".xpm", ".svg")

def try_icon_name(filename):
    # Detect if the user picked an icon, and make
    # it into an icon name.
    if not filename.endswith(EXTENSIONS):
        return filename

    theme = Gtk.IconTheme.get_default()
    resolved_path = None
    for path in theme.get_search_path():
        if filename.startswith(path):
            resolved_path = filename[len(path):].lstrip(os.sep)
            break

    if resolved_path is None:
        return filename

    parts = resolved_path.split(os.sep)
    # icon-theme/size/category/icon
    if len(parts) != 4:
        return filename

    icon_name = parts[3]

    # strip extension
    return icon_name[:-4]

def get_icon_string(editor, image):
    filename = editor.icon_file
    if filename is not None:
        return try_icon_name(filename)

    return image.props.icon_name

def strip_extensions(icon):
    if icon.endswith(EXTENSIONS):
        return icon[:-4]
    else:
        return icon

def set_icon_file(editor, image, file_name):
    editor.icon_file = file_name

    scale = image.get_scale_factor()
    size = 64 * scale

    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(file_name, size, size)
    except GLib.GError:
        return

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)

    context = cairo.Context(surface)
    Gdk.cairo_set_source_pixbuf(context,
                                pixbuf,
                                (size - pixbuf.get_width()) / 2,
                                (size - pixbuf.get_height()) / 2)
    context.paint()

    surface.set_device_scale(scale, scale)
    image.props.surface = surface

def set_icon_string(editor, image, icon):
    if GLib.path_is_absolute(icon):
        set_icon_file(editor, image, icon)
    else:
        image.props.icon_name = strip_extensions(icon)

DESKTOP_GROUP = GLib.KEY_FILE_DESKTOP_GROUP

# XXX - replace with a better UI eventually
class IconPicker(object):
    def __init__(self, editor, dialog, button, image):
        self.editor = editor
        self.dialog = dialog
        self.button = button
        self.button.connect('clicked', self.pick_icon)
        self.image = image

    def pick_icon(self, button):
        chooser = Gtk.FileChooserDialog(title=_("Choose an icon"),
                                        parent=self.dialog,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                        Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))

        filter = Gtk.FileFilter()
        filter.set_name(_("Images"));
        filter.add_mime_type("image/*")
        chooser.add_filter(filter)

        response = chooser.run()
        if response == Gtk.ResponseType.ACCEPT:
            set_icon_file(self.editor, self.image, chooser.get_filename())
        chooser.destroy()

class ItemEditor(GObject.GObject):
    icon_file = None
    ui_file = None

    __gsignals__ = {
        'response': (GObject.SIGNAL_RUN_FIRST, None, (bool,))
    }

    def __init__(self, parent, item_path):
        GObject.GObject.__init__(self)
        self.builder = Gtk.Builder()
        self.builder.add_from_file(os.path.join(config.pkgdatadir, self.ui_file))

        self.dialog = self.builder.get_object('editor')
        self.dialog.set_transient_for(parent)
        self.dialog.connect('response', self.on_response)

        self.build_ui()

        self.item_path = item_path
        self.load()
        self.resync_validity()

    def build_ui(self):
        raise NotImplementedError()

    def get_keyfile_edits(self):
        raise NotImplementedError()

    def set_text(self, ctl, name):
        try:
            val = self.keyfile.get_string(DESKTOP_GROUP, name)
        except GLib.GError:
            pass
        else:
            self.builder.get_object(ctl).set_text(val)

    def set_check(self, ctl, name):
        try:
            val = self.keyfile.get_boolean(DESKTOP_GROUP, name)
        except GLib.GError:
            pass
        else:
            self.builder.get_object(ctl).set_active(val)

    def set_icon(self, ctl, name):
        try:
            val = self.keyfile.get_string(DESKTOP_GROUP, name)
        except GLib.GError:
            pass
        else:
            set_icon_string(self, self.builder.get_object(ctl), val)

    def load(self):
        self.keyfile = GLib.KeyFile()
        try:
            self.keyfile.load_from_file(self.item_path, util.KEY_FILE_FLAGS)
        except GLib.GError:
            pass

    def save(self):
        util.fillKeyFile(self.keyfile, self.get_keyfile_edits())
        contents, length = self.keyfile.to_data()
        with open(self.item_path, 'w') as f:
            f.write(contents)

    def run(self):
        self.dialog.present()

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.save()
        self.dialog.destroy()
        self.emit('response', response == Gtk.ResponseType.OK)

class LauncherEditor(ItemEditor):
    ui_file = 'launcher-editor.ui'

    def build_ui(self):
        self.icon_picker = IconPicker(self,
                                      self.dialog,
                                      self.builder.get_object('icon-button'),
                                      self.builder.get_object('icon-image'))

        self.builder.get_object('exec-browse').connect('clicked', self.pick_exec)

        self.builder.get_object('name-entry').connect('changed', self.resync_validity)
        self.builder.get_object('exec-entry').connect('changed', self.resync_validity)
        self.dialog.connect('focus-in-event', self.resync_validity)

    def exec_line_is_valid(self, exec_text):
        try:
            success, parsed = GLib.shell_parse_argv(exec_text)

            # Make sure program (first part of the command) is in the path
            command = parsed[0]
            return (GLib.find_program_in_path(command) is not None)
        except GLib.GError:
            return False

    def resync_validity(self, *args):
        name_text = self.builder.get_object('name-entry').get_text()
        exec_text = self.builder.get_object('exec-entry').get_text()
        valid = (name_text != "" and self.exec_line_is_valid(exec_text))
        self.builder.get_object('ok').set_sensitive(valid)

    def load(self):
        super(LauncherEditor, self).load()
        self.set_text('name-entry', "Name")
        self.set_text('exec-entry', "Exec")
        self.set_text('comment-entry', "Comment")
        self.set_check('terminal-check', "Terminal")
        self.set_icon('icon-image', "Icon")

    def get_keyfile_edits(self):
        return dict(Name=self.builder.get_object('name-entry').get_text(),
                    Exec=self.builder.get_object('exec-entry').get_text(),
                    Comment=self.builder.get_object('comment-entry').get_text(),
                    Terminal=self.builder.get_object('terminal-check').get_active(),
                    Icon=get_icon_string(self, self.builder.get_object('icon-image')),
                    Type="Application")

    def pick_exec(self, button):
        chooser = Gtk.FileChooserDialog(title=_("Choose a command"),
                                        parent=self.dialog,
                                        buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,
                                        Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
        response = chooser.run()
        if response == Gtk.ResponseType.ACCEPT:
            self.builder.get_object('exec-entry').set_text(chooser.get_filename())
        chooser.destroy()

class DirectoryEditor(ItemEditor):
    ui_file = 'directory-editor.ui'

    def build_ui(self):
        self.icon_picker = IconPicker(self,
                                      self.dialog,
                                      self.builder.get_object('icon-button'),
                                      self.builder.get_object('icon-image'))

        self.builder.get_object('name-entry').connect('changed', self.resync_validity)

    def resync_validity(self, *args):
        name_text = self.builder.get_object('name-entry').get_text()
        valid = (name_text != "")
        self.builder.get_object('ok').set_sensitive(valid)

    def load(self):
        super(DirectoryEditor, self).load()
        self.set_text('name-entry', "Name")
        self.set_text('comment-entry', "Comment")
        self.set_icon('icon-image', "Icon")

    def get_keyfile_edits(self):
        return dict(Name=self.builder.get_object('name-entry').get_text(),
                    Comment=self.builder.get_object('comment-entry').get_text(),
                    Icon=get_icon_string(self, self.builder.get_object('icon-image')),
                    Type="Directory")

def test_editor(path):
    if path.endswith('.directory'):
        return DirectoryEditor(path)
    elif path.endswith('.desktop'):
        return LauncherEditor(path)
    else:
        raise ValueError("Invalid filename, %r" % (path,))

def test():
    import sys

    Gtk.Window.set_default_icon_name('alacarte')
    editor = test_editor(sys.argv[1])
    editor.dialog.connect('destroy', Gtk.main_quit)
    editor.run()
    Gtk.main()

if __name__ == "__main__":
    test()
