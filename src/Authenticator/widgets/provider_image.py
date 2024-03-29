"""
 Copyright © 2017 Bilal Elmoussaoui <bil.elmoussaoui@gmail.com>

 This file is part of Authenticator.

 Authenticator is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as published
 by the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Authenticator is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Authenticator. If not, see <http://www.gnu.org/licenses/>.
"""

from gi.repository import Gtk, GObject, GdkPixbuf, GLib, Gio
from os import path
from tempfile import NamedTemporaryFile
from threading import Thread

from Authenticator.models import FaviconManager, Provider


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/provider_image.ui')
class ProviderImage(Gtk.Stack):
    """
        An Object that represents the provider service's image

        It contains a Gtk.Spinner and a Gtk.Image inside a Gtk.Stack
        It shows the Spinner when the provider image is being downloaded,
        once the download was successful, we show that image
    """

    __gtype_name__ = 'ProviderImage'
    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, (str, str, )),
        'image-downloaded': (GObject.SignalFlags.RUN_FIRST, None, (str, ))
    }

    provider_image = Gtk.Template.Child()
    provider_spinner = Gtk.Template.Child()
    insert_image = Gtk.Template.Child()
    not_found_box = Gtk.Template.Child()

    _timeout_id = 0

    def __init__(self, provider=None, image_size=48):
        super(ProviderImage, self).__init__()
        self.init_template('ProviderImage')
        self.provider = provider if provider else Provider()
        self.image_size = image_size
        self.not_found_box.props.width_request = image_size
        self.not_found_box.props.height_request = image_size
        self.provider_image.set_pixel_size(image_size)
        self.connect("changed", self.__on_provider_changed)
        if self.provider.image:
            self.set_image(self.provider.image)
            self.set_visible_child_name("provider_image")
        else:
            self.set_visible_child_name("provider_not_found")

    def emit(self, *args):
        GLib.idle_add(GObject.GObject.emit, self, *args)

    @property
    def image(self):
        if self.provider:
            return self.provider.image
        return None

    def set_image(self, image):
        updated = False
        if len(path.split(image)) == 2:
            image = path.join(FaviconManager.CACHE_DIR, image)
            updated = True
        try:
            if image and path.exists(image):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image, self.image_size, self.image_size)

                if pixbuf and (pixbuf.props.width != self.image_size or pixbuf.props.height != self.image_size):
                    pixbuf = pixbuf.scale_simple(self.image_size, self.image_size,
                                                 GdkPixbuf.InterpType.BILINEAR)
                if updated and self.provider:
                    self.provider.update(image=image)
                self.provider_image.set_from_pixbuf(pixbuf)
                self.set_visible_child_name("provider_image")
                return True
        except GLib.Error:
            pass

        self.set_visible_child_name("provider_not_found")
        return False

    # Callbacks

    @Gtk.Template.Callback('select_image_clicked')
    def __on_select_image_clicked(self, *args):
        dialog = Gtk.FileChooserNative()
        dialog.set_action(Gtk.FileChooserAction.OPEN)
        dialog.set_transient_for(self.get_toplevel())

        # Allow to select images only
        images_filter = Gtk.FileFilter()
        mimes = ('image/jpeg', 'image/png', 'image/svg+xml')
        for mime_type in mimes:
            images_filter.set_name(mime_type)
            images_filter.add_mime_type(mime_type)
        dialog.add_filter(images_filter)

        if dialog.run() == Gtk.ResponseType.ACCEPT:
            file_uri = dialog.get_uri()
            cache_file = self.__create_cache_file(file_uri)
            self.set_image(cache_file)
        dialog.destroy()

    # Signals

    def __on_provider_changed(self, _, provider_website, provider_image):
        self.provider_spinner.start()
        self.set_visible_child_name("provider_spinner")

        if provider_image and provider_website:
            favicon_manager = FaviconManager()
            t = Thread(target=lambda: favicon_manager.grab_favicon(provider_image,
                                                                   provider_website,
                                                                   self.__on_favicon_downloaded)
                       )
            t.daemon = True
            t.start()
        else:
            if provider_image:
                self.set_image(provider_image)
            self.set_visible_child_name("provider_image")

    # Private

    def __create_cache_file(self, file_uri):
        """
            Store a copy of the image under the cache dir of Authenticator.
        """
        gfile = Gio.File.new_for_uri(file_uri)
        # Copy file to cache dir
        cache_filename = path.basename(NamedTemporaryFile().name)
        destination_file = path.join(FaviconManager.CACHE_DIR, cache_filename)
        dfile = Gio.File.new_for_path(destination_file)
        gfile.copy(dfile, Gio.FileCopyFlags.NONE, None, None, None)

        self.set_image(destination_file)
        return destination_file

    def __on_favicon_downloaded(self, img_path):
        self.emit("image-downloaded", img_path)

    def do_image_downloaded(self, img_path):
        self.provider_spinner.stop()
        if img_path:
            self.set_image(img_path)
            self.set_visible_child_name("provider_image")
        else:
            self.set_visible_child_name("provider_not_found")
