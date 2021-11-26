from decouple import config
from Alteryx_Gallery.api_connections.subscription import GallerySubscription


client_key = config('client_key')
client_secret = config('client_secret')
apiLocation = config('gallery_url')

test_conn = GallerySubscription(apiLocation, client_key, client_secret)


def test_subscription():
    response = test_conn.subscription()[0]
    assert response.status_code is response


def test_questions():
    assert True
