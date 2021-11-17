import pytest
from decouple import config

from alteryxGallery.gallery_connection import Gallery
from alteryxGallery.api_connections.admin import GalleryAdmin
from alteryxGallery.api_connections.gallery import GalleryUser

@pytest.fixture(scope="session")
def api_con():
    client_key = config('client_key')
    client_secret = config('client_secret')
    apiLocation = config('gallery_url')

    with Gallery(apiLocation, client_secret, client_key) as test_conn:
        yield test_conn


@pytest.fixture(scope="session")
def api_con():
    admin_client_key = config('admin_client_key')
    admin_client_secret = config('admin_client_secret')
    apiLocation = config('gallery_url')

    with GalleryAdmin(apiLocation, admin_client_secret, admin_client_key) as test_admin_conn:
        yield test_admin_conn
