import secrets
from decouple import config
from Alteryx_Gallery.api_connections.subscription import GallerySubscription
import logging


nonce = secrets.token_urlsafe(5)

logging.info(nonce)

client_key = config('client_key')
client_secret = config('client_secret')
apiLocation = config('gallery_url')

test_conn = GallerySubscription(apiLocation, client_secret, client_key)

response = test_conn.subscription()

logging.info(response[0].status_code)
