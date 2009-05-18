/* util.vala
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

namespace Util
{
	private Gdk.Pixbuf? get_icon (Garcon.MenuElement item, int size = 24)
	{
		var icon_theme = Gtk.IconTheme.get_default ();
		Gdk.Pixbuf pixbuf = null;

		var icon_name = item.get_icon_name ();
		if (icon_name != null)
		{
			// Strip extension if it is a common icon extension
			if (!GLib.Path.is_absolute (icon_name))
			{
				if (icon_name.has_suffix (".xpm") ||
					icon_name.has_suffix (".png") ||
					icon_name.has_suffix (".jpg") ||
					icon_name.has_suffix (".gif"))
				{
					var basename = GLib.Path.get_basename (icon_name);
					var extension = basename.rchr (-1, '.');

					if (extension != null)
						icon_name = basename.substring (0, basename.size () - extension.size ());
				}
			}

			try
			{
				pixbuf = icon_theme.load_icon (icon_name, size, Gtk.IconLookupFlags.USE_BUILTIN);
			}
			catch (Error e)
			{
				if (GLib.Path.is_absolute (icon_name) && GLib.FileUtils.test (icon_name, GLib.FileTest.EXISTS))
					pixbuf = new Gdk.Pixbuf.from_file_at_scale (icon_name, size, size, true);
			}
		}

		if (pixbuf == null)
		{
			if (item is Garcon.Menu)
				icon_name = "gnome-fs-directory";
			else if (item is Garcon.MenuItem)
				icon_name = "application-default-icon";
			else
				return null;

			pixbuf = icon_theme.load_icon (icon_name, size, Gtk.IconLookupFlags.USE_BUILTIN);
		}

		if (pixbuf != null)
			pixbuf = pixbuf.scale_simple (size, size, Gdk.InterpType.BILINEAR);

		return pixbuf;
	}
}

