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
from gettext import gettext as _

from gi import require_version

require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from .add import AccountConfig

@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/account_edit.ui')
class EditAccountWindow(Gtk.Window, GObject.GObject):
    __gsignals__ = {
        'updated': (GObject.SignalFlags.RUN_LAST, None, (str, str,)),
    }

    __gtype_name__ = 'EditAccountWindow'

    headerbar = Gtk.Template.Child()
    save_btn = Gtk.Template.Child()

    def __init__(self, account):
        super(EditAccountWindow, self).__init__()
        self.init_template('EditAccountWindow')
        GObject.GObject.__init__(self)

        self._account = account

        self.__init_widgets()

    def __init_widgets(self):
        self.headerbar.set_title(_("Edit {} - {}".format(self._account.username,
                                                         self._account.provider)))

        self.account_config = AccountConfig(edit=True, account=self._account)
        self.account_config.connect("changed", self._on_account_config_changed)

        self.add(self.account_config)

    def _on_account_config_changed(self, _, state):
        """
        Set the sensitivity of the AddButton
            depends on the AccountConfig.

        :param state: the state of the save button
        :type state: bool
        """
        self.save_btn.set_sensitive(state)

    @Gtk.Template.Callback('save_btn_clicked')
    def _on_save(self, *_):
        """
            Save Button clicked signal handler.
        """
        new_account = self.account_config.account
        username = new_account["username"]
        provider = new_account["provider"]
        old_provider = self._account.provider
        # Update the AccountRow widget
        self.emit("updated", username, provider)
        # Update the providers list
        if provider != old_provider:
            from .list import AccountsWidget
            ac_widget = AccountsWidget.get_default()
            ac_widget.update_provider(self._account, provider)
        self._on_quit()

    @Gtk.Template.Callback('close_btn_clicked')
    def _on_quit(self, *_):
        """
            Close the window.
        """
        self.destroy()
