/* elementeditor.vala
 *
 * Copyright (C) 2009 Travis Watkins
 *
 * This library is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 2.1 of the License, or
 * (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Author:
 *      Travis Watkins <amaranth@ubuntu.com>
 */

using GLib;
using Gtk;
using Garcon;
using Config;

public class ElementEditor
{
	private Builder builder;
	private Garcon.MenuElement element;
	private Garcon.Menu parent;
	private string new_type;


	public ElementEditor (Garcon.MenuElement element)
	{
		this.element = element;
	}

	public ElementEditor.new_item (Garcon.Menu parent, string new_type)
	{
		this.parent = parent;
		this.new_type = new_type;
	}

	private void setup_dialog ()
	{
		var dialog = builder.get_object ("element_dialog") as Gtk.Dialog;

		if (element != null)
		{
			var cancel_button = builder.get_object ("cancel_button") as Gtk.Button;
			cancel_button.set_label (Gtk.STOCK_REVERT_TO_SAVED);
			var ok_button = builder.get_object ("ok_button") as Gtk.Button;
			ok_button.set_label (Gtk.STOCK_CLOSE);

			var name_entry = builder.get_object ("element_name_entry") as Gtk.Entry;
			name_entry.set_text (element.get_name ());
			name_entry.select_region (0, -1);
			var comment_entry = builder.get_object ("element_comment_entry") as Gtk.Entry;
			comment_entry.set_text (element.get_comment ());

			var icon_button = builder.get_object ("icon_button") as Gtk.Button;
			var image = new Gtk.Image.from_pixbuf (Util.get_icon (element, 48));
			icon_button.set_image (image);
		}

		if (element != null && element is Garcon.MenuItem)
		{
			dialog.set_title ("Item Properties");
			var item = element as Garcon.MenuItem;
			var type_combo = builder.get_object ("item_type_combo") as Gtk.ComboBox;
			var renderer = new Gtk.CellRendererText ();
			type_combo.pack_start (renderer, false);
			type_combo.set_attributes (renderer, "text", 0, null);
			if (item.requires_terminal)
				type_combo.set_active (1);
			else
				type_combo.set_active (0);

			var command_entry = builder.get_object ("item_command_entry") as Gtk.Entry;
			command_entry.set_text (item.command);
		}
		else if ((element != null && element is Garcon.Menu) || new_type == "menu")
		{
			dialog.set_title ("Menu Properties");
			var type_combo = builder.get_object ("item_type_combo") as Gtk.ComboBox;
			var type_label = builder.get_object ("item_type_label") as Gtk.Label;
			var command_label = builder.get_object ("item_command_label") as Gtk.Label;
			var command_entry = builder.get_object ("item_command_entry") as Gtk.Entry;
			var command_button = builder.get_object ("item_command_button") as Gtk.Button;
			(type_combo.get_parent () as Gtk.Container).remove (type_combo);
			(type_label.get_parent () as Gtk.Container).remove (type_label);
			(command_label.get_parent () as Gtk.Container).remove (command_label);
			(command_entry.get_parent () as Gtk.Container).remove (command_entry);
			(command_button.get_parent () as Gtk.Container).remove (command_button);

			var table = builder.get_object ("element_table") as Gtk.Table;
			table.resize (2, 2);
		}
	}

	[CCode (instance_pos = -1)]
	private void connect_signals (Builder builder, GLib.Object object,
								  string signal_name, string handler_name,
								  GLib.Object? connect_object,
								  ConnectFlags flags)
	{
		var module = Module.open (null, ModuleFlags.BIND_LAZY);
		void* sym;

		var real_handler_name = "element_editor_" + handler_name;

		if (!module.symbol (real_handler_name, out sym))
		{
			stdout.printf ("Symbol %s not found!\n", real_handler_name);
		}
		else
		{
			Signal.connect (object, signal_name, (GLib.Callback) sym, this);
		}
	}

	public void run ()
	{
		try
		{
			string[] objects = {
				"element_dialog",
				"item_type_store",
				null
			};
			builder = new Builder ();
			builder.add_objects_from_file (Config.pkgdatadir + "/alacarte.ui", objects);
		}
		catch (Error e)
		{
			var msg = new MessageDialog (null, DialogFlags.MODAL,
										 MessageType.ERROR, ButtonsType.CLOSE,
										 "Failed to load UI\n%s", e.message);
			msg.run ();
		}

		builder.connect_signals_full (connect_signals);
		setup_dialog ();
		var dialog = builder.get_object ("element_dialog") as Gtk.Dialog;
		dialog.show_all ();
	}
}

