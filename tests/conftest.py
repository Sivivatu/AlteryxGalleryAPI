import pytest
from decouple import config


from Alteryx_Gallery.api_connections.admin import GalleryAdmin
from Alteryx_Gallery.api_connections.subscription import GallerySubscription


@pytest.fixture(scope="session")
def api_con():
    client_key = config('client_key')
    client_secret = config('client_secret')
    apiLocation = config('gallery_url')

    with GallerySubscription(apiLocation, client_secret, client_key) as test_conn:
        return test_conn


@pytest.fixture(scope="session")
def api_admin_con():
    admin_client_key = config('admin_client_key')
    admin_client_secret = config('admin_client_secret')
    apiLocation = config('gallery_url')

    with GalleryAdmin(apiLocation, admin_client_secret, admin_client_key) as test_admin_conn:
        return test_admin_conn
