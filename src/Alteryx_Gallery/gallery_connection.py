import secrets
import time
import collections
import math
import base64
import urllib
import hmac
import hashlib
from abc import ABC
import requests


class Gallery(ABC):
    '''
    Base Class for a gallery connection details
    Order of arguments: api_location, api_key, api_secret
    '''
    def __init__(self, api_location: str, api_key: str, api_secret: str):
        self.api_location = api_location
        self.api_key = api_key
        self.api_secret = api_secret

    @property
    def api_location(self):
        '''define the api location as a property'''
        return self._api_location

    @api_location.setter
    def api_location(self, loc):
        if not loc:
            raise Exception("'api_location' cannot be empty")
        if not isinstance(loc, str):
            raise TypeError(f"Invalid type {type(loc)} for variable 'api_location'")
        self._api_location = loc

    @property
    def api_key(self):
        '''define the api key as a property'''
        return self._api_key

    @api_key.setter
    def api_key(self, key):
        if not key:
            raise Exception("'api_key' cannot be empty")
        if not isinstance(key, str):
            raise TypeError(f"Invalid type: {type(key)} for variable 'api_key'")
        self._api_key = key

    @property
    def api_secret(self):
        '''define the api secret as a property'''
        return self._api_secret

    @api_secret.setter
    def api_secret(self, secret_key):
        if not secret_key:
            raise Exception("'api_secret' cannot be empty")
        if not isinstance(secret_key, str):
            raise TypeError(f"Invalid type {type(secret_key)} for variable 'api_secret'")
        self._api_secret = secret_key

    def build_oauth_params(self) -> dict:
        """
        :return:  A dictionary consisting of params for third-party
        signature generation code based upon the OAuth 1.0a standard.
        """
        return {'oauth_timestamp': str(int(math.floor(time.time()))),
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_consumer_key': self.api_key,
                'oauth_version': '1.0',
                'oauth_nonce': secrets.token_urlsafe(5),
                }

    def generate_signature(self, http_method, url, params) -> dict:
        """
        :return: returns HMAC-SHA1 signature
        """
        def quote(x):
            return requests.utils.quote(x, safe="~")
        sorted_params = collections.OrderedDict(sorted(params.items()))

        normalized_params = urllib.parse.urlencode(sorted_params)
        base_string = "&".join((http_method.upper(), quote(url), quote(normalized_params)))

        secret_bytes = bytes("&".join([self.api_secret, '']), 'ascii')
        base_bytes = bytes(base_string, 'ascii')
        sig = hmac.new(secret_bytes, base_bytes, hashlib.sha1)
        return base64.b64encode(sig.digest())
