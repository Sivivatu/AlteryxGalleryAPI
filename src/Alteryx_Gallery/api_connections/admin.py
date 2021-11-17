import json
import requests
from Alteryx_Gallery.gallery_connection import Gallery

class GalleryAdmin(Gallery):
    '''Extends the Gallery Class containing connection to access Alteryx Server API endpoints'''
    def __init__(self, api_location: str, api_key: str, api_secret: str):
        super().__init__(self.api_location, self.api_key, self.api_secret)
        api_location_base = api_location.rsplit("/", 1)
        self.api_location = api_location_base[0]+ "/admin/" + api_location_base[1] + "/"

    @property
    def api_location(self):
        return self._api_location

    @api_location.setter
    def api_location(self, loc):
        if not loc:
            raise Exception("'api_location' cannot be empty")
        if not isinstance(loc, str):
            raise TypeError(f"Invalid type {type(loc)} for variable 'api_location'")
        api_location_base = loc.rsplit("/", 1)
        self.api_location = api_location_base[0]+ "/admin/" + api_location_base[1] + "/"

    @property
    def admin_api_key(self):
        '''return the admin key property'''
        return self._api_key

    @admin_api_key.setter
    def admin_api_key(self, key):
        if not key:
            raise Exception("'api_key' cannot be empty and should be an admin key")
        if not isinstance(key, str):
            raise TypeError(f"Invalid type: {type(key)} for variable 'api_key'")
        self._api_key = key

    @property
    def admin_api_secret(self):
        '''return the admin api secret'''
        return self._api_secret

    @admin_api_secret.setter
    def api_secret(self, secret_key):
        if not secret_key:
            raise Exception("'api_secret' cannot be empty")
        if not isinstance(secret_key, str):
            raise TypeError(f"Invalid type {type(secret_key)} for variable 'api_secret'")
        self._api_secret = secret_key

    def get_workflows_migratable(self, app_id = None, **kwargs):
        """:return: Generate a list of workflows that have been set as migratable"""
        method = 'GET'
        url = self.api_location + '/workflows/migratable'
        params = self.build_oauth_params()
        signature = self.generate_signature(method, url, params)
        params.update({'oauth_signature': signature})
        response = requests.get(url, params=params)
        output, output_content = response, json.loads(response.content.decode("utf8"))
        return output, output_content
