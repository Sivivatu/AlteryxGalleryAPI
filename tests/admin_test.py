import pytest
from AlteryxGallery import AlteryxGalleryAPI as ag
from decouple import config


client_key = config('client_key')
client_secret = config('client_secret')
apiLocation = config('gallery_url')

con = ag.Gallery(apiLocation, client_key, client_secret)