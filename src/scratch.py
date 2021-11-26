from decouple import config
from Alteryx_Gallery.api_connections.subscription import GallerySubscription
import logging
import sys

from Alteryx_Gallery.api_connections.admin import GalleryAdmin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

client_key = config('client_key')
client_secret = config('client_secret')
apiLocation = config('gallery_url')
admin_client_key = config('admin_client_key')
admin_client_secret = config('admin_client_secret')

test_conn = GallerySubscription(apiLocation, client_key, client_secret)

response = test_conn.subscription()

logging.info(response[0].status_code)

admin_conn = GalleryAdmin(apiLocation, admin_client_key, admin_client_secret)
res = admin_conn.get_workflows_migratable()
logging.info(res[0].status_code)
logging.info(res[0].content)
