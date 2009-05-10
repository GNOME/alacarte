/* mainwindow.vala
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
using Gdk;
using Garcon;
using Config;


public class MainWindow
{
	private Builder builder;
	private Garcon.Menu applications;

	private Gdk.Pixbuf? get_icon (Garcon.MenuElement item)
	{
		Gdk.Pixbuf pixbuf = null;

		var icon_name = item.get_icon_name ();

		if (icon_name == null)
		{
			if (item is Garcon.Menu)
				icon_name = "gnome-fs-directory";
			else if (item is Garcon.MenuItem)
				icon_name = "application-default-icon";
		}

		if (icon_name != null)
		{
			// Strip extension if it is not an absolute path
			if (!GLib.Path.is_absolute (icon_name))
			{
				var basename = GLib.Path.get_basename (icon_name);
				var extension = basename.rchr (-1, '.');

				if (extension != null)
					icon_name = basename.substring (0, basename.size () - extension.size ());
			}

			var icon_theme = Gtk.IconTheme.get_default ();
			try
			{
				pixbuf = icon_theme.load_icon (icon_name, 24, Gtk.IconLookupFlags.USE_BUILTIN);
			}
			catch (Error e)
			{
				if (GLib.Path.is_absolute (icon_name) && GLib.FileUtils.test (icon_name, GLib.FileTest.EXISTS))
					pixbuf = new Gdk.Pixbuf.from_file_at_scale (icon_name, 24, 24, true);
			}
		}

		if (pixbuf != null)
			pixbuf = pixbuf.scale_simple (24, 24, Gdk.InterpType.BILINEAR);

		return pixbuf;
	}

	private void update_icons (Gtk.TreeIter iter)
	{
		Gtk.TreeIter child_iter;
		unowned Garcon.Menu menu;

		var tree_store = builder.get_object ("menu_tree_store") as Gtk.TreeStore;
		tree_store.get (iter, 2, out menu, -1);
		tree_store.set (iter, 0, get_icon (menu), -1);

		if (tree_store.iter_has_child (iter))
		{
			tree_store.iter_children (out child_iter, iter);
			do
			{
				update_icons (child_iter);
			} while (tree_store.iter_next (ref child_iter));
		}
	}

	private void show_menus (Gtk.TreeIter? parent, List<Garcon.MenuElement>? items)
	{
		Gtk.TreeIter iter;
		var tree_store = builder.get_object ("menu_tree_store") as Gtk.TreeStore;

		foreach (Garcon.MenuElement item in items)
		{
			if (!item.get_show_in_environment ())
				continue;
			if (item.get_no_display ())
				continue;

			if (item is Garcon.Menu)
			{
				var name = GLib.Markup.escape_text (item.get_name ());
				if (!item.get_visible ())
					name = "<small><i>" + name + "</i></small>";

				tree_store.append (out iter, parent);
				tree_store.set (iter, 0, get_icon (item), -1);
				tree_store.set (iter, 1, name, -1);
				tree_store.set (iter, 2, item);

				show_menus (iter, (item as Garcon.Menu).get_elements ());
			}
		}
	}

	private void show_items (Garcon.Menu parent)
	{
		Gtk.TreeIter iter;
		var list_store = builder.get_object ("item_tree_store") as Gtk.ListStore;
		list_store.clear ();

		unowned List<Garcon.MenuElement> items = parent.get_elements ();
		foreach (Garcon.MenuElement item in items)
		{
			if (!item.get_show_in_environment ())
				continue;
			if (item.get_no_display ())
				continue;

			list_store.append (out iter);

			var name = item.get_name ();
			if (name == null)
				name = "---";
			name = GLib.Markup.escape_text (name);

			if (!item.get_visible ())
				name = "<small><i>" + name + "</i></small>";

			list_store.set (iter, 0, item.get_visible (), -1);
			list_store.set (iter, 1, get_icon (item), -1);
			list_store.set (iter, 2, name, -1);
			list_store.set (iter, 3, item);
		}
	}

	private void fill_trees ()
	{
		//menu tree
		var column = builder.get_object ("menu_column") as Gtk.TreeViewColumn;
		column.set_spacing (4);

		var pixbuf_cell = new Gtk.CellRendererPixbuf ();
		column.pack_start (pixbuf_cell, false);
		column.add_attribute (pixbuf_cell, "pixbuf", 0);

		var text_cell = new Gtk.CellRendererText ();
		text_cell.set_fixed_size (-1, 25);
		column.pack_start (text_cell, true);
		column.add_attribute (text_cell, "markup", 1);

		//item tree
		column = builder.get_object ("show_column") as Gtk.TreeViewColumn;
		var toggle_cell = new Gtk.CellRendererToggle ();
		//toggle_cell.connect ("toggled", (GLib.Callback) on_item_tree_show_toggled);
		column.pack_start (toggle_cell, true);
		column.add_attribute (toggle_cell, "active", 0);
		// Hide toggle for separators
		column.set_cell_data_func (toggle_cell, toggle_cell_data_toggle_func);

		column = builder.get_object ("item_column") as Gtk.TreeViewColumn;
		column.set_spacing (4);

		var pixbuf_cell2 = new Gtk.CellRendererPixbuf ();
		column.pack_start (pixbuf_cell2, false);
		column.add_attribute (pixbuf_cell2, "pixbuf", 1);

		var text_cell2 = new Gtk.CellRendererText ();
		text_cell2.set_fixed_size (-1, 25);
		column.pack_start (text_cell2, true);
		column.add_attribute (text_cell2, "markup", 2);


		//start adding the menus here
		applications = new Garcon.Menu.applications ();
		applications.load (null);
		unowned List<Garcon.MenuElement> items = applications.get_elements ();

		Gtk.TreeIter iter;
		var tree_store = builder.get_object ("menu_tree_store") as Gtk.TreeStore;
		tree_store.append (out iter, null);
		tree_store.set (iter, 0, get_icon (applications), -1);
		tree_store.set (iter, 1, GLib.Markup.escape_text (applications.get_name ()), -1);
		tree_store.set (iter, 2, applications);

		show_menus (iter, items);

		// automatically expand top level and select the first item
		var path = tree_store.get_path (iter);
		var tree_view = builder.get_object ("menu_tree") as Gtk.TreeView;
		var selection = tree_view.get_selection ();
		selection.select_path (path);
		tree_view.expand_row (path, false);
		on_menu_tree_cursor_changed (tree_view);
	}

	[CCode (instance_pos = -1)]
	private void connect_signals (Builder builder, GLib.Object object,
								  string signal_name, string handler_name,
								  GLib.Object? connect_object,
								  ConnectFlags flags)
	{
		var module = Module.open (null, ModuleFlags.BIND_LAZY);
		void* sym;

		var real_handler_name = "main_window_" + handler_name;

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
			builder = new Builder ();
			builder.add_from_file (Config.pkgdatadir + "/alacarte.ui");
		}
		catch (Error e)
		{
			var msg = new MessageDialog (null, DialogFlags.MODAL,
										 MessageType.ERROR, ButtonsType.CLOSE,
										 "Failed to load UI\n%s", e.message);
			msg.run ();
		}

		builder.connect_signals_full (connect_signals);
		var window = builder.get_object ("main_window") as Gtk.Window;
		window.show_all ();
		fill_trees ();
		Gtk.main ();
	}

	private void toggle_cell_data_toggle_func (Gtk.CellLayout cell_layout,
												Gtk.CellRenderer cell,
												Gtk.TreeModel tree_model,
												Gtk.TreeIter iter)
	{
		unowned Garcon.MenuElement item;
		tree_model.get (iter, 3, out item, -1);
		if (item is Garcon.MenuSeparator)
			cell.visible = false;
		else
			cell.visible = true;
	}

	[CCode (instance_pos = -1)]
	public void on_style_set (Gtk.Window window, Gtk.Style prev_style)
	{
		Gtk.TreeIter iter;
		Gtk.TreeIter selected_iter;
		Gtk.TreePath selected_path;
		weak Gtk.TreeModel model;

		var tree_store = builder.get_object ("menu_tree_store") as Gtk.TreeStore;
		tree_store.get_iter_first (out iter);
		do
		{
			update_icons (iter);
		} while (tree_store.iter_next (ref iter));

		//first get the selection for the item tree
		var list_view = builder.get_object ("item_tree") as Gtk.TreeView;
		var selection = list_view.get_selection ();
		selection.get_selected (out model, out selected_iter);
		//iters don't work after you clear the model, get the path
		selected_path = model.get_path (selected_iter);

		//reloading the item tree will update the icons...
		var tree_view = builder.get_object ("menu_tree") as Gtk.TreeView;
		on_menu_tree_cursor_changed (tree_view);

		//now selected the previously selected item
		selection.select_path (selected_path);
	}

	[CCode (instance_pos = -1)]
	public void on_help_button_clicked (Gtk.Button button)
	{
		var main_window = builder.get_object ("main_window") as Gtk.Window;
		var screen = main_window.get_screen ();

		try
		{
			Gtk.show_uri (screen, "ghelp:user-guide#menu-editor", 
						  Gtk.get_current_event_time ());
		}
		catch (Error e)
		{
			var msg = new MessageDialog (null, DialogFlags.MODAL,
										 MessageType.ERROR, ButtonsType.CLOSE,
										 "%s", "Unable to open help file");
			msg.format_secondary_text ("%s", e.message);
			msg.run ();
		}
	}

	[CCode (instance_pos = -1)]
	public void on_close_button_clicked (GLib.Object garbage)
	{
		Gtk.main_quit ();
	}



	//start of menu tree signal handlers
	[CCode (instance_pos = -1)]
	public void on_menu_tree_cursor_changed (Gtk.TreeView tree_view)
	{
		Gtk.TreeIter iter;
		weak Gtk.TreeModel model;
		unowned Garcon.Menu menu;

		var selection = tree_view.get_selection ();
		selection.get_selected (out model, out iter);

		model.get (iter, 2, out menu, -1);
		show_items (menu);
	}


	//start of item tree signal handlers
	public bool do_popup_menu (Gtk.Widget widget, Gdk.EventButton? event)
	{
		uint button;
		uint event_time;

		var menu = builder.get_object ("edit_menu") as Gtk.Menu;

		if (event != null)
		{
			//ignore double-clicks and triple-clicks
			if (event.button != 3 || event.type != Gdk.EventType.BUTTON_PRESS)
				return false;

			button = event.button;
			event_time = event.time;
		}
		else
		{
			button = 0;
			event_time = Gtk.get_current_event_time ();
		}

		//menu.attach_to_widget (widget, Gtk.Object.destroy);
		menu.popup (null, null, null, button, event_time);

		return true;
	}

	[CCode (instance_pos = -1)]
	public bool on_item_tree_popup_menu (Gtk.Widget widget)
	{
		return do_popup_menu (widget, null);
	}

	[CCode (instance_pos = -1)]
	public bool on_item_tree_button_press_event (Gtk.Widget widget, Gdk.EventButton event)
	{
		return do_popup_menu (widget, event);
	}
}

static int main (string[] args)
{
	Garcon.init ("GNOME");
	Gtk.init (ref args);

	var main_window = new MainWindow ();
	main_window.run ();
	Garcon.shutdown ();

	return 0;
}

