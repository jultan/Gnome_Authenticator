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
from Authenticator.models import Database

class Provider:

    instance = None

    def __init__(self, provider_id=None, name=None, website=None, doc_url=None, image=None):
        self.provider_id = provider_id
        self.name = name
        self.website = website
        self.doc_url = doc_url
        self.image = image

    @staticmethod
    def get_default():
        if ProviderManager.instance is None:
            ProviderManager.instance = ProviderManager()
        return ProviderManager.instance

    @staticmethod
    def get_by_id(id_):
        provider = Database.get_default().provider_by_id(id_)
        if provider:
            return Provider(*provider)
        return None

    @staticmethod
    def get_by_name(name):
        provider = Database.get_default().provider_by_name(name)
        if provider:
            return Provider(*provider)
        return None
    
    @staticmethod
    def all():
        providers = Database.get_default().get_providers()
        return [
            Provider(*provider)
            for provider in providers
        ]


    @staticmethod
    def create(name, website, doc_url, image):
        provider = Database.get_default().insert_provider(name, website, doc_url, image)
        return Provider(*provider)

    def update(self, provider_data):
        self.image = provider_data.get("image", self.image)
        self.name = provider_data.get("name", self.name)
        Database.get_default().update_provider(provider_data, self.provider_id)

