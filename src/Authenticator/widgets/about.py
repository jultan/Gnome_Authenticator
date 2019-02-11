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
from gi.repository import Gtk


@Gtk.Template(resource_path='/com/github/bilelmoussaoui/Authenticator/about_dialog.ui')
class AboutDialog(Gtk.AboutDialog):
    """
        AboutDialog Widget.
    """
    __gtype_name__ ="AboutDialog"

    def __init__(self):
        super().__init__(self)

    def __repr__(self):
        return '<AboutDialog>'
